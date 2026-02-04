import asyncio
from collections.abc import AsyncIterator
from contextlib import AbstractContextManager, asynccontextmanager
from typing import cast

from rdflib import BNode, Graph
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.sparql import Query
from sparqlx.types import SPARQLQuery, SPARQLQueryTypeLiteral, SPARQLResponseFormat
from sparqlx.utils.converters import _convert_ask, _convert_bindings, _convert_graph


class SPARQLParseException(Exception): ...


def _get_query_type(query: SPARQLQuery) -> SPARQLQueryTypeLiteral:
    try:
        _prepared_query: Query = prepareQuery(query)
    except Exception as exc:
        raise SPARQLParseException(exc) from exc
    else:
        query_type = _prepared_query.algebra.name

    return cast(SPARQLQueryTypeLiteral, query_type)


def _get_response_converter(
    query_type: SPARQLQueryTypeLiteral, response_format: SPARQLResponseFormat | str
):
    if query_type in ["SelectQuery", "AskQuery"] and response_format not in [
        "application/json",
        "application/sparql-results+json",
    ]:
        msg = "JSON response format required for convert=True on SELECT and ASK query results."
        raise ValueError(msg)

    match query_type:
        case "SelectQuery":
            converter = _convert_bindings
        case "AskQuery":
            converter = _convert_ask
        case "DescribeQuery" | "ConstructQuery":
            converter = _convert_graph
        case _:  # pragma: no cover
            raise ValueError(f"Unsupported query type: {query_type}")

    return converter


class Endpoint:
    def __init__(self, endpoint: str | Graph | None):
        self._endpoint = endpoint

    @property
    def url(self) -> str:
        match self._endpoint:
            case str():
                return self._endpoint
            case Graph():
                graph_uri = (
                    identifier.skolemize()
                    if isinstance((identifier := self._endpoint.identifier), BNode)
                    else identifier
                )
                return graph_uri
            case None:
                raise ValueError(
                    "Unable to run SPARQL operations: Endpoint is not defined."
                )
            case _:  # pragma: no cover
                assert False, "This should never happen."

    @property
    def graph(self) -> Graph | None:
        return self._endpoint if isinstance(self._endpoint, Graph) else None


@asynccontextmanager
async def as_async_context[T](sync_cm: AbstractContextManager[T]) -> AsyncIterator[T]:
    """Async context wrapper around a sync context manager.

    The async context manager allows to call a sync context manager
    from an async context statement. This workaround is mentioned in PEP 806,
    see https://peps.python.org/pep-0806/#workaround-an-as-acm-wrapper.
    """
    with sync_cm as result:
        await asyncio.sleep(0)
        yield result
