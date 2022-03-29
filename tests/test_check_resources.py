#!/usr/bin/env python3

"""Tests for images and translations."""

from pathlib import Path

from dycall.util import LCIDS

root = Path(__file__).parent.parent.resolve()


def test_check_translations():
    """Checks if translations exist and are syntactically correct.

    1. Whether all the locale IDs (except English) mentioned in
       `dycall.util.LCIDS` have a translation file.
    2. Checks if the command `::msgcat::mcset` and the correct LCID
       is present every line.
    """
    msgs = root / "dycall/msgs"
    lcids = list(LCIDS)
    lcids.remove("en")
    for lcid in lcids:
        msg = Path(msgs / f"{lcid}.msg")
        assert msg.is_file()
        with open(msg, encoding="utf-8") as fp:
            for line in fp.readlines():
                command, locale = line.strip().split()[:2]
                assert command == "::msgcat::mcset"
                assert locale == lcid


def test_check_images():
    """Checks whether all the images used by DyCall are present in the package."""
    imgs = root / "dycall/img"
    for img in (
        "clock.png",
        "dycall.ico",
        "dycall.png",
        "github.png",
        "info.png",
        "sort.png",
        "sort_name_asc.png",
        "sort_name_desc.png",
        "theme.png",
        "translate.png",
    ):
        assert Path(imgs / img).is_file()
