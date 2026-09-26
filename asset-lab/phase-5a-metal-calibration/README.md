# Phase 5A final metal calibration

This directory is an isolated, non-production art-direction comparison. Nothing here is referenced by the public website.

The approved Phase 4A component geometry, Phase 4B manufacturing programme, camera position and target, 31° field of view, component coordinate system, crop and dark environment remain unchanged. The renderer delegates directly to `scripts/render_cinematic_art_direction.py` for geometry and registration. Only deterministic surface and neutral studio-light response varies.

## Generate and verify

Run from the repository root:

```powershell
python scripts/render_metal_calibration.py
python scripts/render_metal_calibration.py --verify-existing
```

The first command creates twelve native 1600×1600 PNG review states, six representative finished-state AVIF encodes and the comparison sheet. The second performs a complete isolated rerender and compares all 19 media hashes.

## Controlled variants

- **A · Balanced satin:** neutral satin steel, moderate directional separation and balanced dark-form readability.
- **B · Crisp directional:** brighter steel, narrower highlights and the strongest shoulder/bore definition; highest contrast and highest expected encode entropy.
- **C · Broad technical satin:** darker steel with broader reflection bands, stronger shadow readability and the most visible restrained process texture.

These are trade-offs for review, not a selected final treatment. None changes geometry, camera, object registration, background hue or component proportions.

## Scope and claims

The component, surface response and packaging remain illustrative. They do not establish a material grade, surface-finish value, tolerance, machining result, equipment, facility, inspection outcome or approved packaging standard. No generative image enhancement or third-party visual asset is used.

Do not copy these files into `assets/`, integrate them into `index.html`, or generate the longer machining sequence until a variant has been reviewed and selected.
