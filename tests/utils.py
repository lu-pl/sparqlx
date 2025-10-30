"""SPARQLx testing utils."""

import asyncio
from collections.abc import Iterable
from typing import Any
from urllib.parse import parse_qs

import httpx

from sparqlx.utils.types import _TSPARQLBinding


def parse_response_qs(response: httpx.Response) -> dict[str, list]:
    content = response.request.content.decode("utf-8")
    return parse_qs(content)


async def acall(obj: Any, method: str, *args, **kwargs):
    f = getattr(obj, method)

    return (
        await f(*args, **kwargs)
        if asyncio.iscoroutinefunction(f)
        else f(*args, **kwargs)
    )


def sparql_result_set_equal(
    result_1: Iterable[_TSPARQLBinding], result_2: Iterable[_TSPARQLBinding]
) -> bool:
    def freeze(
        result: Iterable[_TSPARQLBinding],
    ) -> set[frozenset[tuple[str, _TSPARQLBinding]]]:
        return {frozenset(binding.items()) for binding in result}

    return freeze(result_1) == freeze(result_2)
