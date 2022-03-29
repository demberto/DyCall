#!/usr/bin/env python3

"""Pytest fixtures"""

import appdirs
import pytest

from dycall.app import App


@pytest.fixture
def create_app(monkeypatch, tmp_path):
    """Instantiates DyCall with a monkeypatched config dir."""

    def mock_config_dir(*_):
        return tmp_path

    monkeypatch.setattr(appdirs, "user_config_dir", mock_config_dir)
    return App()
