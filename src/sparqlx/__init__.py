"""SPARQLx - Enhanced SPARQL wrapper for Python.

This package provides a modern, type-safe interface for executing SPARQL queries
against SPARQL endpoints. It wraps the SPARQLWrapper library with additional
features including connection pooling, structured query types, and improved
type conversions.

The main entry point is the SPARQLWrapper class which handles query execution
and result processing.
"""

from sparqlx.sparqlwrapper import SPARQLWrapper
from sparqlx.utils.types import (
    AskQuery,
    ConstructQuery,
    DescribeQuery,
    SelectQuery,
    _TBindingsResponseFormat,
    _TGraphResponseFormat,
    _TLiteralToPython,
    _TSPARQLBinding,
    _TSPARQLBindingValue,
)
