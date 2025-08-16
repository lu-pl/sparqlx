"""SPARQL query and update operation classes implementing the SPARQL 1.1 Protocol."""

import asyncio
from collections.abc import AsyncIterator, Callable, Iterator
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
from sparqlwrapper.utils.types import _TResponseFormat, _TSPARQLBinding
from sparqlwrapper.utils.utils import QueryParameters, get_query_parameters


class _SPARQLOperationWrapper(AbstractContextManager, AbstractAsyncContextManager):
    def __init__(
        self,
        endpoint: str,
        client: httpx.Client | None = None,
        client_config: dict | None = None,
        aclient: httpx.AsyncClient | None = None,
        aclient_config: dict | None = None,
    ) -> None:
        self.endpoint = endpoint

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
        self.__context_wrapper = self.__class__(
            endpoint=self.endpoint,
            client=self._client,
            client_config=self._client_config,
        )
        return self.__context_wrapper

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.__context_wrapper._client.close()

    async def __aenter__(self) -> Self:
        self.__context_wrapper = self.__class__(
            endpoint=self.endpoint,
            aclient=self._aclient,
            aclient_config=self._aclient_config,
        )
        return self.__context_wrapper

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.__context_wrapper._aclient.aclose()


class _SPARQLQueryWrapper(_SPARQLOperationWrapper):
    @overload
    def query(
        self,
        query: str,
        to_rdflib: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
    ) -> Iterator[_TSPARQLBinding] | Graph: ...

    @overload
    def query(
        self,
        query: str,
        to_rdflib: TLiteral[False] = False,
        response_format: _TResponseFormat | str | None = None,
    ) -> httpx.Response: ...

    def query(
        self,
        query: str,
        to_rdflib: bool = False,
        response_format: _TResponseFormat | str | None = None,
    ) -> httpx.Response | Iterator[_TSPARQLBinding] | Graph:
        query_parameters: QueryParameters = get_query_parameters(
            query=query, to_rdflib=to_rdflib, response_format=response_format
        )

        with self._managed_client() as client:
            response = client.post(
                **self._get_request_params(
                    query=query, response_format=query_parameters.response_format
                )
            )
            response.raise_for_status()

        if to_rdflib:
            return query_parameters.rdflib_converter(response)
        return response

    @overload
    async def aquery(
        self,
        query: str,
        to_rdflib: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
    ) -> Iterator[_TSPARQLBinding] | Graph: ...

    @overload
    async def aquery(
        self,
        query: str,
        to_rdflib: TLiteral[False] = False,
        response_format: _TResponseFormat | str | None = None,
    ) -> httpx.Response: ...

    async def aquery(
        self,
        query: str,
        to_rdflib: bool = False,
        response_format: _TResponseFormat | str | None = None,
    ) -> httpx.Response | Iterator[_TSPARQLBinding] | Graph:
        query_parameters: QueryParameters = get_query_parameters(
            query=query, to_rdflib=to_rdflib, response_format=response_format
        )

        async with self._managed_aclient() as aclient:
            response = await aclient.post(
                **self._get_request_params(
                    query=query, response_format=query_parameters.response_format
                )
            )
            response.raise_for_status()

        if to_rdflib:
            return query_parameters.rdflib_converter(response)
        return response

    def query_stream[T](
        self,
        query: str,
        response_format: _TResponseFormat | str | None = None,
        streaming_method: Callable[
            [httpx.Response], Iterator[T]
        ] = httpx.Response.iter_bytes,
        chunk_size: int | None = None,
    ) -> Iterator[T]:
        query_parameters: QueryParameters = get_query_parameters(
            query=query, response_format=response_format
        )

        _streaming_method = (
            streaming_method
            if chunk_size is None
            else functools.partial(streaming_method, chunk_size=chunk_size)  # type: ignore
        )

        with self._managed_client() as client:
            with client.stream(
                "POST",
                **self._get_request_params(
                    query=query, response_format=query_parameters.response_format
                ),
            ) as response:
                response.raise_for_status()

                for chunk in _streaming_method(response):
                    yield chunk

    async def aquery_stream[T](
        self,
        query: str,
        response_format: _TResponseFormat | str | None = None,
        streaming_method: Callable[
            [httpx.Response], AsyncIterator[T]
        ] = httpx.Response.aiter_bytes,
        chunk_size: int | None = None,
    ) -> AsyncIterator[T]:
        query_parameters: QueryParameters = get_query_parameters(
            query=query, response_format=response_format
        )

        _streaming_method = (
            streaming_method
            if chunk_size is None
            else functools.partial(streaming_method, chunk_size=chunk_size)  # type: ignore
        )

        async with self._managed_aclient() as aclient:
            async with aclient.stream(
                "POST",
                **self._get_request_params(
                    query=query, response_format=query_parameters.response_format
                ),
            ) as response:
                response.raise_for_status()

                async for chunk in _streaming_method(response):
                    yield chunk

    @overload
    def queries(
        self,
        *queries: str,
        to_rdflib: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
    ) -> Iterator[Iterator[_TSPARQLBinding]] | Iterator[Graph]: ...

    @overload
    def queries(
        self,
        *queries: str,
        to_rdflib: TLiteral[False] = False,
        response_format: _TResponseFormat | str | None = None,
    ) -> Iterator[httpx.Response]: ...

    def queries(
        self,
        *queries: str,
        to_rdflib: bool = False,
        response_format: _TResponseFormat | str | None = None,
    ) -> (
        Iterator[Iterator[_TSPARQLBinding]] | Iterator[httpx.Response] | Iterator[Graph]
    ):
        query_component = _SPARQLQueryWrapper(
            endpoint=self.endpoint, aclient=self._aclient
        )

        async def _runner() -> Iterator[httpx.Response]:
            async with query_component, asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(
                        query_component.aquery(
                            query=query,
                            to_rdflib=to_rdflib,
                            response_format=response_format,
                        )
                    )
                    for query in queries
                ]

            return map(asyncio.Task.result, tasks)

        results = asyncio.run(_runner())
        return results

    def _get_request_params(self, query: str, response_format: str) -> dict:
        return {
            "url": self.endpoint,
            "data": {"query": query},
            "headers": {"Accept": response_format},
        }


class _SPARQLUpdateWrapper(_SPARQLOperationWrapper):
    def update(
        self,
        update_request: str,
    ) -> httpx.Response:
        raise NotImplementedError

    def aupdate(
        self,
        update_request: str,
    ) -> httpx.Response:
        raise NotImplementedError

    def updates(self, *update_requests) -> Iterator[httpx.Response]:
        raise NotImplementedError


class SPARQLWrapper(_SPARQLQueryWrapper, _SPARQLUpdateWrapper):
    """Simple wrapper around a SPARQL service.

    The class provides functionality for running SPARQL Query and Update Operations
    according to the SPARQL 1.1 protocol.
    """
