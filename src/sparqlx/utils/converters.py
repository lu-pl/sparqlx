"""Response converters for SPARQL query results.

This module provides functions to convert SPARQL query responses into Python
data structures, including bindings lists, RDF graphs, and boolean results.
"""

from collections.abc import Iterator
import json

import httpx
from rdflib import BNode, Graph, Literal, URIRef
from sparqlx.utils.types import _TSPARQLBinding, _TSPARQLBindingValue


def _convert_bindings(
    response: httpx.Response,
) -> list[_TSPARQLBinding]:
    """Convert a SPARQL SELECT JSON response to a list of binding dictionaries.

    Parses the JSON response from a SPARQL SELECT query and converts each
    binding to a Python dictionary with RDFLib types (URIRef, Literal, BNode)
    and native Python types for literal values.

    Args:
        response: The httpx.Response from a SPARQL SELECT query.
            Must have JSON content type.

    Returns:
        A list of dictionaries where each dictionary represents one result row,
        with variable names as keys and converted RDFLib/Python values as values.

    Raises:
        json.JSONDecodeError: If the response cannot be parsed as JSON.

    """
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
        """Generate key-value pairs from a SPARQL binding.

        Examines the 'type' and 'datatype' fields of the JSON response binding
        and converts values to appropriate Python types according to RDFLib
        conventions.

        Args:
            binding: A single binding object from the SPARQL JSON response.

        Yields:
            Tuples of (variable_name, converted_value) where converted_value is
            a URIRef, BNode, or Python object from Literal.toPython().

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
    """Convert a SPARQL CONSTRUCT/DESCRIBE response to an rdflib.Graph.

    Parses the response content using RDFLib's Graph parser, automatically
    detecting the format from the Content-Type header.

    Args:
        response: The httpx.Response from a SPARQL CONSTRUCT or DESCRIBE query.
            The Content-Type header is used to determine the RDF serialization
            format.

    Returns:
        An rdflib.Graph containing the parsed RDF triples.

    Note:
        httpx.Response.headers is always an instance of httpx.Headers
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
    """Convert a SPARQL ASK response to a boolean value.

    Parses the JSON response from a SPARQL ASK query and extracts the
    boolean result.

    Args:
        response: The httpx.Response from a SPARQL ASK query.
            Must have JSON content type with a "boolean" field.

    Returns:
        The boolean result of the ASK query.

    """
    return response.json()["boolean"]
