"""Basic sad path tests for SPARQLWrapper."""

import pytest
from sparqlx import SPARQLWrapper
from sparqlx.utils.utils import bindings_format_map

from data.queries import ask_false_query, ask_true_query, select_values_query


@pytest.mark.parametrize(
    "query", [select_values_query, ask_true_query, ask_false_query]
)
@pytest.mark.parametrize(
    "response_format", filter(lambda k: k != "json", bindings_format_map.keys())
)
def test_sparqlwrapper_result_binding_conversion_non_json_fail(
    query, response_format, fuseki_service
):
    msg = "JSON response format required for convert=True on SELECT and ASK query results."
    with pytest.raises(ValueError, match=msg):
        SPARQLWrapper(endpoint=fuseki_service).query(
            query, convert=True, response_format=response_format
        )
