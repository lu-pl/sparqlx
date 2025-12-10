"""SPARQLx testing utils."""

import asyncio
from collections.abc import AsyncIterator, Iterable
from contextlib import AbstractContextManager, asynccontextmanager
from typing import Any
from urllib.parse import parse_qs

import httpx
from sparqlx.types import SPARQLResultBinding, SPARQLResultBindingValue


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
    result_1: Iterable[SPARQLResultBinding], result_2: Iterable[SPARQLResultBinding]
) -> bool:
    def freeze(
        result: Iterable[SPARQLResultBinding],
    ) -> set[frozenset[tuple[str, SPARQLResultBindingValue]]]:
        return {frozenset(binding.items()) for binding in result}

    return freeze(result_1) == freeze(result_2)


@asynccontextmanager
async def as_async_cm[T](sync_cm: AbstractContextManager[T]) -> AsyncIterator[T]:
    """Async context wrapper around a sync context manager.

    The async context manager allows to call a sync context manager
    from an async context statement. This workaround is mentioned in PEP 806,
    see https://peps.python.org/pep-0806/#workaround-an-as-acm-wrapper.
    """
    with sync_cm as result:
        await asyncio.sleep(0)
        yield result
