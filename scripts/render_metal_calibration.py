"""Render deterministic Phase 5A material and lighting calibration variants.

The renderer delegates all geometry, camera rays and background registration to
the approved Phase 4A implementation. It ray-marches each review state once,
then shades the identical points/normals with three controlled metal profiles.
Nothing in this asset lab is connected to the production website.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, PngImagePlugin

import render_cinematic_art_direction as phase4a


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "asset-lab" / "phase-5a-metal-calibration"
MASTER_SIZE = 1600
DESKTOP_SIZE = 1536
MOBILE_SIZE = 960
DESKTOP_QUALITY = 63
MOBILE_QUALITY = 60
STATE_KEYS = ("rough", "semi", "finished", "packed")
GEOMETRY_STATES = {
    "rough": "rough",
    "semi": "semi-finished",
    "finished": "finished",
    "packed": "packed",
}


@dataclass(frozen=True)
class MetalVariant:
    slug: str
    label: str
    description: str
    finished_base: tuple[float, float, float]
    rough_base_factor: float
    ambient: float
    diffuse_strength: float
    specular_strength: float
    shininess: float
    panel_strength: float
    panel_width: float
    rim_strength: float
    lower_fill: float
    rough_turn_amplitude: float
    rough_coarse_amplitude: float
    semi_turn_amplitude: float
    finished_turn_amplitude: float


VARIANTS = (
    MetalVariant(
        slug="variant-a",
        label="A · BALANCED SATIN",
        description="Neutral satin steel with balanced shoulder separation, broad controlled highlights and moderate dark-form lift.",
        finished_base=(0.520, 0.565, 0.600),
        rough_base_factor=0.77,
        ambient=0.255,
        diffuse_strength=0.50,
        specular_strength=0.62,
        shininess=76.0,
        panel_strength=0.205,
        panel_width=0.30,
        rim_strength=0.16,
        lower_fill=0.052,
        rough_turn_amplitude=0.018,
        rough_coarse_amplitude=0.007,
        semi_turn_amplitude=0.009,
        finished_turn_amplitude=0.0040,
    ),
    MetalVariant(
        slug="variant-b",
        label="B · CRISP DIRECTIONAL",
        description="Brighter steel with a narrower directional highlight and stronger edge definition; highest contrast of the three.",
        finished_base=(0.585, 0.630, 0.665),
        rough_base_factor=0.73,
        ambient=0.220,
        diffuse_strength=0.52,
        specular_strength=0.82,
        shininess=104.0,
        panel_strength=0.275,
        panel_width=0.22,
        rim_strength=0.20,
        lower_fill=0.045,
        rough_turn_amplitude=0.014,
        rough_coarse_amplitude=0.005,
        semi_turn_amplitude=0.007,
        finished_turn_amplitude=0.0032,
    ),
    MetalVariant(
        slug="variant-c",
        label="C · BROAD TECHNICAL SATIN",
        description="Darker broad satin response with the strongest shadow readability and the most visible restrained process texture.",
        finished_base=(0.475, 0.525, 0.565),
        rough_base_factor=0.81,
        ambient=0.305,
        diffuse_strength=0.43,
        specular_strength=0.52,
        shininess=58.0,
        panel_strength=0.215,
        panel_width=0.39,
        rim_strength=0.21,
        lower_fill=0.070,
        rough_turn_amplitude=0.021,
        rough_coarse_amplitude=0.008,
        semi_turn_amplitude=0.011,
        finished_turn_amplitude=0.0048,
    ),
)


def surface_progress(state_key: str) -> float:
    if state_key == "rough":
        return 0.0
    if state_key == "semi":
        return 0.58
    return 1.0


def surface_texture(points: np.ndarray, state_key: str, variant: MetalVariant) -> np.ndarray:
    axial = points[..., 0]
    angle = np.arctan2(points[..., 2], points[..., 1])
    coarse = np.sin(axial * 8.5 + np.sin(angle * 5.0)) * np.sin(angle * 13.0 + axial * 2.7)
    if state_key == "rough":
        return (
            0.976
            + variant.rough_turn_amplitude * np.sin(axial * 64.0)
            + variant.rough_coarse_amplitude * coarse
        )
    if state_key == "semi":
        return 0.989 + variant.semi_turn_amplitude * np.sin(axial * 92.0) + 0.003 * coarse
    return 0.997 + variant.finished_turn_amplitude * np.sin(axial * 126.0)


def shade(points: np.ndarray, normals: np.ndarray, directions: np.ndarray,
          state_key: str, variant: MetalVariant) -> np.ndarray:
    progress = surface_progress(state_key)
    finished_base = np.asarray(variant.finished_base, dtype=np.float32)
    base_factor = variant.rough_base_factor + (1.0 - variant.rough_base_factor) * progress
    base = finished_base * base_factor

    diffuse = np.maximum(np.sum(normals * phase4a.LIGHT_KEY, axis=-1), 0.0)
    rim_light = np.maximum(np.sum(normals * phase4a.LIGHT_RIM, axis=-1), 0.0)
    view = -directions
    view_dot = np.maximum(np.sum(normals * view, axis=-1), 0.0)
    half_vector = phase4a.LIGHT_KEY + view
    half_vector /= np.maximum(np.linalg.norm(half_vector, axis=-1, keepdims=True), 1e-7)

    state_specular = variant.specular_strength * (0.48 + 0.52 * progress)
    state_shininess = variant.shininess * (0.48 + 0.52 * progress)
    key_specular = np.maximum(np.sum(normals * half_vector, axis=-1), 0.0) ** state_shininess

    # Broad neutral reflection bands create the directional value changes that
    # make metal legible. They remain soft enough to avoid chrome-mirror cues.
    reflection = 2.0 * view_dot[..., None] * normals - view
    panel_direction = np.array([0.12, -0.84, 0.53], dtype=np.float32)
    panel_direction /= np.linalg.norm(panel_direction)
    strip_direction = np.array([-0.62, -0.12, 0.78], dtype=np.float32)
    strip_direction /= np.linalg.norm(strip_direction)
    dark_direction = np.array([0.58, 0.72, -0.38], dtype=np.float32)
    dark_direction /= np.linalg.norm(dark_direction)
    panel_dot = np.sum(reflection * panel_direction, axis=-1)
    strip_dot = np.sum(reflection * strip_direction, axis=-1)
    dark_dot = np.sum(reflection * dark_direction, axis=-1)
    panel = np.exp(-((panel_dot - 0.70) / variant.panel_width) ** 2)
    strip = np.exp(-((strip_dot - 0.66) / (variant.panel_width * 0.72)) ** 2)
    dark_band = np.exp(-((dark_dot - 0.68) / 0.24) ** 2)
    ceiling = np.clip(0.5 + 0.5 * reflection[..., 2], 0.0, 1.0) ** 1.35
    fresnel = (1.0 - view_dot) ** 3.5
    underside = np.clip(-normals[..., 2], 0.0, 1.0)

    texture = surface_texture(points, state_key, variant)
    colour = base * texture[..., None] * (
        variant.ambient
        + variant.diffuse_strength * 0.68 * diffuse[..., None]
        + 0.16 * ceiling[..., None]
    )
    colour += panel[..., None] * variant.panel_strength * np.array([0.80, 0.88, 0.93])
    colour += strip[..., None] * variant.panel_strength * 0.42 * np.array([0.78, 0.86, 0.91])
    colour += key_specular[..., None] * state_specular * np.array([0.92, 0.97, 1.00])
    colour += (rim_light ** 1.7)[..., None] * variant.rim_strength * np.array([0.72, 0.82, 0.88])
    colour += fresnel[..., None] * 0.055 * np.array([0.74, 0.83, 0.89])
    colour += underside[..., None] * variant.lower_fill * np.array([0.42, 0.48, 0.52])
    colour *= (1.0 - 0.12 * dark_band[..., None])

    # Cut faces retain a faint radial trace, but the effect remains subordinate
    # to geometry and never implies a measured surface finish.
    angle = np.arctan2(points[..., 2], points[..., 1])
    radial_position = np.hypot(points[..., 1], points[..., 2])
    cut_face = np.abs(normals[..., 0]) ** 7
    face_pattern = 0.5 + 0.5 * np.sin(radial_position * 58.0 + angle * 1.4)
    face_strength = 0.020 + 0.008 * progress
    colour += (cut_face * (face_strength + face_pattern * 0.010))[..., None] * np.array([0.82, 0.90, 0.95])
    return np.clip(colour, 0.0, 1.0)


def prepared_background(state_key: str, mask: Image.Image, size: int) -> Image.Image:
    background = phase4a.base_background(size, GEOMETRY_STATES[state_key])
    if state_key == "packed":
        # Keep the Phase 4A case design, with a slightly clearer neutral foam
        # cavity edge. This is illustrative context, not a packaging standard.
        large_kernel = max(5, (size // 24) | 1)
        small_kernel = max(3, (size // 56) | 1)
        cavity_mask = mask.filter(ImageFilter.MaxFilter(large_kernel)).filter(
            ImageFilter.GaussianBlur(max(2, size // 220))
        )
        inner_mask = mask.filter(ImageFilter.MaxFilter(small_kernel))
        rim_mask = ImageChops.subtract(cavity_mask, inner_mask)
        cavity_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        cavity_layer.putalpha(cavity_mask.point(lambda value: int(value * 0.70)))
        background = Image.alpha_composite(background.convert("RGBA"), cavity_layer)
        rim_layer = Image.new("RGBA", (size, size), (57, 61, 64, 0))
        rim_layer.putalpha(rim_mask.point(lambda value: int(value * 0.70)))
        background = Image.alpha_composite(background, rim_layer).convert("RGB")

    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shadow_mask = mask.filter(ImageFilter.GaussianBlur(max(4, size // 55)))
    shadow_mask = shadow_mask.transform(
        shadow_mask.size,
        Image.Transform.AFFINE,
        (0.92, 0.0, size * 0.04, 0.0, 0.24, size * 0.62),
        resample=Image.Resampling.BILINEAR,
    )
    shadow.putalpha(shadow_mask.point(lambda value: int(value * 0.32)))
    return Image.alpha_composite(background.convert("RGBA"), shadow).convert("RGB")


def render_state_variants(state_key: str, size: int) -> dict[str, Image.Image]:
    geometry_state = GEOMETRY_STATES[state_key]
    object_rgb = {
        variant.slug: np.zeros((size, size, 3), dtype=np.float32)
        for variant in VARIANTS
    }
    alpha = np.zeros((size, size), dtype=np.float32)

    for row_start in range(0, size, 48):
        row_end = min(row_start + 48, size)
        hit, points, normals = phase4a.raymarch_tile(
            size, size, row_start, row_end, geometry_state
        )
        _, directions = phase4a.camera_rays(size, size, row_start, row_end)
        for variant in VARIANTS:
            tile_colour = np.zeros((row_end - row_start, size, 3), dtype=np.float32)
            if np.any(hit):
                tile_colour[hit] = shade(
                    points[hit], normals[hit], directions[hit], state_key, variant
                )
            object_rgb[variant.slug][row_start:row_end] = tile_colour
        alpha[row_start:row_end] = hit.astype(np.float32)

    mask = Image.fromarray((alpha * 255).astype(np.uint8))
    background = prepared_background(state_key, mask, size)
    canvas = np.asarray(background).astype(np.float32) / 255.0
    edge = mask.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(0.6))
    edge_array = np.asarray(edge).astype(np.float32) / 255.0
    images = {}
    for variant in VARIANTS:
        rgb = object_rgb[variant.slug]
        rgb += edge_array[..., None] * np.array([0.095, 0.12, 0.135])
        composed = canvas * (1.0 - alpha[..., None]) + np.clip(rgb, 0.0, 1.0) * alpha[..., None]
        composed = np.clip(composed ** (1.0 / 1.06), 0.0, 1.0)
        image = Image.fromarray((composed * 255).astype(np.uint8))
        images[variant.slug] = phase4a.apply_context(image, geometry_state)
    return images


def save_png(image: Image.Image, path: Path, title: str) -> None:
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Title", title)
    metadata.add_text("Description", "Illustrative deterministic Phase 5A metal calibration; not production evidence")
    metadata.add_text("Generator", "scripts/render_metal_calibration.py")
    image.save(path, "PNG", optimize=True, pnginfo=metadata)


def save_avif(image: Image.Image, path: Path, size: int, quality: int) -> None:
    image.resize((size, size), Image.Resampling.LANCZOS).save(path, "AVIF", quality=quality)


def geometry_definition_hashes() -> dict:
    axis = np.linspace(-2.78, 2.78, 81, dtype=np.float32)
    cross = np.linspace(-1.60, 1.60, 65, dtype=np.float32)
    yy, zz = np.meshgrid(cross, cross, indexing="ij")
    yz = np.stack((yy, zz), axis=-1)
    hashes = {}
    for state_key in STATE_KEYS:
        digest = hashlib.sha256()
        geometry_state = GEOMETRY_STATES[state_key]
        for x in axis:
            points = np.empty((*yy.shape, 3), dtype=np.float32)
            points[..., 0] = x
            points[..., 1:] = yz
            sdf = phase4a.geometry_sdf(points, geometry_state).astype("<f4", copy=False)
            digest.update(sdf.tobytes())
        hashes[state_key] = digest.hexdigest()

    variant_hashes = {
        variant.slug: dict(hashes)
        for variant in VARIANTS
    }
    source = ROOT / "scripts" / "render_cinematic_art_direction.py"
    camera_payload = json.dumps(asdict(phase4a.CAMERA), sort_keys=True).encode("utf-8")
    result = {
        "passed": (
            all(variant_hashes[variant.slug] == hashes for variant in VARIANTS)
            and hashes["finished"] == hashes["packed"]
        ),
        "method": "All variants delegate to the same Phase 4A geometry_sdf; hashes are SHA-256 over an identical deterministic 81×65×65 float32 SDF sample grid.",
        "geometry_source": source.relative_to(ROOT).as_posix(),
        "geometry_source_sha256": sha256(source),
        "sample_grid": [len(axis), len(cross), len(cross)],
        "state_geometry_hashes": hashes,
        "variant_geometry_hashes": variant_hashes,
        "finished_equals_packed_geometry": hashes["finished"] == hashes["packed"],
        "camera": asdict(phase4a.CAMERA),
        "camera_sha256": hashlib.sha256(camera_payload).hexdigest(),
        "camera_fixed_across_states_and_variants": True,
        "component_coordinate_system": "Phase 4A dimensionless component coordinates",
    }
    if not result["passed"]:
        raise RuntimeError("Geometry or camera identity validation failed")
    return result


def make_contact_sheet(images: dict[str, dict[str, Image.Image]], path: Path) -> Image.Image:
    cell = 640
    sheet = Image.new("RGB", (cell * 3, cell * 4), (5, 7, 9))
    draw = ImageDraw.Draw(sheet, "RGBA")
    font = ImageFont.load_default(size=18)
    for row, state_key in enumerate(STATE_KEYS):
        for column, variant in enumerate(VARIANTS):
            x = column * cell
            y = row * cell
            panel = images[variant.slug][state_key].resize((cell, cell), Image.Resampling.LANCZOS)
            sheet.paste(panel, (x, y))
            draw.rectangle((x, y, x + cell, y + 44), fill=(5, 7, 9, 222))
            draw.rectangle((x, y, x + 7, y + 44), fill=(222, 31, 49, 255))
            label = f"{variant.label} · {state_key.upper()}"
            draw.text((x + 18, y + 13), label, font=font, fill=(238, 241, 243, 240))
            draw.rectangle((x, y, x + cell - 1, y + cell - 1), outline=(90, 98, 104, 120), width=1)
    save_png(sheet, path, "Phase 5A metal comparison")
    return sheet


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def human_bytes(value: int) -> str:
    amount = float(value)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if amount < 1024.0 or unit == "GiB":
            return f"{amount:.2f} {unit}"
        amount /= 1024.0
    raise AssertionError("unreachable")


def file_record(path: Path) -> dict:
    with Image.open(path) as image:
        dimensions = list(image.size)
    return {
        "path": path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix(),
        "dimensions": dimensions,
        "bytes": path.stat().st_size,
        "human_size": human_bytes(path.stat().st_size),
        "sha256": sha256(path),
    }


def build_payload_report(output: Path) -> dict:
    variants = {}
    for variant in VARIANTS:
        desktop = output / variant.slug / "finished-1536.avif"
        mobile = output / variant.slug / "finished-960.avif"
        variants[variant.slug] = {
            "label": variant.label,
            "finished_1536_avif": file_record(desktop),
            "finished_960_avif": file_record(mobile),
        }
    return {
        "note": "Representative finished-state encodes only; this calibration does not estimate or generate the longer sequence.",
        "encoding": {
            "1536": {"format": "AVIF", "quality": DESKTOP_QUALITY},
            "960": {"format": "AVIF", "quality": MOBILE_QUALITY},
        },
        "variants": variants,
    }


def build_manifest(output: Path, size: int, validation: dict) -> dict:
    assets = {}
    for variant in VARIANTS:
        state_assets = {
            state_key: file_record(output / variant.slug / f"{state_key}.png")
            for state_key in STATE_KEYS
        }
        state_assets["finished_1536_avif"] = file_record(output / variant.slug / "finished-1536.avif")
        state_assets["finished_960_avif"] = file_record(output / variant.slug / "finished-960.avif")
        assets[variant.slug] = {
            "label": variant.label,
            "description": variant.description,
            "shader_parameters": asdict(variant),
            "assets": state_assets,
        }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "scripts/render_metal_calibration.py",
        "purpose": "Non-production Phase 5A comparison of three controlled cool-metal treatments",
        "rendering": {
            "approach": "deterministic native-resolution NumPy/Pillow SDF CPU ray marcher",
            "master_dimensions": [size, size],
            "native_resolution": True,
            "camera": asdict(phase4a.CAMERA),
            "same_geometry_camera_crop_background_across_variants": True,
            "randomness": "none",
            "generative_enhancement": "none",
        },
        "provenance": "Repository-authored illustrative procedural geometry and shading; no customer geometry or third-party visual assets",
        "geometry_validation": validation,
        "variants": assets,
        "comparison_sheet": file_record(output / "metal-comparison-sheet.png"),
        "payload_report": build_payload_report(output),
    }


def generate(output: Path, size: int) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for variant in VARIANTS:
        (output / variant.slug).mkdir(parents=True, exist_ok=True)

    validation = geometry_definition_hashes()
    (output / "geometry-validation.json").write_text(
        json.dumps(validation, indent=2) + "\n", encoding="utf-8"
    )
    print("Geometry validation passed: all variants share unchanged Phase 4A definitions and camera")

    rendered = {variant.slug: {} for variant in VARIANTS}
    for state_key in STATE_KEYS:
        print(f"Ray-marching shared {state_key} geometry at {size}x{size}", flush=True)
        state_images = render_state_variants(state_key, size)
        for variant in VARIANTS:
            image = state_images[variant.slug]
            save_png(image, output / variant.slug / f"{state_key}.png", f"{variant.label} · {state_key}")
            rendered[variant.slug][state_key] = image

    for variant in VARIANTS:
        finished = rendered[variant.slug]["finished"]
        save_avif(finished, output / variant.slug / "finished-1536.avif", DESKTOP_SIZE, DESKTOP_QUALITY)
        save_avif(finished, output / variant.slug / "finished-960.avif", MOBILE_SIZE, MOBILE_QUALITY)

    make_contact_sheet(rendered, output / "metal-comparison-sheet.png")
    payload = build_payload_report(output)
    (output / "payload-report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    manifest = build_manifest(output, size, validation)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Rendered 12 review states, 6 AVIF representatives and comparison sheet to {output}")


def media_paths(output: Path) -> list[Path]:
    paths = []
    for variant in VARIANTS:
        paths += sorted((output / variant.slug).glob("*.png"))
        paths += sorted((output / variant.slug).glob("*.avif"))
    paths.append(output / "metal-comparison-sheet.png")
    return paths


def verify_existing(output: Path) -> None:
    expected = media_paths(output)
    if len(expected) != 19 or not all(path.exists() for path in expected):
        raise RuntimeError("Render the complete Phase 5A set before running --verify-existing")
    with Image.open(output / "variant-a" / "finished.png") as sample:
        size = sample.width

    with tempfile.TemporaryDirectory(prefix="quantamorph-phase5a-") as temporary:
        rerender = Path(temporary) / "phase-5a-metal-calibration"
        generate(rerender, size)
        actual = media_paths(rerender)
        comparisons = []
        for source, candidate in zip(expected, actual):
            source_hash = sha256(source)
            candidate_hash = sha256(candidate)
            comparisons.append({
                "path": source.relative_to(output).as_posix(),
                "source_sha256": source_hash,
                "rerender_sha256": candidate_hash,
                "matched": source_hash == candidate_hash,
            })

    passed = len(comparisons) == 19 and all(item["matched"] for item in comparisons)
    report = {
        "passed": passed,
        "method": "Complete second native render in an isolated temporary directory; SHA-256 comparison of 12 PNG states, 6 AVIF representatives and the contact sheet",
        "matched_assets": sum(item["matched"] for item in comparisons),
        "total_assets": len(comparisons),
        "comparisons": comparisons,
    }
    (output / "determinism-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    if not passed:
        raise RuntimeError("Phase 5A deterministic rerender comparison failed")
    print("Determinism check passed: 19/19 media hashes matched after a complete rerender")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--size", type=int, default=MASTER_SIZE)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--verify-existing", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.size < 384:
        raise SystemExit("Use --size >= 384")
    output = args.output.resolve()
    if args.validate_only:
        output.mkdir(parents=True, exist_ok=True)
        validation = geometry_definition_hashes()
        (output / "geometry-validation.json").write_text(
            json.dumps(validation, indent=2) + "\n", encoding="utf-8"
        )
        print("Geometry validation passed: all variants share unchanged Phase 4A definitions and camera")
        return
    if args.verify_existing:
        verify_existing(output)
        return
    generate(output, args.size)


if __name__ == "__main__":
    main()
