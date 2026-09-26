# Final cinematic production assets

This directory records the deterministic production-review asset pass used by the feature branch. The approved material treatment is Phase 5A **Variant B — Crisp directional**.

## Scope

- 32 registered machining frames from the exact Phase 4A rough solid to the exact Phase 4A finished solid.
- Extra temporal samples in the former Phase 4B 10→11 and 12→15 intervals.
- Seven key states: CAD, stock, prepared blank, rough, finished, inspection and packed.
- Native 1600×1600 PNG review masters under `masters/`.
- Responsive 1536×1536 and 960×960 AVIF delivery assets under `assets/cinematic/`.
- Fixed Phase 4A camera, 31° vertical FOV, target, crop, lights and component coordinates.

The artwork is illustrative. It does not communicate measured tolerances, machine ownership, packaging standards, certification status or customer-part provenance.

## Reproduce

```text
python scripts/render_final_cinematic.py
python scripts/render_final_cinematic.py --verify-existing
```

The renderer validates the full removal-only programme before rendering. `adjacent-containment.json` contains analytic parameter checks and sampled containment results for all 31 adjacent frame pairs. `determinism-report.json` is written by the complete rerender check.

## Runtime delivery

The public site uses the key-state AVIFs directly. The machining sequence is not referenced by HTML: desktop JavaScript begins staged loading only when the manufacturing section approaches the viewport. Viewports at 780px and below, reduced-motion visitors and no-JavaScript visitors keep the complete stacked semantic route and do not request the sequence.

`runtime-performance.json` is produced by `npm run qa` and records the initial resource payload, activation delta and both sequence tiers. The screenshots in `evidence/` are production browser captures, not renderer composites.
