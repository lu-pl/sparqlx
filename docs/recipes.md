# Recipes

The following is a loose collection of `sparqlx` recipes.

Some of those recipes might become `sparqlx` features in the future.


## JSON Response Streaming

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

## Graph Response Streaming

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
