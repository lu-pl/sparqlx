from typing import NamedTuple

import httpx
import pytest
from sparqlx import QueryParseException, SPARQLWrapper, UpdateParseException
from sparqlx.types import (
    AskQuery,
    ConstructQuery,
    DescribeQuery,
    SPARQLQuery,
    SelectQuery,
)

from utils import acall


class OptionalParseParameters(NamedTuple):
    exception: type[Exception]
    invalid_sparql: str | SPARQLQuery = "INVALID"

    wrapper_parse: bool = True
    method_parse: bool | None = None


query_params = [
    OptionalParseParameters(exception=QueryParseException),
    OptionalParseParameters(
        invalid_sparql=SelectQuery("INVALID"),
        exception=httpx.HTTPStatusError,
        wrapper_parse=False,
    ),
    OptionalParseParameters(
        invalid_sparql=AskQuery("INVALID"),
        exception=httpx.HTTPStatusError,
        wrapper_parse=False,
    ),
    OptionalParseParameters(
        invalid_sparql=ConstructQuery("INVALID"),
        exception=httpx.HTTPStatusError,
        wrapper_parse=False,
    ),
    OptionalParseParameters(
        invalid_sparql=DescribeQuery("INVALID"),
        exception=httpx.HTTPStatusError,
        wrapper_parse=False,
    ),
    OptionalParseParameters(exception=ValueError, wrapper_parse=False),
    OptionalParseParameters(
        exception=QueryParseException, wrapper_parse=False, method_parse=True
    ),
    OptionalParseParameters(exception=QueryParseException, method_parse=True),
]


@pytest.mark.parametrize("method", ["query", "aquery"])
@pytest.mark.parametrize("param", query_params)
@pytest.mark.parametrize("managed_client", [True, False])
@pytest.mark.asyncio
async def test_sparqlwrapper_query_optional_parse(
    method, param, triplestore, managed_client
):
    sparql_endpoint: str = triplestore.sparql_endpoint

    client, aclient = (
        (httpx.Client(), httpx.AsyncClient()) if managed_client else (None, None)
    )

    sparqlwrapper = SPARQLWrapper(
        sparql_endpoint=sparql_endpoint,
        client=client,
        aclient=aclient,
        parse=param.wrapper_parse,
    )

    with pytest.raises(param.exception):
        await acall(
            sparqlwrapper, method, query=param.invalid_sparql, parse=param.method_parse
        )


update_params = [
    OptionalParseParameters(exception=UpdateParseException),
    OptionalParseParameters(
        exception=UpdateParseException, wrapper_parse=False, method_parse=True
    ),
    OptionalParseParameters(exception=UpdateParseException, method_parse=True),
    OptionalParseParameters(exception=httpx.HTTPStatusError, wrapper_parse=False),
    OptionalParseParameters(exception=httpx.HTTPStatusError, method_parse=False),
    OptionalParseParameters(
        exception=UpdateParseException, wrapper_parse=False, method_parse=True
    ),
]


@pytest.mark.parametrize("method", ["update", "aupdate"])
@pytest.mark.parametrize("param", update_params)
@pytest.mark.parametrize("managed_client", [True, False])
@pytest.mark.asyncio
async def test_sparqlwrapper_update_optional_parse(
    method, param, triplestore, managed_client
):
    update_endpoint: str = triplestore.update_endpoint

    client, aclient = (
        (httpx.Client(), httpx.AsyncClient()) if managed_client else (None, None)
    )

    sparqlwrapper = SPARQLWrapper(
        update_endpoint=update_endpoint,
        client=client,
        aclient=aclient,
        parse=param.wrapper_parse,
    )

    with pytest.raises(param.exception):
        await acall(
            sparqlwrapper,
            method,
            update_request=param.invalid_sparql,
            parse=param.method_parse,
        )
