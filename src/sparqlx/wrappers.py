"""SPARQL query and update operation classes implementing the SPARQL 1.1 Protocol."""

import asyncio
from collections.abc import AsyncIterator, Callable, Iterable, Iterator
from contextlib import (
    AbstractAsyncContextManager,
    AbstractContextManager,
    asynccontextmanager,
    contextmanager,
)
import functools
from typing import Literal as TLiteral, Self, overload
import warnings

import httpx
from rdflib import Graph

from sparqlx.utils.types import _TResponseFormat, _TSPARQLBinding
from sparqlx.utils.utils import QueryOperationParameters, UpdateOperationParameters


class _SPARQLOperationWrapper(AbstractContextManager, AbstractAsyncContextManager):
    def __init__(
        self,
        sparql_endpoint: str | None = None,
        update_endpoint: str | None = None,
        client: httpx.Client | None = None,
        client_config: dict | None = None,
        aclient: httpx.AsyncClient | None = None,
        aclient_config: dict | None = None,
    ) -> None:
        self.sparql_endpoint = sparql_endpoint
        self.update_endpoint = update_endpoint

        self.client: httpx.Client | None = client
        self._client_config: dict = client_config or {}

        self.aclient: httpx.AsyncClient | None = aclient
        self._aclient_config: dict = aclient_config or {}

        self._manage_client: bool = client is None
        self._manage_aclient: bool = aclient is None

    @property
    def _client(self) -> httpx.Client:
        if self._manage_client:
            return httpx.Client(**self._client_config)

        assert isinstance(self.client, httpx.Client)  # type narrow
        return self.client

    @property
    def _aclient(self) -> httpx.AsyncClient:
        if self._manage_aclient:
            return httpx.AsyncClient(**self._aclient_config)

        assert isinstance(self.aclient, httpx.AsyncClient)  # type narrow
        return self.aclient

    @contextmanager
    def _managed_client(self) -> Iterator[httpx.Client]:
        client = self._client
        yield client

        if self._manage_client:
            client.close()
            return
        self._open_client_warning(client)

    @asynccontextmanager
    async def _managed_aclient(self) -> AsyncIterator[httpx.AsyncClient]:
        aclient = self._aclient
        yield aclient

        if self._manage_aclient:
            await aclient.aclose()
            return
        self._open_client_warning(aclient)

    @staticmethod
    def _open_client_warning(client: httpx.Client | httpx.AsyncClient) -> None:
        msg = (
            f"httpx Client instance '{client}' is not managed. "
            "Client.close/AsyncClient.aclose should be called at some point."
        )
        warnings.warn(msg, stacklevel=2)

    def __enter__(self) -> Self:
        self.client = self._client
        self._manage_client = False
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        assert isinstance(self.client, httpx.Client)  # type narrow
        self.client.close()

    async def __aenter__(self) -> Self:
        self.aclient = self._aclient
        self._manage_aclient = False
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        assert isinstance(self.aclient, httpx.AsyncClient)  # type narrow
        await self.aclient.aclose()


