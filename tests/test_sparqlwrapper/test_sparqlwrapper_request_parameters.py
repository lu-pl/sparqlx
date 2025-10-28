from typing import NamedTuple

import pytest

from sparqlx import SPARQLWrapper
from utils import parse_response_qs


class ProtocolRequestParameters(NamedTuple):
    kwargs: dict
    expected: dict


query_request_params = [
    ProtocolRequestParameters(
        kwargs={"named_graph_uri": "https://named.graph"},
        expected={
            "query": ["select * where {?s ?p ?o}"],
            "named-graph-uri": ["https://named.graph"],
        },
    ),
    ProtocolRequestParameters(
        kwargs={
            "default_graph_uri": "https://default.graph",
            "named_graph_uri": "https://named.graph",
        },
        expected={
            "query": ["select * where {?s ?p ?o}"],
            "default-graph-uri": ["https://default.graph"],
            "named-graph-uri": ["https://named.graph"],
        },
    ),
    ProtocolRequestParameters(
        kwargs={
            "default_graph_uri": "https://default.graph",
            "named_graph_uri": "https://named.graph",
            "version": "1.2",
        },
        expected={
            "query": ["select * where {?s ?p ?o}"],
            "default-graph-uri": ["https://default.graph"],
            "named-graph-uri": ["https://named.graph"],
            "version": ["1.2"],
        },
    ),
    ProtocolRequestParameters(
        kwargs={
            "default_graph_uri": "https://default.graph",
            "named_graph_uri": ["https://named.graph", "https://othernamed.graph"],
        },
        expected={
            "query": ["select * where {?s ?p ?o}"],
            "default-graph-uri": ["https://default.graph"],
            "named-graph-uri": ["https://named.graph", "https://othernamed.graph"],
        },
    ),
    ProtocolRequestParameters(
        kwargs={
            "default_graph_uri": [
                "https://default.graph",
                "https://otherdefault.graph",
            ],
            "named_graph_uri": ["https://named.graph", "https://othernamed.graph"],
        },
        expected={
            "query": ["select * where {?s ?p ?o}"],
            "default-graph-uri": [
                "https://default.graph",
                "https://otherdefault.graph",
            ],
            "named-graph-uri": ["https://named.graph", "https://othernamed.graph"],
        },
    ),
]

update_request_params = [
    ProtocolRequestParameters(
        kwargs={"using_graph_uri": "https://named.graph"},
        expected={
            "update": ["insert data {}"],
            "using-graph-uri": ["https://named.graph"],
        },
    ),
    ProtocolRequestParameters(
        kwargs={"using_graph_uri": ["https://named.graph", "https://othernamed.graph"]},
        expected={
            "update": ["insert data {}"],
            "using-graph-uri": ["https://named.graph", "https://othernamed.graph"],
        },
    ),
    ProtocolRequestParameters(
        kwargs={
            "using_named_graph_uri": [
                "https://named.graph",
                "https://othernamed.graph",
            ],
        },
        expected={
            "update": ["insert data {}"],
            "using-named-graph-uri": [
                "https://named.graph",
                "https://othernamed.graph",
            ],
        },
    ),
    ProtocolRequestParameters(
        kwargs={
            "using_graph_uri": "https://named.graph",
            "using_named_graph_uri": "https://othernamed.graph",
        },
        expected={
            "update": ["insert data {}"],
            "using-graph-uri": ["https://named.graph"],
            "using-named-graph-uri": ["https://othernamed.graph"],
        },
    ),
    ProtocolRequestParameters(
        kwargs={
            "using_graph_uri": ["https://named.graph"],
            "using_named_graph_uri": ["https://othernamed.graph"],
        },
        expected={
            "update": ["insert data {}"],
            "using-graph-uri": ["https://named.graph"],
            "using-named-graph-uri": ["https://othernamed.graph"],
        },
    ),
]


@pytest.mark.parametrize("param", query_request_params)
def test_sparqlwrapper_query_request_params(param, triplestore):
    sparqlwrapper = SPARQLWrapper(sparql_endpoint=triplestore.sparql_endpoint)
    response = sparqlwrapper.query("select * where {?s ?p ?o}", **param.kwargs)

    assert parse_response_qs(response) == param.expected


@pytest.mark.parametrize("param", update_request_params)
def test_sparqlwrapper_update_request_params(param, triplestore):
    sparqlwrapper = SPARQLWrapper(update_endpoint=triplestore.update_endpoint)
    response = sparqlwrapper.update("insert data {}", **param.kwargs)

    assert parse_response_qs(response) == param.expected
