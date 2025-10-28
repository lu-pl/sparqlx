"""Basic tests for SPARQLWrapper.update."""

from typing import NamedTuple

import httpx
import pytest
from rdflib import URIRef

from sparqlx import SPARQLWrapper
from utils import acall


class UpdateTestParameter(NamedTuple):
    update_request: str
    update_params: dict
    query: str
    expected: list[dict]


params = [
    UpdateTestParameter(
        update_request="insert data {graph <urn:ng> {<urn:s> <urn:p> <urn:o>}}",
        update_params={},
        query="select ?s ?p ?o where {graph <urn:ng> {?s ?p ?o}}",
        expected=[{"s": URIRef("urn:s"), "p": URIRef("urn:p"), "o": URIRef("urn:o")}],
    ),
    UpdateTestParameter(
        update_request="insert {?s <urn:p> <urn:o>} where {graph <urn:ng1> {?s ?p ?o}}",
        update_params={},
        query="select ?o where {<http://example.org/bob> <urn:p> ?o}",
        expected=[{"o": URIRef("urn:o")}],
    ),
    UpdateTestParameter(
        update_request="insert {?s <urn:p> <urn:o>} where {?s ?p ?o}",
        update_params={"using_graph_uri": "urn:ng1"},
        query="select ?o where {<http://example.org/bob> <urn:p> ?o}",
        expected=[{"o": URIRef("urn:o")}],
    ),
    UpdateTestParameter(
        update_request="""
        insert data {<urn:s> <urn:p> <urn:o>} ;
        insert {graph ?g {<urn:s> <urn:p> <urn:o>}} where {graph ?g {?s ?p ?o}}
        """,
        update_params={},
        query="select ?g ?s ?p ?o where {{<urn:s> ?p ?o} union {graph ?g {<urn:s> ?p ?o}}}",
        expected=[
            {
                "g": URIRef("urn:ng2"),
                "o": URIRef("urn:o"),
                "p": URIRef("urn:p"),
                "s": None,
            },
            {
                "g": URIRef("urn:ng1"),
                "o": URIRef("urn:o"),
                "p": URIRef("urn:p"),
                "s": None,
            },
            {
                "g": None,
                "o": URIRef("urn:o"),
                "p": URIRef("urn:p"),
                "s": None,
            },
        ],
    ),
    UpdateTestParameter(
        update_request="""
        insert data {<urn:s> <urn:p> <urn:o>} ;
        insert {graph ?g {<urn:s> <urn:p> <urn:o>}} where {graph ?g {?s ?p ?o}}
        """,
        update_params={"using_named_graph_uri": "urn:ng1"},
        query="select ?g ?s ?p ?o where {{<urn:s> ?p ?o} union {graph ?g {<urn:s> ?p ?o}}}",
        expected=[
            {
                "g": URIRef("urn:ng1"),
                "o": URIRef("urn:o"),
                "p": URIRef("urn:p"),
                "s": None,
            },
            {
                "g": None,
                "o": URIRef("urn:o"),
                "p": URIRef("urn:p"),
                "s": None,
            },
        ],
    ),
]


@pytest.mark.parametrize("method", ["update", "aupdate"])
@pytest.mark.parametrize("param", params)
@pytest.mark.asyncio
async def test_sparqlwrapper_update(method, param, oxigraph_service_with_data):
    sparqlwrapper = SPARQLWrapper(
        sparql_endpoint=oxigraph_service_with_data.sparql_endpoint,
        update_endpoint=oxigraph_service_with_data.update_endpoint,
    )

    with sparqlwrapper as wrapper:
        result_before_update = wrapper.query(param.query, convert=True)
        assert not result_before_update

        await acall(
            obj=wrapper,
            method=method,
            update_request=param.update_request,
            **param.update_params,
        )

        result_after_update = wrapper.query(param.query, convert=True)
        assert result_after_update == param.expected


def test_sparqlwrapper_updates(fuseki_service):
    """Basic test for SPARQLWrapper.updates.

    Note: This test runs against a Fuseki Triplestore to also test auth for updates.
    """
    sparqlwrapper = SPARQLWrapper(
        sparql_endpoint=fuseki_service.sparql_endpoint,
        update_endpoint=fuseki_service.update_endpoint,
        aclient_config={"auth": httpx.BasicAuth(username="admin", password="pm")},
    )

    sparqlwrapper.updates(
        "insert data {<urn:s> <urn:p> <urn:o>}",
        "insert data {graph <urn:ng1> {<urn:s> <urn:p> <urn:o>}}",
        "insert data {graph <urn:ng2> {<urn:s> <urn:p> <urn:o>}}",
    )

    result = sparqlwrapper.query(
        "select ?g ?s ?p ?o where { {?s ?p ?o} union { graph ?g {?s ?p ?o} }}",
        convert=True,
    )

    expected = [
        {
            "g": None,
            "s": URIRef("urn:s"),
            "p": URIRef("urn:p"),
            "o": URIRef("urn:o"),
        },
        {
            "g": URIRef("urn:ng1"),
            "s": URIRef("urn:s"),
            "p": URIRef("urn:p"),
            "o": URIRef("urn:o"),
        },
        {
            "g": URIRef("urn:ng2"),
            "s": URIRef("urn:s"),
            "p": URIRef("urn:p"),
            "o": URIRef("urn:o"),
        },
    ]

    assert all(_result in expected for _result in result)
    assert all(_expected in result for _expected in expected)
