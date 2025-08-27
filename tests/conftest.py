"""Global fixture definitions for the SPARQLx test suite."""

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


@pytest.fixture(scope="session")
def fuseki_service():
    with DockerContainer("secoresearch/fuseki").with_exposed_ports(3030) as container:
        wait_for_logs(container, "Start Fuseki")

        host = container.get_container_host_ip()
        port = container.get_exposed_port(3030)

        sparql_endpoint = f"http://{host}:{port}/ds/sparql"

        yield sparql_endpoint
