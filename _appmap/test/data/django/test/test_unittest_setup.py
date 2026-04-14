
from unittest import TestCase

from django.test import Client

class DisabledRequestsRecordingTest(TestCase):
    def setUp(self) -> None:
        Client().get("/")

    def test_request_in_setup(self):
        pass
