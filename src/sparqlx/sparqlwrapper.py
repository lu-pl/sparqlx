"""SPARQLWrapper: An httpx-based SPARQL 1.2 Protocol client."""

import asyncio
from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import AbstractAsyncContextManager, AbstractContextManager
import functools
from typing import Literal as TLiteral, Self, overload

import httpx
from rdflib import Dataset, Graph
from sparqlx.types import (
    AskQuery,
    ConstructQuery,
    DescribeQuery,
    RDFParseSource,
    RequestDataValue,
    SPARQLQuery,
    SPARQLQueryTypeLiteral,
    SPARQLResponseFormat,
    SPARQLResultBinding,
    SelectQuery,
)
from sparqlx.utils.client_manager import ClientManager
from sparqlx.utils.operation_parameters import (
    QueryOperationParametersConstructor,
    SPARQLOperationParameters,
    UpdateOperationParametersConstructor,
)
from sparqlx.utils.transports import (
    AsyncRDFLibQueryTransport,
    AsyncRDFLibUpdateTransport,
    RDFLibQueryTransport,
    RDFLibUpdateTransport,
)
from sparqlx.utils.utils import Endpoint, _get_query_type, _get_response_converter


class SPARQLWrapper(AbstractContextManager, AbstractAsyncContextManager):
    """SPARQLWrapper: An httpx-based SPARQL 1.2 Protocol client.

    The class provides functionality for running SPARQL Query and Update Operations
    according to the SPARQL 1.2 protocol and supports both sync and async interfaces.
    """

    def __init__(
        self,
        sparql_endpoint: str | Graph | None = None,
        update_endpoint: str | Graph | None = None,
        client: httpx.Client | None = None,
        client_config: dict | None = None,
        aclient: httpx.AsyncClient | None = None,
        aclient_config: dict | None = None,
        query_method: TLiteral["GET", "POST", "POST-direct"] = "POST",
        update_method: TLiteral["POST", "POST-direct"] = "POST",
    ) -> None:
        if sparql_endpoint is None and update_endpoint is None:
            raise ValueError(
                "Invalid SPARQLWrapper configuration: "
                "at least one of 'sparql_endpoint' or 'update_endpoint' must be set."
            )
        self._sparql_endpoint = Endpoint(sparql_endpoint)
        self._update_endpoint = Endpoint(update_endpoint)

        self._query_method = query_method
        self._update_method = update_method

        self._client_config: dict = client_config or {}
        self._aclient_config: dict = aclient_config or {}

        self._client_manager = ClientManager(
            client=client,
            client_config=client_config,
            aclient=aclient,
            aclient_config=aclient_config,
        )

    @classmethod
    def from_rdf_source(
        cls, rdf_source: RDFParseSource | Graph, **parse_kwargs
    ) -> Self:
        """Alternative constructor for instantiating a SPARQLWrapper from an RDF source.

        The constructor instantiates a sparqlx.SPARQLWrapper with an rdflib.Graph target;
        the target for both sparql_endpoint and update_endpoint will be either an rdflib.Dataset
        obtained by parsing an RDFParseSource or an rdflib.Graph object passed to the constructor.

        kwargs are forwarded to the rdflib.Graph.parse methods.

        Note that the constructor does not allow to exert control over the constructed SPARQLWrapper;
        the SPARQLWrapper config concerns HTTP targets (clients, client configs and HTTP methods)
        and are effectively meaningless for rdflib.Graph targets.
        """

        graph: Graph = (
            rdf_source
            if isinstance(rdf_source, Graph)
            else Dataset().parse(source=rdf_source, **parse_kwargs)
        )

        return cls(sparql_endpoint=graph, update_endpoint=graph)

    def __enter__(self) -> Self:
        self._client_manager._client = self._client_manager.client
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._client_manager.client.close()

    async def __aenter__(self) -> Self:
        self._client_manager._aclient = self._client_manager.aclient
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self._client_manager.aclient.aclose()

    @overload
    def query(
        self,
        query: SelectQuery,
        convert: TLiteral[True],
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> list[SPARQLResultBinding]: ...

    @overload
    def query(
        self,
        query: AskQuery,
        convert: TLiteral[True],
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> bool: ...

    @overload
    def query(
        self,
        query: ConstructQuery | DescribeQuery,
        convert: TLiteral[True],
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> Graph: ...

    @overload
    def query(
        self,
        query: SPARQLQuery,
        convert: TLiteral[True],
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> list[SPARQLResultBinding] | Graph | bool: ...

    @overload
    def query(
        self,
        query: SPARQLQuery,
        convert: TLiteral[False] = False,
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> httpx.Response: ...

    def query(
        self,
        query: SPARQLQuery,
        convert: bool = False,
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> httpx.Response | list[SPARQLResultBinding] | Graph | bool:
        query_type: SPARQLQueryTypeLiteral = _get_query_type(query=query)

        params: SPARQLOperationParameters = QueryOperationParametersConstructor(
            query=query,
            query_type=query_type,
            response_format=response_format,
            version=version,
            default_graph_uri=default_graph_uri,
            named_graph_uri=named_graph_uri,
        ).get_params(method=self._query_method)  # pyright: ignore

        response_handler = (
            _get_response_converter(
                query_type=query_type, response_format=params.headers["Accept"]
            )
            if convert
            else lambda response: response
        )

        client_context: AbstractContextManager[httpx.Client] = (
            self._client_manager.context()
            if (graph := self._sparql_endpoint.graph) is None
            else httpx.Client(
                **self._client_config,
                transport=RDFLibQueryTransport(
                    query=query,
                    graph=graph,
                    version=version,
                    default_graph_uri=default_graph_uri,
                    named_graph_uri=named_graph_uri,
                ),
            )
        )

        with client_context as client:
            response = client.request(
                method=params.method,
                url=self._sparql_endpoint.url,
                content=params.content,
                data=params.data,
                headers=params.headers,
                params=params.params,
            )

            if raise_for_status:
                response.raise_for_status()

        return response_handler(response=response)

    @overload
    async def aquery(
        self,
        query: SelectQuery,
        convert: TLiteral[True],
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> list[SPARQLResultBinding]: ...

    @overload
    async def aquery(
        self,
        query: AskQuery,
        convert: TLiteral[True],
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> bool: ...

    @overload
    async def aquery(
        self,
        query: ConstructQuery | DescribeQuery,
        convert: TLiteral[True],
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> Graph: ...

    @overload
    async def aquery(
        self,
        query: SPARQLQuery,
        convert: TLiteral[True],
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> list[SPARQLResultBinding] | Graph | bool: ...

    @overload
    async def aquery(
        self,
        query: SPARQLQuery,
        convert: TLiteral[False] = False,
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> httpx.Response: ...

    async def aquery(
        self,
        query: SPARQLQuery,
        convert: bool = False,
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> httpx.Response | list[SPARQLResultBinding] | Graph | bool:
        query_type: SPARQLQueryTypeLiteral = _get_query_type(query=query)

        params: SPARQLOperationParameters = QueryOperationParametersConstructor(
            query=query,
            query_type=query_type,
            response_format=response_format,
            version=version,
            default_graph_uri=default_graph_uri,
            named_graph_uri=named_graph_uri,
        ).get_params(method=self._query_method)  # pyright: ignore

        response_handler = (
            _get_response_converter(
                query_type=query_type, response_format=params.headers["Accept"]
            )
            if convert
            else lambda response: response
        )

        aclient_context: AbstractAsyncContextManager[httpx.AsyncClient] = (
            self._client_manager.acontext()
            if (graph := self._sparql_endpoint.graph) is None
            else httpx.AsyncClient(
                **self._client_config,
                transport=AsyncRDFLibQueryTransport(
                    query=query,
                    graph=graph,
                    version=version,
                    default_graph_uri=default_graph_uri,
                    named_graph_uri=named_graph_uri,
                ),
            )
        )

        async with aclient_context as aclient:
            response = await aclient.request(
                method=params.method,
                url=self._sparql_endpoint.url,
                content=params.content,
                data=params.data,
                headers=params.headers,
                params=params.params,
            )

            if raise_for_status:
                response.raise_for_status()

        return response_handler(response=response)

    def query_stream[T](
        self,
        query: SPARQLQuery,
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        streaming_method: Callable[
            [httpx.Response], Iterator[T]
        ] = httpx.Response.iter_bytes,
        chunk_size: int | None = None,
    ) -> Iterator[T]:
        if self._sparql_endpoint.graph is not None:
            msg = "Response streaming is currently not supported for rdflib.Graph targets."
            raise NotImplementedError(msg)

        query_type: SPARQLQueryTypeLiteral = _get_query_type(query=query)

        params: SPARQLOperationParameters = QueryOperationParametersConstructor(
            query=query,
            query_type=query_type,
            response_format=response_format,
            version=version,
            default_graph_uri=default_graph_uri,
            named_graph_uri=named_graph_uri,
        ).get_params(method=self._query_method)  # pyright: ignore

        _streaming_method = (
            streaming_method
            if chunk_size is None
            else functools.partial(streaming_method, chunk_size=chunk_size)  # type: ignore
        )

        with self._client_manager.context() as client:
            with client.stream(
                method=params.method,
                url=self._sparql_endpoint.url,
                content=params.content,
                data=params.data,
                headers=params.headers,
                params=params.params,
            ) as response:
                response.raise_for_status()

                for chunk in _streaming_method(response):
                    yield chunk

    async def aquery_stream[T](
        self,
        query: SPARQLQuery,
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        streaming_method: Callable[
            [httpx.Response], AsyncIterator[T]
        ] = httpx.Response.aiter_bytes,
        chunk_size: int | None = None,
    ) -> AsyncIterator[T]:
        if self._sparql_endpoint.graph is not None:
            msg = "Response streaming is currently not supported for rdflib.Graph targets."
            raise NotImplementedError(msg)

        query_type: SPARQLQueryTypeLiteral = _get_query_type(query=query)

        params: SPARQLOperationParameters = QueryOperationParametersConstructor(
            query=query,
            query_type=query_type,
            response_format=response_format,
            version=version,
            default_graph_uri=default_graph_uri,
            named_graph_uri=named_graph_uri,
        ).get_params(method=self._query_method)  # pyright: ignore

        _streaming_method = (
            streaming_method
            if chunk_size is None
            else functools.partial(streaming_method, chunk_size=chunk_size)  # type: ignore
        )

        async with self._client_manager.acontext() as aclient:
            async with aclient.stream(
                method=params.method,
                url=self._sparql_endpoint.url,
                content=params.content,
                data=params.data,
                headers=params.headers,
                params=params.params,
            ) as response:
                response.raise_for_status()

                async for chunk in _streaming_method(response):
                    yield chunk

    @overload
    def queries(
        self,
        *queries: SPARQLQuery,
        convert: TLiteral[True],
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> Iterator[list[SPARQLResultBinding] | Graph | bool]: ...

    @overload
    def queries(
        self,
        *queries: SPARQLQuery,
        convert: TLiteral[False] = False,
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> Iterator[httpx.Response]: ...

    def queries(
        self,
        *queries: SPARQLQuery,
        convert: bool = False,
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> Iterator[httpx.Response | list[SPARQLResultBinding] | Graph | bool]:
        query_component = SPARQLWrapper(
            sparql_endpoint=self._sparql_endpoint._endpoint,
            aclient=self._client_manager.aclient,
            query_method=self._query_method,  # pyright: ignore
        )

        async def _runner() -> Iterator[httpx.Response]:
            async with query_component, asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(
                        query_component.aquery(
                            query=query,
                            convert=convert,
                            response_format=response_format,
                            version=version,
                            default_graph_uri=default_graph_uri,
                            named_graph_uri=named_graph_uri,
                            raise_for_status=raise_for_status,
                        )
                    )
                    for query in queries
                ]

            return map(asyncio.Task.result, tasks)

        results = asyncio.run(_runner())
        return results

    def update(
        self,
        update_request: str,
        version: str | None = None,
        using_graph_uri: RequestDataValue = None,
        using_named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        params: SPARQLOperationParameters = UpdateOperationParametersConstructor(
            update_request=update_request,
            version=version,
            using_graph_uri=using_graph_uri,
            using_named_graph_uri=using_named_graph_uri,
        ).get_params(method=self._update_method)  # pyright: ignore

        client_context: AbstractContextManager[httpx.Client] = (
            self._client_manager.context()
            if (graph := self._update_endpoint.graph) is None
            else httpx.Client(
                **self._client_config,
                transport=RDFLibUpdateTransport(
                    update_request=update_request,
                    graph=graph,
                    version=version,
                    using_graph_uri=using_graph_uri,
                    using_named_graph_uri=using_named_graph_uri,
                ),
            )
        )

        with client_context as client:
            response = client.request(
                method=params.method,
                url=self._update_endpoint.url,
                content=params.content,
                data=params.data,
                headers=params.headers,
                params=params.params,
            )

            if raise_for_status:
                response.raise_for_status()

            return response

    async def aupdate(
        self,
        update_request: str,
        version: str | None = None,
        using_graph_uri: RequestDataValue = None,
        using_named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        params: SPARQLOperationParameters = UpdateOperationParametersConstructor(
            update_request=update_request,
            version=version,
            using_graph_uri=using_graph_uri,
            using_named_graph_uri=using_named_graph_uri,
        ).get_params(method=self._update_method)  # pyright: ignore

        aclient_context: AbstractAsyncContextManager[httpx.AsyncClient] = (
            self._client_manager.acontext()
            if (graph := self._update_endpoint.graph) is None
            else httpx.AsyncClient(
                **self._aclient_config,
                transport=AsyncRDFLibUpdateTransport(
                    update_request=update_request,
                    graph=graph,
                    version=version,
                    using_graph_uri=using_graph_uri,
                    using_named_graph_uri=using_named_graph_uri,
                ),
            )
        )

        async with aclient_context as aclient:
            response = await aclient.request(
                method=params.method,
                url=self._update_endpoint.url,
                content=params.content,
                data=params.data,
                headers=params.headers,
                params=params.params,
            )

            if raise_for_status:
                response.raise_for_status()

            return response

    def updates(
        self,
        *update_requests,
        version: str | None = None,
        using_graph_uri: RequestDataValue = None,
        using_named_graph_uri: RequestDataValue = None,
        raise_for_status: bool = True,
    ) -> Iterator[httpx.Response]:
        update_component = SPARQLWrapper(
            update_endpoint=self._update_endpoint._endpoint,
            aclient=self._client_manager.aclient,
            update_method=self._update_method,  # pyright: ignore
        )

        async def _runner() -> Iterator[httpx.Response]:
            async with update_component, asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(
                        update_component.aupdate(
                            update_request=update_request,
                            version=version,
                            using_graph_uri=using_graph_uri,
                            using_named_graph_uri=using_named_graph_uri,
                            raise_for_status=raise_for_status,
                        )
                    )
                    for update_request in update_requests
                ]

            return map(asyncio.Task.result, tasks)

        results = asyncio.run(_runner())
        return results
