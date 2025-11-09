"""SPARQLWrapper: An httpx-based SPARQL 1.2 Protocol client."""

import asyncio
from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import AbstractAsyncContextManager, AbstractContextManager
import functools
from typing import Literal as TLiteral, Self, overload

import httpx
from rdflib import Graph
from sparqlx.utils.client_manager import ClientManager
from sparqlx.utils.types import (
    AskQuery,
    ConstructQuery,
    DescribeQuery,
    SelectQuery,
    _TQuery,
    _TRequestDataValue,
    _TResponseFormat,
    _TSPARQLBinding,
)
from sparqlx.utils.utils import QueryOperationParameters, UpdateOperationParameters


class SPARQLWrapper(AbstractContextManager, AbstractAsyncContextManager):
    """SPARQLWrapper: An httpx-based SPARQL 1.2 Protocol client.

    The class provides functionality for running SPARQL Query and Update Operations
    according to the SPARQL 1.2 protocol and supports both sync and async interfaces.
    """

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

        self._client_manager = ClientManager(
            client=client,
            client_config=client_config,
            aclient=aclient,
            aclient_config=aclient_config,
        )

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
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> list[_TSPARQLBinding]: ...

    @overload
    def query(
        self,
        query: AskQuery,
        convert: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> bool: ...

    @overload
    def query(
        self,
        query: ConstructQuery | DescribeQuery,
        convert: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> Graph: ...

    @overload
    def query(
        self,
        query: _TQuery,
        convert: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> list[_TSPARQLBinding] | Graph | bool: ...

    @overload
    def query(
        self,
        query: _TQuery,
        convert: TLiteral[False] = False,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> httpx.Response: ...

    def query(
        self,
        query: _TQuery,
        convert: bool = False,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> httpx.Response | list[_TSPARQLBinding] | Graph | bool:
        params = QueryOperationParameters(
            query=query,
            convert=convert,
            response_format=response_format,
            version=version,
            default_graph_uri=default_graph_uri,
            named_graph_uri=named_graph_uri,
        )

        with self._client_manager.context() as client:
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
        query: SelectQuery,
        convert: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> list[_TSPARQLBinding]: ...

    @overload
    async def aquery(
        self,
        query: AskQuery,
        convert: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> bool: ...

    @overload
    async def aquery(
        self,
        query: ConstructQuery | DescribeQuery,
        convert: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> Graph: ...

    @overload
    async def aquery(
        self,
        query: _TQuery,
        convert: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> list[_TSPARQLBinding] | Graph | bool: ...

    @overload
    async def aquery(
        self,
        query: _TQuery,
        convert: TLiteral[False] = False,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> httpx.Response: ...

    async def aquery(
        self,
        query: _TQuery,
        convert: bool = False,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> httpx.Response | list[_TSPARQLBinding] | Graph | bool:
        params = QueryOperationParameters(
            query=query,
            convert=convert,
            response_format=response_format,
            version=version,
            default_graph_uri=default_graph_uri,
            named_graph_uri=named_graph_uri,
        )

        async with self._client_manager.acontext() as aclient:
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
        query: _TQuery,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
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

        with self._client_manager.context() as client:
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
        query: _TQuery,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
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

        async with self._client_manager.acontext() as aclient:
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
        *queries: _TQuery,
        convert: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> Iterator[list[_TSPARQLBinding] | Graph | bool]: ...

    @overload
    def queries(
        self,
        *queries: _TQuery,
        convert: TLiteral[False] = False,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> Iterator[httpx.Response]: ...

    def queries(
        self,
        *queries: _TQuery,
        convert: bool = False,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> Iterator[httpx.Response | list[_TSPARQLBinding] | Graph | bool]:
        query_component = SPARQLWrapper(
            sparql_endpoint=self.sparql_endpoint, aclient=self._client_manager.aclient
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
        using_graph_uri: _TRequestDataValue = None,
        using_named_graph_uri: _TRequestDataValue = None,
    ) -> httpx.Response:
        params = UpdateOperationParameters(
            update_request=update_request,
            version=version,
            using_graph_uri=using_graph_uri,
            using_named_graph_uri=using_named_graph_uri,
        )

        with self._client_manager.context() as client:
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
        using_graph_uri: _TRequestDataValue = None,
        using_named_graph_uri: _TRequestDataValue = None,
    ) -> httpx.Response:
        params = UpdateOperationParameters(
            update_request=update_request,
            version=version,
            using_graph_uri=using_graph_uri,
            using_named_graph_uri=using_named_graph_uri,
        )

        async with self._client_manager.acontext() as aclient:
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
        using_graph_uri: _TRequestDataValue = None,
        using_named_graph_uri: _TRequestDataValue = None,
    ) -> Iterator[httpx.Response]:
        update_component = SPARQLWrapper(
            update_endpoint=self.update_endpoint, aclient=self._client_manager.aclient
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
