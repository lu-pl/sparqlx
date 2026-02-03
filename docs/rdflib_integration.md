# RDFLib Integration

## SPARQL Result Conversion
[todo]

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
