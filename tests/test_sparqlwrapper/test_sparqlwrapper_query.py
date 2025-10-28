"""Pytest entry point for basic SPARQLWrapper Query Operation tests."""

import asyncio
from collections.abc import Callable
import datetime
from decimal import Decimal
import operator
from typing import NamedTuple
from typing import Any

import httpx
import pytest
from rdflib import BNode, Graph, Literal, URIRef, XSD
from rdflib.compare import isomorphic

from conftest import FusekiEndpoints
from data.queries import (
    ask_query_false,
    ask_query_true,
    construct_query_x_values,
    describe_query,
    select_query_bnode,
    select_query_types,
    select_query_xy_values,
)
from sparqlx import SPARQLWrapper
from sparqlx.utils.utils import bindings_format_map, graph_format_map
from utils import acall


class QueryOperationParameter(NamedTuple):
    query: str
    expected: bool | list[dict] | Graph
    compare: Callable[[Any, Any], bool] = operator.eq


ntriples_data = """
<urn:s> <urn:p> "1"^^<http://www.w3.org/2001/XMLSchema#integer> .
<urn:s> <urn:p> "3"^^<http://www.w3.org/2001/XMLSchema#integer> .
<urn:s> <urn:p> "2"^^<http://www.w3.org/2001/XMLSchema#integer> .
"""
expected_graph = Graph().parse(data=ntriples_data)


params = [
    QueryOperationParameter(
        query=select_query_xy_values,
        expected=[{"x": 1, "y": 2}, {"x": 3, "y": 4}],
    ),
    QueryOperationParameter(query=ask_query_true, expected=True),
    QueryOperationParameter(query=ask_query_false, expected=False),
    QueryOperationParameter(
        query=construct_query_x_values, expected=expected_graph, compare=isomorphic
    ),
    #
    QueryOperationParameter(
        query=select_query_types,
        expected=[
            {"x": 2},
            {"x": Decimal("2.2")},
            {"x": None},
            {"x": URIRef("https://test.uri")},
            {"x": datetime.date(2024, 1, 1)},
            {"x": Literal("2024", datatype=XSD.gYear)},
            {"x": Literal("2024-01", datatype=XSD.gYearMonth)},
        ],
    ),
    QueryOperationParameter(
        query=select_query_bnode,
        expected=[{"x": BNode()}],
        compare=lambda x, y: all(
            isinstance(v, BNode) for v in map(lambda r: list(r)[0]["x"], [x, y])
        ),
    ),
    QueryOperationParameter(query=describe_query, expected=Graph(), compare=isomorphic),
]


@pytest.mark.parametrize("method", ["query", "aquery"])
@pytest.mark.parametrize("param", params)
@pytest.mark.asyncio
async def test_sparqlwrapper_query(method, param, triplestore):
    """Run a query with convert=True and compare the result to the expected bindings."""

    endpoint: str = triplestore.sparql_endpoint
    sparqlwrapper = SPARQLWrapper(sparql_endpoint=endpoint)

    result_converted = await acall(
        sparqlwrapper, method, query=param.query, convert=True
    )

    assert param.compare(result_converted, param.expected)


@pytest.mark.parametrize("method", ["query", "aquery"])
@pytest.mark.parametrize(
    "query",
    [
        select_query_xy_values,
        ask_query_true,
        ask_query_false,
        select_query_bnode,
        select_query_types,
    ],
)
@pytest.mark.parametrize(
    "response_format",
    [None, *bindings_format_map.keys()],
)
@pytest.mark.asyncio
async def test_sparqlwrapper_query_binding_result_formats(
    method,
    query,
    response_format,
    triplestore,
):
    """Run SELECT and ASK queries with bindings result formats."""

    endpoint: str = triplestore.sparql_endpoint
    sparqlwrapper = SPARQLWrapper(sparql_endpoint=endpoint)

    result = await acall(
        sparqlwrapper, method, query=query, response_format=response_format
    )

    assert result.content


