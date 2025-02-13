"""Stub definitions for SPARQLWrapper."""

from collections.abc import Iterable, Iterator
from typing import Any, Literal as TypingLiteral, Self, overload
from typing import Literal as TypingLiteral

import httpx

class _SPARQLBase:
    def __init__(
        self,
        endpoint: str,
        output_format: TypingLiteral["json"] = "json",
        headers: dict | None = None,
    ) -> None: ...
    @staticmethod
    def _to_python(response: httpx.Response) -> Iterator[dict[str, Any]]: ...

class SPARQLClient(_SPARQLBase):
    def __init__(
        self,
        *args,
        client: httpx.Client | None = None,
        **kwargs,
    ) -> None: ...
    @overload
    def query(self, query: str, to_python: TypingLiteral[False]) -> httpx.Response: ...
    @overload
    def query(
        self, query: str, to_python: TypingLiteral[True]
    ) -> Iterator[dict[str, Any]]: ...
    @overload
    def queries(
        self, queries: Iterable[str], to_python: TypingLiteral[False]
    ) -> list[httpx.Response]: ...
    @overload
    def queries(
        self, queries: Iterable[str], to_python: TypingLiteral[True]
    ) -> list[Iterator[dict[str, Any]]]: ...
    def _close(self) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type, exc, tb) -> None: ...

class AsyncSPARQLClient(_SPARQLBase):
    @overload
    async def aquery(
        self, query: str, to_python: TypingLiteral[False]
    ) -> httpx.Response: ...
    @overload
    async def aquery(
        self, query: str, to_python: TypingLiteral[True]
    ) -> Iterator[dict[str, Any]]: ...
    @overload
    async def aqueries(
        self, queries: Iterable[str], to_python: TypingLiteral[False]
    ) -> list[httpx.Response]: ...
    @overload
    async def aqueries(
        self, queries: Iterable[str], to_python: TypingLiteral[True]
    ) -> list[dict[str, Any]]: ...
    def __init__(
        self, *args, aclient: httpx.AsyncClient | None = None, **kwargs
    ) -> None: ...
    async def _aclose(self) -> None: ...
    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...

class SPARQLWrapper(_SPARQLBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ...

    @overload
    def query(self, query: str, to_python: TypingLiteral[False]) -> httpx.Response: ...
    @overload
    def query(
        self, query: str, to_python: TypingLiteral[True]
    ) -> Iterator[dict[str, Any]]: ...
    @overload
    def queries(
        self, queries: Iterable[str], to_python: TypingLiteral[False]
    ) -> list[httpx.Response]: ...
    @overload
    def queries(
        self, queries: Iterable[str], to_python: TypingLiteral[True]
    ) -> list[Iterator[dict[str, Any]]]: ...
