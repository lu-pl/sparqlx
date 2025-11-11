# SPARQLx ✨🦋

![tests](https://github.com/lu-pl/sparqlx/actions/workflows/tests.yml/badge.svg)
[![coverage](https://coveralls.io/repos/github/lu-pl/sparqlx/badge.svg?branch=lupl/setup-test-ci)](https://coveralls.io/github/lu-pl/sparqlx?branch=lupl/setup-test-ci)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

Python library for [httpx](https://www.python-httpx.org/)-based SPARQL Query and Update Operations according to the [SPARQL 1.2 Protocol](https://www.w3.org/TR/sparql12-protocol/).


> WARNING: This project is in an early stage of development and should be used with caution.

## Features

- **Async Interface**: `asyncio` support with `aquery()` and `AsyncContextManager` API.
- **Query Response Streaming**: Streaming iterators for large result sets available with `query_stream()` and `aquery_stream()`
- **Synchronous Concurrency Wrapper**: Support for concurrent execution of multiple queries from synchronous code with `queries()`
- **RDFLib Integration**: Direct conversion to [RDFLib](https://github.com/RDFLib/rdflib) SPARQL result representations
- **Context Managers**: Synchronous and asynchronous context managers for lexical resource management
- **Client Sharing**: Support for sharing and re-using `httpx` clients for HTTP connection pooling


## Installation
`sparqlx` is a [PEP 621](https://peps.python.org/pep-0621/)-compliant package and available on PyPI.

```shell
pip install sparqlx
```


## Usage

> Also see the [Recipes](#Recipes) section below.

### SPARQLWrapper.query

To run a query against an endpoint, instantiate a `SPARQLWrapper` object and call its `query` method:

```python
from sparqlx import SPARQLWrapper

sparql_wrapper = SPARQLWrapper(
	sparql_endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql"
)

result: httpx.Response = sparql_wrapper.query("select * where {?s ?p ?o} limit 10")
```

The default response formats are JSON for `SELECT` and `ASK` queries and Turtle for `CONSTRUCT` and `DESCRIBE` queries.

`SPARQLWrapper.query` features a `response_format` parameter that takes

- `"json"`, `"xml"`, `"csv"`, `"tsv"` for `SELECT` and `ASK` queries
- `"turtle"`, `"xml"`, `"ntriples"`, `"json-ld"` for `CONSTRUCT` and `DESCRIBE` queries
- any other string; the supplied value will be passed as MIME Type to the `Accept` header.


If the `convert` parameter is set to `True`, `SPARQLWrapper.query` returns

- a `list` of Python dictionaries with dict-values cast to RDFLib objects for `SELECT` queries
- a Python `bool` for `ASK` queries
- an `rdflib.Graph` instance for `CONSTRUCT` and `DESCRIBE` queries.

Note that only JSON is supported as a response format for `convert=True` on `SELECT` and `ASK` query results.

#### Converted Result Typing

The return type for calls to `SPARQLWrapper.query` with `convert=True` is a union type `list[sparqlx._TSPARQLBinding] | bool | rdflib.Graph` - the actual runtime return type depends on the query type (`SELECT`, `ASK`, `CONSTRUCT` or `DESCRIBE`).

Since the query type is not known at static time, type checkers are not able to narrow the union type without explicit annotation.

`sparqlx` defines `typing.overloads` for the simple `str` subclasses
- `sparqlx.SelectQuery`,
- `sparqlx.AskQery`,
- `sparqlx.ConstructQuery` and
- `sparqlx.DescribeQuery`

which can be used to inform static checkers about the type of query and ergo allow static analysis to narrow the return type.

```python
from typing import reveal_type
from sparqlx import ConstructQuery, SPARQLWrapper


sparqlwrapper = SPARQLWrapper(sparql_endpoint=wikidata_sparql_endpoint)
query = "construct {?s ?p ?p} where {?s ?p ?o} limit 10"

result_1 = sparqlwrapper.query(query, convert=True)
result_2 = sparqlwrapper.query(ConstructQuery(query), convert=True)

reveal_type(result_1)  # list[_SPARQLBinding] | bool | rdflib.Graph
reveal_type(result_2)  # rdflib.Graph
```

> Note that fully typing `SPARQLWrapper.queries` is currently not possible since Python does not support variadic type mappings.


#### Client Sharing and Configuration

By default, `SPARQLWrapper` creates and manages `httpx.Client` instances internally.

An `httpx.Client` can also be supplied by user code; this provides a configuration interface and allows for HTTP connection pooling.

> Note that if an `httpx.Client` is supplied to `SPARQLWrapper`, user code is responsible for managing (closing) the client.

```python
import httpx
from sparqlx import SPARQLWrapper

client = httpx.Client(timeout=10.0)

sparql_wrapper = SPARQLWrapper(
	sparql_endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql", client=client
)

result: httpx.Response = sparql_wrapper.query("select * where {?s ?p ?o} limit 10")

print(client.is_closed)  # False
client.close()
print(client.is_closed)  # True
```

It is also possible to configure `SPARQLWrapper`-managed clients by passing a `dict` holding `httpx.Client` kwargs to the `client_config` parameter:

```python
from sparqlx import SPARQLWrapper

sparql_wrapper = SPARQLWrapper(
	sparql_endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql",
	client_config={"timeout": 10.0},
)

result: httpx.Response = sparql_wrapper.query("select * where {?s ?p ?o} limit 10")
```

In that case, `SPARQLWrapper` will internally create and manage `httpx.Client` instances (the default behavior if no client is provided), but will instantiate clients based on the supplied `client_config` kwargs.


---
### SPARQLWrapper.aquery

`SPARQLWrapper.aquery` is an asynchronous version of `SPARQLWrapper.query`.

```python
import asyncio
from sparqlx import SPARQLWrapper

sparql_wrapper = SPARQLWrapper(
	sparql_endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql"
)

async def run_queries(*queries: str) -> list[httpx.Response]:
	return await asyncio.gather(*[sparql_wrapper.aquery(query) for query in queries])

results: list[httpx.Response] = asyncio.run(
	run_queries(*["select * where {?s ?p ?o} limit 10" for _ in range(10)])
)
```

For client sharing or configuration of internal client instances, pass an `httpx.AsyncClient` instance to `aclient` or kwargs to `aclient_config` respectively (see `SPARQLWrapper.query`).


---
### SPARQLWrapper.queries

`SPARQLWrapper.queries` is a synchronous wrapper around asynchronous code and allows to run multiple queries concurrently from synchronous code.

```python
from sparqlx import SPARQLWrapper

sparql_wrapper = SPARQLWrapper(
	sparql_endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql"
)

results: Iterator[httpx.Response] = sparql_wrapper.queries(
	*["select * where {?s ?p ?o} limit 100" for _ in range(10)]
)
```

Note that since `SPARQLWrapper.queries` runs async code under the hood, httpx client sharing or configuration requires setting `aclient` or `aclient_config` in the respective `SPARQLWrapper`.
Also, `SPARQLWrapper.queries` creates an event loop and therefore cannot be called from asynchronous code.

If an `httpx.AsyncClient` is supplied, the client will be closed after the first call to `SPARQLWrapper.queries`.

User code that wants to run multiple calls to `queries` can still exert control over the client by using `aclient_config`. For finer control over concurrent query execution, use the async interface.


---
### Response Streaming

HTTP Responses can be streamed using the `SPARQLWrapper.query_stream` and `SPARQLWrapper.aquery_stream` Iterators.


```python
from sparqlx import SPARQLWrapper

sparql_wrapper = SPARQLWrapper(
	sparql_endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql",
)

stream: Iterator[bytes] = sparql_wrapper.query_stream(
	"select * where {?s ?p ?o} limit 10000"
)

astream: AsyncIterator = sparql_wrapper.aquery_stream(
	"select * where {?s ?p ?o} limit 10000"
)
```

The streaming method and chunk size (for chunked responses) can be controlled with the `streaming_method` and `chunk_size` parameters respectively.


---
### Context Managers

`SPARQLWrapper` also implements the context manager protocol. This can be useful in two ways:

- Managed Client: Unless an httpx client is passed, `SPARQLWrapper` creates and manages clients internally. In that case, the context manager uses a single client per context and enables connection pooling within the context.
- Supplied Client: If an httpx client is passed, `SPARQLWrapper` will use that client instance and calling code is responsible for client management. In that case, the context manager will manage the supplied client.

```python
from sparqlx import SPARQLWrapper

sparql_wrapper = SPARQLWrapper(
	sparql_endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql",
)

with sparql_wrapper as context_wrapper:
	result: httpx.Response = context_wrapper.query("select * where {?s ?p ?o} limit 10")
```

```python
import httpx
from sparqlx import SPARQLWrapper

client = httpx.Client()

sparql_wrapper = SPARQLWrapper(
	sparql_endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql", client=client
)

with sparql_wrapper as context_wrapper:
	result: httpx.Response = context_wrapper.query("select * where {?s ?p ?o} limit 10")

	print(client.is_closed)  # False
print(client.is_closed)  # True
```

---
### Update Operations

`sparqlx` supports [Update Operations](https://www.w3.org/TR/sparql12-protocol/#update-operation) according to the SPARQL 1.2 Protocol.

The following methods implement SPARQL Update:

- `SPARQLWrapper.update`
- `SPARQLWrapper.aupdate`
- `SPARQLWrapper.updates`


Given an initially empty Triplestore with SPARQL and SPARQL Update endpoints, one could e.g. insert data like so:

```python
import httpx
from sparqlx import SPARQLWrapper

sparql_wrapper = SPARQLWrapper(
	sparql_endpoint="https://triplestore/query",
	update_endpoint="https://triplestore/update",
	aclient_config = {
		"auth": httpx.BasicAuth(username="admin", password="supersecret123")
	}
)

with sparql_wrapper as wrapper:
	store_empty: bool = not wrapper.query(
		"ask where {{?s ?p ?o} union {graph ?g {?s ?p ?o}}}", convert=True
	)
	assert store_empty, "Expected store to be empty."

	wrapper.updates(
		"insert data {<urn:s> <urn:p> <urn:o>}",
		"insert data {graph <urn:ng1> {<urn:s> <urn:p> <urn:o>}}",
		"insert data {graph <urn:ng2> {<urn:s> <urn:p> <urn:o>}}",
	)

	result = wrapper.query(
		"select ?g ?s ?p ?o where { {?s ?p ?o} union { graph ?g {?s ?p ?o} }}",
		convert=True,
	)
```

This will run the specified update operations asynchronously with an internally managed event loop; the query then returns the following Python conversion:

```python
[
	{
		"g": rdflib.term.URIRef("urn:ng2"),
		"s": rdflib.term.URIRef("urn:s"),
		"p": rdflib.term.URIRef("urn:p"),
		"o": rdflib.term.URIRef("urn:o"),
	},
	{
		"g": rdflib.term.URIRef("urn:ng1"),
		"s": rdflib.term.URIRef("urn:s"),
		"p": rdflib.term.URIRef("urn:p"),
		"o": rdflib.term.URIRef("urn:o"),
	},
	{
		"g": None,
		"s": rdflib.term.URIRef("urn:s"),
		"p": rdflib.term.URIRef("urn:p"),
		"o": rdflib.term.URIRef("urn:o"),
	},
]
```

## SPARQL 1.2 Protocol Client Implementation

`sparqlx` aims to provide a convenient Python interface for interacting with SPARQL endpoints according to the [SPARQL 1.2 Protocol](https://www.w3.org/TR/sparql12-protocol/).

The SPARQL Protocol provides a specification for HTTP operations targeting SPARQL Query and Update endpoints.

> "[The SPARQL 1.2 Protocol] describes a means for conveying SPARQL queries and updates to a SPARQL processing service and returning the results via HTTP to the entity that requested them."
> (SPARQL 1.2 Protocol - Abstract)

Generally, the SPARQL 1.2 Protocol defines the following HTTP operations for SPARQL operations:

- GET (query)
- URL-encoded POST (query and update)
- POST directly (query and update)

See [2.2 Query Operation](https://www.w3.org/TR/sparql12-protocol/#query-operation) and [2.3 Update Operation](https://www.w3.org/TR/sparql12-protocol/#update-operation).


`sparqlx` implements <b>URL-encoded POST</b> for both Query and Update operations.

This allows to send a Request Content Type in the Accept Header and both the Query/Update Request strings and Query Parameters in the Request Message Body.


### SPARQL Protocol Request Parameters

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


## Recipes

The following is a loose collection of `sparqlx` recipes.

Some of those recipes might become `sparqlx` features in the future.


### JSON Response Streaming

The example below uses [ijson](https://github.com/ICRAR/ijson) to process a `sparqlx.SPARQLWrapper.query_stream` byte stream.

Note that `ijson` currently requires an adapter for Iterator input, see issue [#58](https://github.com/ICRAR/ijson/issues/58#issuecomment-917655522).

```python
from collections.abc import Iterator

import ijson
from sparqlx import SPARQLWrapper


qlever_wikidata_endpoint = "https://qlever.cs.uni-freiburg.de/api//wikidata"
sparql_wrapper = SPARQLWrapper(sparql_endpoint=qlever_wikidata_endpoint)

json_result_stream: Iterator[bytes] = sparql_wrapper.query_stream(
	query="select ?s ?p ?o where {?s ?p ?o} limit 100000"
)

class IJSONIteratorAdapter:
	def __init__(self, byte_stream: Iterator[bytes]):
		self.byte_stream = byte_stream

	def read(self, n):
		if n == 0:
			return b""
		return next(self.byte_stream, b"")

adapter = IJSONIteratorAdapter(byte_stream=json_result_stream)
json_result_iterator: Iterator[dict] = ijson.items(adapter, "results.bindings.item")

print(next(json_result_iterator))
```

The `json_result_iterator` generator yields Python dictionaries holding SPARQL JSON response bindings coming from a byte stream. Buffering and incremental parsing is done by `ijson`.

### Graph Response Streaming

The following example processes a stream of RDF graph data coming from a SPARQL CONSTRUCT response.

It uses an Iterator chunking facility `ichunk` to implement a generator that yields sized sub-graphs from a streamed graph response.
To avoid incremental RDF parsing and possibly skolemization, `ntriples` are requested with line-based streaming.


```python
from collections.abc import Iterator
from itertools import chain, islice
from typing import cast

import httpx
from rdflib import Graph
from sparqlx import SPARQLWrapper


def ichunk[T](iterator: Iterator[T], size: int) -> Iterator[Iterator[T]]:
	_missing = object()
	chunk = islice(iterator, size)

	if (first := next(chunk, _missing)) is _missing:
		return

	yield chain[T]([cast(T, first)], chunk)
	yield from ichunk(iterator, size=size)


releven_sparql_endpoint = "https://graphdb.r11.eu/repositories/RELEVEN"
sparql_wrapper = SPARQLWrapper(sparql_endpoint=releven_sparql_endpoint)

graph_result_stream: Iterator[bytes] = sparql_wrapper.query_stream(
	query="construct {?s ?p ?o} where {?s ?p ?o} limit 100000",
	response_format="ntriples",
	streaming_method=httpx.Response.iter_lines,
)

def graph_result_iterator(size: int = 1000) -> Iterator[Graph]:
	for chunk in ichunk(graph_result_stream, size=size):
		graph = Graph()
		for ntriple in chunk:
			graph.parse(data=ntriple, format="ntriples")

		yield graph
```
