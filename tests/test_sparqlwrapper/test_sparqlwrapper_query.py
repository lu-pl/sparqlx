"""Pytest entry point for basic SPARQLWrapper Query Operation tests."""

import asyncio
import datetime
from decimal import Decimal
import operator

import httpx
import pytest
from rdflib import BNode, Graph, Literal, URIRef, XSD
from rdflib.compare import isomorphic
from sparqlx import SPARQLWrapper
from sparqlx.utils.utils import (
    _convert_ask,
    _convert_bindings,
    _convert_graph,
    bindings_format_map,
    graph_format_map,
)

from data.queries import (
    ask_false_query,
    ask_true_query,
    construct_values_query,
    describe_query,
    select_query_bnode,
    select_query_types,
    select_values_query,
)


@pytest.mark.parametrize("method", ["query", "aquery"])
@pytest.mark.asyncio
async def test_sparqlwrapper_query_select(method, fuseki_service):
    attr_getter = operator.attrgetter(method)

    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

    if method == "aquery":
        result = await attr_getter(sparqlwrapper)(select_values_query)
        result_converted = await attr_getter(sparqlwrapper)(
            select_values_query, convert=True
        )
    else:
        result = attr_getter(sparqlwrapper)(select_values_query)
        result_converted = attr_getter(sparqlwrapper)(select_values_query, convert=True)

    expected = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]

    assert list(result_converted) == expected
    assert list(_convert_bindings(result)) == expected


@pytest.mark.parametrize("method", ["query", "aquery"])
@pytest.mark.asyncio
async def test_sparqlwrapper_query_ask_true(method, fuseki_service):
    attr_getter = operator.attrgetter(method)

    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

    if method == "aquery":
        result = await attr_getter(sparqlwrapper)(ask_true_query)
        result_converted = await attr_getter(sparqlwrapper)(
            ask_true_query, convert=True
        )
    else:
        result = attr_getter(sparqlwrapper)(ask_true_query)
        result_converted = attr_getter(sparqlwrapper)(ask_true_query, convert=True)

    assert result_converted == True
    assert _convert_ask(result) == True


@pytest.mark.parametrize("method", ["query", "aquery"])
@pytest.mark.asyncio
async def test_sparqlwrapper_query_ask_false(method, fuseki_service):
    attr_getter = operator.attrgetter(method)

    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

    if method == "aquery":
        result = await attr_getter(sparqlwrapper)(ask_false_query)
        result_converted = await attr_getter(sparqlwrapper)(
            ask_false_query, convert=True
        )
    else:
        result = attr_getter(sparqlwrapper)(ask_false_query)
        result_converted = attr_getter(sparqlwrapper)(ask_false_query, convert=True)

    assert result_converted == False
    assert _convert_ask(result) == False


@pytest.mark.parametrize("method", ["query", "aquery"])
@pytest.mark.asyncio
async def test_sparqlwrapper_query_construct(method, fuseki_service):
    attr_getter = operator.attrgetter(method)

    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

    if method == "aquery":
        result = await attr_getter(sparqlwrapper)(construct_values_query)
        result_converted = await attr_getter(sparqlwrapper)(
            construct_values_query, convert=True
        )

    else:
        result = attr_getter(sparqlwrapper)(construct_values_query)
        result_converted = attr_getter(sparqlwrapper)(
            construct_values_query, convert=True
        )

    ntriples_data = """
    <urn:s> <urn:p> "1"^^<http://www.w3.org/2001/XMLSchema#integer> .
    <urn:s> <urn:p> "3"^^<http://www.w3.org/2001/XMLSchema#integer> .
    <urn:s> <urn:p> "2"^^<http://www.w3.org/2001/XMLSchema#integer> .
    """
    expected_graph = Graph().parse(data=ntriples_data)

    assert isomorphic(_convert_graph(result), expected_graph)
    assert isomorphic(result_converted, expected_graph)


@pytest.mark.parametrize("method", ["query", "aquery"])
@pytest.mark.asyncio
async def test_sparqlwrapper_query_describe(method, fuseki_service):
    attr_getter = operator.attrgetter(method)

    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

    if method == "aquery":
        result = await attr_getter(sparqlwrapper)(describe_query)
        result_converted = await attr_getter(sparqlwrapper)(
            describe_query, convert=True
        )
    else:
        result = attr_getter(sparqlwrapper)(describe_query)
        result_converted = attr_getter(sparqlwrapper)(describe_query, convert=True)

    assert not result.content
    assert not result_converted


