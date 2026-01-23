"""Basic sad path tests for SPARQLWrapper."""

from typing import NamedTuple

import pytest
from sparqlx import SPARQLParseException, SPARQLWrapper
from sparqlx.utils.operation_parameters import sparql_result_response_format_map

from data.queries import ask_query_false, ask_query_true, select_query_xy_values


@pytest.mark.parametrize(
    "query", [select_query_xy_values, ask_query_true, ask_query_false]
)
@pytest.mark.parametrize(
    "response_format",
    filter(lambda k: k != "json", sparql_result_response_format_map.keys()),
)
def test_sparqlwrapper_result_binding_conversion_non_json_fail(
    query, response_format, triplestore
):
    msg = "JSON response format required for convert=True on SELECT and ASK query results."
    with pytest.raises(ValueError, match=msg):
        SPARQLWrapper(sparql_endpoint=triplestore.sparql_endpoint).query(
            query, convert=True, response_format=response_format
        )


class SPARQLParseExceptionTestParameter(NamedTuple):
    invalid_input: str
    exception_match_text: str


params = [
    SPARQLParseExceptionTestParameter(
        invalid_input="NOT A SPARQL QUERY",
        exception_match_text="Expected {SelectQuery | ConstructQuery | DescribeQuery | AskQuery}, found 'NOT'",
    ),
    SPARQLParseExceptionTestParameter(
        invalid_input="select * where {?s ?p ?o ",
        exception_match_text="Expected SelectQuery, found end of text",
    ),
    SPARQLParseExceptionTestParameter(
        invalid_input="ask ?s where {?s ?p ?o}",
        exception_match_text="Expected AskQuery, found '?'",
    ),
]


@pytest.mark.parametrize("param", params)
def test_sparqlwrapper_parse_exception(param, triplestore):
    """Simple test case for invalid SPARQL query inputs.

    Check that an invalid SPARQL query input raises SPARQLParseException and
    that the pyparsing.ParseException message is propagated to SPARQLParseException.
    """
    with pytest.raises(SPARQLParseException, match=param.exception_match_text):
        SPARQLWrapper(sparql_endpoint=triplestore.sparql_endpoint).query(
            param.invalid_input
        )


def test_sparqlwrapper_invalid_config():
    """Check that SPARQLWrapper init without any endpoint definition fails."""

    msg = (
        "Invalid SPARQLWrapper configuration: "
        "at least one of 'sparql_endpoint' or 'update_endpoint' must be set."
    )

    with pytest.raises(ValueError, match=msg):
        SPARQLWrapper()
