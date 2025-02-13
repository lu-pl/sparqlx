"""SPARQLWrapper: Simple Python wrapper around a SPARQL service."""

import asyncio
from collections.abc import Iterable, Iterator
import logging
from typing import Any, Literal as TypingLiteral, Self
import warnings

import httpx
from rdflib import BNode, Literal, URIRef


logger = logging.getLogger(__name__)
warnings.simplefilter("always")


class _SPARQLBase:
    def __init__(
        self,
        endpoint: str,
        output_format: TypingLiteral["json"] = "json",
        headers: dict | None = None,
    ) -> None:
        """Base class for SPARQLWrapper, SPARQLClient and AsyncSPARQLClient."""
        self.endpoint = endpoint
        self.output_format = output_format

        self._json_headers = {"Accept": "application/sparql-results+json"}
        self.headers = self._json_headers if headers is None else headers

    @staticmethod
    def _to_python(response: httpx.Response) -> Iterator[dict[str, Any]]:
        """Get flat dicts from a SPARQL SELECT JSON response."""
        json_response = response.json()
        variables = json_response["head"]["vars"]
        response_bindings = json_response["results"]["bindings"]

        def _get_binding_pairs(binding) -> Iterator[tuple[str, Any]]:
            """Generate key value pairs from response_bindings.

            The 'type' and 'datatype' fields of the JSON response
            are examined to cast values to Python types according to RDFLib.
            """
            for var in variables:
                if (binding_data := binding.get(var, None)) is None:
                    yield (var, None)
                    continue

                match binding_data["type"]:
                    case "uri":
                        yield (var, URIRef(binding_data["value"]))
                    case "literal":
                        yield (
                            var,
                            Literal(
                                binding_data["value"],
                                datatype=binding_data.get("datatype", None),
                            ).toPython(),
                        )
                    case "bnode":
                        yield (var, BNode(binding_data["value"]))
                    case _:  # pragma: no cover
                        assert False, "This should never happen."

        for binding in response_bindings:
            yield dict(_get_binding_pairs(binding))


class SPARQLClient(_SPARQLBase):
    """Context manager for running SPARQL queries against an endpoint.

    SPARQLClient is a wrapper over httpx.Client.
    For an asynchronous context manager interface see sparqlwrapper.AsyncSPARQLClient.

    If client is supplied, client management is the supplier's responsibility;
    else, an httpx.Client instance is created and management by SPARQLClient.

    Note that not closing a SPARQLClient/AsyncSPARQLClient on exit
    is not necessarily a problem as long as the client/aclient is closed at some point.
    """

    def __init__(
        self,
        *args,
        client: httpx.Client | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.client: httpx.Client = httpx.Client() if client is None else client
        # track client ownership
        self._owns_client: bool = client is None

    def query(
        self, query: str, to_python: bool = False
    ) -> httpx.Response | Iterator[dict[str, Any]]:
        """Run a query against endpoint.

        This method is intended to be used in the SPARQLWrapper context,
        else httpx.Client must be closed explicitely.
        """
        data = {"output": self.output_format, "query": query}
        response = self.client.post(self.endpoint, headers=self.headers, data=data)

        if to_python:
            return self._to_python(response)
        return response

    def _close(self) -> None:
        if self._owns_client and not self.client.is_closed:
            self.client.close()

        elif not self._owns_client and not self.client.is_closed:
            warnings.warn(
                f"SPARQLWrapper client '{self.client}' is still open.", ResourceWarning
            )

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._close()


class AsyncSPARQLClient(_SPARQLBase):
    """Asynchronous context manager for running SPARQL queries against an endpoint.

    AsyncSPARQLClient is a wrapper over httpx.AsyncClient.
    For a synchronous context manager interface see sparqlwrapper.SPARQLClient.

    If aclient is supplied, client management is the supplier's responsibility;
    else, an httpx.AsyncClient instance is created and management by SPARQLClient.

    Note that not closing a SPARQLClient/AsyncSPARQLClient on exit
    is not necessarily a problem as long as the client/aclient is closed at some point.
    """

    def __init__(
        self, *args, aclient: httpx.AsyncClient | None = None, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self.aclient: httpx.AsyncClient = (
            httpx.AsyncClient() if aclient is None else aclient
        )
        # track aclient ownership
        self._owns_aclient: bool = aclient is None

    async def aquery(
        self, query: str, to_python: bool = False
    ) -> httpx.Response | Iterator[dict[str, Any]]:
        data = {"output": self.output_format, "query": query}
        response = await self.aclient.post(
            self.endpoint, headers=self.headers, data=data
        )

        if to_python:
            return self._to_python(response)
        return response

    async def aqueries(
        self, queries: Iterable[str], to_python: bool = False
    ) -> list[httpx.Response] | list[dict[str, Any]]:
        coros = [self.aquery(query=query, to_python=to_python) for query in queries]
        result = await asyncio.gather(*coros)

        return result

    async def _aclose(self) -> None:
        """Close the HTTP client if it was created by this instance."""
        if self._owns_aclient and not self.aclient.is_closed:
            await self.aclient.aclose()

        elif not self._owns_aclient and not self.aclient.is_closed:
            warnings.warn(
                f"SPARQLWrapper aclient '{self.aclient}' is still open.",
                ResourceWarning,
            )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._aclose()


class SPARQLWrapper(_SPARQLBase):
    """Simple wrapper class for executing SPARQL queries against an endpoint.

    SPARQLWrapper.query executes a single synchronous SPARQL query.
    SPARQLWrapper.queries is a synchronous wrapper over sparqlwrapper.AsyncSPARQLClient
    and therefore executes multiple SPARQL queries asynchronously.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.sparql_client = SPARQLClient(
            endpoint=self.endpoint,
            output_format=self.output_format,
            headers=self.headers,
        )

        self.sparql_aclient = AsyncSPARQLClient(
            endpoint=self.endpoint,
            output_format=self.output_format,
            headers=self.headers,
        )

    def query(
        self, query: str, to_python: bool = False
    ) -> httpx.Response | dict[str, Any]:
        """Run a SPARQL query against endpoint."""

        with self.sparql_client:
            result = self.sparql_client.query(query=query, to_python=to_python)

        assert self.sparql_client.client.is_closed
        return result

    def queries(
        self, queries: Iterable[str], to_python: bool = False
    ) -> list[httpx.Response] | list[Iterator[dict[str, Any]]]:
        """Run multiple SPARQL queries against endpoint asynchronously."""

        async def _awrapper():
            async with self.sparql_aclient:
                result = await self.sparql_aclient.aqueries(
                    queries=queries, to_python=to_python
                )

            return result

        result = asyncio.run(_awrapper())
        assert self.sparql_aclient.aclient.is_closed
        return result
