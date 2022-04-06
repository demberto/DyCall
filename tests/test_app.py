#!/usr/bin/env python3

"""Tests DyCall UI and its behaviors."""

from __future__ import annotations

import json

from dycall.app import App


def test_default_config(create_app: App, tmp_path):
    """Tests the configuration file saved on first exit.

    Since `create_app` is destroyed here, this test should run at the end.
    """
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


# def test_non_windows(create_app: App, monkeypatch: pytest.MonkeyPatch):
#     """Checks DyCall's behaviour when it is not running on WIndows.

#     This includes checking the absence of:
#     - `--call-conv` and `--hide-gle` command line options.
#     - **Calling Convention** combobox.
#     - **Options** -> **Show GetLastError** menu option.
#     - GetLastError label in status bar.
#     """
#     monkeypatch.setattr(platform, "system", "")
