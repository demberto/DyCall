# -*- coding: utf-8 -*-
"""Check for images and translations."""

from pathlib import Path

from dycall.util import LCIDS

root = Path(__file__).parent.parent.resolve()


def test_check_translations():
    """Checks whther all the locale IDs (except English) mentioned in
    `dycall.util.LCIDS` have a translation file available in the package.
    """  # noqa: D205, D415
    msgs = root / "dycall/msgs"
    lcids = list(LCIDS)
    lcids.remove("en")
    for lcid in lcids:
        assert Path(msgs / f"{lcid}.msg").is_file()


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
