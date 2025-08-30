"""SPARQL queries and update requests for SPARQLx testing."""

select_query_xy_values = """
    select ?x ?y
    where {
      values (?x ?y) {
        (1 2)
        (3 4)
      }
    }
"""

select_query_types = """
prefix xsd: <http://www.w3.org/2001/XMLSchema#>

select *
where {
  values (?x) {
     (2)
     (2.2)
     (UNDEF)
     (<https://test.uri>)
     ('2024-01-01'^^xsd:date)
     ('2024'^^xsd:gYear)
     ('2024-01'^^xsd:gYearMonth)
    }
}
"""

select_query_bnode = """
select *
where {
    bind (BNODE() as ?x)
}
"""

ask_query_true = """
    ask where {
      values (?x ?y) {
        (1 2)
        (3 4)
      }
    }
"""

ask_query_false = "ask where {filter(false)}"


construct_query_x_values = """
    construct {<urn:s> <urn:p> ?x}
    where {
    values ?x {
        1 2 3
      }
    }
"""

describe_query = "describe ?s where {?s ?p ?o}"
