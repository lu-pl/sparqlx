"""Basic tests for the SPARQLWrapper.from_rdf_source constructor."""

from io import StringIO

import pytest
from rdflib import Dataset, Graph, URIRef
from sparqlx import SPARQLWrapper
from sparqlx.types import SPARQLResultBinding, SelectQuery

from utils import sparql_result_set_equal


@pytest.mark.parametrize("graph_source", [Graph(), Dataset()])
def test_sparqlwrapper_from_graph_source(graph_source):
    """Check that Graph objects passed to the constructor get set as endpoints."""
    wrapper = SPARQLWrapper.from_rdf_source(rdf_source=graph_source)

    assert wrapper._sparql_endpoint.graph is graph_source
    assert wrapper._update_endpoint.graph is graph_source


@pytest.mark.parametrize(
    "rdf_source",
    [
        StringIO("<urn:s> <urn:p> <urn:o>."),
        Graph().parse(StringIO("<urn:s> <urn:p> <urn:o>.")),
        Dataset().parse(StringIO("<urn:s> <urn:p> <urn:o>.")),
    ],
)
def test_sparqlwrapper_from_source(rdf_source):
    """Construct a SPARQLWrapper from an RDF source and check a query result."""

    wrapper = SPARQLWrapper.from_rdf_source(rdf_source=rdf_source)

    result = wrapper.query(
        SelectQuery("select ?s ?p ?o where {?s ?p ?o}"), convert=True
    )
    excepted: list[SPARQLResultBinding] = [
        {
            "s": URIRef("urn:s"),
            "p": URIRef("urn:p"),
            "o": URIRef("urn:o"),
        }
    ]

    assert sparql_result_set_equal(result, excepted)
