"""Build responsive AVIF/WebP assets from the supplied and generated source images."""

from pathlib import Path

from PIL import Image, ImageOps


PROJECT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT / "dist" / "assets"
ATTACHMENTS = Path(
    r"C:\Users\PRASAD\.codex\codex-remote-attachments\01a077e3-c71b-7202-b87d-25f200fe946f"
    r"\BF1785EA-84B4-40E9-B7E9-679AA5550D23"
)
GENERATED = Path(
    r"C:\Users\PRASAD\.codex\generated_images\01a077e9-a4b3-7393-986e-10a5ba745c78"
)

SOURCES = {
    "hero-finished": ATTACHMENTS / "6-stage5_finished.jpg",
    "cad-requirement": GENERATED / "exec-be444b52-0985-47d3-9f56-198ede88923f.png",
    "raw-material": ATTACHMENTS / "1-stage1_raw.jpg",
    "rough-machined": GENERATED / "exec-2ba517f9-f2c4-412b-a875-6f2c49269638.png",
    "turning": ATTACHMENTS / "3-stage2_cutting.jpg",
    "cnc-milling": ATTACHMENTS / "7-stage3_milling.jpg",
    "inspection": ATTACHMENTS / "4-stage4_inspect.jpg",
    "delivery": GENERATED / "exec-bc2f2759-9e5d-490f-a9f4-3868cac01bad.png",
    "turned-components": ATTACHMENTS / "2-turned_gears.jpg",
    "press-tool": ATTACHMENTS / "5-press_tool.jpg",
    "fabrication": ATTACHMENTS / "8-welding.jpg",
}

WIDTHS = (960, 1536)
CROPS = {
    # Keep the supplied welding scene focused on the process and remove the
    # unrelated machine-brand panel at the far right.
    "fabrication": (0, 0, 1220, 1024),
}


def render(source: Path, name: str) -> None:
    image = ImageOps.exif_transpose(Image.open(source)).convert("RGB")
    if name in CROPS:
        image = image.crop(CROPS[name])
    for width in WIDTHS:
        if image.width <= width:
            resized = image.copy()
        else:
            height = round(image.height * width / image.width)
            resized = image.resize((width, height), Image.Resampling.LANCZOS)
        resized.save(OUTPUT / f"{name}-{width}.webp", "WEBP", quality=84, method=6)
        resized.save(OUTPUT / f"{name}-{width}.avif", "AVIF", quality=72)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    missing = [str(path) for path in SOURCES.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing source images:\n" + "\n".join(missing))
    for name, source in SOURCES.items():
        render(source, name)
    print(f"Prepared {len(SOURCES) * len(WIDTHS) * 2} responsive assets in {OUTPUT}")


if __name__ == "__main__":
    main()