@pytest.mark.parametrize("method", ["query", "aquery"])
@pytest.mark.parametrize("query", [construct_query_x_values, describe_query])
@pytest.mark.parametrize(
    "response_format", [None, *graph_format_map.keys(), "application/n-triples"]
)
@pytest.mark.asyncio
async def test_sparqlwrapper_query_graph_result_formats(
    method,
    query,
    response_format,
    triplestore_with_data,
):
    """Run CONSTRUCT and DESCRIBE queries with graph result formats.

    The tests uses the oxigraph_service_with_data fixture in order
    to retrieve a non-empty graph object on DESCRIBE queries.

    Note: Fuseki responds with 406 if 'application/rdf+xml' is requested as graph format;
    the store can handle 'text/xml' though, so this can be considered a bug in Fuseki.
    """
    if isinstance(triplestore_with_data, FusekiEndpoints) and response_format == "xml":
        pytest.skip(
            reason="Fuseki currently only handles 'text/xml', not 'application/rdf+xml."
        )

    endpoint: str = triplestore_with_data.sparql_endpoint
    sparqlwrapper = SPARQLWrapper(sparql_endpoint=endpoint)

    result = await acall(
        sparqlwrapper, method, query=query, response_format=response_format
    )

    result_converted = await acall(
        sparqlwrapper,
        method,
        query=query,
        convert=True,
        response_format=response_format,
    )

    assert result
    assert result_converted


@pytest.mark.asyncio
async def test_sparqlwrapper_warn_open_client(triplestore):
    """Pass a client/aclient and check if a warning is emitted."""
    endpoint: str = triplestore.sparql_endpoint

    client = httpx.Client()
    aclient = httpx.AsyncClient()

    sparqlwrapper = SPARQLWrapper(
        sparql_endpoint=endpoint, client=client, aclient=aclient
    )

    def _get_msg(client):
        return (
            f"httpx Client instance '{client}' is not managed. "
            "Client.close/AsyncClient.aclose should be called at some point."
        )

    with pytest.warns(UserWarning, match=_get_msg(client)):
        sparqlwrapper.query(select_query_xy_values)

    with pytest.warns(UserWarning, match=_get_msg(aclient)):
        await sparqlwrapper.aquery(select_query_xy_values)


@pytest.mark.parametrize(
    "query",
    [
        select_query_xy_values,
        ask_query_false,
        ask_query_true,
        construct_query_x_values,
        describe_query,
    ],
)
@pytest.mark.asyncio
async def test_sparql_wrapper_context_managers(query, triplestore):
    """Check unmanaged client/aclient status in context managers.

    The tests assert that client/aclient is open within a context
    and is closed after leaving the context."""
    endpoint: str = triplestore.sparql_endpoint

    client = httpx.Client()
    aclient = httpx.AsyncClient()

    sparqlwrapper = SPARQLWrapper(
        sparql_endpoint=endpoint, client=client, aclient=aclient
    )

    with sparqlwrapper as context_wrapper:
        result_1 = context_wrapper.query(query=query)
        assert not client.is_closed

    async with sparqlwrapper as context_wrapper:
        result_2 = await context_wrapper.aquery(query=query)
        assert not aclient.is_closed

    assert client.is_closed
    assert aclient.is_closed

    assert result_1.content == result_2.content


@pytest.mark.parametrize(
    "query",
    [
        select_query_xy_values,
        ask_query_false,
        ask_query_true,
        construct_query_x_values,
        describe_query,
        select_query_types,
        # note: bnode query cannot be compared
    ],
)
@pytest.mark.asyncio
async def test_sparqlwrapper_streaming(query, triplestore):
    """Sync/async stream a response and compare lists of chunks."""
    endpoint: str = triplestore.sparql_endpoint
    sparqlwrapper = SPARQLWrapper(sparql_endpoint=endpoint)

    stream = sparqlwrapper.query_stream(query, chunk_size=1)
    astream = sparqlwrapper.aquery_stream(query, chunk_size=1)

    chunks = [chunk for chunk in stream]
    achunks = [chunk async for chunk in astream]

    assert chunks == achunks


@pytest.mark.parametrize(
    "query",
    [
        select_query_xy_values,
        ask_query_false,
        ask_query_true,
        construct_query_x_values,
        describe_query,
    ],
)
def test_sparqlwrapper_queries(query, triplestore):
    endpoint: str = triplestore.sparql_endpoint
    sparqlwrapper = SPARQLWrapper(sparql_endpoint=endpoint)

    queries: list[str] = [query for _ in range(5)]

    results_queries = sparqlwrapper.queries(*queries)

    async def _runner():
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(sparqlwrapper.aquery(query)) for query in queries]

        return map(asyncio.Task.result, tasks)

    results_aqueries = asyncio.run(_runner())

    assert all(
        response_1.content == response_2.content
        for response_1, response_2 in zip(results_queries, results_aqueries)
    )
