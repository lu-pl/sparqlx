"""Pytest entry point for sparqlx.SPARQLWrapper URI parameter tests."""

import itertools
from typing import NamedTuple

import pytest
from rdflib import URIRef

from conftest import FusekiEndpoints
from sparqlx import SPARQLWrapper
from utils import sparql_result_set_equal


class URITestParameter(NamedTuple):
    query: str
    expected: list[dict]

    default_graph_uri: str | list[str] | None = None
    named_graph_uri: str | list[str] | None = None


count_triples_query = "select (count(*) as ?cnt) where {?s ?p ?o}"
select_graphs_query = "select distinct ?g where {graph ?g {?s ?p ?o}}"

default_graph_uri_params = [
    URITestParameter(
        query=count_triples_query, expected=[{"cnt": 33}], default_graph_uri=None
    ),
    URITestParameter(
        query=count_triples_query, expected=[{"cnt": 2}], default_graph_uri="urn:ng1"
    ),
    URITestParameter(
        query=count_triples_query,
        expected=[{"cnt": 4}],
        default_graph_uri=["urn:ng1", "urn:ng2"],
    ),
]

named_graph_uri_params = [
    URITestParameter(
        query=select_graphs_query,
        expected=[
            {"g": URIRef("urn:ng2")},
            {"g": URIRef("urn:ng1")},
        ],
    ),
    URITestParameter(
        query=select_graphs_query,
        named_graph_uri="urn:ng1",
        expected=[
            {"g": URIRef("urn:ng1")},
        ],
    ),
    URITestParameter(
        query=select_graphs_query,
        named_graph_uri=["urn:ng1", "urn:ng2"],
        expected=[
            {"g": URIRef("urn:ng1")},
            {"g": URIRef("urn:ng2")},
        ],
    ),
]

mixed_uri_parameters = [
    URITestParameter(
        query=count_triples_query,
        expected=[{"cnt": 4}],
        default_graph_uri=["urn:ng1", "urn:ng2"],
        named_graph_uri="urn:ng1",
    ),
    URITestParameter(
        query=select_graphs_query,
        expected=[{"g": URIRef("urn:ng1")}],
        default_graph_uri=["urn:ng1", "urn:ng2"],
        named_graph_uri="urn:ng1",
    ),
]


@pytest.mark.parametrize(
    "params",
    itertools.chain(
        default_graph_uri_params, named_graph_uri_params, mixed_uri_parameters
    ),
)
def test_sparqlwrapper_default_graph_uri(params, triplestore_with_data):
    if (
        isinstance(triplestore_with_data, FusekiEndpoints)
        and params == default_graph_uri_params[0]
    ):
        reason = """The Fuseki store actually cannot implicitely access the default graph.

        The secoresearch/fuseki image unfortunately sets the
        tdb:unionDefaultGraph setting to true, which makes the union of
        named graphs the default graph and excludes the actual default graph data.

        See https://jena.apache.org/documentation/tdb/datasets.html (Dataset Query).
        """
        pytest.skip(reason=reason)

    sparqlwrapper = SPARQLWrapper(sparql_endpoint=triplestore_with_data.sparql_endpoint)
    result = sparqlwrapper.query(
        query=params.query,
        convert=True,
        default_graph_uri=params.default_graph_uri,
        named_graph_uri=params.named_graph_uri,
    )

    assert sparql_result_set_equal(result, params.expected)
