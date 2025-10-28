"""Global fixture definitions for the SPARQLx test suite."""

from collections.abc import Iterator
import time
from typing import Protocol

import httpx
import pytest

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


class _TriplestoreEndpoints(Protocol):
    sparql_endpoint: str
    update_endpoint: str
    graphstore_endpoint: str

    def __iter__(self) -> Iterator[str]:
        yield from (
            self.sparql_endpoint,
            self.update_endpoint,
            self.graphstore_endpoint,
        )


class OxiGraphEndpoints(_TriplestoreEndpoints):
    """Data Container for Oxigraph SPARQL and Graphstore Endpoints."""

    def __init__(self, host, port):
        self._endpoint_base = f"http://{host}:{port}"

        self.sparql_endpoint = f"{self._endpoint_base}/query"
        self.update_endpoint = f"{self._endpoint_base}/update"
        self.graphstore_endpoint = f"{self._endpoint_base}/store"


def wait_for_service(url: str, timeout: int = 10) -> None:
    for _ in range(10):
        try:
            response = httpx.get(url)
            if response.status_code == 200:
                break
        except httpx.RequestError:
            time.sleep(1)
        else:
            raise RuntimeError(
                f"Requested serivce at {url} "
                f"did not become available after {timeout} seconds."
            )


@pytest.fixture(scope="session")
def oxigraph_service() -> Iterator[OxiGraphEndpoints]:
    """Fixture that starts an Oxigraph Triplestore container and exposes an Endpoint object."""

    with DockerContainer("oxigraph/oxigraph").with_exposed_ports(7878) as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(7878)
        oxigraph_endpoints = OxiGraphEndpoints(host=host, port=port)

        wait_for_service(oxigraph_endpoints.sparql_endpoint, timeout=10)
        yield oxigraph_endpoints


@pytest.fixture(scope="function")
def oxigraph_service_with_data(oxigraph_service) -> Iterator[OxiGraphEndpoints]:
    """Dependent Fixture that ingests an RDF graph into a running Oxigraph container."""

    oxigraph_endpoints = oxigraph_service

    with httpx.Client() as client, open("tests/data/test_graphs.trig") as f:
        response = client.put(
            url=oxigraph_endpoints.graphstore_endpoint,
            headers={"Content-Type": "application/trig"},
            content=f.read(),
        )
        response.raise_for_status()

        yield oxigraph_endpoints

        client.delete(
            url=oxigraph_endpoints.graphstore_endpoint,
        )


class FusekiEndpoints(_TriplestoreEndpoints):
    """Data Container for Fuseki SPARQL and Graphstore Endpoints."""

    def __init__(self, host, port):
        self._endpoint_base = f"http://{host}:{port}/ds"

        self.sparql_endpoint = f"{self._endpoint_base}/sparql"
        self.update_endpoint = f"{self._endpoint_base}/update"
        self.graphstore_endpoint = f"{self._endpoint_base}/data"


@pytest.fixture(scope="session")
def fuseki_service() -> Iterator[FusekiEndpoints]:
    """Fixture that starts a Fuseki Triplestore container and exposes an Endpoint object."""

    with (
        DockerContainer("secoresearch/fuseki")
        .with_exposed_ports(3030)
        .with_env("ENABLE_DATA_WRITE", "true")
        .with_env("ENABLE_UPDATE", "true")
    ) as container:
        wait_for_logs(container, "Start Fuseki")

        host = container.get_container_host_ip()
        port = container.get_exposed_port(3030)

        endpoints = FusekiEndpoints(host=host, port=port)
        yield endpoints


@pytest.fixture(scope="function")
def fuseki_service_with_data(fuseki_service) -> Iterator[FusekiEndpoints]:
    """Dependent Fixture that ingests an RDF graph into a running Fuseki container.

    Note: For some reason, Fuseki does not accept DELETE to its GSP endpoint
    for deleting all graphs in the store. However, DROP ALL works just fine.
    """
    auth = httpx.BasicAuth(username="admin", password="pw")

    with httpx.Client(auth=auth) as client, open("tests/data/test_graphs.trig") as f:
        response = client.put(
            url=fuseki_service.graphstore_endpoint,
            content=f.read(),
            headers={"Content-Type": "application/trig"},
        )
        response.raise_for_status()

        yield fuseki_service

        client.post(url=fuseki_service.update_endpoint, data={"update": "drop all"})


@pytest.fixture(params=["oxigraph_service", "fuseki_service"])
def triplestore(request) -> _TriplestoreEndpoints:
    return request.getfixturevalue(request.param)


@pytest.fixture(params=["oxigraph_service_with_data", "fuseki_service_with_data"])
def triplestore_with_data(request) -> _TriplestoreEndpoints:
    return request.getfixturevalue(request.param)
