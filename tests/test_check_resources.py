#!/usr/bin/env python3

"""Tests for images and translations."""

import csv
import hashlib
import pathlib

from dycall.util import LCIDS

root = pathlib.Path(__file__).parent.parent.resolve()


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
        msg = pathlib.Path(msgs / f"{lcid}.msg")
        assert msg.is_file()
        with open(msg, encoding="utf-8") as fp:
            for line in fp.readlines():
                command, locale = line.strip().split()[:2]
                assert command == "::msgcat::mcset"
                assert locale == lcid


def test_verify_images():
    """Verifies the MD5 checksum of all images in `dycall/img` folder."""
    csvpath = root / "tests" / "img_checksums.csv"
    with open(csvpath, newline="", encoding="utf-8") as fp:
        for filename, md5 in csv.reader(fp):
            imgpath = root / "dycall" / "img" / filename
            with open(imgpath, "rb") as img:
                assert hashlib.md5(img.read()).hexdigest() == md5
