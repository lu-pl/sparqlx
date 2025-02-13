# SPARQLWrapper

Simple Python wrapper around a SPARQL service.

> Warning: This is merely a **prototype** for an asynchronous version of [RDFLib/sparqlwrapper](https://github.com/RDFLib/sparqlwrapper).

## Installation
This is a [PEP621](https://peps.python.org/pep-0621/)-compliant package. I recommend using [uv](https://docs.astral.sh/uv/).

## Usage


### SPARQLWrapper

The `sparqlwrapper.SPARQLWrapper` class provides a very simple interface for running SPARQL queries against a remote service. It uses the `sparqlwrapper.SPARQLClient` and `sparqlwrapper.AsyncClient` context managers internally.

```python
endpoint = "https://graphdb.r11.eu/repositories/RELEVEN"

query = """
select *
where {
  values (?x) {
	 (2) (2.2) (UNDEF)
	 (<https://test.uri>)
	 ('2024-01-01'^^xsd:date)
	}
}
"""

sparql_wrapper = SPARQLWrapper(endpoint=endpoint)
result = sparql_wrapper.query(query, to_python=True)
```

If the `to_python` flag is set to `False` (the default) an `httpx.Response` object is returned.
If `to_python` is set to `True`, an `Iterator[dict]` is returned. In that case, `dicts` well hold flat SPARQL binding mappings with values cast to Python using `RDFLib`.

For example, in the snippet above, `list(result)` will be

```python
[
	{"x": 2},
	{"x": decimal.Decimal("2.2")},
	{"x": None},
	{"x": rdflib.term.URIRef("https://test.uri")},
	{"x": datetime.date(2024, 1, 1)},
]
```

`SPARQLWrapper.queries` is a synchronous wrapper around `sparqlwrapper.AsyncSPARQLClient`, the method takes an iterable of queries and runs the queries asynchronously against an endpoint.

```python
sparql_wrapper = SPARQLWrapper(endpoint=endpoint)
result = sparql_wrapper.queries([query_1, query_2, query_3], to_python=True)
```

This will return a list of either `httpx.Response` or a list of `Iterator[dict]` (if `to_python=True`).

### SPARQLClient

`sparqlwrapper.SPARQLClient` is a context manager that wraps `httpx.Client` and is also used in `SPARQLWrapper.query`.

The example above can be expressed with `SPARQLClient` like so:

```python
with SPARQLClient(endpoint=endpoint) as sparql_client:
	result = sparql_client.query(query, to_python=True)
```

Unlike `SPARQLWrapper`, `SPARQLClient` allows users to pass an `httpx.Client` themselves and thus utilize `httpx` connection pooling (see [Clients](https://www.python-httpx.org/advanced/clients/)).

```python
sparql_client = SPARQLClient(endpoint=endpoint, client=httpx.Client())

with sparql_client:
	result = sparql_client.query(query, to_python=True)
```

Note that if an `httpx.Client` is passed to `SPARQLClient`, the `SPARQLClient` instance will not manage the internal `client` instance, because users might wish to re-use that instance. That means that the `client` must be managed and closed manually by the callers by accessing the public `SPARQClient.client` component, e.g. in the above case : `sparql_client.client.close()`.

`SPARQLClient` will emit a warning if the `client` component is still open on exit. Should it?

### AsyncSPARQLClient

`sparqlwrapper.AsyncSPARQLClient` is an asynchronous context manager that behaves much like `sparqlwrapper.SPARQLClient`.

Both the `AsyncSPARQLClient.aquery` and `AsyncSPARQLClient.aqueries` methods are native coroutine methods and can be used to build `asyncio` applications.
