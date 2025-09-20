from collections import UserDict

from rdflib.plugins.sparql import prepareQuery
from sparqlx.utils.converters import _convert_ask, _convert_bindings, _convert_graph
from sparqlx.utils.types import _TRequestDataValue, _TResponseFormat


class MimeTypeMap(UserDict):
    def __missing__(self, key):
        return key


bindings_format_map = MimeTypeMap(
    {
        "json": "application/sparql-results+json",
        "xml": "application/sparql-results+xml",
        "csv": "text/csv",
        "tsv": "text/tab-separated-values",
    }
)
graph_format_map = MimeTypeMap(
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


class QueryOperationParameters:
    def __init__(
        self,
        query: str,
        convert: bool | None = None,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> None:
        self._query = query
        self._convert = convert
        self._query_type = prepareQuery(query).algebra.name
        self._response_format = response_format

        self.data: SPARQLOperationDataMap = SPARQLOperationDataMap(
            query=query,
            version=version,
            default_graph_uri=default_graph_uri,
            named_graph_uri=named_graph_uri,
        )
        self.headers = {
            "Accept": self.response_format,
            "Content-Type": "application/x-www-form-urlencoded",
        }

    @property
    def converter(self):
        match self._query_type:
            case "SelectQuery":
                converter = _convert_bindings
            case "AskQuery":
                converter = _convert_ask
            case "DescribeQuery" | "ConstructQuery":
                converter = _convert_graph
            case _:  # pragma: no cover
                raise ValueError(f"Unsupported query type: {self._query_type}")

        return converter

    @property
    def response_format(self) -> str:
        match self._query_type:
            case "SelectQuery" | "AskQuery":
                _response_format = bindings_format_map[self._response_format or "json"]

                if self._convert and _response_format not in [
                    "application/json",
                    "application/sparql-results+json",
                ]:
                    msg = "JSON response format required for convert=True on SELECT and ASK query results."
                    raise ValueError(msg)

            case "DescribeQuery" | "ConstructQuery":
                _response_format = graph_format_map[self._response_format or "turtle"]
            case _:  # pragma: no cover
                raise ValueError(f"Unsupported query type: {self._query_type}")

        return _response_format


class UpdateOperationParameters:
    def __init__(
        self,
        update_request: str,
        version: str | None = None,
        using_graph_uri: _TRequestDataValue = None,
        using_named_graph_uri: _TRequestDataValue = None,
    ):
        self.data: SPARQLOperationDataMap = SPARQLOperationDataMap(
            update=update_request,
            version=version,
            using_graph_uri=using_graph_uri,
            using_named_graph_uri=using_named_graph_uri,
        )
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
