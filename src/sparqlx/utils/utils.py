from typing import TypeGuard, get_args

from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.parser import parseUpdate
from rdflib.plugins.sparql.sparql import Query
from sparqlx.types import (
    AskQuery,
    ConstructQuery,
    DescribeQuery,
    SPARQLQuery,
    SPARQLQueryTypeLiteral,
    SPARQLResponseFormat,
    SelectQuery,
)
from sparqlx.utils.converters import _convert_ask, _convert_bindings, _convert_graph


class SPARQLParseException(Exception): ...


class QueryParseException(SPARQLParseException): ...


class UpdateParseException(SPARQLParseException): ...


def _parse_udpate_request(update_request: str) -> None:
    try:
        parseUpdate(update_request)
    except Exception as exc:
        raise UpdateParseException(exc) from exc


def _is_sparql_query_type_literal(value) -> TypeGuard[SPARQLQueryTypeLiteral]:
    return value in get_args(SPARQLQueryTypeLiteral.__value__)


def _get_query_type(query: SPARQLQuery, parse: bool) -> SPARQLQueryTypeLiteral:
    def _from_typed_query(
        query: SelectQuery | AskQuery | ConstructQuery | DescribeQuery,
    ) -> SPARQLQueryTypeLiteral:
        match query:
            case SelectQuery():
                query_type = "SelectQuery"
            case AskQuery():
                query_type = "AskQuery"
            case ConstructQuery():
                query_type = "ConstructQuery"
            case DescribeQuery():
                query_type = "DescribeQuery"
            case _:  # pragma: no cover
                assert False, "This should never happen."

        return query_type

    def _from_parsed_query(query: str) -> SPARQLQueryTypeLiteral:
        try:
            _prepared_query: Query = prepareQuery(query)
        except Exception as exc:
            raise QueryParseException(exc) from exc
        else:
            query_type = _prepared_query.algebra.name

        assert _is_sparql_query_type_literal(query_type)
        return query_type

    is_typed_query: bool = isinstance(
        query, SelectQuery | AskQuery | ConstructQuery | DescribeQuery
    )

    if not is_typed_query and not parse:
        msg = "Query must be of type SelectQuery | AskQuery | ConstructQuery | DescribeQuery if parse=False."
        raise ValueError(msg)
    elif is_typed_query and not parse:
        return _from_typed_query(query)
    else:
        return _from_parsed_query(query)


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
