"""Global fixture definitions for the SPARQLx test suite."""

from collections.abc import Iterator

import httpx
import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


class FusekiEndpoints:
    """Data Container for Fuseki SPARQL and Graphstore Endpoints.

    Endpoints are computed given a host and port.
    The class implements the Iterable protocol for unpacking.
    """

    def __init__(self, host, port):
        self._endpoint_base = f"http://{host}:{port}/ds"

        self.sparql_endpoint = f"{self._endpoint_base}/sparql"
        self.graphstore_endpoint = f"{self._endpoint_base}/data"

    def __iter__(self):
        return iter((self.sparql_endpoint, self.graphstore_endpoint))


@pytest.fixture(scope="session")
def fuseki_service() -> Iterator[FusekiEndpoints]:
    """Fixture that starts a Fuseki Triplestore container and exposes an Endpoint object."""
    with (
        DockerContainer("secoresearch/fuseki")
        .with_exposed_ports(3030)
        .with_env("ENABLE_DATA_WRITE", "true")
    ) as container:
        wait_for_logs(container, "Start Fuseki")

        host = container.get_container_host_ip()
        port = container.get_exposed_port(3030)

        endpoints = FusekiEndpoints(host=host, port=port)
        yield endpoints


@pytest.fixture(scope="function")
def fuseki_service_graph(fuseki_service) -> Iterator[FusekiEndpoints]:
    """Dependent Fixture that ingests an RDF graph into a running Fuseki container.

    Note that, since `tdb:unionDefaultGraph` is set to `true` in the image,
    data ingest via the Graphstore Protocol has to target a named graph.
    See https://jena.apache.org/documentation/tdb/datasets.html (Section: Dataset Query).
    """
    _, graphstore_endpoint = fuseki_service
    auth = httpx.BasicAuth(username="admin", password="pw")

    with httpx.Client(auth=auth) as client, open("tests/data/test_graph.ttl") as f:
        response = client.put(
            url=f"{graphstore_endpoint}?graph=urn%3Agraph",
            content=f.read(),
            headers={"Content-Type": "text/turtle"},
        )
        response.raise_for_status()

        yield fuseki_service

        client.delete(
            url=f"{graphstore_endpoint}?graph=urn%3Agraph",
        )
