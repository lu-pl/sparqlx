"""Custom httpx.Transports for rdflb.Graph targets."""

import asyncio

import pyparsing
from rdflib import Graph

import httpx
from sparqlx.types import RequestDataValue, SPARQLQuery


class _RDFLibQueryTransportBase:
    def __init__(
        self,
        query: SPARQLQuery,
        graph: Graph,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
    ) -> None:
        if any(param is not None for param in [default_graph_uri, named_graph_uri]):
            msg = (
                "URI Parameters 'default-graph-uri' and 'named-graph-uri' "
                "are currently not supported for rdflib.Graph targets."
            )

            raise NotImplementedError(msg)

        self._query = query
        self._graph = graph

    def _handle_request(self, request: httpx.Request) -> httpx.Response:
        _format = request.headers["Accept"]

        try:
            content = self._graph.query(self._query).serialize(format=_format)
        except (
            pyparsing.exceptions.ParseBaseException
        ) as e:  # pragma: no cover ; this is currently unreachable
            return httpx.Response(
                status_code=400,
                headers={
                    "Content-Type": "text/plain; charset=utf-8",
                },
                request=request,
                content=str(e),
            )
        except Exception as e:
            return httpx.Response(
                status_code=500,
                headers={
                    "Content-Type": "text/plain; charset=utf-8",
                },
                request=request,
                content=str(e),
            )

        else:
            return httpx.Response(
                status_code=200,
                headers={"Content-Type": _format},
                request=request,
                content=content,
            )


class RDFLibQueryTransport(_RDFLibQueryTransportBase, httpx.BaseTransport):
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        return self._handle_request(request)


class AsyncRDFLibQueryTransport(_RDFLibQueryTransportBase, httpx.AsyncBaseTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        return await asyncio.to_thread(self._handle_request, request)


class _RDFLibUpdateTransportBase(httpx.BaseTransport):
    def __init__(
        self,
        update_request: str,
        graph: Graph,
        version: str | None = None,
        using_graph_uri: RequestDataValue = None,
        using_named_graph_uri: RequestDataValue = None,
    ) -> None:
        if any(param is not None for param in [using_graph_uri, using_named_graph_uri]):
            msg = (
                "URI Parameters 'using-graph-uri' and 'using-named-graph-uri' "
                "are currently not supported for rdflib.Graph targets."
            )

            raise NotImplementedError(msg)

        self._update_request = update_request
        self._graph = graph

    def _handle_request(self, request: httpx.Request) -> httpx.Response:
        try:
            self._graph.update(self._update_request)
        except pyparsing.exceptions.ParseBaseException as e:
            return httpx.Response(
                status_code=400,
                headers={
                    "Content-Type": "text/plain; charset=utf-8",
                },
                request=request,
                content=str(e),
            )
        except Exception as e:
            return httpx.Response(
                status_code=500,
                headers={
                    "Content-Type": "text/plain; charset=utf-8",
                },
                request=request,
                content=str(e),
            )

        else:
            return httpx.Response(
                status_code=200,
                headers={
                    "Content-Length": "0",
                    "Content-Type": "text/plain; charset=utf-8",
                },
                request=request,
                content=b"",
            )


class RDFLibUpdateTransport(_RDFLibUpdateTransportBase, httpx.BaseTransport):
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        return self._handle_request(request)


class AsyncRDFLibUpdateTransport(_RDFLibUpdateTransportBase, httpx.AsyncBaseTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        return await asyncio.to_thread(self._handle_request, request)
