"""Pytest entry point for basic SPARQLWrapper Query Operation tests."""

import json

import pytest
from rdflib import Graph
from rdflib.compare import isomorphic

from sparqlx import SPARQLWrapper
from sparqlx.utils.utils import _convert_ask, _convert_bindings, _convert_graph


def test_sparqlwrapper_query_select(fuseki_service):
    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

    query = """
    select ?x ?y
    where {
      values (?x ?y) {
        (1 2)
        (3 4)
      }
    }
    """

    result = sparqlwrapper.query(query)
    result_converted = sparqlwrapper.query(query, convert=True)

    expected = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]

    assert list(result_converted) == expected
    assert list(_convert_bindings(result)) == expected


def test_sparqlwrapper_query_ask_true(fuseki_service):
    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

    query = """
    ask where {
      values (?x ?y) {
        (1 2)
        (3 4)
      }
    }
    """

    result = sparqlwrapper.query(query)
    result_converted = sparqlwrapper.query(query, convert=True)

    assert result_converted == True
    assert _convert_ask(result) == True


def test_sparqlwrapper_query_ask_false(fuseki_service):
    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

    query = "ask where {?s ?p ?o}"

    result = sparqlwrapper.query(query)
    result_converted = sparqlwrapper.query(query, convert=True)

    assert result_converted == False
    assert _convert_ask(result) == False


def test_sparqlwrapper_query_construct(fuseki_service):
    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

    query = """
    construct {<urn:s> <urn:p> ?x}
    where {
    values ?x {
        1 2 3
      }
    }
    """

    result = sparqlwrapper.query(query)
    result_converted = sparqlwrapper.query(query, convert=True)

    ntriples_data = """
    <urn:s> <urn:p> "1"^^<http://www.w3.org/2001/XMLSchema#integer> .
    <urn:s> <urn:p> "3"^^<http://www.w3.org/2001/XMLSchema#integer> .
    <urn:s> <urn:p> "2"^^<http://www.w3.org/2001/XMLSchema#integer> .
    """
    expected_graph = Graph().parse(data=ntriples_data)

    assert isomorphic(_convert_graph(result), expected_graph)
    assert isomorphic(result_converted, expected_graph)


def test_sparqlwrapper_query_describe(fuseki_service):
    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

    query = "describe ?s where {?s ?p ?o}"

    result = sparqlwrapper.query(query)
    result_converted = sparqlwrapper.query(query, convert=True)

    assert not result.content
    assert not result_converted
