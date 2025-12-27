"""Sad path tests for SPARQLOperationParametersConstructor."""

import pytest
from sparqlx.utils.operation_parameters import (
    QueryOperationParametersConstructor,
    UpdateOperationParametersConstructor,
)


def test_query_operation_parameters_invalid_method():
    msg = "Expected query method 'GET', 'POST' or 'POST-direct'. Got 'invalid'."
    with pytest.raises(ValueError, match=msg):
        QueryOperationParametersConstructor(
            query="select * where {}", query_type="SelectQuery"
        ).get_params("invalid")  # type: ignore


def test_update_operation_parameters_invalid_method():
    msg = "Expected update method 'POST' or 'POST-direct'. Got 'invalid'."
    with pytest.raises(ValueError, match=msg):
        UpdateOperationParametersConstructor(
            update_request="insert {} where {}"
        ).get_params("invalid")  # type: ignore
