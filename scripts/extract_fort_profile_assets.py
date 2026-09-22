"""Extract approved website imagery from the supplied Fort Automation profile.

Usage:
    python extract_fort_profile_assets.py PROFILE.pdf OUTPUT_DIRECTORY

The page and image indexes are deliberately explicit so the website assets remain
traceable to the supplied partner profile. The source PDF is not modified.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps
from pypdf import PdfReader


SELECTIONS = {
    "fort-spm": (8, 3),
    "fort-checking-fixture": (14, 2),
    "fort-application-fixture": (19, 2),
    "fort-reverse-engineering": (21, 2),
}


def prepare(image: Image.Image, max_width: int = 960) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    if image.width > max_width:
        height = round(image.height * max_width / image.width)
        image = image.resize((max_width, height), Image.Resampling.LANCZOS)
    image = ImageEnhance.Contrast(image).enhance(1.04)
    return image


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: extract_fort_profile_assets.py PROFILE.pdf OUTPUT_DIRECTORY")

    pdf_path = Path(sys.argv[1]).resolve()
    output_dir = Path(sys.argv[2]).resolve()
    if not pdf_path.is_file():
        raise SystemExit(f"Profile not found: {pdf_path}")
    output_dir.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(pdf_path))
    for stem, (page_number, image_index) in SELECTIONS.items():
        page = reader.pages[page_number - 1]
        source_image = page.images[image_index]
        image = prepare(Image.open(io.BytesIO(source_image.data)))
        image.save(output_dir / f"{stem}.webp", "WEBP", quality=82, method=6)
        image.save(output_dir / f"{stem}.avif", "AVIF", quality=58)
        print(f"{stem}: {image.width}x{image.height}")


if __name__ == "__main__":
    main()
