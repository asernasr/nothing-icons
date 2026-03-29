#!/usr/bin/env python3
"""Invert RGB channels of all PNG files in a directory tree, preserving alpha."""

import os
import sys
from PIL import Image, ImageChops


def invert_png(path):
    img = Image.open(path).convert("RGBA")
    r, g, b, a = img.split()
    rgb = Image.merge("RGB", (r, g, b))
    rgb_inv = ImageChops.invert(rgb)
    ri, gi, bi = rgb_inv.split()

    # Zero out RGB on fully transparent pixels to keep them clean
    empty = Image.new("L", img.size, 0)
    mask = a  # use alpha as mask
    ri = Image.composite(ri, empty, mask)
    gi = Image.composite(gi, empty, mask)
    bi = Image.composite(bi, empty, mask)

    Image.merge("RGBA", (ri, gi, bi, a)).save(path)


def main():
    root = sys.argv[1]
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(".png"):
                invert_png(os.path.join(dirpath, fn))


if __name__ == "__main__":
    main()