class SPARQLWrapper(_SPARQLOperationWrapper):
    """SPARQLWrapper: An httpx-based SPARQL client.

    The class provides functionality for running SPARQL Query and Update Operations
    according to the SPARQL 1.2 protocol and supports both sync and async interfaces.
    """

    @overload
    def query(
        self,
        query: str,
        convert: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: str | Iterable[str] | None = None,
        named_graph_uri: str | Iterable[str] | None = None,
    ) -> Iterator[_TSPARQLBinding] | Graph | bool: ...

    @overload
    def query(
        self,
        query: str,
        convert: TLiteral[False] = False,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: str | Iterable[str] | None = None,
        named_graph_uri: str | Iterable[str] | None = None,
    ) -> httpx.Response: ...

    def query(
        self,
        query: str,
        convert: bool = False,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: str | Iterable[str] | None = None,
        named_graph_uri: str | Iterable[str] | None = None,
    ) -> httpx.Response | Iterator[_TSPARQLBinding] | Graph | bool:
        params = QueryOperationParameters(
            query=query,
            convert=convert,
            response_format=response_format,
            version=version,
            default_graph_uri=default_graph_uri,
            named_graph_uri=named_graph_uri,
        )

        with self._managed_client() as client:
            response = client.post(
                url=self.sparql_endpoint,  # type: ignore
                data=params.data,
                headers=params.headers,
            )
            response.raise_for_status()

        if convert:
            return params.converter(response=response)
        return response

    @overload
    async def aquery(
        self,
        query: str,
        convert: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: str | Iterable[str] | None = None,
        named_graph_uri: str | Iterable[str] | None = None,
    ) -> Iterator[_TSPARQLBinding] | Graph | bool: ...

    @overload
    async def aquery(
        self,
        query: str,
        convert: TLiteral[False] = False,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: str | Iterable[str] | None = None,
        named_graph_uri: str | Iterable[str] | None = None,
    ) -> httpx.Response: ...

    async def aquery(
        self,
        query: str,
        convert: bool = False,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: str | Iterable[str] | None = None,
        named_graph_uri: str | Iterable[str] | None = None,
    ) -> httpx.Response | Iterator[_TSPARQLBinding] | Graph | bool:
        params = QueryOperationParameters(
            query=query,
            convert=convert,
            response_format=response_format,
            version=version,
            default_graph_uri=default_graph_uri,
            named_graph_uri=named_graph_uri,
        )

        async with self._managed_aclient() as aclient:
            response = await aclient.post(
                url=self.sparql_endpoint,  # type: ignore
                data=params.data,
                headers=params.headers,
            )
            response.raise_for_status()

        if convert:
            return params.converter(response=response)
        return response

    def query_stream[T](
        self,
        query: str,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: str | Iterable[str] | None = None,
        named_graph_uri: str | Iterable[str] | None = None,
        streaming_method: Callable[
            [httpx.Response], Iterator[T]
        ] = httpx.Response.iter_bytes,
        chunk_size: int | None = None,
    ) -> Iterator[T]:
        params = QueryOperationParameters(
            query=query,
            response_format=response_format,
            version=version,
            default_graph_uri=default_graph_uri,
            named_graph_uri=named_graph_uri,
        )

        _streaming_method = (
            streaming_method
            if chunk_size is None
            else functools.partial(streaming_method, chunk_size=chunk_size)  # type: ignore
        )

        with self._managed_client() as client:
            with client.stream(
                "POST",
                url=self.sparql_endpoint,  # type: ignore
                data=params.data,
                headers=params.headers,
            ) as response:
                response.raise_for_status()

                for chunk in _streaming_method(response):
                    yield chunk

    async def aquery_stream[T](
        self,
        query: str,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: str | Iterable[str] | None = None,
        named_graph_uri: str | Iterable[str] | None = None,
        streaming_method: Callable[
            [httpx.Response], AsyncIterator[T]
        ] = httpx.Response.aiter_bytes,
        chunk_size: int | None = None,
    ) -> AsyncIterator[T]:
        params = QueryOperationParameters(
            query=query,
            response_format=response_format,
            version=version,
            default_graph_uri=default_graph_uri,
            named_graph_uri=named_graph_uri,
        )

        _streaming_method = (
            streaming_method
            if chunk_size is None
            else functools.partial(streaming_method, chunk_size=chunk_size)  # type: ignore
        )

        async with self._managed_aclient() as aclient:
            async with aclient.stream(
                "POST",
                url=self.sparql_endpoint,  # type: ignore
                data=params.data,
                headers=params.headers,
            ) as response:
                response.raise_for_status()

                async for chunk in _streaming_method(response):
                    yield chunk

    @overload
    def queries(
        self,
        *queries: str,
        convert: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: str | Iterable[str] | None = None,
        named_graph_uri: str | Iterable[str] | None = None,
    ) -> Iterator[Iterator[_TSPARQLBinding] | Graph | bool]: ...

    @overload
    def queries(
        self,
        *queries: str,
        convert: TLiteral[False] = False,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: str | Iterable[str] | None = None,
        named_graph_uri: str | Iterable[str] | None = None,
    ) -> Iterator[httpx.Response]: ...

    def queries(
        self,
        *queries: str,
        convert: bool = False,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: str | Iterable[str] | None = None,
        named_graph_uri: str | Iterable[str] | None = None,
    ) -> Iterator[httpx.Response | Iterator[_TSPARQLBinding] | Graph | bool]:
        query_component = SPARQLWrapper(
            sparql_endpoint=self.sparql_endpoint, aclient=self._aclient
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
        using_graph_uri: str | Iterable[str] | None = None,
        using_named_graph_uri: str | Iterable[str] | None = None,
    ) -> httpx.Response:
        params = UpdateOperationParameters(
            update_request=update_request,
            version=version,
            using_graph_uri=using_graph_uri,
            using_named_graph_uri=using_named_graph_uri,
        )

        with self._managed_client() as client:
            response = client.post(
                url=self.update_endpoint,  # type: ignore
                data=params.data,
                headers=params.headers,
            )
            response.raise_for_status()
            return response

    async def aupdate(
        self,
        update_request: str,
        version: str | None = None,
        using_graph_uri: str | Iterable[str] | None = None,
        using_named_graph_uri: str | Iterable[str] | None = None,
    ) -> httpx.Response:
        params = UpdateOperationParameters(
            update_request=update_request,
            version=version,
            using_graph_uri=using_graph_uri,
            using_named_graph_uri=using_named_graph_uri,
        )

        async with self._managed_aclient() as aclient:
            response = await aclient.post(
                url=self.update_endpoint,  # type: ignore
                data=params.data,
                headers=params.headers,
            )
            response.raise_for_status()
            return response

    def updates(
        self,
        *update_requests,
        version: str | None = None,
        using_graph_uri: str | Iterable[str] | None = None,
        using_named_graph_uri: str | Iterable[str] | None = None,
    ) -> Iterator[httpx.Response]:
        update_component = SPARQLWrapper(
            update_endpoint=self.update_endpoint, aclient=self._aclient
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
                        )
                    )
                    for update_request in update_requests
                ]

            return map(asyncio.Task.result, tasks)

        results = asyncio.run(_runner())
        return results
