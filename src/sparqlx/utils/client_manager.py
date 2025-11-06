from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from typing import Literal
import warnings

import httpx
from sparqlx.utils.logging_hooks import (
    alog_request,
    alog_response,
    log_request,
    log_response,
)


class ClientManager:
    def __init__(
        self,
        client: httpx.Client | None = None,
        client_config: dict | None = None,
        aclient: httpx.AsyncClient | None = None,
        aclient_config: dict | None = None,
    ) -> None:
        self._client = client
        self._client_config = client_config
        self._aclient = aclient
        self._aclient_config = aclient_config

    @property
    def client(self) -> httpx.Client:
        return self._get_client(client=self._client, client_config=self._client_config)

    @property
    def aclient(self) -> httpx.AsyncClient:
        return self._get_aclient(
            aclient=self._aclient, aclient_config=self._aclient_config
        )

    @contextmanager
    def context(self) -> Iterator[httpx.Client]:
        client = self.client
        yield client

        if self._client is None:
            client.close()
            return
        self._open_client_warning(client)

    @asynccontextmanager
    async def acontext(self) -> AsyncIterator[httpx.AsyncClient]:
        aclient = self.aclient
        yield aclient

        if self._aclient is None:
            await aclient.aclose()
            return
        self._open_client_warning(aclient)

    @staticmethod
    def _open_client_warning(client: httpx.Client | httpx.AsyncClient) -> None:
        msg = (
            f"httpx Client instance '{client}' is not managed. "
            "Client.close/AsyncClient.aclose should be called at some point."
        )
        warnings.warn(msg, stacklevel=2)

    @staticmethod
    def _add_event_hook(
        client: httpx.Client | httpx.AsyncClient,
        hook_type: Literal["request", "response"],
        hook: httpx._client.EventHook,
    ) -> None:
        if hook not in (hooks := client.event_hooks[hook_type]):
            hooks.append(hook)

    def _get_client(
        self, client: httpx.Client | None, client_config: dict | None
    ) -> httpx.Client:
        client = httpx.Client(**(client_config or {})) if client is None else client

        self._add_event_hook(client, "request", log_request)
        self._add_event_hook(client, "response", log_response)

        return client

    def _get_aclient(
        self, aclient: httpx.AsyncClient | None, aclient_config: dict | None
    ) -> httpx.AsyncClient:
        aclient = (
            httpx.AsyncClient(**(aclient_config or {})) if aclient is None else aclient
        )

        self._add_event_hook(aclient, "request", alog_request)
        self._add_event_hook(aclient, "response", alog_response)

        return aclient