@pytest.mark.parametrize("method", ["query", "aquery"])
@pytest.mark.parametrize(
    "query", [select_values_query, ask_true_query, ask_false_query]
)
@pytest.mark.parametrize(
    "response_format",
    [None, *bindings_format_map.keys(), "application/x-binary-rdf-results-table"],
)
@pytest.mark.asyncio
async def test_sparqlwrapper_query_binding_result_formats(
    method, query, response_format, fuseki_service
):
    """Run SELECT and ASK queries with bindings result formats."""
    attr_getter = operator.attrgetter(method)

    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

    if method == "aquery":
        result = await attr_getter(sparqlwrapper)(
            query, response_format=response_format
        )
    else:
        result = attr_getter(sparqlwrapper)(query, response_format=response_format)

    assert result.content


@pytest.mark.parametrize("method", ["query", "aquery"])
@pytest.mark.parametrize("query", [construct_values_query])
@pytest.mark.parametrize(
    "response_format", [None, *graph_format_map.keys(), "application/n-triples"]
)
@pytest.mark.asyncio
async def test_sparqlwrapper_query_graph_result_formats(
    method, query, response_format, fuseki_service
):
    """Run CONSTRUCT and DESCRIBE queries with graph result formats."""
    attr_getter = operator.attrgetter(method)

    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

    if method == "aquery":
        result = await attr_getter(sparqlwrapper)(
            query, response_format=response_format
        )
        result_converted = await attr_getter(sparqlwrapper)(
            query, response_format=response_format, convert=True
        )

    else:
        result = attr_getter(sparqlwrapper)(query, response_format=response_format)
        result_converted = attr_getter(sparqlwrapper)(
            query, response_format=response_format, convert=True
        )

    assert result
    assert result_converted


@pytest.mark.asyncio
async def test_sparqlwrapper_warn_open_client(fuseki_service):
    endpoint: str = fuseki_service

    client = httpx.Client()
    aclient = httpx.AsyncClient()

    sparqlwrapper = SPARQLWrapper(endpoint=endpoint, client=client, aclient=aclient)

    def _get_msg(client):
        return (
            f"httpx Client instance '{client}' is not managed. "
            "Client.close/AsyncClient.aclose should be called at some point."
        )

    with pytest.warns(UserWarning, match=_get_msg(client)):
        sparqlwrapper.query(select_values_query)

    with pytest.warns(UserWarning, match=_get_msg(aclient)):
        await sparqlwrapper.aquery(select_values_query)


@pytest.mark.asyncio
async def test_sparql_wrapper_context_managers(fuseki_service):
    endpoint: str = fuseki_service

    client = httpx.Client()
    aclient = httpx.AsyncClient()

    sparqlwrapper = SPARQLWrapper(endpoint=endpoint, client=client, aclient=aclient)

    with sparqlwrapper as context_wrapper:
        result_1 = context_wrapper.query(select_values_query, convert=True)

    async with sparqlwrapper as context_wrapper:
        result_2 = await context_wrapper.aquery(select_values_query, convert=True)

    assert list(result_1) == list(result_2)


@pytest.mark.parametrize(
    "query",
    [
        select_values_query,
        ask_false_query,
        ask_true_query,
        construct_values_query,
        describe_query,
    ],
)
@pytest.mark.asyncio
async def test_sparqlwrapper_streaming(query, fuseki_service):
    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

    stream = sparqlwrapper.query_stream(query, chunk_size=1)
    astream = sparqlwrapper.aquery_stream(query, chunk_size=1)

    chunks = [chunk for chunk in stream]
    achunks = [chunk async for chunk in astream]

    assert chunks == achunks


@pytest.mark.parametrize(
    "query",
    [
        select_values_query,
        ask_false_query,
        ask_true_query,
        construct_values_query,
        describe_query,
    ],
)
def test_sparqlwrapper_queries(query, fuseki_service):
    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

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


def test_sparqlwrapper_python_cast_types(fuseki_service):
    """Run a query featuring several RDF types and check for Python-casting."""
    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

    result = sparqlwrapper.query(select_query_types, convert=True)

    expected = [
        {"x": 2},
        {"x": Decimal("2.2")},
        {"x": None},
        {"x": URIRef("https://test.uri")},
        {"x": datetime.date(2024, 1, 1)},
        {"x": Literal("2024", datatype=XSD.gYear)},
        {"x": Literal("2024-01", datatype=XSD.gYearMonth)},
    ]

    assert list(result) == expected


def test_sparqlwrapper_python_cast_bnodes(fuseki_service):
    """Run a query which mocks a BNode and check for BNode-casting."""
    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

    result, *_ = sparqlwrapper.query(select_query_bnode, convert=True)
    assert isinstance(result["x"], BNode)
