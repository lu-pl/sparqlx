import asyncio
import random

import httpx
import pytest
from sparqlx.utils.client_manager import ClientManager


def test_client_manager_automanaged_client():
    client_manager = ClientManager()

    assert client_manager.client is not client_manager.client
    assert client_manager._client is None

    with client_manager.context() as client:
        assert not client.is_closed
    assert client.is_closed

    with client_manager.context() as client1:
        assert not client1.is_closed
        with client_manager.context() as client2:
            assert client1 is not client2

            assert not client1.is_closed
            assert not client2.is_closed

        assert not client1.is_closed
        assert client2.is_closed
    assert client1.is_closed


def test_client_shared_client():
    shared_client = httpx.Client()
    client_manager = ClientManager(client=shared_client)

    assert client_manager.client is shared_client
    assert client_manager.client is client_manager.client
    assert client_manager._client is not None

    with client_manager.context() as client:
        assert client is shared_client
        assert client is client_manager.client

        assert not client.is_closed
        assert not shared_client.is_closed

    assert not client.is_closed
    assert not shared_client.is_closed

    with client_manager.context() as client1:
        assert client1 is shared_client
        assert client1 is client_manager.client

        assert not client1.is_closed

        with client_manager.context() as client2:
            assert client1 is shared_client
            assert client1 is client_manager.client
            assert client1 is client2

            assert not client1.is_closed
            assert not client2.is_closed

        assert not client1.is_closed
        assert not client2.is_closed

    assert not client1.is_closed
    assert not client2.is_closed


@pytest.mark.asyncio
async def test_client_manager_automanaged_aclient():
    client_manager = ClientManager()

    assert client_manager.aclient is not client_manager.aclient
    assert client_manager._aclient is None

    async with client_manager.acontext() as aclient:
        assert not aclient.is_closed
    assert aclient.is_closed

    async with client_manager.acontext() as aclient1:
        assert not aclient1.is_closed
        async with client_manager.acontext() as aclient2:
            assert aclient1 is not aclient2

            assert not aclient1.is_closed
            assert not aclient2.is_closed

        assert not aclient1.is_closed
        assert aclient2.is_closed
    assert aclient1.is_closed


@pytest.mark.asyncio
async def test_client_manager_shared_aclient():
    shared_aclient = httpx.AsyncClient()
    client_manager = ClientManager(aclient=shared_aclient)

    assert client_manager.aclient is shared_aclient
    assert client_manager.aclient is client_manager.aclient
    assert client_manager._aclient is not None

    async with client_manager.acontext() as aclient:
        assert aclient is shared_aclient
        assert aclient is client_manager.aclient

        assert not aclient.is_closed
        assert not shared_aclient.is_closed

    assert not aclient.is_closed
    assert not shared_aclient.is_closed

    async with client_manager.acontext() as aclient1:
        assert aclient1 is shared_aclient
        assert aclient1 is client_manager.aclient

        assert not aclient1.is_closed

        async with client_manager.acontext() as aclient2:
            assert aclient1 is shared_aclient
            assert aclient1 is client_manager.aclient
            assert aclient1 is aclient2

            assert not aclient1.is_closed
            assert not aclient2.is_closed

        assert not aclient1.is_closed
        assert not aclient2.is_closed

    assert not aclient1.is_closed
    assert not aclient2.is_closed


@pytest.mark.asyncio
async def test_client_manager_automanaged_aclient_multi_coros():
    client_manager = ClientManager()

    async def coro(tag):
        async with client_manager.acontext() as aclient:
            assert not aclient.is_closed

            await asyncio.sleep(random.uniform(0, 0.1))

            assert not aclient.is_closed

        assert aclient.is_closed
        return tag

    _range = list(range(5))
    result = await asyncio.gather(*[coro(i) for i in _range])

    assert result == _range


@pytest.mark.asyncio
async def test_client_manager_shared_aclient_multi_coros():
    shared_aclient = httpx.AsyncClient()
    client_manager = ClientManager(aclient=shared_aclient)

    async def coro(tag):
        async with client_manager.acontext() as aclient:
            assert aclient is shared_aclient
            assert not aclient.is_closed

            await asyncio.sleep(random.uniform(0, 0.1))

            assert not aclient.is_closed
        assert not aclient.is_closed
        return tag

    _range = list(range(5))
    result = await asyncio.gather(*[coro(i) for i in _range])

    assert result == _range
    assert not shared_aclient.is_closed

    await shared_aclient.aclose()
    assert shared_aclient.is_closed
