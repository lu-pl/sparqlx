"""Global fixture definitions for the SPARQLx test suite."""

from collections.abc import Iterator
import time

import httpx
import pytest
from testcontainers.core.container import DockerContainer


class OxiGraphEndpoints:
    def __init__(self, host, port):
        self._endpoint_base = f"http://{host}:{port}"

        self.sparql_endpoint = f"{self._endpoint_base}/query"
        self.update_endpoint = f"{self._endpoint_base}/update"
        self.graphstore_endpoint = f"{self._endpoint_base}/store"

    def __iter__(self):
        return iter((self.sparql_endpoint, self.graphstore_endpoint))


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
    with DockerContainer("oxigraph/oxigraph").with_exposed_ports(7878) as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(7878)
        oxigraph_endpoints = OxiGraphEndpoints(host=host, port=port)

        wait_for_service(oxigraph_endpoints.sparql_endpoint, timeout=10)
        yield oxigraph_endpoints


@pytest.fixture(scope="function")
def oxigraph_service_graph(oxigraph_service) -> Iterator[OxiGraphEndpoints]:
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
