# Phase 4A production-art-direction proof

This directory is an isolated asset lab. Nothing here is referenced by the production website.

Run from the repository root:

```powershell
python scripts/render_cinematic_art_direction.py
```

The repository-owned renderer uses a refined, dimensionless signed-distance-field model of one illustrative flanged shaft. It validates the containment chain before rendering, then uses one fixed camera, optical axis, crop and lighting family for all eight states. The default pass ray-marches natively at 1600×1600; it does not upscale a lower-resolution render.

The component is not customer geometry or a verified Quantamorph part. The materials, process marks, inspection context and packaging are visual direction only. They do not establish a material grade, tolerance, inspection method, equipment ownership, packaging standard or operational result.

Required proof outputs:

- `proof-00-cad.png`
- `proof-01-stock.png`
- `proof-02-blank.png`
- `proof-03-rough.png`
- `proof-04-semi-finished.png`
- `proof-05-finished.png`
- `proof-06-inspection.png`
- `proof-07-packed.png`
- `proof-contact-sheet.png`
- `envelope-validation.json`
- `manifest.json`

The proof stills are an art-direction gate. Do not copy them into `assets/`, connect them to the live page, or expand them into a 40–80-frame sequence without a separate reviewed task.

## Review status

Phase 4A is suitable as the source for a limited Phase 4B machining-transition pilot, subject to the constraints in `PHASE_4B_PILOT_PLAN.md`. It is not approval for production-site integration or the full sequence.

Remaining limitations:

- The source is a rotational procedural solid rather than approved CAD.
- Surface direction is deliberately lightweight and cannot match a path-traced physically based material.
- The cross-hole is a plausible illustrative minor feature but is not prominent from the fixed camera.
- Inspection graphics are abstract and intentionally do not identify a gauge, machine or result.
- The case and foam demonstrate protective contact and depth but do not represent an approved packaging standard.
- A pilot should test whether feature-growth interpolation reads as removal rather than as a dissolve before any longer sequence is authorised.
