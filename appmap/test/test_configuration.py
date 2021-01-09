"""Test Configuration"""
import appmap

from .appmap_test_base import AppMapTestBase


class TestConfiguration(AppMapTestBase):
    def test_can_be_enabled(self, monkeypatch):
        """Test that recording is enabled when APPMAP=true"""
        monkeypatch.setenv("APPMAP", "true")
        assert appmap.enabled()

    def test_is_disabled_when_unset(self, monkeypatch):
        """Test that recording is disabled when APPMAP is unset"""
        monkeypatch.delenv("APPMAP", raising=False)
        assert not appmap.enabled()

    def test_is_disabled_when_false(self, monkeypatch):
        """Test that recording is disabled when APPMAP=false"""
        monkeypatch.setenv("APPMAP", "false")
        assert not appmap.enabled()
