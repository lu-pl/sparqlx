"""Utility classes for SPARQL operation parameter management.

This module provides classes for managing SPARQL query and update operation
parameters, including MIME type mapping, request data formatting, and response
format handling.
"""

from collections import UserDict

from rdflib.plugins.sparql import prepareQuery
from sparqlx.utils.converters import _convert_ask, _convert_bindings, _convert_graph
from sparqlx.utils.types import _TRequestDataValue, _TResponseFormat


class MimeTypeMap(UserDict):
    """A dictionary that returns the key itself if not found in the mapping.

    This class extends UserDict to provide a fallback behavior where if a key
    is not found in the dictionary, the key itself is returned as the value.
    This is useful for allowing both short format names (e.g., 'json') and
    full MIME types (e.g., 'application/json') to be used interchangeably.
    """

    def __missing__(self, key):
        """Return the key itself when it's not found in the dictionary.

        Args:
            key: The key that was not found.

        Returns:
            The key itself.

        """
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
    """A dictionary for SPARQL operation request data.

    Converts keyword arguments to a dictionary suitable for use as request data,
    replacing underscores with hyphens in parameter names and filtering out None
    values. This follows SPARQL protocol parameter naming conventions.
    """

    def __init__(self, **kwargs):
        """Initialize the operation data map.

        Args:
            **kwargs: Keyword arguments representing SPARQL operation parameters.
                Parameter names with underscores are converted to hyphens, and
                parameters with None values are excluded.

        """
        self.data = {k.replace("_", "-"): v for k, v in kwargs.items() if v is not None}


class QueryOperationParameters:
    """Manages parameters for SPARQL query operations.

    This class handles the configuration of SPARQL query requests, including
    query type detection, response format selection, and appropriate converter
    function selection based on the query type.
    """

    def __init__(
        self,
        query: str,
        convert: bool | None = None,
        response_format: _TResponseFormat | str | None = None,
        version: str | None = None,
        default_graph_uri: _TRequestDataValue = None,
        named_graph_uri: _TRequestDataValue = None,
    ) -> None:
        """Initialize query operation parameters.

        Args:
            query: The SPARQL query string.
            convert: Whether to convert the response to Python objects.
            response_format: Desired response format (e.g., 'json', 'turtle').
            version: SPARQL version parameter.
            default_graph_uri: URI(s) of default graph(s) to query.
            named_graph_uri: URI(s) of named graph(s) to query.

        """
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
        """Get the appropriate converter function for the query type.

        Returns:
            A converter function (_convert_bindings, _convert_ask, or
            _convert_graph) appropriate for the detected query type.

        Raises:
            ValueError: If the query type is not supported.

        """
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
        """Get the appropriate MIME type for the response format.

        Determines the correct MIME type based on the query type and requested
        format. For SELECT/ASK queries, defaults to JSON and validates that JSON
        is used when convert=True. For CONSTRUCT/DESCRIBE queries, defaults to
        Turtle format.

        Returns:
            The MIME type string for the Accept header.

        Raises:
            ValueError: If convert=True but response format is not JSON for
                SELECT/ASK queries, or if the query type is not supported.

        """
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
    """Manages parameters for SPARQL update operations.

    This class handles the configuration of SPARQL update requests, including
    formatting request data and setting appropriate headers according to the
    SPARQL 1.1 Update protocol.
    """

    def __init__(
        self,
        update_request: str,
        version: str | None = None,
        using_graph_uri: _TRequestDataValue = None,
        using_named_graph_uri: _TRequestDataValue = None,
    ):
        """Initialize update operation parameters.

        Args:
            update_request: The SPARQL Update request string.
            version: SPARQL version parameter.
            using_graph_uri: URI(s) of graph(s) to use for the update operation.
            using_named_graph_uri: URI(s) of named graph(s) to use for the update.

        """
        self.data: SPARQLOperationDataMap = SPARQLOperationDataMap(
            update=update_request,
            version=version,
            using_graph_uri=using_graph_uri,
            using_named_graph_uri=using_named_graph_uri,
        )
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
