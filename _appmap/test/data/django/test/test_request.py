from django.test import TestCase
from django.test import Client


class TestRequest(TestCase):
    def test_request_test(self):
        resp = self.client.get("/test")
        assert resp.status_code == 200
