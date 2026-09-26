# Phase 3 deterministic cinematic proof

This directory is an asset lab. Nothing here is referenced by the production website.

Run from the repository root:

```powershell
python scripts/render_cinematic_proof.py
```

The repository-owned renderer uses a deterministic signed-distance-field model of one illustrative flanged shaft. It validates the containment chain before rendering, then uses one camera, optical axis, crop and lighting rig for all eight states. CAD, finished, inspection and packed states share the exact final solid. Inspection and packing add context only.

The proof geometry is illustrative, dimensionless and does not represent customer work, a verified Quantamorph part, machining capability, tolerances or inspection data.

Generated outputs:

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

The eight images are proof keyframes, not a production frame sequence. Do not copy them into `assets/` or connect them to the live page without a separate review.

## Review status and limitations

The proof validates the deterministic pipeline, state registration and removal-only geometry. It is not yet approval for a 40–80-frame production render.

- The 1600×1600 PNGs are ray-marched at 800×800 and deterministically upscaled for proof review; a production pass should render at native delivery resolution.
- The dimensionless rotational solid is intentionally generic and does not come from customer or verified Quantamorph CAD.
- Materials use a lightweight procedural studio shader rather than a path-traced physically based metal system.
- Inspection and packing are abstract context treatments, not evidence of specific equipment, readings, packaging standards or operational practice.
- The final production model needs an art-direction pass for edge breaks, believable tool marks, fastener/hole treatment, foam contact and case depth before interpolation.

`manifest.json` records exact proof sizes and both measured keyframe compression and conservative AVIF planning ranges for 40, 60 and 80 frames.
