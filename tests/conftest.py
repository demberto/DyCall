# -*- coding: utf-8 -*-
import appdirs
import pytest

from dycall.app import App


@pytest.fixture
def create_app(monkeypatch, tmp_path):
    def mock_config_dir(*_):
        return tmp_path

    monkeypatch.setattr(appdirs, "user_config_dir", mock_config_dir)
    return App()
