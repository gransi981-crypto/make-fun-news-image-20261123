"""Entrypoint: draw the 23 November 2026 front page to /output/entry.png.

Deterministic and offline: the renderer uses fixed text, fixed
geometry and no clock or random input, so two runs write identical
bytes.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from render import render  # noqa: E402


def main():
    out = "/output/entry.png"
    os.makedirs("/output", exist_ok=True)
    render(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
