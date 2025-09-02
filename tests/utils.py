"""SPARQLx testing utils."""

from urllib.parse import parse_qs

import httpx


def parse_reponse_qs(response: httpx.Response) -> dict[str, list]:
    content = response.request.content.decode("utf-8")
    return parse_qs(content)
