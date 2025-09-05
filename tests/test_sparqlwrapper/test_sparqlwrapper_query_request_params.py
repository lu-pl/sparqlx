from typing import NamedTuple

import pytest

from sparqlx import SPARQLWrapper
from utils import parse_reponse_qs


class ProtocolRequestParameters(NamedTuple):
    kwargs: dict
    expected: dict


params = [
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


@pytest.mark.parametrize("param", params)
def test_sparqlwrapper_query_request_params(param, oxigraph_service):
    sparqlwrapper = SPARQLWrapper(endpoint=oxigraph_service.sparql_endpoint)
    response = sparqlwrapper.query("select * where {?s ?p ?o}", **param.kwargs)

    assert parse_reponse_qs(response) == param.expected
