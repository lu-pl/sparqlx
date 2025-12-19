from typing import cast

from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.parser import parseUpdate
from rdflib.plugins.sparql.sparql import Query
from sparqlx.types import SPARQLQuery, SPARQLQueryTypeLiteral, SPARQLResponseFormat
from sparqlx.utils.converters import _convert_ask, _convert_bindings, _convert_graph


class SPARQLParseException(Exception): ...


class QueryParseException(SPARQLParseException): ...


class UpdateParseException(SPARQLParseException): ...


def _parse_udpate_request(update_request: str) -> None:
    try:
        parseUpdate(update_request)
    except Exception as exc:
        raise UpdateParseException(exc) from exc


def _get_query_type(query: SPARQLQuery) -> SPARQLQueryTypeLiteral:
    try:
        _prepared_query: Query = prepareQuery(query)
    except Exception as exc:
        raise QueryParseException(exc) from exc
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
