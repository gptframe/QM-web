# Phase 4B deterministic machining-transition pilot

This directory is an isolated motion proof. It is not linked from the public website and nothing here is a production runtime dependency.

The sequence tests one question: can the Phase 4A representative component move from its exact rough-machined solid to its exact finished solid through visually continuous, physically valid material removal?

## Generate and validate

Run from the repository root:

```powershell
python scripts/render_machining_pilot.py
python scripts/render_machining_pilot.py --verify-existing
```

The first command validates all geometric parameters and 15 adjacent solid pairs before rendering. It then creates sixteen native 1600×1600 PNG review masters, 1536×1536 and 960×960 AVIF derivatives, a 4×4 contact sheet, the containment report, payload report and manifest.

The second command performs a complete second native render in an isolated temporary directory and compares SHA-256 hashes for all 49 media outputs.

## Preview

Serve the repository root through HTTP:

```powershell
python -m http.server 4173 --bind 127.0.0.1
```

Open:

`http://127.0.0.1:4173/asset-lab/phase-4b-machining-pilot/preview/`

Use the native range control, Left/Right arrow keys, the mouse wheel over the viewer, or the 12 fps play control. The preview is intentionally simple and is not linked from `index.html`.

## Scope and provenance

- `pilot-00` delegates to the exact Phase 4A rough signed-distance solid and surface treatment.
- `pilot-15` delegates to the exact Phase 4A finished signed-distance solid and surface treatment.
- Intermediate solids only reduce outer allowances, increase edge-break removal, or enlarge subtractive bores and holes.
- Camera position, camera target, 31° vertical field of view, component coordinates, crop, background and light directions remain fixed.
- Rough turning character evolves in component space with a fixed procedural phase; it is not an image dissolve and contains no randomness.
- The geometry is repository-authored, dimensionless and illustrative. It is not customer CAD or evidence of a material, tolerance, process result, machine, inspection system or Quantamorph-owned facility.

Do not copy these files into `assets/`, integrate the preview into the public page, or expand the pilot into a 40–80-frame sequence without a separate reviewed task.
