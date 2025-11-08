"""Interface definitions for sparqlx.sparqlwrapper."""

from collections.abc import Iterator
from typing import Literal as TLiteral, overload

import httpx
from rdflib import Graph
from sparqlx.utils.types import _TRequestDataValue, _TResponseFormat, _TSPARQLBinding

class SPARQLWrapper:
    @overload
    def query(
        self,
        query: str,
        convert: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> list[_TSPARQLBinding] | Graph | bool: ...
    @overload
    def query(
        self,
        query: str,
        convert: TLiteral[False] = False,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> httpx.Response: ...
    @overload
    async def aquery(
        self,
        query: str,
        convert: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> list[_TSPARQLBinding] | Graph | bool: ...
    @overload
    async def aquery(
        self,
        query: str,
        convert: TLiteral[False] = False,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> httpx.Response: ...
    @overload
    def queries(
        self,
        *queries: str,
        convert: TLiteral[True],
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> Iterator[list[_TSPARQLBinding] | Graph | bool]: ...
    @overload
    def queries(
        self,
        *queries: str,
        convert: TLiteral[False] = False,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> Iterator[httpx.Response]: ...
