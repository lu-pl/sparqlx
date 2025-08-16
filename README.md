# SPARQLWrapper ✨📡

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

Python library for running SPARQL Query and Update Operations according to the [SPARQL 1.1 Protocol](https://www.w3.org/TR/sparql11-protocol/).

## Features

- **Async Interface**: `asyncio` support with `aquery()` and `AsyncContextManager` API.
- **Query Response Streaming**: Streaming iterators for large result sets available with `query_stream()` and `aquery_stream()`
- **Synchronous Concurrency Wrapper**: Support for concurrent execution of multiple queries from synchronous code with `queries()`
- **RDFLib Integration**: Direct conversion to [RDFLib](https://github.com/RDFLib/rdflib) SPARQL result representations
- **Context Managers**: Synchronous and asynchronous context managers for lexical resource management
- **Client Sharing**: Support for sharing and re-using [httpx](https://www.python-httpx.org/) clients for HTTP connection pooling


## Installation
`sparqlwrapper` is a [PEP621](https://peps.python.org/pep-0621/)-compliant package.

The library can be installed by using e.g. [uv](https://docs.astral.sh/uv/) and will be available on PyPI soon.

## Usage

### SPARQLWrapper.query

To run a query against an endpoint, instantiate a `SPARQLWrapper` object and call its `query` method:

```python
from sparqlwrapper import SPARQLWrapper

sparqlwrapper = SPARQLWrapper(
	endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql"
)

result: httpx.Response = sparqlwrapper.query("select * where {?s ?p ?o} limit 10")
```

The default response formats are JSON for `SELECT` and `ASK` queries and Turtle for `CONSTRUCT` and `DESCRIBE` queries.

`SPARQLWrapper.query` features a `response_format` parameter that takes

- `"json"`, `"xml"`, `"csv"`, `"tsv"` for `SELECT` and `ASK` queries
- `"turtle"`, `"xml"`, `"ntriples"`, `"json-ld"` for `CONSTRUCT` and `DESCRIBE` queries
- any other string; the supplied value will be passed as MIME Type to the `Accept` header.


If the `to_rdflib` parameter is set to `True`, `SPARQLWrapper.query` returns

- an `Iterator` of Python dictionaries with dict-values cast to RDFLib objects for `SELECT` and `ASK` queries
- an `rdflib.Graph` instance for `CONSTRUCT` and `DESCRIBE` queries.

Note that only JSON is supported as a response format for `to_rdflib` conversions on `SELECT` and `ASK` query results.


#### Client Sharing and Configuration

By default, `SPARQLWrapper` creates and manages `httpx.Client` instances internally.

An `httpx.Client` can also be supplied by client code; this provides a configuration interface and allows for HTTP connection pooling.

> Note that if an `httpx.Client` is supplied to `SPARQLWrapper`, client code is responsible for managing (closing) the client.

```python
import httpx
from sparqlwrapper import SPARQLWrapper

client = httpx.Client(timeout=10.0)

sparqlwrapper = SPARQLWrapper(
	endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql", client=client
)

result: httpx.Response = sparqlwrapper.query("select * where {?s ?p ?o} limit 10")

print(client.is_closed)  # False
client.close()
print(client.is_closed)  # True
```

It is also possible to configure `SPARQLWrapper`-managed clients by passing a `dict` holding `httpx.Client` kwargs to the `client_config` parameter:

```python
from sparqlwrapper import SPARQLWrapper

sparqlwrapper = SPARQLWrapper(
	endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql",
	client_config={"timeout": 10.0},
)

result: httpx.Response = sparqlwrapper.query("select * where {?s ?p ?o} limit 10")
```

In that case, `SPARQLWrapper` will internally create and manage `httpx.Client` instances (the default behavior if no client is provided), but will instantiate clients based on the supplied `client_config` kwargs.


---
### SPARQLWrapper.aquery

`SPARQLWrapper.aquery` is an asynchronous version of `SPARQLWrapper.query`.

```python
import asyncio
from sparqlwrapper import SPARQLWrapper

sparqlwrapper = SPARQLWrapper(
	endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql"
)

async def run_queries(*queries: str) -> list[httpx.Response]:
	return await asyncio.gather(*[sparqlwrapper.aquery(query) for query in queries])

results: list[httpx.Response] = asyncio.run(
	run_queries(*["select * where {?s ?p ?o} limit 10" for _ in range(10)])
)
```

For client sharing or configuration of internal client instances, pass an `httpx.AsyncClient` instance to `aclient` or kwargs to `aclient_config` respectively (see `SPARQLWrapper.query`).


---
### SPARQLWrapper.queries

`SPARQLWrapper.queries` is a synchronous wrapper around asynchronous code and allows to run multiple queries concurrently from synchronous code.

```python
from sparqlwrapper import SPARQLWrapper

sparqlwrapper = SPARQLWrapper(
	endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql"
)

results: Iterator[httpx.Response] = sparqlwrapper.queries(
	*["select * where {?s ?p ?o} limit 100" for _ in range(10)]
)
```

Note that since `SPARQLWrapper.queries` runs async code under the hood, httpx client sharing or configuration requires setting `aclient` or `aclient_config` in the respective `SPARQLWrapper`."

If an `httpx.AsyncClient` is supplied, the client will be closed after the first call to `SPARQLWrapper.queries`.

User code that wants to run multiple calls to `queries` can still exert control over the client by using `aclient_config`. For finer control over concurrent query execution, use the async interface.

---
### Response Streaming

HTTP Responses can be streamed using the `SPARQLWrapper.query_stream` and `SPARQLWrapper.aquery_stream` Iterators.


```python
from sparqlwrapper import SPARQLWrapper

sparqlwrapper = SPARQLWrapper(
	endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql",
)

stream: Iterator[bytes] = sparqlwrapper.query_stream(
	"select * where {?s ?p ?o} limit 10000"
)

astream: AsyncIterator = sparqlwrapper.aquery_stream(
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
from sparqlwrapper import SPARQLWrapper

sparqlwrapper = SPARQLWrapper(
	endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql",
)

with sparqlwrapper as context_wrapper:
	result: httpx.Response = context_wrapper.query("select * where {?s ?p ?o} limit 10")
```

```python
import httpx
from sparqlwrapper import SPARQLWrapper

client = httpx.Client()

sparqlwrapper = SPARQLWrapper(
	endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql", client=client
)

with sparqlwrapper as context_wrapper:
	result: httpx.Response = context_wrapper.query("select * where {?s ?p ?o} limit 10")

	print(client.is_closed)  # False
print(client.is_closed)  # True
```

---
### Update Operations
SPARQL 1.1 Protocol Update Operations are supported and follow the same API structure as Query Operations.

The following methods implement SPARQL Update Operations:

- `SPARQLWrapper.update`
- `SPARQLWrapper.aupdate`
- `SPARQLWrapper.updates`

Update Operations can also be run from a `SPARQLWrapper` context manager.
