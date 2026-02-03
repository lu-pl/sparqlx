# RDFLib Integration

## SPARQL Result Conversion

As mentioned in the [README](../README.md), `SPARQLWrapper` query methods feature a `convert: bool` flag  for conversion of SPARQL responses to Python result representations.

E.g. if the `convert` parameter is set to `True`, `SPARQLWrapper.query` returns

- a `list` of Python dictionaries with dict-values cast to RDFLib objects for `SELECT` queries
- a Python `bool` for `ASK` queries
- an `rdflib.Graph` instance for `CONSTRUCT` and `DESCRIBE` queries.

Note that currently only JSON is supported as a response format for `convert=True` on `SELECT` and `ASK` query results.


### JSON Response Conversion of SELECT Query Results

While for graph result conversion (`CONSTRUCT` and `DESCRIBE` queries), the requested `response_format` is simply passed to `rdflib.Graph.parse` along with the response content,
the `SELECT` query converter logic in `sparqlx` processes response JSON adhering to the [SPARQL 1.2 Query Results JSON Format](https://www.w3.org/TR/sparql12-results-json/) and generates a Python mapping with RDFLib-casted JSON result values;
i.e. the conversion of `SELECT` query results returns a `list` of mappings with values of type `sparqlx.types.SPARQLResultBindingValue` (a union type `rdflib.URIRef | rdflib.BNode | sparqlx.types.LiteralToPython`).


An important divergence from the SPARQL 1.2 Query Results JSON Format lies in how `sparqlx` handles `UNDEF` SPARQL bindings in `SELECT` result conversions.
While `UNDEF` SPARQL bindings are actually *dropped entirely* for the respective result row in the standard Query Results JSON, `sparqlx` inspects the projection and guarantees stable result shapes by assigning `None` for `UNDEF` bindings.

Consider the following `VALUES` example:

```sparql
select ?x
where {
  values ?x {1 undef}
}
```

The raw JSON response for this query will be:

```json
{
  "head": {
	"vars": [
	  "x"
	]
  },
  "results": {
	"bindings": [
	  {
		"x": {
		  "datatype": "http://www.w3.org/2001/XMLSchema#integer",
		  "type": "literal",
		  "value": "1"
		}
	  },
	  {}
	]
  }
}
```

Note that the second binding map is empty.


The same query with `SPARQLWrapper.query` and `convert=True` produces the following result of type `sparqlx.types.SPARQLResultBinding`:

```python
[{'x': 1}, {'x': None}]
```

This normalization of result shapes according to the query projection is convenient for SPARQL result processing e.g. with Pydantic models or the like.


The explication of missing data as `None`-bindings in `sparqlx` has subtle consequences that one should be aware of though.

The following lists a few noteworthy cases.


#### Examples: JSON Response Conversion

- Query: `select ?s ?o where {values ?o {1} optional {?s ?p ?o}}`
  - convert=False: `{'head': {'vars': ['s', 'o']}, 'results': {'bindings': [{'o': {'datatype': 'xsd:integer', ..., 'value': '1'}}]}}`
  - convert=True: `[{'s': None, 'o': 1}]`
  - Comment: Here, optional`?s` will never be bound. The SPARQL JSON response omits unbound variables while `sparqlx` conversion guarantees stable result shapes according to the projection.

- Query: `select ?dne where {}`
  - convert=False: `{'head': {'vars': ['dne']}, 'results': {'bindings': [{}]}}`
  - convert=True: `[{ 'dne': None }]`
  - Comment: See [5.2.1 Empty Group Pattern](https://www.w3.org/TR/sparql12-query/#emptyGroupPattern) in the SPARQL 1.2 Spec. `?dne` is in the projection and therefore present in the converted result.

- Query: `select * where {}`
  -	convert=False: `{'head': {'vars': []}, 'results': {'bindings': [{}]}}`
  -	convert=True: `[{}]`
  -	Comment: The query has an Empty Group Pattern (see above). Since there are no variables in the projection, the converted result holds just an empty mapping.

- Query: `select * where {?s ?p ?o} limit 0`
  -	convert=False: `{'head': {'vars': ['s', 'p', 'o']}, 'results': {'bindings': []}}`
  -	convert=True: `[]`
  -	Comment: Variables in the projection, but no bindings; so nothing to do for the bindings converter.

- Query: `select * where {minus {?s ?p ?o}}`
  -	convert=False: `{'head': {'vars': ['s', 'p', 'o']}, 'results': {'bindings': [{}]}}`
  -	convert=True: `[{'s': None, 'p': None, 'o': None}]`
  -	Comment: The MINUS set operation performed on an Empty Group Pattern; this behaves as the Empty Group Pattern, but with variables in the projection, which has consequences for the `sparqlx` conversion.

- Query: `select * where {filter not exists {?s ?p ?o}}` (non-empty graph)
  -	convert=False: `{'head': {'vars': []}, 'results': {'bindings': []}}`
  -	convert=True: `[]`
  -	Comment: Given a non-empty graph, the existential condition in the filter clause is not satisfiable and the query therefore has no solution.

- Query: `select * where {filter not exists {?s ?p ?o}}` (empty graph)
  -	convert=False: `{'head': {'vars': ['s', 'p', 'o']}, 'results': {'bindings': [{}]}}`
  -	convert=True: `[{'s': None, 'p': None, 'o': None}]`
  -	Comment: Given an empty graph, the existential condition in the filter is always satisfiable and therefore results in an identity join on the Empty Group Pattern.

For the differences between FILTER NOT EXISTS and MINUS see [8. Negation](https://www.w3.org/TR/sparql12-query/#negation) in the SPARQL 1.2 Spec.


A generally interesting case: Join Identity/Annihilator.

- Query: `select * where {filter(true)}`
  - convert=False: `{'head': {'vars': []}, 'results': {'bindings': [{}]}}`
  - convert=True: `[{}]`
  - Comment: The filter clause is always satisfiable, so this is essentially Join Identity.

- Query: `select * where {filter(false)}`
  - convert=False: `{'head': {'vars': []}, 'results': {'bindings': []}}`
  - convert=True: `[]`
  - Comment: The filter clause is never satisfiable, so this annihilates any join.


## `rdflib.Graph` Targets

Apart from targeting remote SPARQL query and update endpoints, `SPARQLWrapper` also supports running SPARQL operations against `rdflib.Graph` objects.

```python
import httpx
from rdflib import Graph
from sparqlx import SPARQLWrapper

query = "select ?x ?y where {values (?x ?y) {(1 2) (3 4)}}"
sparql_wrapper = SPARQLWrapper(sparql_endpoint=Graph())

result: httpx.Response = sparql_wrapper.query(query)
```

The feature essentially treats `rdflib.Graph` as a SPARQL endpoint i.e. SPARQL operations are delegated to an in-memory graph object using a custom transport that builds and returns an `httpx.Response`.

> Note that response streaming is currently not supported for `rdflib.Graph` targets.

### RDF Source Constructor

The `SPARQLWrapper` class features an alternative constructor, `sparqlx.SPARQLWrapper.from_rdf_source`, that, given a `sparqlx.types.RDFParseSource`, parses the RDF source into an `rdflib.Graph` and returns a `SPARQLWrapper` instance targeting that graph object.
kwargs are forwarded to the rdflib.Graph.parse methods.

```python
from sparqlx import SPARQLWrapper

query = """
select distinct ?s
where {
	?s ?p ?o .
	filter (contains(str(?s), 'Spacetime'))
}
"""

wrapper = SPARQLWrapper.from_rdf_source(
	rdf_source="https://cidoc-crm.org/rdfs/7.1.3/CIDOC_CRM_v7.1.3.rdf"
)

result = wrapper.query(
	query=query,
	convert=True,
)

print(result)  # [{'s': URIRef('http://www.cidoc-crm.org/cidoc-crm/E92_Spacetime_Volume')}]
```

The `sparqlx.types.RDFParseSource` is the exact type expected by the `source` parameter of `rdflib.Graph.parse`.

> `sparqlx.SPARQLWrapper.from_rdf_source` creates an `rdflib.Dataset` internally in order to support RDF Quad sources.
