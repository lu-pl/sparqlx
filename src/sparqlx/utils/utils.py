from collections import UserDict
from collections.abc import Callable, Iterator
import json
from typing import Literal as TypingLiteral, NamedTuple

import httpx
from rdflib import BNode, Graph, Literal, URIRef, XSD
from rdflib.plugins.sparql import prepareQuery
from sparqlx.utils.types import _TSPARQLBinding, _TSPARQLBindingValue


def _convert_bindings(
    response: httpx.Response,
) -> Iterator[_TSPARQLBinding]:
    """Get flat dicts from a SPARQL SELECT JSON response."""

    try:
        json_response = response.json()
    except (
        json.JSONDecodeError
    ) as error:  # pragma: no cover ; this should be unreachable
        error.add_note("Note that convert=True requires JSON as response format.")
        raise error

    variables = json_response["head"]["vars"]
    response_bindings = json_response["results"]["bindings"]

    def _get_binding_pairs(binding) -> Iterator[tuple[str, _TSPARQLBindingValue]]:
        """Generate key value pairs from response_bindings.

        The 'type' and 'datatype' fields of the JSON response
        are examined to cast values to Python types according to RDFLib.
        """
        for var in variables:
            if (binding_data := binding.get(var, None)) is None:
                yield (var, None)
                continue

            match binding_data["type"]:
                case "uri":
                    yield (var, URIRef(binding_data["value"]))
                case "literal":
                    literal = Literal(
                        binding_data["value"],
                        datatype=binding_data.get("datatype", None),
                    )

                    # call toPython in any case for validation
                    literal_to_python = literal.toPython()

                    if literal.datatype in (XSD.gYear, XSD.gYearMonth):
                        yield (var, literal)
                    else:
                        yield (var, literal_to_python)

                case "bnode":
                    yield (var, BNode(binding_data["value"]))
                case _:  # pragma: no cover
                    assert False, "This should never happen."

    for binding in response_bindings:
        yield dict(_get_binding_pairs(binding))


def _convert_graph(response: httpx.Response) -> Graph:
    _format, *_ = response.headers["content-type"].split(";")
    graph = Graph().parse(response.content, format=_format)
    return graph


def _convert_ask(response: httpx.Response) -> bool:
    return json.loads(response.content)["boolean"]


class MimeTypeMap(UserDict):
    def __missing__(self, key):
        return key


bindings_format_map = MimeTypeMap(
    {
        "json": "application/sparql-results+json",
        "xml": "application/sparql-results+xml",
        "csv": "text/csv",
        "tsv": "text/tab-separated-values",
    }
)
graph_format_map = MimeTypeMap(
    {
        "turtle": "text/turtle",
        "xml": "application/xml",
        "ntriples": "application/n-triples",
        "json-ld": "application/ld+json",
    }
)


class QueryOperationParameters(NamedTuple):
    response_format: str
    converter: Callable[[httpx.Response], Iterator[_TSPARQLBinding] | Graph]


def get_query_type(query: str) -> str:
    return prepareQuery(queryString=query).algebra.name


def get_query_operation_parameters(
    query: str, convert: bool = False, response_format: str | None = None
) -> QueryOperationParameters:
    query_type = get_query_type(query)

    match query_type:
        case "SelectQuery" | "AskQuery":
            _response_format = bindings_format_map[response_format or "json"]

            if convert and not _response_format in [
                "application/json",
                "application/sparql-results+json",
            ]:
                msg = "JSON response format required for convert=True on SELECT and ASK query results."
                raise ValueError(msg)

            converter = (
                _convert_bindings if query_type == "SelectQuery" else _convert_ask
            )

        case "DescribeQuery" | "ConstructQuery":
            _response_format = graph_format_map[response_format or "turtle"]
            converter = _convert_graph
        case _:  # pragma: no cover
            raise ValueError(f"Unsupported query type: {query_type}")

    return QueryOperationParameters(
        response_format=_response_format, converter=converter
    )
