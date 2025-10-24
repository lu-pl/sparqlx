from collections.abc import Iterator
import json

import httpx
from rdflib import BNode, Graph, Literal, URIRef
from sparqlx.utils.types import _TSPARQLBinding, _TSPARQLBindingValue


def _convert_bindings(
    response: httpx.Response,
) -> list[_TSPARQLBinding]:
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

                    literal_to_python = literal.toPython()
                    yield (var, literal_to_python)

                case "bnode":
                    yield (var, BNode(binding_data["value"]))
                case _:  # pragma: no cover
                    assert False, "This should never happen."

    return [dict(_get_binding_pairs(binding)) for binding in response_bindings]


def _convert_graph(response: httpx.Response) -> Graph:
    """Convert the content of an HTTP response to an rdflib.Graph.

    Note: httpx.Response.headers is always an instance of httpx.Headers
    (a mutable mapping).
    """
    _format: str | None = (
        content_type
        if (content_type := response.headers.get("content-type")) is None
        else content_type.split(";")[0].strip()
    )

    graph = Graph().parse(response.content, format=_format)
    return graph


def _convert_ask(response: httpx.Response) -> bool:
    return response.json()["boolean"]
