"""Basic sad path tests for SPARQLWrapper."""

import pytest

from data.queries import ask_query_false, ask_query_true, select_query_xy_values
from sparqlx import SPARQLWrapper
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
