"""SPARQLWrapper: An httpx-based SPARQL 1.2 Protocol client."""

import asyncio
from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import AbstractAsyncContextManager, AbstractContextManager
import functools
from typing import Literal as TLiteral, Self, overload

import httpx
from rdflib import Graph
from sparqlx.types import (
    AskQuery,
    ConstructQuery,
    DescribeQuery,
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
from sparqlx.utils.utils import _get_query_type, _get_response_converter


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
        query_method: TLiteral["GET", "POST", "POST-direct"] = "POST",
        update_method: TLiteral["POST", "POST-direct"] = "POST",
    ) -> None:
        self._sparql_endpoint = sparql_endpoint
        self._update_endpoint = update_endpoint

        self._query_method = query_method
        self._update_method = update_method

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
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
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
    ) -> httpx.Response: ...

    def query(
        self,
        query: SPARQLQuery,
        convert: bool = False,
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
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

        with self._client_manager.context() as client:
            response = client.request(
                method=params.method,
                url=self._sparql_endpoint,  # type: ignore
                content=params.content,
                data=params.data,
                headers=params.headers,
                params=params.params,
            )
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
    ) -> httpx.Response: ...

    async def aquery(
        self,
        query: SPARQLQuery,
        convert: bool = False,
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
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

        async with self._client_manager.acontext() as aclient:
            response = await aclient.request(
                method=params.method,
                url=self._sparql_endpoint,  # type: ignore
                content=params.content,
                data=params.data,
                headers=params.headers,
                params=params.params,
            )
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
                url=self._sparql_endpoint,  # type: ignore
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
                url=self._sparql_endpoint,  # type: ignore
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
    ) -> Iterator[httpx.Response]: ...

    def queries(
        self,
        *queries: SPARQLQuery,
        convert: bool = False,
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
    ) -> Iterator[httpx.Response | list[SPARQLResultBinding] | Graph | bool]:
        query_component = SPARQLWrapper(
            sparql_endpoint=self._sparql_endpoint,
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
    ) -> httpx.Response:
        params: SPARQLOperationParameters = UpdateOperationParametersConstructor(
            update_request=update_request,
            version=version,
            using_graph_uri=using_graph_uri,
            using_named_graph_uri=using_named_graph_uri,
        ).get_params(method=self._update_method)  # pyright: ignore

        with self._client_manager.context() as client:
            response = client.request(
                method=params.method,
                url=self._update_endpoint,  # type: ignore
                content=params.content,
                data=params.data,
                headers=params.headers,
                params=params.params,
            )
            response.raise_for_status()
            return response

    async def aupdate(
        self,
        update_request: str,
        version: str | None = None,
        using_graph_uri: RequestDataValue = None,
        using_named_graph_uri: RequestDataValue = None,
    ) -> httpx.Response:
        params: SPARQLOperationParameters = UpdateOperationParametersConstructor(
            update_request=update_request,
            version=version,
            using_graph_uri=using_graph_uri,
            using_named_graph_uri=using_named_graph_uri,
        ).get_params(method=self._update_method)  # pyright: ignore

        async with self._client_manager.acontext() as aclient:
            response = await aclient.request(
                method=params.method,
                url=self._update_endpoint,  # type: ignore
                content=params.content,
                data=params.data,
                headers=params.headers,
                params=params.params,
            )
            response.raise_for_status()
            return response

    def updates(
        self,
        *update_requests,
        version: str | None = None,
        using_graph_uri: RequestDataValue = None,
        using_named_graph_uri: RequestDataValue = None,
    ) -> Iterator[httpx.Response]:
        update_component = SPARQLWrapper(
            update_endpoint=self._update_endpoint,
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
                        )
                    )
                    for update_request in update_requests
                ]

            return map(asyncio.Task.result, tasks)

        results = asyncio.run(_runner())
        return results
