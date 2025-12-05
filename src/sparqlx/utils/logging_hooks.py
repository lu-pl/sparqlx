"""Logging event hooks for httpx requests and responses.

This module provides structured logging functionality for HTTP requests and
responses made by the SPARQL wrapper. It implements httpx event hooks that
log detailed information about SPARQL operations.
"""

import json
import logging

import httpx


logger = logging.getLogger(__name__)


class StructuredMessage:
    """Simple structured log message class.

    This class provides structured logging output by formatting a message
    along with additional context as JSON. Implementation is based on the
    Python logging cookbook:
    https://docs.python.org/3/howto/logging-cookbook.html#implementing-structured-logging
    """

    def __init__(self, message: str, **kwargs):
        """Initialize a structured message.

        Args:
            message: The main log message.
            **kwargs: Additional structured data to include in the log output.

        """
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        """Format the structured message as a string.

        Returns:
            A string combining the message with JSON-formatted kwargs.

        """
        return "%s >>> %s" % (self.message, json.dumps(self.kwargs, default=str))


def log_request(request: httpx.Request) -> None:
    """Log an httpx request with structured information.

    This function is designed to be used as an httpx event hook. It logs
    basic request information at INFO level and detailed request information
    (including headers and content) at DEBUG level.

    Args:
        request: The httpx.Request object to log.

    See Also:
        httpx Event Hooks: https://www.python-httpx.org/advanced/event-hooks/

    """
    info_message = StructuredMessage(
        "Request",
        method=request.method,
        url=request.url,
    )
    logger.info(info_message)

    debug_message = StructuredMessage(
        "Request",
        request=request,
        method=request.method,
        url=request.url,
        content=request.content,
        headers=request.headers,
    )
    logger.debug(debug_message)


def log_response(response: httpx.Response) -> None:
    """Log an httpx response with structured information.

    This function is designed to be used as an httpx event hook. It logs
    basic response information (status code and URL) at INFO level and
    detailed response information (including headers and HTTP version) at
    DEBUG level.

    Args:
        response: The httpx.Response object to log.

    See Also:
        httpx Event Hooks: https://www.python-httpx.org/advanced/event-hooks/

    """
    info_message = StructuredMessage(
        "Response",
        status_code=response.status_code,
        url=response.url,
    )
    logger.info(info_message)

    debug_message = StructuredMessage(
        "Response",
        status_code=response.status_code,
        reason_phrase=response.reason_phrase,
        http_version=response.http_version,
        url=response.url,
        headers=response.headers,
    )
    logger.debug(debug_message)


async def alog_request(request: httpx.Request) -> None:
    """Async version of log_request for use with httpx.AsyncClient.

    This is an async wrapper around log_request() for use as an event hook
    with httpx.AsyncClient. The actual logging is synchronous.

    Args:
        request: The httpx.Request object to log.

    """
    log_request(request=request)


async def alog_response(response: httpx.Response) -> None:
    """Async version of log_response for use with httpx.AsyncClient.

    This is an async wrapper around log_response() for use as an event hook
    with httpx.AsyncClient. The actual logging is synchronous.

    Args:
        response: The httpx.Response object to log.

    """
    log_response(response=response)
