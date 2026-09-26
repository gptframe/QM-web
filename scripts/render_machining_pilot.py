"""Render and validate the deterministic Phase 4B machining-transition pilot.

This asset-lab utility is isolated from the production website. It reuses the
Phase 4A component, camera and lighting definitions, then renders sixteen
registered frames whose signed-distance solids can only lose material.
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
from PIL import Image, ImageDraw, ImageFilter, ImageFont, PngImagePlugin

import render_cinematic_art_direction as phase4a


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "asset-lab" / "phase-4b-machining-pilot"
FRAME_COUNT = 16
MASTER_SIZE = 1600
DESKTOP_SIZE = 1536
MOBILE_SIZE = 960
DESKTOP_QUALITY = 63
MOBILE_QUALITY = 60


@dataclass(frozen=True)
class FrameParameters:
    allowances: tuple[float, ...]
    outer_rounding: float
    bore_radius: float
    bolt_hole_radius: float
    mouth_radius: float
    mouth_half_length: float
    mouth_rounding: float
    counterbore_radius: float
    counterbore_half_length: float
    counterbore_rounding: float
    cross_hole_radius: float
    surface_progress: float


def uniform_allowance(value: float) -> tuple[float, ...]:
    return (value,) * len(phase4a.FINISHED_RADII)


# The programme is explicit rather than generated from easing functions so a
# reviewer can audit every geometric change. Allowances only fall; edge
# rounding and every subtractive radius/depth only rise.
FRAME_PARAMETERS = (
    FrameParameters(uniform_allowance(0.140), 0.0250, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.00),
    FrameParameters(uniform_allowance(0.126), 0.0260, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.05),
    FrameParameters(uniform_allowance(0.113), 0.0270, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.10),
    FrameParameters(uniform_allowance(0.100), 0.0280, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.15),
    FrameParameters(uniform_allowance(0.090), 0.0295, 0.055, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.22),
    FrameParameters(uniform_allowance(0.080), 0.0310, 0.105, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.30),
    FrameParameters(uniform_allowance(0.072), 0.0330, 0.165, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.38),
    FrameParameters(uniform_allowance(0.065), 0.0350, 0.245, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.46),
    FrameParameters((0.048, 0.050, 0.054, 0.056, 0.056, 0.050, 0.056, 0.056, 0.056, 0.056), 0.0380, 0.260, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.54),
    FrameParameters((0.030, 0.034, 0.040, 0.044, 0.044, 0.034, 0.044, 0.044, 0.044, 0.044), 0.0410, 0.275, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.62),
    FrameParameters((0.014, 0.020, 0.028, 0.032, 0.032, 0.020, 0.032, 0.032, 0.032, 0.032), 0.0450, 0.286, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.70),
    FrameParameters(uniform_allowance(0.000), 0.0500, 0.296, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.78),
    FrameParameters(uniform_allowance(0.000), 0.0500, 0.304, 0.025, 0.000, 0.000, 0.000, 0.345, 0.040, 0.008, 0.025, 0.84),
    FrameParameters(uniform_allowance(0.000), 0.0500, 0.312, 0.050, 0.085, 0.025, 0.008, 0.385, 0.080, 0.017, 0.052, 0.90),
    FrameParameters(uniform_allowance(0.000), 0.0500, 0.319, 0.075, 0.115, 0.040, 0.013, 0.425, 0.120, 0.026, 0.079, 0.95),
    FrameParameters(uniform_allowance(0.000), 0.0500, 0.325, 0.098, 0.145, 0.055, 0.018, 0.460, 0.160, 0.035, 0.105, 1.00),
)


def stepped_outer_sdf(points: np.ndarray, parameters: FrameParameters) -> np.ndarray:
    distance = np.full(points.shape[:-1], np.inf, dtype=np.float32)
    overlap = 0.022
    for index, (radius, allowance) in enumerate(zip(phase4a.FINISHED_RADII, parameters.allowances)):
        left = float(phase4a.BREAKS[index])
        right = float(phase4a.BREAKS[index + 1])
        centre = (left + right) * 0.5
        half = (right - left) * 0.5 + overlap
        segment_rounding = min(parameters.outer_rounding, max(0.018, half * 0.32))
        distance = np.minimum(
            distance,
            phase4a.rounded_cylinder_x_sdf(
                points, centre, half, float(radius + allowance), segment_rounding
            ),
        )
    return distance


def subtract_features(shape: np.ndarray, points: np.ndarray, parameters: FrameParameters) -> np.ndarray:
    result = shape
    if parameters.bore_radius > 0.0:
        result = phase4a.subtract_central_bore(result, points, parameters.bore_radius)

    if parameters.bolt_hole_radius > 0.0:
        circle_radius = 0.82
        x0 = (-2.25 + -1.48) * 0.5
        half = (-1.48 - -2.25) * 0.5 + 0.07
        for angle in np.linspace(0.0, math.tau, 6, endpoint=False):
            y0 = circle_radius * math.cos(float(angle))
            z0 = circle_radius * math.sin(float(angle))
            hole = phase4a.cylinder_x_sdf(
                points, x0, half, parameters.bolt_hole_radius, y0, z0
            )
            result = np.maximum(result, -hole)

            if parameters.mouth_radius > 0.0:
                mouth = phase4a.rounded_cylinder_x_sdf(
                    points,
                    -2.215,
                    parameters.mouth_half_length,
                    parameters.mouth_radius,
                    parameters.mouth_rounding,
                    y0,
                    z0,
                )
                result = np.maximum(result, -mouth)

    if parameters.counterbore_radius > 0.0:
        counterbore = phase4a.rounded_cylinder_x_sdf(
            points,
            -2.17,
            parameters.counterbore_half_length,
            parameters.counterbore_radius,
            parameters.counterbore_rounding,
        )
        result = np.maximum(result, -counterbore)

    if parameters.cross_hole_radius > 0.0:
        cross_hole = phase4a.cylinder_z_sdf(
            points, 1.73, 0.0, 0.58, parameters.cross_hole_radius
        )
        result = np.maximum(result, -cross_hole)
    return result


def geometry_sdf(points: np.ndarray, frame_index: int) -> np.ndarray:
    # Delegating the endpoints makes geometry identity exact rather than merely
    # approximate: frame 00 is Phase 4A rough; frame 15 is Phase 4A finished.
    if frame_index == 0:
        return phase4a.geometry_sdf(points, "rough")
    if frame_index == FRAME_COUNT - 1:
        return phase4a.geometry_sdf(points, "finished")
    parameters = FRAME_PARAMETERS[frame_index]
    return subtract_features(stepped_outer_sdf(points, parameters), points, parameters)


def occupancy(points: np.ndarray, frame_index: int) -> np.ndarray:
    return geometry_sdf(points, frame_index) <= 0.0


def validate_programme() -> dict:
    if len(FRAME_PARAMETERS) != FRAME_COUNT:
        raise RuntimeError(f"Expected {FRAME_COUNT} parameter sets")

    analytic_checks: list[dict] = []
    decreasing_names = [f"outer_allowance_segment_{index:02d}" for index in range(len(phase4a.FINISHED_RADII))]
    increasing_names = (
        "outer_edge_rounding_removal",
        "central_bore_radius",
        "bolt_hole_radius",
        "hole_mouth_radius",
        "hole_mouth_depth",
        "hole_mouth_rounding",
        "counterbore_radius",
        "counterbore_depth",
        "counterbore_rounding",
        "cross_hole_radius",
    )

    for frame_index, (parent, child) in enumerate(zip(FRAME_PARAMETERS, FRAME_PARAMETERS[1:])):
        for segment_index, name in enumerate(decreasing_names):
            passed = parent.allowances[segment_index] >= child.allowances[segment_index]
            analytic_checks.append({
                "pair": f"pilot-{frame_index:02d} contains pilot-{frame_index + 1:02d}",
                "parameter": name,
                "direction": "nonincreasing outer extent",
                "from": parent.allowances[segment_index],
                "to": child.allowances[segment_index],
                "passed": bool(passed),
            })

        parent_values = (
            parent.outer_rounding,
            parent.bore_radius,
            parent.bolt_hole_radius,
            parent.mouth_radius,
            parent.mouth_half_length,
            parent.mouth_rounding,
            parent.counterbore_radius,
            parent.counterbore_half_length,
            parent.counterbore_rounding,
            parent.cross_hole_radius,
        )
        child_values = (
            child.outer_rounding,
            child.bore_radius,
            child.bolt_hole_radius,
            child.mouth_radius,
            child.mouth_half_length,
            child.mouth_rounding,
            child.counterbore_radius,
            child.counterbore_half_length,
            child.counterbore_rounding,
            child.cross_hole_radius,
        )
        for name, before, after in zip(increasing_names, parent_values, child_values):
            passed = before <= after
            analytic_checks.append({
                "pair": f"pilot-{frame_index:02d} contains pilot-{frame_index + 1:02d}",
                "parameter": name,
                "direction": "nondecreasing subtraction",
                "from": before,
                "to": after,
                "passed": bool(passed),
            })

        analytic_checks.append({
            "pair": f"pilot-{frame_index:02d} to pilot-{frame_index + 1:02d}",
            "parameter": "surface_progress",
            "direction": "nondecreasing surface interpolation",
            "from": parent.surface_progress,
            "to": child.surface_progress,
            "passed": parent.surface_progress <= child.surface_progress,
        })

    axis = np.linspace(-2.78, 2.78, 171, dtype=np.float32)
    cross = np.linspace(-1.60, 1.60, 129, dtype=np.float32)
    yy, zz = np.meshgrid(cross, cross, indexing="ij")
    yz = np.stack((yy, zz), axis=-1)
    violations = [0] * (FRAME_COUNT - 1)
    endpoint_rough_equal = True
    endpoint_finished_equal = True
    total_samples = 0

    for x in axis:
        points = np.empty((*yy.shape, 3), dtype=np.float32)
        points[..., 0] = x
        points[..., 1:] = yz
        occupied = [occupancy(points, index) for index in range(FRAME_COUNT)]
        for index in range(FRAME_COUNT - 1):
            violations[index] += int(np.count_nonzero(occupied[index + 1] & ~occupied[index]))
        endpoint_rough_equal &= bool(np.array_equal(occupied[0], phase4a.occupancy(points, "rough")))
        endpoint_finished_equal &= bool(np.array_equal(occupied[-1], phase4a.occupancy(points, "finished")))
        total_samples += points.shape[0] * points.shape[1]

    sampled_checks = []
    for index, count in enumerate(violations):
        sampled_checks.append({
            "parent": f"pilot-{index:02d}",
            "child": f"pilot-{index + 1:02d}",
            "passed": count == 0,
            "violations": count,
            "sample_count": total_samples,
            "grid": [len(axis), len(cross), len(cross)],
        })

    registration = {
        "camera": asdict(phase4a.CAMERA),
        "output_dimensions": [MASTER_SIZE, MASTER_SIZE],
        "component_coordinate_system": "Phase 4A dimensionless component coordinates",
        "background": "Phase 4A neutral machining background, fixed for all frames",
        "light_key": phase4a.LIGHT_KEY.tolist(),
        "light_rim": phase4a.LIGHT_RIM.tolist(),
        "fixed_across_all_frames": True,
    }
    endpoint_checks = [
        {"check": "pilot-00 occupancy equals Phase 4A rough geometry", "passed": endpoint_rough_equal},
        {"check": "pilot-15 occupancy equals Phase 4A finished geometry", "passed": endpoint_finished_equal},
        {"check": "pilot-00 delegates to Phase 4A rough SDF", "passed": True},
        {"check": "pilot-15 delegates to Phase 4A finished SDF", "passed": True},
    ]
    passed = (
        all(check["passed"] for check in analytic_checks)
        and all(check["passed"] for check in sampled_checks)
        and all(check["passed"] for check in endpoint_checks)
    )
    report = {
        "passed": passed,
        "rule": "pilot-00 ⊇ pilot-01 ⊇ … ⊇ pilot-15",
        "method": "analytic parameter monotonicity plus deterministic 171×129×129 occupancy sampling for every adjacent pair",
        "analytic_checks": analytic_checks,
        "sampled_adjacent_checks": sampled_checks,
        "endpoint_checks": endpoint_checks,
        "fixed_registration": registration,
        "geometry_units": "dimensionless illustrative model units",
    }
    if not passed:
        raise RuntimeError("Phase 4B monotonic geometry validation failed before rendering")
    return report


def estimate_normals(points: np.ndarray, frame_index: int) -> np.ndarray:
    epsilon = 0.0035
    offsets = np.eye(3, dtype=np.float32) * epsilon
    gradients = [
        geometry_sdf(points + offset, frame_index) - geometry_sdf(points - offset, frame_index)
        for offset in offsets
    ]
    normal = np.stack(gradients, axis=-1)
    normal /= np.maximum(np.linalg.norm(normal, axis=-1, keepdims=True), 1e-7)
    return normal


def raymarch_tile(width: int, height: int, row_start: int, row_end: int,
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


def shade(points: np.ndarray, normals: np.ndarray, directions: np.ndarray,
          surface_progress: float) -> np.ndarray:
    if surface_progress == 0.0:
        return phase4a.shade(points, normals, directions, "rough")
    if surface_progress == 1.0:
        return phase4a.shade(points, normals, directions, "finished")

    rough_base, rough_specular, rough_shininess = phase4a.palette_for("rough")
    final_base, final_specular, final_shininess = phase4a.palette_for("finished")
    base = rough_base * (1.0 - surface_progress) + final_base * surface_progress
    specular_strength = rough_specular * (1.0 - surface_progress) + final_specular * surface_progress
    shininess = rough_shininess * (1.0 - surface_progress) + final_shininess * surface_progress

    diffuse = np.maximum(np.sum(normals * phase4a.LIGHT_KEY, axis=-1), 0.0)
    rim = np.maximum(np.sum(normals * phase4a.LIGHT_RIM, axis=-1), 0.0)
    view = -directions
    half_vector = phase4a.LIGHT_KEY + view
    half_vector /= np.maximum(np.linalg.norm(half_vector, axis=-1, keepdims=True), 1e-7)
    specular = np.maximum(np.sum(normals * half_vector, axis=-1), 0.0) ** shininess

    axial = points[..., 0]
    angle = np.arctan2(points[..., 2], points[..., 1])
    radial_position = np.hypot(points[..., 1], points[..., 2])
    coarse = np.sin(axial * 8.5 + np.sin(angle * 5.0)) * np.sin(angle * 13.0 + axial * 2.7)
    rough_texture = 0.935 + 0.050 * np.sin(axial * 58.0) + 0.018 * coarse
    final_texture = 0.994 + 0.006 * np.sin(axial * 112.0)
    texture = rough_texture * (1.0 - surface_progress) + final_texture * surface_progress

    colour = base * texture[..., None] * (0.16 + 0.72 * diffuse[..., None])
    colour += np.array([0.14, 0.19, 0.23]) * (0.38 * rim[..., None])
    colour += specular[..., None] * specular_strength
    environment_band = np.exp(-((normals[..., 2] - 0.26) / 0.34) ** 2)
    colour += environment_band[..., None] * np.array([0.032, 0.043, 0.052])
    cut_face = np.abs(normals[..., 0]) ** 6
    face_pattern = 0.55 + 0.45 * np.sin(radial_position * 54.0 + angle * 1.5)
    colour += (cut_face * (0.026 + face_pattern * 0.018))[..., None] * np.array([0.86, 0.94, 1.0])
    return np.clip(colour, 0.0, 1.0)


def render_frame(frame_index: int, size: int) -> Image.Image:
    if frame_index == 0:
        return phase4a.render_state("rough", size, size)
    if frame_index == FRAME_COUNT - 1:
        return phase4a.render_state("finished", size, size)

    background = phase4a.base_background(size, "rough")
    canvas = np.asarray(background).astype(np.float32) / 255.0
    object_rgb = np.zeros_like(canvas)
    alpha = np.zeros((size, size), dtype=np.float32)

    for row_start in range(0, size, 48):
        row_end = min(row_start + 48, size)
        hit, points, normals = raymarch_tile(size, size, row_start, row_end, frame_index)
        _, directions = phase4a.camera_rays(size, size, row_start, row_end)
        tile_colour = np.zeros((row_end - row_start, size, 3), dtype=np.float32)
        if np.any(hit):
            tile_colour[hit] = shade(
                points[hit], normals[hit], directions[hit], FRAME_PARAMETERS[frame_index].surface_progress
            )
        object_rgb[row_start:row_end] = tile_colour
        alpha[row_start:row_end] = hit.astype(np.float32)

    mask = Image.fromarray((alpha * 255).astype(np.uint8))
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
    edge_array = np.asarray(edge).astype(np.float32) / 255.0
    object_rgb += edge_array[..., None] * np.array([0.10, 0.13, 0.15])
    composed = canvas * (1.0 - alpha[..., None]) + np.clip(object_rgb, 0.0, 1.0) * alpha[..., None]
    composed = np.clip(composed ** (1.0 / 1.06), 0.0, 1.0)
    return Image.fromarray((composed * 255).astype(np.uint8))


def save_png(image: Image.Image, path: Path, frame_name: str) -> None:
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Title", frame_name)
    metadata.add_text("Description", "Illustrative deterministic Phase 4B machining-motion proof; not production evidence")
    metadata.add_text("Generator", "scripts/render_machining_pilot.py")
    image.save(path, "PNG", optimize=True, pnginfo=metadata)


def save_avif(image: Image.Image, path: Path, size: int, quality: int) -> None:
    resized = image.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(path, "AVIF", quality=quality)


def make_contact_sheet(images: list[tuple[str, Image.Image]], path: Path) -> Image.Image:
    cell = 640
    sheet = Image.new("RGB", (cell * 4, cell * 4), (5, 7, 9))
    draw = ImageDraw.Draw(sheet, "RGBA")
    font = ImageFont.load_default(size=18)
    for index, (name, image) in enumerate(images):
        x = (index % 4) * cell
        y = (index // 4) * cell
        sheet.paste(image.resize((cell, cell), Image.Resampling.LANCZOS), (x, y))
        draw.rectangle((x, y, x + cell, y + 42), fill=(5, 7, 9, 218))
        draw.rectangle((x, y, x + 7, y + 42), fill=(222, 31, 49, 255))
        draw.text((x + 19, y + 12), name.upper(), font=font, fill=(235, 238, 240, 238))
        draw.rectangle((x, y, x + cell - 1, y + cell - 1), outline=(90, 98, 104, 110), width=1)
    save_png(sheet, path, "phase-4b-contact-sheet")
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


def file_record(path: Path, state: str) -> dict:
    with Image.open(path) as image:
        width, height = image.size
    return {
        "state": state,
        "path": path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix(),
        "width": width,
        "height": height,
        "bytes": path.stat().st_size,
        "human_size": human_bytes(path.stat().st_size),
        "sha256": sha256(path),
    }


def pixel_equal(left: Path, right: Path) -> bool:
    with Image.open(left) as left_image, Image.open(right) as right_image:
        return bool(np.array_equal(np.asarray(left_image.convert("RGB")), np.asarray(right_image.convert("RGB"))))


def payload_report(output: Path) -> dict:
    tiers = {}
    for label, directory in (("avif_1536", output / "avif-1536"), ("avif_960", output / "avif-960")):
        paths = sorted(directory.glob("pilot-*.avif"))
        sizes = [path.stat().st_size for path in paths]
        tiers[label] = {
            "frame_count": len(paths),
            "total_bytes": sum(sizes),
            "total_human": human_bytes(sum(sizes)),
            "average_bytes": int(round(sum(sizes) / len(sizes))),
            "average_human": human_bytes(int(round(sum(sizes) / len(sizes)))),
            "minimum_bytes": min(sizes),
            "maximum_bytes": max(sizes),
        }
    master_paths = sorted((output / "masters").glob("pilot-*.png"))
    master_total = sum(path.stat().st_size for path in master_paths)
    return {
        "delivery_note": "The pilot preview loads one responsive AVIF tier; PNG files are review masters and are not proposed as web delivery assets.",
        "masters_png": {
            "frame_count": len(master_paths),
            "total_bytes": master_total,
            "total_human": human_bytes(master_total),
        },
        "responsive_tiers": tiers,
    }


def build_manifest(output: Path, validation: dict) -> dict:
    assets = []
    for index in range(FRAME_COUNT):
        name = f"pilot-{index:02d}"
        assets.append({
            "frame": name,
            "parameters": asdict(FRAME_PARAMETERS[index]),
            "master": file_record(output / "masters" / f"{name}.png", name),
            "avif_1536": file_record(output / "avif-1536" / f"{name}.avif", name),
            "avif_960": file_record(output / "avif-960" / f"{name}.avif", name),
        })

    rough_source = ROOT / "asset-lab" / "phase-4-art-direction-proof" / "proof-03-rough.png"
    final_source = ROOT / "asset-lab" / "phase-4-art-direction-proof" / "proof-05-finished.png"
    endpoint_identity = {
        "pilot_00_pixels_equal_phase_4a_rough": pixel_equal(output / "masters" / "pilot-00.png", rough_source),
        "pilot_15_pixels_equal_phase_4a_finished": pixel_equal(output / "masters" / "pilot-15.png", final_source),
        "note": "PNG metadata and filenames differ; decoded RGB pixels are required to be identical.",
    }
    if not all(value for key, value in endpoint_identity.items() if key.startswith("pilot_")):
        raise RuntimeError("Endpoint pixel identity check failed")

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "scripts/render_machining_pilot.py",
        "purpose": "Non-production Phase 4B motion proof from rough-machined to finished illustrative geometry",
        "rendering": {
            "approach": "deterministic native-resolution NumPy/Pillow signed-distance-field CPU ray marcher",
            "master_dimensions": [MASTER_SIZE, MASTER_SIZE],
            "native_resolution": True,
            "responsive_derivatives": {
                "1536": {"dimensions": [DESKTOP_SIZE, DESKTOP_SIZE], "format": "AVIF", "quality": DESKTOP_QUALITY},
                "960": {"dimensions": [MOBILE_SIZE, MOBILE_SIZE], "format": "AVIF", "quality": MOBILE_QUALITY},
            },
            "camera": asdict(phase4a.CAMERA),
            "fixed_camera_lighting_crop": True,
            "randomness": "none",
            "surface_interpolation": "Component-space rough turning texture amplitude and material response progress monotonically; geometry is never image-blended.",
        },
        "provenance": "Repository-authored illustrative procedural geometry; no customer geometry or third-party visual assets",
        "endpoint_identity": endpoint_identity,
        "validation_summary": {
            "passed": validation["passed"],
            "adjacent_pairs": len(validation["sampled_adjacent_checks"]),
            "containment_violations": sum(check["violations"] for check in validation["sampled_adjacent_checks"]),
        },
        "assets": assets,
        "contact_sheet": file_record(output / "pilot-contact-sheet.png", "pilot-contact-sheet"),
        "payload_report": payload_report(output),
    }


def generate(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    masters = output / "masters"
    desktop = output / "avif-1536"
    mobile = output / "avif-960"
    for directory in (masters, desktop, mobile):
        directory.mkdir(parents=True, exist_ok=True)

    validation = validate_programme()
    (output / "adjacent-containment.json").write_text(
        json.dumps(validation, indent=2) + "\n", encoding="utf-8"
    )
    print("Validation passed: all 15 adjacent solids are monotonic with zero sampled violations")

    rendered = []
    for index in range(FRAME_COUNT):
        name = f"pilot-{index:02d}"
        print(f"Rendering {name} at {MASTER_SIZE}x{MASTER_SIZE}", flush=True)
        image = render_frame(index, MASTER_SIZE)
        save_png(image, masters / f"{name}.png", name)
        save_avif(image, desktop / f"{name}.avif", DESKTOP_SIZE, DESKTOP_QUALITY)
        save_avif(image, mobile / f"{name}.avif", MOBILE_SIZE, MOBILE_QUALITY)
        rendered.append((name, image))

    make_contact_sheet(rendered, output / "pilot-contact-sheet.png")
    payload = payload_report(output)
    (output / "payload-report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    manifest = build_manifest(output, validation)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Rendered {FRAME_COUNT} masters, 32 AVIF derivatives and the contact sheet to {output}")


def media_paths(output: Path) -> list[Path]:
    paths = sorted((output / "masters").glob("pilot-*.png"))
    paths += sorted((output / "avif-1536").glob("pilot-*.avif"))
    paths += sorted((output / "avif-960").glob("pilot-*.avif"))
    paths.append(output / "pilot-contact-sheet.png")
    return paths


def verify_existing(output: Path) -> None:
    expected = media_paths(output)
    if len(expected) != 49 or not all(path.exists() for path in expected):
        raise RuntimeError("Render the complete pilot before running --verify-existing")

    with tempfile.TemporaryDirectory(prefix="quantamorph-phase4b-") as temporary:
        rerender = Path(temporary) / "phase-4b-machining-pilot"
        generate(rerender)
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

    passed = len(comparisons) == 49 and all(item["matched"] for item in comparisons)
    report = {
        "passed": passed,
        "method": "Complete second native render in an isolated temporary directory; SHA-256 comparison of 16 PNG masters, 32 AVIF derivatives and the contact sheet",
        "matched_assets": sum(item["matched"] for item in comparisons),
        "total_assets": len(comparisons),
        "comparisons": comparisons,
    }
    (output / "determinism-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not passed:
        raise RuntimeError("Deterministic rerender comparison failed")
    print("Determinism check passed: 49/49 media hashes matched after a complete rerender")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--verify-existing", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = args.output.resolve()
    if args.validate_only:
        report = validate_programme()
        output.mkdir(parents=True, exist_ok=True)
        (output / "adjacent-containment.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("Validation passed: all 15 adjacent solids are monotonic with zero sampled violations")
        return
    if args.verify_existing:
        verify_existing(output)
        return
    generate(output)


if __name__ == "__main__":
    main()
