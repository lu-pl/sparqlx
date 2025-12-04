"""Basic sad path tests for SPARQLWrapper."""

import httpx
import pytest

from data.queries import ask_query_false, ask_query_true, select_query_xy_values
from sparqlx import SPARQLWrapper
from sparqlx.utils.converters import _convert_ask
from sparqlx.utils.utils import bindings_format_map


@pytest.mark.parametrize(
    "query", [select_query_xy_values, ask_query_true, ask_query_false]
)
@pytest.mark.parametrize(
    "response_format", filter(lambda k: k != "json", bindings_format_map.keys())
)
def test_sparqlwrapper_result_binding_conversion_non_json_fail(
    query, response_format, triplestore
):
    msg = "JSON response format required for convert=True on SELECT and ASK query results."
    with pytest.raises(ValueError, match=msg):
        SPARQLWrapper(sparql_endpoint=triplestore.sparql_endpoint).query(
            query, convert=True, response_format=response_format
        )


def test_invalid_sparql_query_error_message():
    wrapper = SPARQLWrapper(sparql_endpoint="http://example.org")

    with pytest.raises(ValueError, match="Invalid SPARQL query"):
        wrapper.query("THIS IS NOT SPARQL")


def test_convert_ask_invalid_json_error_message():
    response = httpx.Response(status_code=200, content=b"NOT JSON")

    with pytest.raises(ValueError, match="Expected JSON response for ASK query"):
        _convert_ask(response)


def test_convert_ask_missing_boolean_key():
    response = httpx.Response(status_code=200, json={"answer": True})

    with pytest.raises(ValueError, match="ASK response missing 'boolean' key"):
        _convert_ask(response)
