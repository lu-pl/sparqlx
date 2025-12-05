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
        """Initialize a new SPARQLWrapper instance.

        Args:
            sparql_endpoint: URL of the SPARQL query endpoint.
            update_endpoint: URL of the SPARQL update endpoint.
            client: Optional pre-configured httpx.Client for synchronous requests.
            client_config: Configuration dict for creating a new httpx.Client if
                client is not provided.
            aclient: Optional pre-configured httpx.AsyncClient for async requests.
            aclient_config: Configuration dict for creating a new httpx.AsyncClient
                if aclient is not provided.

        """
        self.sparql_endpoint = sparql_endpoint
        self.update_endpoint = update_endpoint

        self._client_manager = ClientManager(
            client=client,
            client_config=client_config,
            aclient=aclient,
            aclient_config=aclient_config,
        )

    def __enter__(self) -> Self:
        """Enter the synchronous context manager.

        Returns:
            Self: The SPARQLWrapper instance.

        """
        self._client_manager._client = self._client_manager.client
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit the synchronous context manager and close the client.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_value: Exception value if an exception occurred.
            traceback: Traceback if an exception occurred.

        """
        self._client_manager.client.close()

    async def __aenter__(self) -> Self:
        """Enter the asynchronous context manager.

        Returns:
            Self: The SPARQLWrapper instance.

        """
        self._client_manager._aclient = self._client_manager.aclient
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """Exit the asynchronous context manager and close the async client.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_value: Exception value if an exception occurred.
            traceback: Traceback if an exception occurred.

        """
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
        """Execute a SPARQL query synchronously.

        Args:
            query: The SPARQL query string. Can be a SelectQuery, AskQuery,
                ConstructQuery, or DescribeQuery for type-safe results.
            convert: If True, convert the response to a Python object
                (list of bindings, Graph, or bool). If False, return the
                raw httpx.Response.
            response_format: Desired response format (e.g., 'json', 'xml', 'turtle').
                If not specified, defaults are chosen based on query type.
            version: SPARQL version parameter to include in the request.
            default_graph_uri: URI(s) of default graph(s) to query. Can be a single
                URI string or a list of URI strings.
            named_graph_uri: URI(s) of named graph(s) to query. Can be a single
                URI string or a list of URI strings.

        Returns:
            If convert=True, returns type-specific results:
                - SelectQuery: list[_TSPARQLBinding]
                - AskQuery: bool
                - ConstructQuery/DescribeQuery: rdflib.Graph
            If convert=False, returns the raw httpx.Response.

        Raises:
            httpx.HTTPStatusError: If the request returns an error status code.

        """
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
        """Execute a SPARQL query asynchronously.

        Args:
            query: The SPARQL query string. Can be a SelectQuery, AskQuery,
                ConstructQuery, or DescribeQuery for type-safe results.
            convert: If True, convert the response to a Python object
                (list of bindings, Graph, or bool). If False, return the
                raw httpx.Response.
            response_format: Desired response format (e.g., 'json', 'xml', 'turtle').
                If not specified, defaults are chosen based on query type.
            version: SPARQL version parameter to include in the request.
            default_graph_uri: URI(s) of default graph(s) to query. Can be a single
                URI string or a list of URI strings.
            named_graph_uri: URI(s) of named graph(s) to query. Can be a single
                URI string or a list of URI strings.

        Returns:
            If convert=True, returns type-specific results:
                - SelectQuery: list[_TSPARQLBinding]
                - AskQuery: bool
                - ConstructQuery/DescribeQuery: rdflib.Graph
            If convert=False, returns the raw httpx.Response.

        Raises:
            httpx.HTTPStatusError: If the request returns an error status code.

        """
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
        """Execute a SPARQL query and stream the response synchronously.

        Args:
            query: The SPARQL query string.
            response_format: Desired response format (e.g., 'json', 'xml', 'turtle').
            version: SPARQL version parameter to include in the request.
            default_graph_uri: URI(s) of default graph(s) to query.
            named_graph_uri: URI(s) of named graph(s) to query.
            streaming_method: Method to use for streaming the response.
                Defaults to httpx.Response.iter_bytes.
            chunk_size: Size of chunks to stream. If None, uses the streaming
                method's default chunk size.

        Yields:
            Chunks of type T as determined by the streaming_method.

        Raises:
            httpx.HTTPStatusError: If the request returns an error status code.

        """
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
        """Execute a SPARQL query and stream the response asynchronously.

        Args:
            query: The SPARQL query string.
            response_format: Desired response format (e.g., 'json', 'xml', 'turtle').
            version: SPARQL version parameter to include in the request.
            default_graph_uri: URI(s) of default graph(s) to query.
            named_graph_uri: URI(s) of named graph(s) to query.
            streaming_method: Method to use for streaming the response.
                Defaults to httpx.Response.aiter_bytes.
            chunk_size: Size of chunks to stream. If None, uses the streaming
                method's default chunk size.

        Yields:
            Chunks of type T as determined by the streaming_method.

        Raises:
            httpx.HTTPStatusError: If the request returns an error status code.

        """
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
        """Execute multiple SPARQL queries concurrently.

        This method runs multiple queries in parallel using asyncio.TaskGroup
        and returns their results as an iterator.

        Args:
            *queries: Variable number of SPARQL query strings to execute.
            convert: If True, convert responses to Python objects. If False,
                return raw httpx.Response objects.
            response_format: Desired response format for all queries.
            version: SPARQL version parameter for all queries.
            default_graph_uri: URI(s) of default graph(s) for all queries.
            named_graph_uri: URI(s) of named graph(s) for all queries.

        Returns:
            Iterator of results, one for each query in the order they were provided.

        Raises:
            httpx.HTTPStatusError: If any request returns an error status code.

        """
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
        """Execute a SPARQL Update operation synchronously.

        Args:
            update_request: The SPARQL Update request string.
            version: SPARQL version parameter to include in the request.
            using_graph_uri: URI(s) of graph(s) to use for the update operation.
                Can be a single URI string or a list of URI strings.
            using_named_graph_uri: URI(s) of named graph(s) to use for the update.
                Can be a single URI string or a list of URI strings.

        Returns:
            The raw httpx.Response from the update endpoint.

        Raises:
            httpx.HTTPStatusError: If the request returns an error status code.

        """
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
        """Execute a SPARQL Update operation asynchronously.

        Args:
            update_request: The SPARQL Update request string.
            version: SPARQL version parameter to include in the request.
            using_graph_uri: URI(s) of graph(s) to use for the update operation.
                Can be a single URI string or a list of URI strings.
            using_named_graph_uri: URI(s) of named graph(s) to use for the update.
                Can be a single URI string or a list of URI strings.

        Returns:
            The raw httpx.Response from the update endpoint.

        Raises:
            httpx.HTTPStatusError: If the request returns an error status code.

        """
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
        """Execute multiple SPARQL Update operations concurrently.

        This method runs multiple update operations in parallel using asyncio.TaskGroup
        and returns their results as an iterator.

        Args:
            *update_requests: Variable number of SPARQL Update request strings to execute.
            version: SPARQL version parameter for all update operations.
            using_graph_uri: URI(s) of graph(s) to use for all update operations.
            using_named_graph_uri: URI(s) of named graph(s) to use for all updates.

        Returns:
            Iterator of httpx.Response objects, one for each update request in
            the order they were provided.

        Raises:
            httpx.HTTPStatusError: If any request returns an error status code.

        """
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
