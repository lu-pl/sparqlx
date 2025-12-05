"""HTTP client management for SPARQL operations.

This module provides the ClientManager class which handles httpx.Client and
httpx.AsyncClient lifecycle management, including automatic creation, logging
hook attachment, and proper cleanup.
"""

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
    """Manages httpx Client instances for SPARQL operations.

    This class handles the lifecycle of httpx.Client and httpx.AsyncClient instances,
    providing context managers for proper resource management, and automatically
    attaching logging hooks to clients.
    """

    def __init__(
        self,
        client: httpx.Client | None = None,
        client_config: dict | None = None,
        aclient: httpx.AsyncClient | None = None,
        aclient_config: dict | None = None,
    ) -> None:
        """Initialize a ClientManager instance.

        Args:
            client: Optional pre-configured httpx.Client for synchronous requests.
                If None, a new client will be created on demand.
            client_config: Configuration dict for creating a new httpx.Client.
                Only used if client is None.
            aclient: Optional pre-configured httpx.AsyncClient for async requests.
                If None, a new async client will be created on demand.
            aclient_config: Configuration dict for creating a new httpx.AsyncClient.
                Only used if aclient is None.

        """
        self._client = client
        self._client_config = client_config
        self._aclient = aclient
        self._aclient_config = aclient_config

    @property
    def client(self) -> httpx.Client:
        """Get or create the synchronous httpx.Client.

        Returns:
            httpx.Client: A client instance with logging hooks attached.

        """
        return self._get_client(client=self._client, client_config=self._client_config)

    @property
    def aclient(self) -> httpx.AsyncClient:
        """Get or create the asynchronous httpx.AsyncClient.

        Returns:
            httpx.AsyncClient: An async client instance with logging hooks attached.

        """
        return self._get_aclient(
            aclient=self._aclient, aclient_config=self._aclient_config
        )

    @contextmanager
    def context(self) -> Iterator[httpx.Client]:
        """Provide a context manager for synchronous client operations.

        If a client was provided during initialization, it will be yielded and
        a warning will be issued about resource management. If no client was
        provided, a new client is created and automatically closed on exit.

        Yields:
            httpx.Client: The managed client instance.

        """
        client = self.client
        yield client

        if self._client is None:
            client.close()
            return
        self._open_client_warning(client)

    @asynccontextmanager
    async def acontext(self) -> AsyncIterator[httpx.AsyncClient]:
        """Provide a context manager for asynchronous client operations.

        If an async client was provided during initialization, it will be yielded
        and a warning will be issued about resource management. If no client was
        provided, a new async client is created and automatically closed on exit.

        Yields:
            httpx.AsyncClient: The managed async client instance.

        """
        aclient = self.aclient
        yield aclient

        if self._aclient is None:
            await aclient.aclose()
            return
        self._open_client_warning(aclient)

    @staticmethod
    def _open_client_warning(client: httpx.Client | httpx.AsyncClient) -> None:
        """Issue a warning about unmanaged client resources.

        Args:
            client: The client instance that is not being managed by the
                ClientManager (was provided by the user).

        """
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
        """Add an event hook to a client if not already present.

        Args:
            client: The client instance to add the hook to.
            hook_type: Type of hook to add, either "request" or "response".
            hook: The event hook function to add.

        """
        if hook not in (hooks := client.event_hooks[hook_type]):
            hooks.append(hook)

    def _get_client(
        self, client: httpx.Client | None, client_config: dict | None
    ) -> httpx.Client:
        """Get or create a synchronous client with logging hooks attached.

        Args:
            client: Optional pre-configured httpx.Client.
            client_config: Configuration dict for creating a new client if
                client is None.

        Returns:
            httpx.Client: A client instance with logging hooks attached.

        """
        client = httpx.Client(**(client_config or {})) if client is None else client

        self._add_event_hook(client, "request", log_request)
        self._add_event_hook(client, "response", log_response)

        return client

    def _get_aclient(
        self, aclient: httpx.AsyncClient | None, aclient_config: dict | None
    ) -> httpx.AsyncClient:
        """Get or create an asynchronous client with logging hooks attached.

        Args:
            aclient: Optional pre-configured httpx.AsyncClient.
            aclient_config: Configuration dict for creating a new async client
                if aclient is None.

        Returns:
            httpx.AsyncClient: An async client instance with logging hooks attached.

        """
        aclient = (
            httpx.AsyncClient(**(aclient_config or {})) if aclient is None else aclient
        )

        self._add_event_hook(aclient, "request", alog_request)
        self._add_event_hook(aclient, "response", alog_response)

        return aclient
