#!/usr/bin/env python3

"""Changes a particular color in an image and overwrites it.

Ref: https://stackoverflow.com/a/3850345
"""

from __future__ import annotations

import argparse
import pathlib

from colour import Color
from PIL import Image


def get_rgba(color: str) -> tuple[int, int, int, int]:
    """e.g. black -> (0, 0, 0, 255)."""
    colour = Color(color)
    red = int(colour.get_red() * 255)
    green = int(colour.get_green() * 255)
    blue = int(colour.get_blue() * 255)
    return (red, green, blue, 255)


def main(path: pathlib.Path, src: str, dst: str):  # noqa
    src_rgba = get_rgba(src)
    dst_rgba = get_rgba(dst)
    with Image.open(path) as img:
        pixdata = img.convert("RGBA").load()
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if pixdata[x, y] == src_rgba:
                    img.putpixel((x, y), dst_rgba)
        img.save(path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", type=pathlib.Path)
    ap.add_argument("src", default="black")
    ap.add_argument("dst")
    args = vars(ap.parse_args())
    main(**args)
