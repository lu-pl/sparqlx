"""SPARQLx testing utils."""

import asyncio
from typing import Any
from urllib.parse import parse_qs

import httpx


def parse_reponse_qs(response: httpx.Response) -> dict[str, list]:
    content = response.request.content.decode("utf-8")
    return parse_qs(content)


async def acall(obj: Any, method: str, *args, **kwargs):
    f = getattr(obj, method)

    return (
        await f(*args, **kwargs)
        if asyncio.iscoroutinefunction(f)
        else f(*args, **kwargs)
    )
