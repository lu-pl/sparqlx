import json
import logging

import httpx


logger = logging.getLogger(__name__)


class StructuredMessage:
    """Simple structured log message class.

    This is taken from the Python logging cookbook:
    https://docs.python.org/3/howto/logging-cookbook.html#implementing-structured-logging
    """

    def __init__(self, message: str, **kwargs):
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        return "%s >>> %s" % (self.message, json.dumps(self.kwargs, default=str))


def log_request(request: httpx.Request) -> None:
    """Logging event hook for httpx.Requests.

    See httpx Event Hooks:
    https://www.python-httpx.org/advanced/event-hooks/
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
    """Logging event hook for httpx.Responses.

    See httpx Event Hooks:
    https://www.python-httpx.org/advanced/event-hooks/
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
    log_request(request=request)


async def alog_response(response: httpx.Response) -> None:
    log_response(response=response)
