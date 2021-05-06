"""Common tests for web frameworks such as django and flask."""
import pytest

@pytest.mark.appmap_enabled
class TestRequestCapture:
    """Common tests for HTTP server request and response capture."""
    @staticmethod
    def test_http_capture(client, events):
        """Test GET request and response capture."""
        client.get('/test')

        assert events[0].http_server_request.items() >= {
            'request_method': 'GET',
            'path_info': '/test',
            'protocol': 'HTTP/1.1'
        }.items()

        response = events[1].http_server_response
        assert response.items() >= {
            'status_code': 200,
            'mime_type': 'text/html; charset=utf-8'
        }.items()

        assert 'ETag' in response['headers']

    @staticmethod
    def test_http_capture_post(client, events):
        """Test POST request with JSON body capture."""
        client.post(
            '/test', json={'my_param': 'example'}, headers={
                'Authorization': 'token "test-token"',
                'Accept': 'application/json',
                'Accept-Language': 'pl'
            }
        )

        assert events[0].http_server_request.items() >= {
            'request_method': 'POST',
            'path_info': '/test',
            'protocol': 'HTTP/1.1',
            'authorization': 'token "test-token"',
            'mime_type': 'application/json',
        }.items()

        assert events[0].http_server_request['headers'].items() >= {
            'Accept': 'application/json',
            'Accept-Language': 'pl'
        }.items()
