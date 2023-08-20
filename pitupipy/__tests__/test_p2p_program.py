import pytest
import socket
import logging
from client.client import Client, ClientProfile, TrackerProfile


LOGGER = logging.getLogger(__name__)

tracker_ip = socket.gethostbyname(socket.gethostname())
tracker_port = 3500
client_ip = socket.gethostbyname(socket.gethostname())


@pytest.fixture
def client_factory():
    class ClientFactory:
        client_list = []
        tracker_ip = socket.gethostbyname(socket.gethostname())
        port = 3000

        def create(self):
            client = Client()
            client.attach_client_profile(
                ClientProfile(host=client_ip, port=ClientFactory.port)
            )
            client.attach_tracker_profile(TrackerProfile(tracker_ip, tracker_port))
            ClientFactory.client_list.append(client)
            ClientFactory.port += 1

        def destroyAll(self):
            for c in ClientFactory.client_list:
                c.shutdown()

    factory = ClientFactory()
    yield factory

    factory.destroyAll()


def test_client(client_factory):
    client = client_factory.create()
    assert True
