# Phase 4B machining-transition pilot plan

Status: planned only; no pilot frames have been rendered.

## Purpose

Test whether a short deterministic sequence can communicate material removal from the Phase 4A rough state to the exact finished component while preserving camera registration, visual quality and a credible delivery budget.

The pilot is limited to machining. It does not include CAD, procurement, cutting, inspection, packing, delivery or production-site integration.

## Proposed output

- 16 keyframes, numbered `pilot-00` through `pilot-15`.
- Native 1600×1600 PNG review masters.
- Responsive AVIF review derivatives at 1536×1536 and 960×960.
- One 4×4 contact sheet.
- Adjacent-frame containment report and exact asset manifest.
- No JavaScript runtime changes and no frame preloader in this phase.

## Removal-only frame programme

All parameters move monotonically towards the final solid. Every later frame must be a subset of the preceding frame.

| Frames | Visual operation | Geometric rule |
|---|---|---|
| 00–03 | Establish rough turned form | Reduce the shared outer allowance from the Phase 4A rough state; no holes appear. |
| 04–07 | Approach semi-finished diameters | Continue reducing outer allowance and grow the central bore only by removing material. |
| 08–11 | Resolve final journals, collar and relief | Reduce the remaining allowance to zero; preserve all completed removals. |
| 12–15 | Resolve final minor features | Increase bore/counterbore and hole-removal radii monotonically to the exact Phase 4A finished state. |

Do not crossfade between geometrically incompatible images. If a feature cannot be expressed as a monotonic CSG subtraction, omit it from the pilot rather than fake the transition.

## Fixed art direction

- Reuse the Phase 4A component definition, camera, optical axis, perspective, crop and light directions without modification.
- Interpolate only geometry allowance, feature-removal radii and process-surface character.
- Progress material from rough/matte to restrained machined metal without changing the apparent material family.
- Keep the background and component registration pixel-stable.
- Add no tools, sparks, coolant, readable data, machine environment or facility implication.

## Validation gate

Before review, require:

1. analytic monotonicity checks for every interpolated parameter;
2. sampled occupancy verification for every adjacent pair (`frame N ⊇ frame N+1`);
3. exact equality between `pilot-15` and Phase 4A `proof-05-finished` geometry;
4. byte-identical output hashes across a repeated render;
5. measured AVIF payload at both responsive tiers;
6. contact-sheet review confirming no camera drift, pulsing scale, feature growth or material popping.

## Decision after the pilot

Proceed towards a longer sequence only if the 16-frame result reads as continuous material removal at the intended scroll speed and the selected responsive tier remains within the agreed delivery budget. Otherwise retain the eight-state still system or revise the model before producing more frames.
