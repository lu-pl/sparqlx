"""Pytest entry point for sad paths tests of SPARQLWrapper with rdflib.Graph targets."""

import httpx
import pytest
from rdflib import Dataset, Graph
from sparqlx import SPARQLWrapper

from utils import acall


@pytest.mark.parametrize("graph", [Graph(), Dataset()])
@pytest.mark.parametrize("query_method", ["query", "aquery"])
@pytest.mark.parametrize("update_method", ["update", "aupdate"])
@pytest.mark.parametrize(
    "query_params",
    [
        {"default_graph_uri": ""},
        {"named_graph_uri": ""},
        {"default_graph_uri": "", "named_graph_uri": ""},
    ],
)
@pytest.mark.parametrize(
    "update_params",
    [
        {"using_graph_uri": ""},
        {"using_named_graph_uri": ""},
        {"using_graph_uri": "", "using_named_graph_uri": ""},
    ],
)
@pytest.mark.asyncio
async def test_sparqlwrapper_graph_target_uriparameters(
    graph, query_params, update_params, query_method, update_method
):
    """Check that URI parameters on rdflib.Graph targets raise NotImplementedError."""

    sparqlwrapper = SPARQLWrapper(sparql_endpoint=graph, update_endpoint=graph)

    partial_fail_msg = "are currently not supported for rdflib.Graph targets."

    with pytest.raises(NotImplementedError, match=partial_fail_msg):
        await acall(
            sparqlwrapper,
            query_method,
            query="select * where {?s ?p ?o}",
            **query_params,
        )

    with pytest.raises(NotImplementedError, match=partial_fail_msg):
        await acall(
            sparqlwrapper,
            update_method,
            update_request="insert data {<urn:s> <urn:p> <urn:o>}",
            **update_params,
        )


@pytest.mark.parametrize("graph", [Graph(), Dataset()])
@pytest.mark.asyncio
async def test_sparqlwrapper_graph_target_streaming(graph):
    """Check that response streaming with rdflib.Graph targets raises NotImplementedError."""

    sparqlwrapper = SPARQLWrapper(sparql_endpoint=graph, update_endpoint=graph)

    fail_msg = "Response streaming is currently not supported for rdflib.Graph targets."
    query = "select * where {?s ?p ?o}"

    stream = sparqlwrapper.query_stream(query, chunk_size=1)
    astream = sparqlwrapper.aquery_stream(query, chunk_size=1)

    with pytest.raises(NotImplementedError, match=fail_msg):
        [chunk for chunk in stream]

    with pytest.raises(NotImplementedError, match=fail_msg):
        [chunk async for chunk in astream]


def test_sparqlwrapper_graph_target_http_500():
    """Cause an HTTP 500 with an rdflib.Graph target."""

    graph = Graph()
    sparqlwrapper = SPARQLWrapper(sparql_endpoint=graph, update_endpoint=graph)

    partial_fail_msg_500 = "Server error '500 Internal Server Error'"
    partial_fail_msg_400 = "Client error '400 Bad Request'"

    with pytest.raises(httpx.HTTPStatusError, match=partial_fail_msg_500):
        sparqlwrapper.query("select * where {graph ?g {?s ?p ?o}}")

    with pytest.raises(httpx.HTTPStatusError, match=partial_fail_msg_500):
        sparqlwrapper.update(
            "insert {graph ?g {<urn:s> <urn:p> <urn:o>}} where {graph ?g {?s ?p ?o}}"
        )

    with pytest.raises(httpx.HTTPStatusError, match=partial_fail_msg_400):
        sparqlwrapper.update("invalid SPARQL")
