import pytest
from unittest import mock
from tracker.tracker_api import TrackerApi
import threading


class TestTrackerApi:
    def test_should_create_a_thread_for_new_connection():
        """
        Test Requirements:
            1. Invoke create_new_client_connection on socket accepts
            2. Create a thread for the new connection made (Verify its 'Thread')
            3. check size and references of client_list so the new connection is added to the list (Equivalent Object)
        """
        with mock.patch("socket.socket") as mock_socket:
            mock_socket.accept.return_value = (None, "111.1.1.1")
            tracker_api = TrackerApi()
            # TODO
            pass

    def test_should_send_back_ACK_with_client_uuid_on_connection_init():
        pass

    def test_start_method(self):
        """
        Test Requirements:
            1. Invoke create_new_client_connection on socket accepts
            2. Create a thread for the new connection made (Verify its 'Thread')
            3. Check size and references of client_list so the new connection is added to the list (Equivalent Object)
        """
        mock_client_socket = mock.Mock()
        mock_client_socket.accept.return_value = (mock_client_socket, "111.1.1.1")

        with mock.patch("socket.socket") as mock_socket:
            mock_socket.return_value = mock_client_socket

            tracker_api = TrackerApi("127.0.0.1", 8000)
            tracker_api.start()

            # Check if create_new_client_connection was invoked
            mock_socket.assert_called_once()

            # Check if a new thread was created for the connection
            assert len(tracker_api.client_list) == 1
            connection = tracker_api.client_list[0]
            assert isinstance(connection, threading.Thread)

        tracker_api = TrackerApi("127.0.0.1", 8080)
        tracker_api.create_new_client_connection = MagicMock(
            return_value=mock_client_connection
        )

        mock_client_socket = MagicMock()
        mock_ip_addr = ("127.0.0.1", 1234)
        tracker_api.recv_socket.accept = MagicMock(
            return_value=(mock_client_socket, mock_ip_addr)
        )

        tracker_api.start()

        tracker_api.create_new_client_connection.assert_called_once_with(
            mock_client_socket, mock_ip_addr
        )
        mock_client_connection.start.assert_called_once()
        assert len(tracker_api.client_list) == 1
        assert tracker_api.client_list[0] == mock_client_connection
