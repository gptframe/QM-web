"""Generate the approved Variant B cinematic production assets.

The renderer extends the audited Phase 4B removal programme to 32 registered
samples while preserving the Phase 4A geometry, camera and 31 degree FOV. It
also produces the seven responsive key states used by the static homepage.
No production runtime dependency is introduced by this offline utility.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tempfile
from dataclasses import asdict, fields
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, PngImagePlugin

import render_cinematic_art_direction as phase4a
import render_machining_pilot as pilot
import render_metal_calibration as metal


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REVIEW = ROOT / "asset-lab" / "final-cinematic-production"
DEFAULT_DELIVERY = ROOT / "assets" / "cinematic"
MASTER_SIZE = 1600
DESKTOP_SIZE = 1536
SMALL_SIZE = 960
DESKTOP_QUALITY = 63
SMALL_QUALITY = 60
VARIANT_B = next(variant for variant in metal.VARIANTS if variant.slug == "variant-b")

# Dense samples are deliberately concentrated around the former pilot 10->11
# and 12->15 intervals, where journals and final subtractive features resolve.
PILOT_COORDINATES = (
    0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0,
    10.20, 10.40, 10.60, 10.80, 11.0,
    11.50, 12.0, 12.375, 12.750, 13.125, 13.500, 13.875,
    14.125, 14.375, 14.625, 14.750, 14.850, 14.925, 14.970, 14.990, 15.0,
)
FRAME_COUNT = len(PILOT_COORDINATES)
KEY_STATES = ("cad", "stock", "blank", "rough", "finished", "inspection", "packed")


def interpolate_parameters(coordinate: float) -> pilot.FrameParameters:
    lower = int(math.floor(coordinate))
    upper = int(math.ceil(coordinate))
    if lower == upper:
        return pilot.FRAME_PARAMETERS[lower]
    fraction = coordinate - lower
    before = pilot.FRAME_PARAMETERS[lower]
    after = pilot.FRAME_PARAMETERS[upper]
    values = {}
    for field in fields(pilot.FrameParameters):
        left = getattr(before, field.name)
        right = getattr(after, field.name)
        if isinstance(left, tuple):
            values[field.name] = tuple(a + (b - a) * fraction for a, b in zip(left, right))
        else:
            values[field.name] = left + (right - left) * fraction
    return pilot.FrameParameters(**values)


FRAME_PARAMETERS = tuple(interpolate_parameters(value) for value in PILOT_COORDINATES)


def geometry_sdf(points: np.ndarray, frame_index: int) -> np.ndarray:
    if frame_index == 0:
        return phase4a.geometry_sdf(points, "rough")
    if frame_index == FRAME_COUNT - 1:
        return phase4a.geometry_sdf(points, "finished")
    parameters = FRAME_PARAMETERS[frame_index]
    return pilot.subtract_features(pilot.stepped_outer_sdf(points, parameters), points, parameters)


def estimate_normals(points: np.ndarray, frame_index: int) -> np.ndarray:
    epsilon = 0.0035
    offsets = np.eye(3, dtype=np.float32) * epsilon
    gradient = [
        geometry_sdf(points + offset, frame_index) - geometry_sdf(points - offset, frame_index)
        for offset in offsets
    ]
    normal = np.stack(gradient, axis=-1)
    normal /= np.maximum(np.linalg.norm(normal, axis=-1, keepdims=True), 1e-7)
    return normal


def raymarch_frame_tile(width: int, height: int, row_start: int, row_end: int,
                        frame_index: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    origins, directions = phase4a.camera_rays(width, height, row_start, row_end)
    distance, active = phase4a.bounding_sphere_entry(origins, directions)
    hit = np.zeros(active.shape, dtype=bool)
    for _ in range(112):
        if not np.any(active):
            break
        points = origins + directions * distance[..., None]
        step = geometry_sdf(points, frame_index)
        newly_hit = active & (step < 0.0018)
        hit |= newly_hit
        active &= ~newly_hit
        distance = np.where(active, distance + np.maximum(step * 0.78, 0.0015), distance)
        active &= distance < 18.0
    points = origins + directions * distance[..., None]
    normals = np.zeros_like(points)
    if np.any(hit):
        normals[hit] = estimate_normals(points[hit], frame_index)
    return hit, points, normals


def surface_texture(points: np.ndarray, progress: float) -> np.ndarray:
    axial = points[..., 0]
    angle = np.arctan2(points[..., 2], points[..., 1])
    coarse = np.sin(axial * 8.5 + np.sin(angle * 5.0)) * np.sin(angle * 13.0 + axial * 2.7)
    rough = 0.976 + VARIANT_B.rough_turn_amplitude * np.sin(axial * 64.0) + VARIANT_B.rough_coarse_amplitude * coarse
    semi = 0.989 + VARIANT_B.semi_turn_amplitude * np.sin(axial * 92.0) + 0.003 * coarse
    finished = 0.997 + VARIANT_B.finished_turn_amplitude * np.sin(axial * 126.0)
    if progress <= 0.58:
        blend = max(0.0, progress) / 0.58
        return rough * (1.0 - blend) + semi * blend
    blend = (min(1.0, progress) - 0.58) / 0.42
    return semi * (1.0 - blend) + finished * blend


def shade(points: np.ndarray, normals: np.ndarray, directions: np.ndarray,
          progress: float) -> np.ndarray:
    variant = VARIANT_B
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
    texture = surface_texture(points, progress)
    colour = base * texture[..., None] * (
        variant.ambient + variant.diffuse_strength * 0.68 * diffuse[..., None] + 0.16 * ceiling[..., None]
    )
    colour += panel[..., None] * variant.panel_strength * np.array([0.80, 0.88, 0.93])
    colour += strip[..., None] * variant.panel_strength * 0.42 * np.array([0.78, 0.86, 0.91])
    colour += key_specular[..., None] * state_specular * np.array([0.92, 0.97, 1.00])
    colour += (rim_light ** 1.7)[..., None] * variant.rim_strength * np.array([0.72, 0.82, 0.88])
    colour += fresnel[..., None] * 0.055 * np.array([0.74, 0.83, 0.89])
    colour += underside[..., None] * variant.lower_fill * np.array([0.42, 0.48, 0.52])
    colour *= 1.0 - 0.12 * dark_band[..., None]
    angle = np.arctan2(points[..., 2], points[..., 1])
    radius = np.hypot(points[..., 1], points[..., 2])
    cut_face = np.abs(normals[..., 0]) ** 7
    face_pattern = 0.5 + 0.5 * np.sin(radius * 58.0 + angle * 1.4)
    face_strength = 0.020 + 0.008 * progress
    colour += (cut_face * (face_strength + face_pattern * 0.010))[..., None] * np.array([0.82, 0.90, 0.95])
    return np.clip(colour, 0.0, 1.0)


def compose(object_rgb: np.ndarray, alpha: np.ndarray, state: str, size: int) -> Image.Image:
    mask = Image.fromarray((alpha * 255).astype(np.uint8))
    if state in metal.GEOMETRY_STATES:
        background = metal.prepared_background(state, mask, size)
    else:
        background = phase4a.base_background(size, state)
        shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        shadow_mask = mask.filter(ImageFilter.GaussianBlur(max(4, size // 55)))
        shadow_mask = shadow_mask.transform(
            shadow_mask.size,
            Image.Transform.AFFINE,
            (0.92, 0.0, size * 0.04, 0.0, 0.24, size * 0.62),
            resample=Image.Resampling.BILINEAR,
        )
        shadow.putalpha(shadow_mask.point(lambda value: int(value * 0.32)))
        background = Image.alpha_composite(background.convert("RGBA"), shadow).convert("RGB")
    canvas = np.asarray(background).astype(np.float32) / 255.0
    edge = mask.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(0.6))
    object_rgb += np.asarray(edge).astype(np.float32)[..., None] / 255.0 * np.array([0.095, 0.12, 0.135])
    composed = canvas * (1.0 - alpha[..., None]) + np.clip(object_rgb, 0.0, 1.0) * alpha[..., None]
    image = Image.fromarray((np.clip(composed ** (1.0 / 1.06), 0.0, 1.0) * 255).astype(np.uint8))
    return phase4a.apply_context(image, state)


def render_sequence_frame(frame_index: int, size: int) -> Image.Image:
    object_rgb = np.zeros((size, size, 3), dtype=np.float32)
    alpha = np.zeros((size, size), dtype=np.float32)
    progress = FRAME_PARAMETERS[frame_index].surface_progress
    for row_start in range(0, size, 48):
        row_end = min(size, row_start + 48)
        hit, points, normals = raymarch_frame_tile(size, size, row_start, row_end, frame_index)
        _, directions = phase4a.camera_rays(size, size, row_start, row_end)
        tile = np.zeros((row_end - row_start, size, 3), dtype=np.float32)
        if np.any(hit):
            tile[hit] = shade(points[hit], normals[hit], directions[hit], progress)
        object_rgb[row_start:row_end] = tile
        alpha[row_start:row_end] = hit.astype(np.float32)
    return compose(object_rgb, alpha, "rough", size)


def render_key_state(state: str, size: int) -> Image.Image:
    geometry_state = "finished" if state in ("cad", "finished", "inspection", "packed") else state
    progress = {"stock": 0.0, "blank": 0.12, "rough": 0.0}.get(state, 1.0)
    object_rgb = np.zeros((size, size, 3), dtype=np.float32)
    alpha = np.zeros((size, size), dtype=np.float32)
    for row_start in range(0, size, 48):
        row_end = min(size, row_start + 48)
        hit, points, normals = phase4a.raymarch_tile(size, size, row_start, row_end, geometry_state)
        _, directions = phase4a.camera_rays(size, size, row_start, row_end)
        tile = np.zeros((row_end - row_start, size, 3), dtype=np.float32)
        if np.any(hit):
            tile[hit] = shade(points[hit], normals[hit], directions[hit], progress)
        object_rgb[row_start:row_end] = tile
        alpha[row_start:row_end] = hit.astype(np.float32)
    image = compose(object_rgb, alpha, state, size)
    if state == "cad":
        draw = ImageDraw.Draw(image, "RGBA")
        inset = int(size * 0.13)
        colour = (137, 186, 214, 48)
        draw.arc((inset, inset, size - inset, size - inset), 194, 348, fill=colour, width=max(1, size // 800))
        draw.line((size * 0.15, size * 0.50, size * 0.85, size * 0.50), fill=colour, width=max(1, size // 900))
        draw.line((size * 0.50, size * 0.16, size * 0.50, size * 0.84), fill=colour, width=max(1, size // 900))
    return image


def save_png(image: Image.Image, path: Path, title: str) -> None:
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Title", title)
    metadata.add_text("Description", "Illustrative deterministic Quantamorph cinematic production artwork")
    metadata.add_text("Generator", "scripts/render_final_cinematic.py")
    image.save(path, "PNG", optimize=True, pnginfo=metadata)


def save_avif(image: Image.Image, path: Path, size: int, quality: int) -> None:
    image.resize((size, size), Image.Resampling.LANCZOS).save(path, "AVIF", quality=quality)


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


def record(path: Path) -> dict:
    with Image.open(path) as image:
        dimensions = list(image.size)
    size = path.stat().st_size
    return {
        "path": path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix(),
        "dimensions": dimensions,
        "bytes": size, "human_size": human_bytes(size), "sha256": sha256(path),
    }


def validate_programme() -> dict:
    analytic = []
    decreasing = [f"allowance_{index:02d}" for index in range(len(phase4a.FINISHED_RADII))]
    increasing = (
        "outer_rounding", "bore_radius", "bolt_hole_radius", "mouth_radius",
        "mouth_half_length", "mouth_rounding", "counterbore_radius",
        "counterbore_half_length", "counterbore_rounding", "cross_hole_radius",
        "surface_progress",
    )
    for index, (parent, child) in enumerate(zip(FRAME_PARAMETERS, FRAME_PARAMETERS[1:])):
        for segment, name in enumerate(decreasing):
            analytic.append({"pair": [index, index + 1], "parameter": name,
                             "from": parent.allowances[segment], "to": child.allowances[segment],
                             "passed": parent.allowances[segment] >= child.allowances[segment]})
        for name in increasing:
            before, after = getattr(parent, name), getattr(child, name)
            analytic.append({"pair": [index, index + 1], "parameter": name,
                             "from": before, "to": after, "passed": before <= after})

    axis = np.linspace(-2.78, 2.78, 171, dtype=np.float32)
    cross = np.linspace(-1.60, 1.60, 129, dtype=np.float32)
    yy, zz = np.meshgrid(cross, cross, indexing="ij")
    yz = np.stack((yy, zz), axis=-1)
    violations = [0] * (FRAME_COUNT - 1)
    rough_equal = True
    finished_equal = True
    sample_count = 0
    for x in axis:
        points = np.empty((*yy.shape, 3), dtype=np.float32)
        points[..., 0] = x
        points[..., 1:] = yz
        parent = geometry_sdf(points, 0) <= 0.0
        rough_equal &= bool(np.array_equal(parent, phase4a.occupancy(points, "rough")))
        for index in range(FRAME_COUNT - 1):
            child = geometry_sdf(points, index + 1) <= 0.0
            violations[index] += int(np.count_nonzero(child & ~parent))
            parent = child
        finished_equal &= bool(np.array_equal(parent, phase4a.occupancy(points, "finished")))
        sample_count += points.shape[0] * points.shape[1]
    sampled = [
        {"parent": f"frame-{index:02d}", "child": f"frame-{index + 1:02d}",
         "violations": count, "passed": count == 0, "sample_count": sample_count,
         "grid": [len(axis), len(cross), len(cross)]}
        for index, count in enumerate(violations)
    ]
    key_geometry_hashes = {}
    hash_axis = np.linspace(-2.78, 2.78, 81, dtype=np.float32)
    hash_cross = np.linspace(-1.60, 1.60, 65, dtype=np.float32)
    hash_yy, hash_zz = np.meshgrid(hash_cross, hash_cross, indexing="ij")
    hash_yz = np.stack((hash_yy, hash_zz), axis=-1)
    for state in KEY_STATES:
        geometry_state = "finished" if state in ("cad", "finished", "inspection", "packed") else state
        digest = hashlib.sha256()
        for x in hash_axis:
            points = np.empty((*hash_yy.shape, 3), dtype=np.float32)
            points[..., 0] = x
            points[..., 1:] = hash_yz
            digest.update(phase4a.geometry_sdf(points, geometry_state).astype("<f4", copy=False).tobytes())
        key_geometry_hashes[state] = digest.hexdigest()
    contextual_geometry_equal = (
        key_geometry_hashes["cad"] == key_geometry_hashes["finished"]
        == key_geometry_hashes["inspection"] == key_geometry_hashes["packed"]
    )
    passed = (
        all(item["passed"] for item in analytic + sampled)
        and rough_equal and finished_equal and contextual_geometry_equal
    )
    report = {
        "passed": passed,
        "rule": "rough ⊇ frame-01 ⊇ ... ⊇ frame-30 ⊇ finished",
        "frame_count": FRAME_COUNT,
        "pilot_coordinates": PILOT_COORDINATES,
        "analytic_checks": analytic,
        "sampled_adjacent_checks": sampled,
        "total_sampled_violations": sum(violations),
        "endpoint_checks": {"rough_exact": rough_equal, "finished_exact": finished_equal},
        "key_state_geometry": {
            "sample_grid": [len(hash_axis), len(hash_cross), len(hash_cross)],
            "hashes": key_geometry_hashes,
            "cad_finished_inspection_packed_identical": contextual_geometry_equal,
        },
        "fixed_registration": {
            "camera": asdict(phase4a.CAMERA), "fov_degrees": phase4a.CAMERA.vertical_fov_degrees,
            "light_key": phase4a.LIGHT_KEY.tolist(), "light_rim": phase4a.LIGHT_RIM.tolist(),
            "crop": [MASTER_SIZE, MASTER_SIZE], "fixed_across_all_frames": True,
            "camera_compensation": "none",
        },
    }
    if not passed:
        raise RuntimeError("Final cinematic containment validation failed before rendering")
    return report


def make_contact_sheet(keys: dict[str, Image.Image], frames: list[Image.Image], path: Path) -> None:
    cell = 360
    labels = [(name, keys[name]) for name in KEY_STATES]
    labels += [(f"machining {index + 1:02d}/32", frames[index]) for index in (0, 5, 10, 15, 20, 25, 31)]
    sheet = Image.new("RGB", (cell * 4, cell * 4), (5, 7, 9))
    draw = ImageDraw.Draw(sheet, "RGBA")
    font = ImageFont.load_default(size=16)
    for index, (label, image) in enumerate(labels):
        x, y = (index % 4) * cell, (index // 4) * cell
        sheet.paste(image.resize((cell, cell), Image.Resampling.LANCZOS), (x, y))
        draw.rectangle((x, y, x + cell, y + 38), fill=(5, 7, 9, 220))
        draw.rectangle((x, y, x + 6, y + 38), fill=(222, 31, 49, 255))
        draw.text((x + 16, y + 11), label.upper(), font=font, fill=(238, 241, 243, 242))
    save_png(sheet, path, "Final cinematic production contact sheet")


def media_paths(review: Path, delivery: Path) -> list[Path]:
    result = sorted((review / "masters" / "machining").glob("frame-*.png"))
    result += sorted((review / "masters" / "key-states").glob("*.png"))
    result += [review / "contact-sheet.png"]
    result += sorted((delivery / "machining" / "1536").glob("frame-*.avif"))
    result += sorted((delivery / "machining" / "960").glob("frame-*.avif"))
    result += sorted(delivery.glob("key-*-1536.avif"))
    result += sorted(delivery.glob("key-*-960.avif"))
    return result


def generate(review: Path, delivery: Path, size: int = MASTER_SIZE, resume: bool = False) -> None:
    sequence_masters = review / "masters" / "machining"
    key_masters = review / "masters" / "key-states"
    desktop = delivery / "machining" / "1536"
    small = delivery / "machining" / "960"
    for directory in (sequence_masters, key_masters, desktop, small):
        directory.mkdir(parents=True, exist_ok=True)
    validation = validate_programme()
    (review / "adjacent-containment.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print("Validation passed: 31 adjacent pairs, zero sampled containment violations", flush=True)

    frames = []
    for index in range(FRAME_COUNT):
        master_path = sequence_masters / f"frame-{index:02d}.png"
        desktop_path = desktop / f"frame-{index:02d}.avif"
        small_path = small / f"frame-{index:02d}.avif"
        if resume and all(path.exists() for path in (master_path, desktop_path, small_path)):
            print(f"Reusing complete machining frame {index + 1:02d}/{FRAME_COUNT}", flush=True)
            with Image.open(master_path) as existing:
                frames.append(existing.convert("RGB").copy())
            continue
        print(f"Rendering machining frame {index + 1:02d}/{FRAME_COUNT} at {size}x{size}", flush=True)
        image = render_sequence_frame(index, size)
        save_png(image, master_path, f"Machining frame {index:02d}")
        save_avif(image, desktop_path, DESKTOP_SIZE, DESKTOP_QUALITY)
        save_avif(image, small_path, SMALL_SIZE, SMALL_QUALITY)
        frames.append(image)

    keys = {}
    for state in KEY_STATES:
        master_path = key_masters / f"{state}.png"
        desktop_path = delivery / f"key-{state}-1536.avif"
        small_path = delivery / f"key-{state}-960.avif"
        if resume and all(path.exists() for path in (master_path, desktop_path, small_path)):
            print(f"Reusing complete {state} key state", flush=True)
            with Image.open(master_path) as existing:
                keys[state] = existing.convert("RGB").copy()
            continue
        if state == "rough":
            image = frames[0].copy()
        elif state == "finished":
            image = frames[-1].copy()
        else:
            print(f"Rendering {state} key state at {size}x{size}", flush=True)
            image = render_key_state(state, size)
        save_png(image, master_path, f"Production key state: {state}")
        save_avif(image, desktop_path, DESKTOP_SIZE, DESKTOP_QUALITY)
        save_avif(image, small_path, SMALL_SIZE, SMALL_QUALITY)
        keys[state] = image

    make_contact_sheet(keys, frames, review / "contact-sheet.png")
    sequence_payload = {}
    for tier in ("1536", "960"):
        paths = sorted((delivery / "machining" / tier).glob("frame-*.avif"))
        total = sum(path.stat().st_size for path in paths)
        sequence_payload[tier] = {"files": len(paths), "bytes": total, "human_size": human_bytes(total)}
    key_paths = sorted(delivery.glob("key-*.avif"))
    payload = {
        "sequence": sequence_payload,
        "key_states_total": {"files": len(key_paths), "bytes": sum(path.stat().st_size for path in key_paths),
                             "human_size": human_bytes(sum(path.stat().st_size for path in key_paths))},
        "mobile_sequence_payload": {"bytes": 0, "human_size": "0 B", "reason": "sequence URLs are not initialized at 780px and below"},
        "encoding": {"1536": {"quality": DESKTOP_QUALITY}, "960": {"quality": SMALL_QUALITY}},
    }
    (review / "payload-report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    assets = [record(path) for path in media_paths(review, delivery)]
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "scripts/render_final_cinematic.py",
        "approved_treatment": asdict(VARIANT_B),
        "frame_count": FRAME_COUNT,
        "rendering": {"approach": "deterministic native-resolution NumPy/Pillow SDF CPU ray marcher",
                      "master_dimensions": [size, size], "native_resolution": True,
                      "camera": asdict(phase4a.CAMERA), "randomness": "none", "generative_enhancement": "none"},
        "provenance": "Repository-authored illustrative procedural geometry and shading; no customer geometry or third-party visual assets",
        "containment_report": "asset-lab/final-cinematic-production/adjacent-containment.json",
        "payload": payload,
        "assets": assets,
    }
    (review / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Rendered {FRAME_COUNT} machining masters, {len(KEY_STATES)} key states and responsive AVIF delivery assets", flush=True)


def verify_existing(review: Path, delivery: Path) -> None:
    expected = media_paths(review, delivery)
    if len(expected) != 118 or not all(path.exists() for path in expected):
        raise RuntimeError(f"Expected 118 generated media files, found {len(expected)}")
    with tempfile.TemporaryDirectory(prefix="quantamorph-final-cinematic-") as temporary:
        root = Path(temporary)
        candidate_review = root / "review"
        candidate_delivery = root / "delivery"
        generate(candidate_review, candidate_delivery)
        actual = media_paths(candidate_review, candidate_delivery)
        comparisons = []
        for source, candidate in zip(expected, actual):
            source_hash, candidate_hash = sha256(source), sha256(candidate)
            comparisons.append({"path": source.relative_to(ROOT).as_posix(), "source_sha256": source_hash,
                                "rerender_sha256": candidate_hash, "matched": source_hash == candidate_hash})
    passed = len(comparisons) == 118 and all(item["matched"] for item in comparisons)
    report = {"passed": passed, "method": "Complete second native render with SHA-256 comparison",
              "matched_assets": sum(item["matched"] for item in comparisons),
              "total_assets": len(comparisons), "comparisons": comparisons}
    (review / "determinism-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not passed:
        raise RuntimeError("Final cinematic deterministic rerender comparison failed")
    print("Determinism check passed: 118/118 media hashes matched", flush=True)


def verify_sampled(review: Path, delivery: Path) -> None:
    """Rerender representative endpoints/dense intervals and every distinct key context."""
    sequence_indices = (0, 10, 15, 18, 23, 27, 31)
    key_states = ("cad", "stock", "blank", "inspection", "packed")
    comparisons = []
    with tempfile.TemporaryDirectory(prefix="quantamorph-final-sampled-") as temporary:
        temporary_root = Path(temporary)
        for index in sequence_indices:
            print(f"Sample-rerendering machining frame {index:02d}", flush=True)
            image = render_sequence_frame(index, MASTER_SIZE)
            candidates = (
                (review / "masters" / "machining" / f"frame-{index:02d}.png", temporary_root / f"frame-{index:02d}.png", MASTER_SIZE, None),
                (delivery / "machining" / "1536" / f"frame-{index:02d}.avif", temporary_root / f"frame-{index:02d}-1536.avif", DESKTOP_SIZE, DESKTOP_QUALITY),
                (delivery / "machining" / "960" / f"frame-{index:02d}.avif", temporary_root / f"frame-{index:02d}-960.avif", SMALL_SIZE, SMALL_QUALITY),
            )
            for source, candidate, size, quality in candidates:
                if quality is None:
                    save_png(image, candidate, f"Machining frame {index:02d}")
                else:
                    save_avif(image, candidate, size, quality)
                comparisons.append({"path": source.relative_to(ROOT).as_posix(),
                                    "source_sha256": sha256(source), "rerender_sha256": sha256(candidate),
                                    "matched": sha256(source) == sha256(candidate)})
        for state in key_states:
            print(f"Sample-rerendering {state} key state", flush=True)
            image = render_key_state(state, MASTER_SIZE)
            candidates = (
                (review / "masters" / "key-states" / f"{state}.png", temporary_root / f"key-{state}.png", MASTER_SIZE, None),
                (delivery / f"key-{state}-1536.avif", temporary_root / f"key-{state}-1536.avif", DESKTOP_SIZE, DESKTOP_QUALITY),
                (delivery / f"key-{state}-960.avif", temporary_root / f"key-{state}-960.avif", SMALL_SIZE, SMALL_QUALITY),
            )
            for source, candidate, size, quality in candidates:
                if quality is None:
                    save_png(image, candidate, f"Production key state: {state}")
                else:
                    save_avif(image, candidate, size, quality)
                comparisons.append({"path": source.relative_to(ROOT).as_posix(),
                                    "source_sha256": sha256(source), "rerender_sha256": sha256(candidate),
                                    "matched": sha256(source) == sha256(candidate)})
    passed = all(item["matched"] for item in comparisons)
    report = {
        "passed": passed,
        "method": "Independent native rerender and SHA-256 comparison of rough/finished endpoints, five dense-interval sequence samples, and every distinct key-state context at PNG/1536 AVIF/960 AVIF tiers",
        "coverage": {"sequence_indices": sequence_indices, "key_states": key_states,
                     "analytic_and_sampled_containment_report": "adjacent-containment.json"},
        "matched_assets": sum(item["matched"] for item in comparisons),
        "total_assets": len(comparisons),
        "comparisons": comparisons,
    }
    (review / "determinism-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not passed:
        raise RuntimeError("Sampled final cinematic deterministic rerender comparison failed")
    print(f"Determinism check passed: {len(comparisons)}/{len(comparisons)} sampled media hashes matched", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--delivery", type=Path, default=DEFAULT_DELIVERY)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--verify-existing", action="store_true")
    parser.add_argument("--verify-sampled", action="store_true")
    parser.add_argument("--resume", action="store_true", help="Reuse complete frame triplets after an interrupted render")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    review, delivery = args.review.resolve(), args.delivery.resolve()
    if args.validate_only:
        review.mkdir(parents=True, exist_ok=True)
        report = validate_programme()
        (review / "adjacent-containment.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("Validation passed: 31 adjacent pairs, zero sampled containment violations")
    elif args.verify_existing:
        verify_existing(review, delivery)
    elif args.verify_sampled:
        verify_sampled(review, delivery)
    else:
        generate(review, delivery, resume=args.resume)


if __name__ == "__main__":
    main()
