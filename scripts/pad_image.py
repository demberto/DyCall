#!/usr/bin/env python3

"""Adds padding to a square image an resizes it back to original resolution.

Use this for creating top menu icons. Resulting image is overwritten.
Ref: https://note.nkmk.me/en/python-pillow-add-margin-expand-canvas/
"""

import argparse
import pathlib

from PIL import Image


def main(img: pathlib.Path, padding: int):  # noqa
    with Image.open(img) as image:
        width, height = image.size
        resized = image.resize((width - (padding * 2), height - (padding * 2)))
        padded_image = Image.new(image.mode, (width, height))
        padded_image.paste(resized, (padding, padding))
    padded_image.save(img)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("img", type=pathlib.Path)
    ap.add_argument("padding", type=int)
    args = vars(ap.parse_args())
    main(**args)
