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

- an `Iterator` of Python dictionaries with dict-values cast to RDFLib objects for `SELECT` queries
- a Python `bool` for `ASK` queries
- an `rdflib.Graph` instance for `CONSTRUCT` and `DESCRIBE` queries.

Note that only JSON is supported as a response format for `convert=True` on `SELECT` and `ASK` query results.


#### Client Sharing and Configuration

By default, `SPARQLWrapper` creates and manages `httpx.Client` instances internally.

An `httpx.Client` can also be supplied by user code; this provides a configuration interface and allows for HTTP connection pooling.

> Note that if an `httpx.Client` is supplied to `SPARQLWrapper`, user code is responsible for managing (closing) the client.

```python
import httpx
from sparqlx import SPARQLWrapper

client = httpx.Client(timeout=10.0)

sparql_wrapper = SPARQLWrapper(
	sparql_endpoint="https://query.wikidata.org/bigdata/namespace/wdq/sparql",
	client=client
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

Note that since `SPARQLWrapper.queries` runs async code under the hood, httpx client sharing or configuration requires setting `aclient` or `aclient_config` in the respective `SPARQLWrapper`."

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

`SPARQLx` also supports the SPARQL 1.2 Protocol [Update Operations](https://www.w3.org/TR/sparql12-protocol/#update-operation).

The following methods implement SPARQL Update Operations:

- `SPARQLWrapper.update`
- `SPARQLWrapper.aupdate`
- `SPARQLWrapper.updates`


For targeting an Update endpoint, the `update_endpoint` parameter must be supplied to `sparqlx.SPARQLWrapper`:

```python
sparql_wrapper = SPARQLWrapper(
	sparql_endpoint="https://some.endpoint/query",
	update_endpoint="https://some.endpoint/update",
	client_config = {"user": "admin", "password": "supersecret123"}
)

sparql_wrapper.update("insert data {<urn:s> <urn:p> <urn:o>}")
sparql_wrapper.query("select * where {<urn:s> ?p ?o}")
```

Update Operations are also available via the `SPARQLWrapper` context manager interface.
