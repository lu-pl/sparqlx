"""Pytest entry point for SPARQLWrapper httpx client sharing."""

import httpx
import pytest

from sparqlx import SPARQLWrapper


def test_client_identity():
    """Check the client attribute of a SPARQLOperationWrapper for supplied/managed client."""
    sparqlwrapper = SPARQLWrapper(endpoint="https://some.endpoint")

    client = httpx.Client()
    aclient = httpx.AsyncClient()
    sparqlwrapper_with_client = SPARQLWrapper(
        endpoint="https://some.endpoint", client=client, aclient=aclient
    )

    assert sparqlwrapper.client is None
    assert sparqlwrapper.aclient is None

    assert sparqlwrapper_with_client.client is client
    assert sparqlwrapper_with_client.aclient is aclient

    assert sparqlwrapper_with_client._client is client
    assert sparqlwrapper_with_client._aclient is aclient


def test_shared_client():
    """Check client identity and closed-status for a shared client."""
    client = httpx.Client()

    sparqlwrapper_1 = SPARQLWrapper(endpoint="https://some.endpoint", client=client)
    sparqlwrapper_2 = SPARQLWrapper(endpoint="https://some.endpoint", client=client)

    assert all(
        _client is client
        for _client in [
            sparqlwrapper_1.client,
            sparqlwrapper_1._client,
            sparqlwrapper_2.client,
            sparqlwrapper_2._client,
        ]
    )

    assert all(
        not _client.is_closed
        for _client in [
            sparqlwrapper_1.client,
            sparqlwrapper_1._client,
            sparqlwrapper_2.client,
            sparqlwrapper_2._client,
        ]
    )


def test_managed_context_client():
    """Check managed client status is a SPARQLOperationWrapper context."""

    sparqlwrapper = SPARQLWrapper(endpoint="https://some.endoint")
    assert sparqlwrapper.client is None

    with sparqlwrapper as wrapper_context:
        assert isinstance(wrapper_context.client, httpx.Client)

        context_client = wrapper_context.client
        context_client_property = wrapper_context._client

        assert context_client is context_client_property

    assert context_client.is_closed
    assert context_client_property.is_closed


def test_shared_context_client():
    """Check shard client status is a SPARQLOperationWrapper context."""
    client = httpx.Client()

    sparqlwrapper = SPARQLWrapper(endpoint="https://some.endoint", client=client)
    assert sparqlwrapper.client is client

    with sparqlwrapper as wrapper_context:
        context_client = wrapper_context.client
        context_client_property = wrapper_context._client

        assert context_client is context_client_property is client

        assert all(
            not _client.is_closed
            for _client in [client, context_client, context_client_property]
        )

    assert all(
        _client.is_closed
        for _client in [client, context_client, context_client_property]
    )
