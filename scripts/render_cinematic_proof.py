"""Render the deterministic Phase 3 cinematic proof set.

This asset-lab renderer deliberately has no connection to the production site.
It models one illustrative flanged shaft as nested signed-distance solids,
validates the removal-only envelope chain, then ray-marches eight registered
proof states with one camera and lighting rig.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, PngImagePlugin


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "asset-lab" / "phase-3-cinematic-proof"
STATE_NAMES = (
    "proof-00-cad",
    "proof-01-stock",
    "proof-02-blank",
    "proof-03-rough",
    "proof-04-semi-finished",
    "proof-05-finished",
    "proof-06-inspection",
    "proof-07-packed",
)

BREAKS = np.array([-2.15, -1.30, -0.82, -0.25, 0.55, 0.85, 1.48, 2.00])
FINISHED_RADII = np.array([1.18, 0.90, 0.76, 0.68, 0.77, 0.64, 0.54])


@dataclass(frozen=True)
class Camera:
    position: tuple[float, float, float] = (-6.8, -8.0, 4.6)
    target: tuple[float, float, float] = (-0.05, 0.0, -0.02)
    up: tuple[float, float, float] = (0.0, 0.0, 1.0)
    vertical_fov_degrees: float = 31.0


CAMERA = Camera()
LIGHT_KEY = np.array([-0.45, -0.55, 0.78], dtype=np.float32)
LIGHT_RIM = np.array([0.65, 0.55, 0.52], dtype=np.float32)
LIGHT_KEY /= np.linalg.norm(LIGHT_KEY)
LIGHT_RIM /= np.linalg.norm(LIGHT_RIM)


def cylinder_x_sdf(points: np.ndarray, x0: float, half_length: float, radius: float,
                   y0: float = 0.0, z0: float = 0.0) -> np.ndarray:
    axial = np.abs(points[..., 0] - x0) - half_length
    radial = np.hypot(points[..., 1] - y0, points[..., 2] - z0) - radius
    outside = np.hypot(np.maximum(axial, 0.0), np.maximum(radial, 0.0))
    inside = np.minimum(np.maximum(axial, radial), 0.0)
    return outside + inside


def stepped_outer_sdf(points: np.ndarray, allowance: float) -> np.ndarray:
    distance = np.full(points.shape[:-1], np.inf, dtype=np.float32)
    overlap = 0.018
    for index, radius in enumerate(FINISHED_RADII + allowance):
        left = float(BREAKS[index])
        right = float(BREAKS[index + 1])
        centre = (left + right) * 0.5
        half = (right - left) * 0.5 + overlap
        distance = np.minimum(distance, cylinder_x_sdf(points, centre, half, float(radius)))
    return distance


def subtract_central_bore(shape: np.ndarray, points: np.ndarray, radius: float) -> np.ndarray:
    bore = np.hypot(points[..., 1], points[..., 2]) - radius
    return np.maximum(shape, -bore)


def subtract_bolt_circle(shape: np.ndarray, points: np.ndarray) -> np.ndarray:
    # Four through-holes exist only in the final geometry. Their positions are
    # illustrative, dimensionless and never published as manufacturing data.
    hole_radius = 0.105
    circle_radius = 0.77
    x0 = (-2.15 + -1.30) * 0.5
    half = (-1.30 - -2.15) * 0.5 + 0.08
    result = shape
    for angle in np.linspace(0.0, math.tau, 4, endpoint=False):
        y0 = circle_radius * math.cos(float(angle))
        z0 = circle_radius * math.sin(float(angle))
        hole = cylinder_x_sdf(points, x0, half, hole_radius, y0, z0)
        result = np.maximum(result, -hole)
    return result


def geometry_sdf(points: np.ndarray, state: str) -> np.ndarray:
    if state == "stock":
        return cylinder_x_sdf(points, 0.0, 2.55, 1.45)
    if state == "blank":
        return cylinder_x_sdf(points, -0.06, 2.18, 1.40)
    if state == "rough":
        return stepped_outer_sdf(points, 0.11)
    if state == "semi-finished":
        shape = stepped_outer_sdf(points, 0.05)
        return subtract_central_bore(shape, points, 0.24)

    # CAD, finished, inspection and packed all use the exact same final solid.
    shape = stepped_outer_sdf(points, 0.0)
    shape = subtract_central_bore(shape, points, 0.31)
    return subtract_bolt_circle(shape, points)


def occupancy(points: np.ndarray, state: str) -> np.ndarray:
    return geometry_sdf(points, state) <= 0.0


def validate_envelopes() -> dict:
    """Validate containment analytically and on a deterministic voxel grid."""
    checks: list[dict] = []

    analytic = [
        ("stock radius contains blank", 1.45 >= 1.40),
        ("stock length contains blank", 2.55 >= 2.24),
        ("blank radius contains rough", 1.40 >= float(np.max(FINISHED_RADII + 0.11))),
        ("blank length contains rough", -2.24 <= float(BREAKS[0]) and 2.12 >= float(BREAKS[-1])),
        ("rough allowance contains semi-finished", 0.11 >= 0.05),
        ("semi-finished allowance contains finished", 0.05 >= 0.0),
        ("semi-finished bore removes no more than finished", 0.24 <= 0.31),
    ]
    for label, passed in analytic:
        checks.append({"type": "analytic", "check": label, "passed": bool(passed)})

    chain = ("stock", "blank", "rough", "semi-finished", "finished")
    axis = np.linspace(-2.62, 2.62, 161, dtype=np.float32)
    cross = np.linspace(-1.52, 1.52, 121, dtype=np.float32)
    total_samples = 0
    voxel_violations = {f"{parent} contains {child}": 0 for parent, child in zip(chain, chain[1:])}

    yy, zz = np.meshgrid(cross, cross, indexing="ij")
    yz = np.stack((yy, zz), axis=-1)
    for x in axis:
        points = np.empty((*yy.shape, 3), dtype=np.float32)
        points[..., 0] = x
        points[..., 1:] = yz
        occupied = {state: occupancy(points, state) for state in chain}
        total_samples += points.shape[0] * points.shape[1]
        for parent, child in zip(chain, chain[1:]):
            key = f"{parent} contains {child}"
            voxel_violations[key] += int(np.count_nonzero(occupied[child] & ~occupied[parent]))

    for label, violations in voxel_violations.items():
        checks.append({
            "type": "voxel",
            "check": label,
            "passed": violations == 0,
            "violations": violations,
            "sample_count": total_samples,
            "grid": [len(axis), len(cross), len(cross)],
        })

    # Context states must not mutate the released component.
    probe = np.stack(np.meshgrid(axis[::4], cross[::3], cross[::3], indexing="ij"), axis=-1)
    finished = occupancy(probe, "finished")
    for state in ("cad", "inspection", "packed"):
        equal = bool(np.array_equal(finished, occupancy(probe, state)))
        checks.append({"type": "identity", "check": f"{state} geometry equals finished", "passed": equal})

    passed = all(check["passed"] for check in checks)
    result = {
        "passed": passed,
        "rule": "raw stock ⊇ cut blank ⊇ rough ⊇ semi-finished ⊇ finished",
        "method": "analytic constraints plus deterministic 161×121×121 occupancy sampling",
        "checks": checks,
        "geometry_units": "dimensionless illustrative model units",
    }
    if not passed:
        failed = [check["check"] for check in checks if not check["passed"]]
        raise RuntimeError(f"Envelope validation failed before rendering: {', '.join(failed)}")
    return result


def camera_rays(width: int, height: int, row_start: int, row_end: int) -> tuple[np.ndarray, np.ndarray]:
    position = np.array(CAMERA.position, dtype=np.float32)
    target = np.array(CAMERA.target, dtype=np.float32)
    up_hint = np.array(CAMERA.up, dtype=np.float32)
    forward = target - position
    forward /= np.linalg.norm(forward)
    right = np.cross(forward, up_hint)
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)

    aspect = width / height
    scale = math.tan(math.radians(CAMERA.vertical_fov_degrees) * 0.5)
    xs = ((np.arange(width, dtype=np.float32) + 0.5) / width * 2.0 - 1.0) * aspect * scale
    ys = (1.0 - (np.arange(row_start, row_end, dtype=np.float32) + 0.5) / height * 2.0) * scale
    xx, yy = np.meshgrid(xs, ys)
    directions = forward + xx[..., None] * right + yy[..., None] * up
    directions /= np.linalg.norm(directions, axis=-1, keepdims=True)
    origins = np.broadcast_to(position, directions.shape)
    return origins, directions


def bounding_sphere_entry(origins: np.ndarray, directions: np.ndarray, radius: float = 3.15) -> tuple[np.ndarray, np.ndarray]:
    b = np.sum(origins * directions, axis=-1)
    c = np.sum(origins * origins, axis=-1) - radius * radius
    discriminant = b * b - c
    valid = discriminant >= 0.0
    root = np.sqrt(np.maximum(discriminant, 0.0))
    entry = np.maximum(-b - root, 0.0)
    return entry.astype(np.float32), valid


def estimate_normals(points: np.ndarray, state: str) -> np.ndarray:
    epsilon = 0.0035
    offsets = np.eye(3, dtype=np.float32) * epsilon
    gradients = []
    for offset in offsets:
        gradients.append(geometry_sdf(points + offset, state) - geometry_sdf(points - offset, state))
    normal = np.stack(gradients, axis=-1)
    normal /= np.maximum(np.linalg.norm(normal, axis=-1, keepdims=True), 1e-7)
    return normal


def raymarch_tile(width: int, height: int, row_start: int, row_end: int, state: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    origins, directions = camera_rays(width, height, row_start, row_end)
    distance, active = bounding_sphere_entry(origins, directions)
    hit = np.zeros(active.shape, dtype=bool)
    max_distance = 18.0

    for _ in range(112):
        if not np.any(active):
            break
        points = origins + directions * distance[..., None]
        step = geometry_sdf(points, state)
        newly_hit = active & (step < 0.0018)
        hit |= newly_hit
        active &= ~newly_hit
        distance = np.where(active, distance + np.maximum(step * 0.78, 0.0015), distance)
        active &= distance < max_distance

    points = origins + directions * distance[..., None]
    normals = np.zeros_like(points)
    if np.any(hit):
        normals[hit] = estimate_normals(points[hit], state)
    return hit, points, normals


def palette_for(state: str) -> tuple[np.ndarray, float, float]:
    if state == "cad":
        return np.array([0.14, 0.22, 0.27], dtype=np.float32), 0.78, 44.0
    if state == "stock":
        return np.array([0.24, 0.27, 0.29], dtype=np.float32), 0.40, 22.0
    if state == "blank":
        return np.array([0.29, 0.32, 0.34], dtype=np.float32), 0.46, 28.0
    if state == "rough":
        return np.array([0.30, 0.34, 0.37], dtype=np.float32), 0.52, 34.0
    if state == "semi-finished":
        return np.array([0.34, 0.38, 0.41], dtype=np.float32), 0.63, 52.0
    return np.array([0.39, 0.43, 0.46], dtype=np.float32), 0.78, 76.0


def shade(points: np.ndarray, normals: np.ndarray, directions: np.ndarray, state: str) -> np.ndarray:
    base, specular_strength, shininess = palette_for(state)
    diffuse = np.maximum(np.sum(normals * LIGHT_KEY, axis=-1), 0.0)
    rim = np.maximum(np.sum(normals * LIGHT_RIM, axis=-1), 0.0)
    view = -directions
    half_vector = LIGHT_KEY + view
    half_vector /= np.maximum(np.linalg.norm(half_vector, axis=-1, keepdims=True), 1e-7)
    specular = np.maximum(np.sum(normals * half_vector, axis=-1), 0.0) ** shininess

    # Deterministic, subtle surface variation distinguishes process states
    # without pretending to be measured machining data.
    axial = points[..., 0]
    angle = np.arctan2(points[..., 2], points[..., 1])
    if state == "stock":
        texture = 0.965 + 0.025 * np.sin(axial * 17.0 + np.sin(angle * 5.0))
    elif state == "blank":
        texture = 0.975 + 0.018 * np.sin(axial * 23.0)
    elif state == "rough":
        texture = 0.960 + 0.035 * np.sin(axial * 52.0)
    elif state == "semi-finished":
        texture = 0.980 + 0.015 * np.sin(axial * 76.0)
    else:
        texture = 0.992 + 0.008 * np.sin(axial * 96.0)

    colour = base * texture[..., None] * (0.18 + 0.72 * diffuse[..., None])
    colour += np.array([0.16, 0.20, 0.23]) * (0.34 * rim[..., None])
    colour += specular[..., None] * specular_strength
    if state in {"blank", "rough", "semi-finished", "finished", "inspection", "packed"}:
        cut_face = np.abs(normals[..., 0]) ** 6
        colour += cut_face[..., None] * np.array([0.045, 0.052, 0.058])

    if state == "cad":
        longitudinal = np.abs(np.sin((axial + 2.15) * math.pi * 2.4))
        radial_grid = np.abs(np.sin(angle * 8.0))
        wire = np.minimum(longitudinal, radial_grid) < 0.075
        colour = np.where(wire[..., None], np.array([0.72, 0.90, 0.96]), colour * 0.54)

    return np.clip(colour, 0.0, 1.0)


def base_background(size: int, state: str) -> Image.Image:
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    nx = xx / max(size - 1, 1)
    ny = yy / max(size - 1, 1)
    radial = np.sqrt((nx - 0.52) ** 2 + (ny - 0.46) ** 2)
    glow = np.clip(1.0 - radial / 0.72, 0.0, 1.0)
    values = 7.0 + glow * 10.0 + (1.0 - ny) * 2.0
    rgb = np.stack((values * 0.72, values * 0.84, values), axis=-1).astype(np.uint8)
    image = Image.fromarray(rgb)
    draw = ImageDraw.Draw(image, "RGBA")

    # One restrained registration system across the full proof family.
    step = max(80, size // 10)
    for position in range(step, size, step):
        draw.line((position, 0, position, size), fill=(150, 170, 185, 7), width=1)
        draw.line((0, position, size, position), fill=(150, 170, 185, 7), width=1)
    draw.line((size // 2, int(size * 0.10), size // 2, int(size * 0.90)), fill=(205, 220, 230, 14), width=1)
    draw.line((int(size * 0.10), size // 2, int(size * 0.90), size // 2), fill=(205, 220, 230, 14), width=1)
    floor_y = int(size * 0.81)
    draw.rectangle((0, floor_y, size, size), fill=(2, 3, 4, 68))
    draw.line((int(size * 0.08), floor_y, int(size * 0.92), floor_y), fill=(150, 160, 168, 16), width=1)

    if state == "inspection":
        table_y = int(size * 0.77)
        draw.rectangle((0, table_y, size, size), fill=(12, 14, 16, 255))
        draw.line((0, table_y, size, table_y), fill=(165, 177, 184, 36), width=max(1, size // 600))
    elif state == "packed":
        margin_x = int(size * 0.105)
        margin_y = int(size * 0.17)
        draw.rounded_rectangle(
            (margin_x, margin_y, size - margin_x, size - margin_y),
            radius=int(size * 0.035), fill=(18, 20, 22, 255), outline=(66, 70, 73, 160), width=max(2, size // 350),
        )
        inset = int(size * 0.035)
        draw.rounded_rectangle(
            (margin_x + inset, margin_y + inset, size - margin_x - inset, size - margin_y - inset),
            radius=int(size * 0.025), fill=(10, 12, 13, 255), outline=(42, 46, 49, 180), width=max(1, size // 500),
        )
    return image


def apply_context(image: Image.Image, state: str) -> Image.Image:
    draw = ImageDraw.Draw(image, "RGBA")
    size = image.width
    if state == "inspection":
        cx, cy = int(size * 0.50), int(size * 0.50)
        red = (235, 43, 60, 120)
        pale = (215, 225, 232, 42)
        draw.ellipse((cx - size * 0.29, cy - size * 0.29, cx + size * 0.29, cy + size * 0.29), outline=pale, width=max(1, size // 600))
        draw.line((cx, int(size * 0.17), cx, int(size * 0.83)), fill=red, width=max(1, size // 500))
        draw.line((int(size * 0.17), cy, int(size * 0.83), cy), fill=red, width=max(1, size // 500))
        draw.ellipse((cx - size * 0.009, cy - size * 0.009, cx + size * 0.009, cy + size * 0.009), outline=(245, 55, 70, 210), width=max(2, size // 450))
    elif state == "packed":
        # The case is context only. The exact released component remains on the
        # same camera transform and is not geometrically changed or obscured.
        draw.rounded_rectangle(
            (int(size * 0.16), int(size * 0.70), int(size * 0.84), int(size * 0.755)),
            radius=int(size * 0.012), fill=(24, 27, 29, 220), outline=(78, 82, 86, 150), width=max(1, size // 550),
        )
        draw.rectangle((int(size * 0.49), int(size * 0.745), int(size * 0.54), int(size * 0.77)), fill=(158, 24, 38, 210))
    return image


def render_state(state: str, internal_size: int, output_size: int) -> Image.Image:
    background = base_background(internal_size, state)
    canvas = np.asarray(background).astype(np.float32) / 255.0
    object_rgb = np.zeros_like(canvas)
    alpha = np.zeros((internal_size, internal_size), dtype=np.float32)
    tile_height = 48

    for row_start in range(0, internal_size, tile_height):
        row_end = min(row_start + tile_height, internal_size)
        hit, points, normals = raymarch_tile(internal_size, internal_size, row_start, row_end, state)
        _, directions = camera_rays(internal_size, internal_size, row_start, row_end)
        tile_colour = np.zeros((row_end - row_start, internal_size, 3), dtype=np.float32)
        if np.any(hit):
            tile_colour[hit] = shade(points[hit], normals[hit], directions[hit], state)
        object_rgb[row_start:row_end] = tile_colour
        alpha[row_start:row_end] = hit.astype(np.float32)

    # Soft studio contact shadow derived from the registered silhouette.
    mask = Image.fromarray((alpha * 255).astype(np.uint8))
    shadow = Image.new("RGBA", (internal_size, internal_size), (0, 0, 0, 0))
    shadow_mask = mask.filter(ImageFilter.GaussianBlur(max(4, internal_size // 55)))
    shadow_mask = shadow_mask.transform(
        shadow_mask.size,
        Image.Transform.AFFINE,
        (0.92, 0.0, internal_size * 0.04, 0.0, 0.24, internal_size * 0.62),
        resample=Image.Resampling.BILINEAR,
    )
    shadow.putalpha(shadow_mask.point(lambda value: int(value * 0.32)))
    background = Image.alpha_composite(background.convert("RGBA"), shadow).convert("RGB")
    canvas = np.asarray(background).astype(np.float32) / 255.0

    # A one-pixel normal-derived edge lift keeps the dark material legible.
    edge = mask.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(0.6))
    edge_array = np.asarray(edge).astype(np.float32) / 255.0
    object_rgb += edge_array[..., None] * np.array([0.10, 0.13, 0.15])
    composed = canvas * (1.0 - alpha[..., None]) + np.clip(object_rgb, 0.0, 1.0) * alpha[..., None]
    composed = np.clip(composed ** (1.0 / 1.06), 0.0, 1.0)
    image = Image.fromarray((composed * 255).astype(np.uint8))
    image = apply_context(image, state)
    if output_size != internal_size:
        image = image.resize((output_size, output_size), Image.Resampling.LANCZOS)
    return image


def state_geometry_name(proof_name: str) -> str:
    suffix = proof_name.removeprefix("proof-")
    if suffix.endswith("cad"):
        return "cad"
    if suffix.endswith("stock"):
        return "stock"
    if suffix.endswith("blank"):
        return "blank"
    if suffix.endswith("rough"):
        return "rough"
    if suffix.endswith("semi-finished"):
        return "semi-finished"
    if suffix.endswith("inspection"):
        return "inspection"
    if suffix.endswith("packed"):
        return "packed"
    return "finished"


def save_png(image: Image.Image, path: Path, state: str) -> None:
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Title", state)
    metadata.add_text("Description", "Illustrative deterministic Quantamorph cinematic proof; not production evidence")
    metadata.add_text("Generator", "scripts/render_cinematic_proof.py")
    image.save(path, "PNG", optimize=True, pnginfo=metadata)


def contact_sheet(images: Iterable[tuple[str, Image.Image]], path: Path) -> Image.Image:
    cells = list(images)
    cell = 800
    sheet = Image.new("RGB", (cell * 4, cell * 2), (5, 7, 9))
    draw = ImageDraw.Draw(sheet, "RGBA")
    font = ImageFont.load_default(size=20)
    for index, (name, image) in enumerate(cells):
        x = (index % 4) * cell
        y = (index // 4) * cell
        panel = image.resize((cell, cell), Image.Resampling.LANCZOS)
        sheet.paste(panel, (x, y))
        draw.rectangle((x, y, x + cell, y + 46), fill=(5, 7, 9, 218))
        draw.text((x + 20, y + 14), name.upper(), font=font, fill=(235, 238, 240, 238))
        draw.rectangle((x, y, x + 7, y + 46), fill=(222, 31, 49, 255))
        draw.rectangle((x, y, x + cell - 1, y + cell - 1), outline=(90, 98, 104, 110), width=1)
    save_png(sheet, path, "phase-3-contact-sheet")
    return sheet


def encoded_size(image: Image.Image, size: int, quality: int) -> int:
    candidate = image.resize((size, size), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    candidate.save(buffer, "AVIF", quality=quality)
    return buffer.tell()


def human_bytes(value: int) -> str:
    units = ("B", "KiB", "MiB", "GiB")
    amount = float(value)
    for unit in units:
        if amount < 1024.0 or unit == units[-1]:
            return f"{amount:.2f} {unit}"
        amount /= 1024.0
    raise AssertionError("unreachable")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_manifest(output: Path, output_size: int, internal_size: int,
                   validation: dict, images: list[tuple[str, Image.Image]]) -> dict:
    assets = []
    desktop_samples = []
    mobile_samples = []
    for name, image in images:
        path = output / f"{name}.png"
        desktop_samples.append(encoded_size(image, 1536, 63))
        mobile_samples.append(encoded_size(image, 960, 60))
        assets.append({
            "state": name,
            "path": path.relative_to(ROOT).as_posix(),
            "width": image.width,
            "height": image.height,
            "bytes": path.stat().st_size,
            "human_size": human_bytes(path.stat().st_size),
            "sha256": sha256(path),
        })

    contact = output / "proof-contact-sheet.png"
    assets.append({
        "state": "contact-sheet",
        "path": contact.relative_to(ROOT).as_posix(),
        "width": 3200,
        "height": 1600,
        "bytes": contact.stat().st_size,
        "human_size": human_bytes(contact.stat().st_size),
        "sha256": sha256(contact),
    })

    desktop_average = int(round(float(np.mean(desktop_samples))))
    mobile_average = int(round(float(np.mean(mobile_samples))))
    estimates = {}
    # Procedural proofs compress far more efficiently than a production asset
    # with dense, photoreal surface detail. Keep the measured extrapolation,
    # but add a conservative planning range for future high-fidelity delivery.
    desktop_planning_per_frame = (90 * 1024, 180 * 1024)
    mobile_planning_per_frame = (40 * 1024, 85 * 1024)
    for frames in (40, 60, 80):
        desktop = desktop_average * frames
        mobile = mobile_average * frames
        estimates[str(frames)] = {
            "measured_proof_extrapolation": {
                "desktop_1536_avif": human_bytes(desktop),
                "mobile_960_avif": human_bytes(mobile),
            },
            "production_planning_range": {
                "desktop_1536_avif": [
                    human_bytes(desktop_planning_per_frame[0] * frames),
                    human_bytes(desktop_planning_per_frame[1] * frames),
                ],
                "mobile_960_avif": [
                    human_bytes(mobile_planning_per_frame[0] * frames),
                    human_bytes(mobile_planning_per_frame[1] * frames),
                ],
                "delivery_note": "A viewport receives one responsive tier, not both; excludes HTTP overhead and any separately loaded fallback",
            },
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "scripts/render_cinematic_proof.py",
        "rendering": {
            "approach": "deterministic NumPy/Pillow signed-distance-field CPU ray marcher",
            "output_dimensions": [output_size, output_size],
            "internal_render_dimensions": [internal_size, internal_size],
            "upscale_filter": "Lanczos" if internal_size != output_size else "none",
            "camera": CAMERA.__dict__,
            "shared_camera_lighting_crop": True,
            "randomness": "none",
        },
        "provenance": "Repository-authored illustrative procedural geometry; no customer geometry or third-party visual assets",
        "validation": validation,
        "assets": assets,
        "sequence_estimates": {
            "basis": "Mean encoded size of the eight proof keyframes using AVIF quality 63 at 1536px and quality 60 at 960px",
            "planning_basis": "Conservative 90-180 KiB desktop and 40-85 KiB mobile per frame to account for future photoreal surface entropy",
            "average_desktop_frame_bytes": desktop_average,
            "average_mobile_frame_bytes": mobile_average,
            "frames": estimates,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--size", type=int, default=1600, help="Square proof output size")
    parser.add_argument("--internal-size", type=int, default=800, help="Square ray-march resolution before deterministic upscaling")
    parser.add_argument("--validate-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.size < 512 or args.internal_size < 384 or args.internal_size > args.size:
        raise SystemExit("Use --size >= 512 and 384 <= --internal-size <= --size")

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    validation = validate_envelopes()  # Must pass before the first render.
    validation_path = output / "envelope-validation.json"
    validation_path.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print("Envelope validation passed: stock contains blank contains rough contains semi-finished contains finished")
    if args.validate_only:
        print(validation_path)
        return

    rendered: list[tuple[str, Image.Image]] = []
    for proof_name in STATE_NAMES:
        state = state_geometry_name(proof_name)
        print(f"Rendering {proof_name} ({state}) at {args.internal_size}px -> {args.size}px")
        image = render_state(state, args.internal_size, args.size)
        path = output / f"{proof_name}.png"
        save_png(image, path, proof_name)
        rendered.append((proof_name, image))

    contact_path = output / "proof-contact-sheet.png"
    contact_sheet(rendered, contact_path)
    manifest = build_manifest(output, args.size, args.internal_size, validation, rendered)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Rendered {len(rendered)} proof states and contact sheet to {output}")


if __name__ == "__main__":
    main()
