# SPARQL 1.2 Protocol Client Implementation

`sparqlx` aims to provide a convenient Python interface for interacting with SPARQL endpoints according to the [SPARQL 1.2 Protocol](https://www.w3.org/TR/sparql12-protocol/).

The SPARQL Protocol provides a specification for HTTP operations targeting SPARQL Query and Update endpoints.

> "[The SPARQL 1.2 Protocol] describes a means for conveying SPARQL queries and updates to a SPARQL processing service and returning the results via HTTP to the entity that requested them."
> (SPARQL 1.2 Protocol - Abstract)

Generally, the SPARQL 1.2 Protocol defines the following HTTP operations for SPARQL operations:

- GET (query)
- URL-encoded POST (query and update)
- POST directly (query and update)

See [2.2 Query Operation](https://www.w3.org/TR/sparql12-protocol/#query-operation) and [2.3 Update Operation](https://www.w3.org/TR/sparql12-protocol/#update-operation).


`sparqlx` uses <b>URL-encoded POST</b> for both Query and Update operations by default.

This allows to send a Request Content Type in the Accept Header and both the Query/Update Request strings and Query/Update Parameters in the Request Message Body.

`sparqlx` also implements GET (for query operations) and POST-direct (for query and update operations); the SPARQL Operation method can be set via the `query_method: typing.Literal["GET", "POST", "POST-direct"]` and `update_method: typing.Literal["POST", "POST-direct"]` parameters in the `SPARQLWrapper` class.

## SPARQL Protocol Request Parameters

The SPARQL Protocol also specifies the following request parameters:

- version (0 or 1)
- default-graph-uri (0 or more)
- named-graph-uri (0 or more)

for **Query Operations**, where `default-graph-uri` and `named-graph-uri` correspond to SPARQL `FROM` and `FROM NAMED` respectively, and, if present, take precedence over SPARQL clauses.

- version (0 or 1)
- using-graph-uri (0 or more)
- using-named-graph-uri (0 or more)

for **Update Operations**, where `using-graph-uri` and `using-named-graph-uri` correspond to SPARQL `USING` and `USING NAMED`, and likewise take precedence over SPARQL clauses.


SPARQL Protocol request parameters are reflected in the `sparqlx` API:

- Methods implementing query operations take `default_graph_uri` and `named_graph_uri` parameters.
- Methods implementing udpate operations take `using_graph_uri` and `using_named_graph_uri` parameters.
- Both query and update methods take a `version` parameter.
