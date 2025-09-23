"""Basic unit tests for StructuredMessage class."""

import json
from typing import Annotated, Any, NamedTuple

import pytest
from sparqlx.utils.logging_hooks import StructuredMessage


class StructuredMessageParams(NamedTuple):
    message: str
    kwargs: dict[str, Any]
    expected: dict[str, Any] | None = None


obj: Annotated[
    object, """Shared instance serving as a non-JSON-serializable object."""
] = object()


params = [
    StructuredMessageParams(
        message="Logging Message",
        kwargs={"x": 1, "y": "2"},
    ),
    StructuredMessageParams(
        message="Logging Message",
        kwargs={"x": 1, "y": None, "obj": obj},
        expected={"x": 1, "y": None, "obj": str(obj)},
    ),
    StructuredMessageParams(
        message="Logging Message",
        kwargs={"x": 1, "y": "y >>> z"},
    ),
]


@pytest.mark.parametrize("param", params)
def test_structured_message(param):
    struct_msg = StructuredMessage(message=param.message, **param.kwargs)
    message, structured = str(struct_msg).split(" >>> ", maxsplit=1)

    assert message == param.message
    assert (param.expected or param.kwargs) == json.loads(structured)
