from pathlib import Path
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "part-evolution-master.png"
OUTPUT = ROOT / "assets"

PANELS = {
    "part-cad": (0, 0, 509, 507),
    "part-stock": (513, 0, 1023, 507),
    "part-blank": (1027, 0, 1536, 507),
    "part-rough": (0, 511, 509, 1024),
    "part-finished": (513, 511, 1023, 1024),
    "part-packed": (1027, 511, 1536, 1024),
}


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE) as sheet:
        sheet = sheet.convert("RGB")
        for name, crop_box in PANELS.items():
            panel = sheet.crop(crop_box)
            # Every state shares an identical square canvas so CSS and GSAP can
            # hold the component on one optical axis without per-stage nudges.
            panel = ImageOps.fit(panel, (512, 512), Image.Resampling.LANCZOS)
            panel.save(OUTPUT / f"{name}.webp", "WEBP", quality=86, method=6)
            panel.save(OUTPUT / f"{name}.avif", "AVIF", quality=72)


if __name__ == "__main__":
    main()
