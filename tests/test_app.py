#!/usr/bin/env python3

"""Tests DyCall UI and its behaviors."""

from __future__ import annotations

import json


def test_default_config(create_app, tmp_path):
    """Tests the configuration file saved on first exit."""
    create_app.destroy()
    settings_file = tmp_path / "settings.json"
    assert settings_file.is_file()
    with open(settings_file, encoding="utf-8") as fp:
        s: dict = json.load(fp)
    assert set(s.keys()) == set(
        (
            "geometry",
            "out_mode",
            "locale",
            "recents",
            "theme",
            "show_errno",
            "show_get_last_error",
        )
    )
