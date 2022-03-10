# -*- coding: utf-8 -*-
from __future__ import annotations

import json


def test_default_config(create_app, tmp_path):
    create_app.destroy()
    settings_file = tmp_path / "settings.json"
    assert settings_file.is_file()
    with open(settings_file) as fp:
        s: dict = json.load(fp)
    assert set(s.keys()) == set(("geometry", "out_mode", "locale", "recents", "theme"))
