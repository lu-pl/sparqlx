from collections import UserDict
from collections.abc import Mapping
from typing import Protocol

from sparqlx.types import (
    RequestDataValue,
    SPARQLQuery,
    SPARQLQueryTypeLiteral,
    SPARQLResponseFormat,
)


class MimeTypeMap(UserDict):
    def __missing__(self, key):
        return key


sparql_result_response_format_map = MimeTypeMap(
    {
        "json": "application/sparql-results+json",
        "xml": "application/sparql-results+xml",
        "csv": "text/csv",
        "tsv": "text/tab-separated-values",
    }
)

rdf_response_format_map = MimeTypeMap(
    {
        "turtle": "text/turtle",
        "xml": "application/rdf+xml",
        "ntriples": "application/n-triples",
        "json-ld": "application/ld+json",
    }
)


class SPARQLOperationDataMap(UserDict):
    def __init__(self, **kwargs):
        self.data = {k.replace("_", "-"): v for k, v in kwargs.items() if v is not None}


class SPARQLOperationParametersProtocol(Protocol):
    @property
    def request_data(self) -> Mapping: ...

    @property
    def request_headers(self) -> Mapping: ...


class QueryOperationParameters(SPARQLOperationParametersProtocol):
    def __init__(
        self,
        query: SPARQLQuery,
        query_type: SPARQLQueryTypeLiteral,
        response_format: SPARQLResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: RequestDataValue = None,
        named_graph_uri: RequestDataValue = None,
    ) -> None:
        self._query = query
        self._query_type = query_type
        self._response_format = response_format
        self._version = (version,)
        self._default_graph_uri = default_graph_uri
        self._named_graph_uri = named_graph_uri

    @property
    def request_data(self) -> Mapping:
        return SPARQLOperationDataMap(
            query=self._query,
            version=self._version,
            default_graph_uri=self._default_graph_uri,
            named_graph_uri=self._named_graph_uri,
        )

    @property
    def request_headers(self) -> Mapping:
        return {
            "Accept": self._get_response_format(),
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def _get_response_format(self) -> str:
        match self._query_type:
            case "SelectQuery" | "AskQuery":
                _response_format = sparql_result_response_format_map[
                    self._response_format or "json"
                ]
            case "DescribeQuery" | "ConstructQuery":
                _response_format = rdf_response_format_map[
                    self._response_format or "turtle"
                ]
            case _:  # pragma: no cover
                raise ValueError(f"Unsupported query type: {self._query_type}")

        return _response_format


class UpdateOperationParameters(SPARQLOperationParametersProtocol):
    def __init__(
        self,
        update_request: str,
        version: str | None = None,
        using_graph_uri: RequestDataValue = None,
        using_named_graph_uri: RequestDataValue = None,
    ):
        self._update_request = (update_request,)
        self._version = version
        self._using_graph_uri = using_graph_uri
        self._using_named_graph_uri = using_named_graph_uri

    @property
    def request_data(self) -> SPARQLOperationDataMap:
        return SPARQLOperationDataMap(
            update=self._update_request,
            version=self._version,
            using_graph_uri=self._using_graph_uri,
            using_named_graph_uri=self._using_named_graph_uri,
        )

    @property
    def request_headers(self) -> Mapping:
        return {"Content-Type": "application/x-www-form-urlencoded"}
