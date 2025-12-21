import abc
from collections import UserDict
from collections.abc import Mapping
from typing import Literal as TLiteral, NamedTuple

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


class SPARQLOperationParameters(NamedTuple):
    method: TLiteral["GET", "POST"]
    headers: Mapping
    content: str | None = None
    data: Mapping | None = None
    params: Mapping | None = None


class SPARQLOperationParametersConstructor(abc.ABC):
    @abc.abstractmethod
    def get_params(self, method) -> SPARQLOperationParameters: ...


class QueryOperationParametersConstructor(SPARQLOperationParametersConstructor):
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
        self._version = version
        self._default_graph_uri = default_graph_uri
        self._named_graph_uri = named_graph_uri

    def get_params(
        self, method: TLiteral["GET", "POST", "POST-direct"]
    ) -> SPARQLOperationParameters:
        match method:
            case "GET":
                return self._build_get_params()
            case "POST":
                return self._build_post_params()
            case "POST-direct":
                return self._build_post_direct_params()
            case _:
                msg = (
                    "Expected query method 'GET', 'POST' or 'POST-direct'. "
                    f"Got '{method}'."
                )
                raise ValueError(msg)

    def _build_get_params(self) -> SPARQLOperationParameters:
        return SPARQLOperationParameters(
            method="GET",
            headers={"Accept": self._get_response_format()},
            params=SPARQLOperationDataMap(
                query=self._query,
                version=self._version,
                default_graph_uri=self._default_graph_uri,
                named_graph_uri=self._named_graph_uri,
            ),
        )

    def _build_post_params(self) -> SPARQLOperationParameters:
        return SPARQLOperationParameters(
            method="POST",
            headers={
                "Accept": self._get_response_format(),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=SPARQLOperationDataMap(
                query=self._query,
                version=self._version,
                default_graph_uri=self._default_graph_uri,
                named_graph_uri=self._named_graph_uri,
            ),
        )

    def _build_post_direct_params(self) -> SPARQLOperationParameters:
        return SPARQLOperationParameters(
            method="POST",
            headers={
                "Accept": self._get_response_format(),
                "Content-Type": (
                    "application/sparql-query"
                    f"{'' if self._version is None else f'; version={self._version}'}"
                ),
            },
            content=self._query,
            params=SPARQLOperationDataMap(
                default_graph_uri=self._default_graph_uri,
                named_graph_uri=self._named_graph_uri,
            ),
        )

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


class UpdateOperationParametersConstructor(SPARQLOperationParametersConstructor):
    def __init__(
        self,
        update_request: str,
        version: str | None = None,
        using_graph_uri: RequestDataValue = None,
        using_named_graph_uri: RequestDataValue = None,
    ):
        self._update_request = update_request
        self._version = version
        self._using_graph_uri = using_graph_uri
        self._using_named_graph_uri = using_named_graph_uri

    def get_params(
        self, method: TLiteral["POST", "POST-direct"]
    ) -> SPARQLOperationParameters:
        match method:
            case "POST":
                return self._build_post_params()
            case "POST-direct":
                return self._build_post_direct_params()
            case _:
                msg = f"Expected update method 'POST' or 'POST-direct'. Got '{method}'."
                raise ValueError(msg)

    def _build_post_params(self) -> SPARQLOperationParameters:
        return SPARQLOperationParameters(
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=SPARQLOperationDataMap(
                update=self._update_request,
                version=self._version,
                using_graph_uri=self._using_graph_uri,
                using_named_graph_uri=self._using_named_graph_uri,
            ),
        )

    def _build_post_direct_params(self) -> SPARQLOperationParameters:
        return SPARQLOperationParameters(
            method="POST",
            headers={
                "Content-Type": (
                    "application/sparql-update"
                    f"{'' if self._version is None else f'; version={self._version}'}"
                ),
            },
            content=self._update_request,
            params=SPARQLOperationDataMap(
                using_graph_uri=self._using_graph_uri,
                using_named_graph_uri=self._using_named_graph_uri,
            ),
        )
