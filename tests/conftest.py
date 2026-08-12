"""Shared fixtures for the Word Clock plugin tests."""

import pytest

from plugins.word_clock import WordClockPlugin


@pytest.fixture
def manifest():
    """Minimal manifest — the plugin reads only ``id`` and ``live_data`` from it."""
    return {
        "id": "word_clock",
        "name": "Word Clock",
        "version": "1.0.0",
        "live_data": True,
    }


@pytest.fixture
def make_plugin(manifest):
    """Build a configured plugin instance."""

    def _make(**config):
        plugin = WordClockPlugin(manifest)
        plugin.config = {"timezone": "Europe/Berlin", **config}
        return plugin

    return _make
