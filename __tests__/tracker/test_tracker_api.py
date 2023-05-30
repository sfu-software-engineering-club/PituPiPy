import pytest
import mock
from tracker.tracker_api import TrackerApi


class TrackerApiTest:
    def should_create_a_thread_for_new_connection():
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

    def should_send_back_ACK_with_client_uuid_on_connection_init():
        pass
