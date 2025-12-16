"""SPARQLWrapper type definitions."""

import datetime
import decimal
from typing import Literal as PyLiteral
from xml.dom.minidom import Document

from rdflib import BNode, Literal, URIRef
from rdflib.compat import long_type
from rdflib.xsd_datetime import Duration


__all__ = (
    "RequestDataValue",
    "LiteralToPython",
    "SPARQLResultBindingValue",
    "SPARQLResultBinding",
    "SPARQLResultResponseFormat",
    "RDFResponseFormat",
    "SPARQLResponseFormat",
    "SPARQLQueryType",
    "SelectQuery",
    "AskQuery",
    "ConstructQuery",
    "DescribeQuery",
    "SPARQLQuery",
    "SPARQLQueryTypeLiteral",
)


type RequestDataValue = str | list[str] | tuple[str, ...] | None
"""Value type for httpx.RequestValue type.

See the httpx URL encoding function:
https://github.com/encode/httpx/blob/4b23574cf83307ce27d3b14b4a425dc58c57d28d/httpx/_content.py#L136
"""

type LiteralToPython = (
    Literal
    | None
    | datetime.date
    | datetime.datetime
    | datetime.time
    | datetime.timedelta
    | Duration
    | bytes
    | bool
    | int
    | float
    | decimal.Decimal
    | long_type
    | Document
)
"""Return type for rdflib.Literal.toPython.

This union type represents all possible return value types of Literal.toPython.
Return type provenance:

    - Literal: rdflib.Literal.toPython
    - None: rdflib.term._castLexicalToPython

    - datetime.datetime: rdflib.xsd_datetime.parse_datetime
    - datetime.time: rdflib.xsd_datetime.parse_time
    - datetime.timedelta, Duration: parse_xsd_duration
    - bytes: rdflib.term._unhexlify, base64.b64decode
    - bool: rdflib.term._parseBoolean
    - int, float, decimal.Decimal, long_type: rdflib.term.XSDToPython
    - Document: rdflib.term._parseXML
"""


type SPARQLResultBindingValue = URIRef | BNode | LiteralToPython
"Return type for SPARQLWrapper result mapping values."

type SPARQLResultBinding = dict[str, SPARQLResultBindingValue]

type SPARQLResultResponseFormat = PyLiteral["json", "xml", "csv", "tsv"]
type RDFResponseFormat = PyLiteral["turtle", "xml", "ntriples", "json-ld"]
type SPARQLResponseFormat = SPARQLResultResponseFormat | RDFResponseFormat


class SPARQLQueryType(str): ...


class SelectQuery(SPARQLQueryType): ...


class AskQuery(SPARQLQueryType): ...


class ConstructQuery(SPARQLQueryType): ...


class DescribeQuery(SPARQLQueryType): ...


type SPARQLQuery = str | SelectQuery | AskQuery | ConstructQuery | DescribeQuery


type SPARQLQueryTypeLiteral = PyLiteral[
    "SelectQuery", "AskQuery", "ConstructQuery", "DescribeQuery"
]
