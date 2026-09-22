"""Build a text-only GitHub mirror of the production static site.

The connected GitHub integration can write UTF-8 files but not binary blobs.
Each selected WebP is therefore wrapped in a standards-compliant SVG data asset.
The production Sites build remains unchanged and continues to use responsive
AVIF/WebP files directly.
"""

from __future__ import annotations

import base64
import html
import re
import shutil
from pathlib import Path

from PIL import Image


PROJECT = Path(__file__).resolve().parents[1]
DIST = PROJECT / "dist"
OUTPUT = PROJECT / "github-dist"

STANDARD_BASES = (
    "cad-requirement",
    "cnc-milling",
    "delivery",
    "hero-finished",
    "inspection",
    "press-tool",
    "raw-material",
    "rough-machined",
    "turned-components",
    "turning",
)

PARTNER_BASES = (
    "fort-application-fixture",
    "fort-checking-fixture",
    "fort-reverse-engineering",
    "fort-spm",
)


def write_svg_asset(source: Path, destination: Path) -> None:
    with Image.open(source) as image:
        width, height = image.size
    payload = base64.b64encode(source.read_bytes()).decode("ascii")
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}"><image width="{width}" height="{height}" '
        f'preserveAspectRatio="xMidYMid slice" href="data:image/webp;base64,{payload}"/></svg>'
    )
    destination.write_text(svg, encoding="utf-8", newline="\n")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    assets = OUTPUT / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    for name in STANDARD_BASES:
        write_svg_asset(DIST / "assets" / f"{name}-1536.webp", assets / f"{name}.svg")
    for name in PARTNER_BASES:
        write_svg_asset(DIST / "assets" / f"{name}.webp", assets / f"{name}.svg")

    source_html = (DIST / "index.html").read_text(encoding="utf-8")
    source_html = re.sub(r"\n\s*<source\b[^>]*>", "", source_html)

    for name in STANDARD_BASES:
        source_html = re.sub(
            rf"assets/{re.escape(name)}-(?:960|1536)\.(?:avif|webp)",
            f"assets/{name}.svg",
            source_html,
        )
    for name in PARTNER_BASES:
        source_html = re.sub(
            rf"assets/{re.escape(name)}\.(?:avif|webp)",
            f"assets/{name}.svg",
            source_html,
        )

    source_html = source_html.replace(
        'href="assets/hero-finished.svg" type="image/avif"',
        'href="assets/hero-finished.svg" type="image/svg+xml"',
    )
    source_html = re.sub(
        r'data-base="([a-z0-9-]+)"',
        lambda match: f'data-base="{match.group(1)}" data-image="assets/{html.escape(match.group(1))}.svg"',
        source_html,
    )

    (OUTPUT / "index.html").write_text(source_html, encoding="utf-8", newline="\n")
    for name in ("styles.css", "script.js", "favicon.svg"):
        shutil.copyfile(DIST / name, OUTPUT / name)

    print(f"GitHub mirror: {OUTPUT}")


if __name__ == "__main__":
    main()
