"""Measure registration and adjacent visual changes in the Phase 4B pilot."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

import render_machining_pilot as pilot


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "asset-lab" / "phase-4b-machining-pilot"
PROJECTION_SIZE = 400


def projected_mask(frame_index: int) -> np.ndarray:
    mask = np.zeros((PROJECTION_SIZE, PROJECTION_SIZE), dtype=bool)
    for row_start in range(0, PROJECTION_SIZE, 40):
        row_end = min(row_start + 40, PROJECTION_SIZE)
        origins, directions = pilot.phase4a.camera_rays(
            PROJECTION_SIZE, PROJECTION_SIZE, row_start, row_end
        )
        distance, active = pilot.phase4a.bounding_sphere_entry(origins, directions)
        hit = np.zeros(active.shape, dtype=bool)
        for _ in range(112):
            if not np.any(active):
                break
            points = origins + directions * distance[..., None]
            step = pilot.geometry_sdf(points, frame_index)
            newly_hit = active & (step < 0.0018)
            hit |= newly_hit
            active &= ~newly_hit
            distance = np.where(active, distance + np.maximum(step * 0.78, 0.0015), distance)
            active &= distance < 18.0
        mask[row_start:row_end] = hit
    return mask


def mask_metrics(mask: np.ndarray) -> dict:
    yy, xx = np.nonzero(mask)
    if len(xx) == 0:
        raise RuntimeError("Projected geometry mask is empty")
    return {
        "occupied_pixels": int(mask.sum()),
        "bbox": [int(xx.min()), int(yy.min()), int(xx.max() + 1), int(yy.max() + 1)],
        "centroid": [round(float(xx.mean()), 4), round(float(yy.mean()), 4)],
    }


def dilate_one_pixel(mask: np.ndarray) -> np.ndarray:
    padded = np.pad(mask, 1, mode="constant", constant_values=False)
    result = np.zeros_like(mask)
    for y_offset in range(3):
        for x_offset in range(3):
            result |= padded[
                y_offset:y_offset + mask.shape[0],
                x_offset:x_offset + mask.shape[1],
            ]
    return result


def visual_delta(left: Path, right: Path) -> dict:
    with Image.open(left) as left_image, Image.open(right) as right_image:
        before = np.asarray(left_image.convert("RGB"), dtype=np.int16)
        after = np.asarray(right_image.convert("RGB"), dtype=np.int16)
    delta = np.abs(after - before)
    per_pixel = np.max(delta, axis=-1)
    return {
        "mean_absolute_channel_delta": round(float(delta.mean()), 4),
        "pixels_changed_more_than_4_levels": int(np.count_nonzero(per_pixel > 4)),
        "changed_percent": round(float(np.count_nonzero(per_pixel > 4) / per_pixel.size * 100.0), 4),
    }


def main() -> None:
    masks = []
    frames = []
    for index in range(pilot.FRAME_COUNT):
        print(f"Measuring projected geometry pilot-{index:02d}", flush=True)
        mask = projected_mask(index)
        masks.append(mask)
        frames.append({"frame": f"pilot-{index:02d}", **mask_metrics(mask)})

    adjacent = []
    for index in range(pilot.FRAME_COUNT - 1):
        parent = frames[index]
        child = frames[index + 1]
        child_outside_parent = int(np.count_nonzero(masks[index + 1] & ~masks[index]))
        child_outside_parent_tolerant = int(np.count_nonzero(
            masks[index + 1] & ~dilate_one_pixel(masks[index])
        ))
        centroid_delta = float(np.linalg.norm(
            np.asarray(child["centroid"]) - np.asarray(parent["centroid"])
        ))
        adjacent.append({
            "parent": parent["frame"],
            "child": child["frame"],
            "raw_projected_child_pixels_outside_parent": child_outside_parent,
            "projected_child_pixels_outside_parent_with_1px_raster_tolerance": child_outside_parent_tolerant,
            "projected_pixel_count_delta": child["occupied_pixels"] - parent["occupied_pixels"],
            "centroid_delta_at_400px": round(centroid_delta, 4),
            "visual_delta": visual_delta(
                OUTPUT / "masters" / f"pilot-{index:02d}.png",
                OUTPUT / "masters" / f"pilot-{index + 1:02d}.png",
            ),
        })

    report = {
        "method": "Fixed-camera 400×400 geometry-only projection plus decoded 1600×1600 adjacent-frame RGB comparison",
        "fixed_registration": {
            "camera": pilot.phase4a.CAMERA.__dict__,
            "projection_dimensions": [PROJECTION_SIZE, PROJECTION_SIZE],
            "camera_or_object_transform_changes": 0,
        },
        "frames": frames,
        "adjacent": adjacent,
        "summary": {
            "raw_projected_child_pixels_outside_parent_total": sum(
                item["raw_projected_child_pixels_outside_parent"] for item in adjacent
            ),
            "projected_child_pixels_outside_parent_with_1px_raster_tolerance_total": sum(
                item["projected_child_pixels_outside_parent_with_1px_raster_tolerance"] for item in adjacent
            ),
            "maximum_centroid_delta_at_400px": max(
                item["centroid_delta_at_400px"] for item in adjacent
            ),
            "maximum_mean_absolute_channel_delta": max(
                item["visual_delta"]["mean_absolute_channel_delta"] for item in adjacent
            ),
            "largest_changed_percent": max(
                item["visual_delta"]["changed_percent"] for item in adjacent
            ),
        },
        "interpretation": "Projected centroid and silhouette changes are consequences of removal from a fixed camera, not camera, crop, scale or object-transform changes. Raw single-pixel boundary differences at the 400px ray-march threshold are reported separately from the one-pixel-tolerant raster result and the higher-density 3D occupancy containment report.",
    }
    (OUTPUT / "motion-review-metrics.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
