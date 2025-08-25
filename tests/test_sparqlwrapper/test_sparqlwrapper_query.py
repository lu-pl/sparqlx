"""Pytest entry point for basic SPARQLWrapper Query Operation tests."""

from sparqlx import SPARQLWrapper


def test_sparqlwrapper_query(fuseki_service):
    endpoint: str = fuseki_service
    sparqlwrapper = SPARQLWrapper(endpoint=endpoint)

    query = """
    SELECT ?x ?y
    WHERE {
      VALUES (?x ?y) {
        (1 2)
        (3 4)
      }
    }
    """

    result = sparqlwrapper.query(query, convert=True)
    assert list(result) == [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
