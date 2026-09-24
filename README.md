# Quantamorph homepage

A static, GitHub Pages-compatible homepage for Quantamorph Limited. The central interaction follows one representative component from requirement through material, preparation, machining, inspection, release and protected supply.

## Architecture

- `index.html` contains the complete semantic page and the non-JavaScript/reduced-motion manufacturing route.
- `styles.css` contains the responsive design system, component layouts and motion fallbacks.
- `script.js` progressively enhances navigation, the capability tabs and the desktop manufacturing story.
- `assets/vendor/` contains pinned local copies of GSAP 3.12.5 and ScrollTrigger 3.12.5, removing the runtime dependency on a public CDN.
- `assets/part-*.avif|webp` are six aligned states of the same representative component. They are generated from `part-evolution-master.png` by `scripts/process_part_sequence.py`.

No build step, Node.js runtime or framework runtime is required for the production website. The page uses relative URLs and can be served directly from a GitHub Pages branch or repository root. Node.js is used only for local browser QA.

## Local preview

Serve the repository root through HTTP:

```powershell
python -m http.server 4173 --bind 127.0.0.1
```

Then open `http://127.0.0.1:4173/`. Opening `index.html` directly is not the supported preview path.

## Motion and responsive behaviour

- At widths above 780px, one GSAP timeline owns the pinned production choreography. The part stays on a fixed optical axis while image state, aperture, scale, inspection overlays, captions and the progress rail advance together.
- At 780px and below, the manufacturing route becomes a deliberate stacked sequence. This avoids fragile mobile pinning and keeps every stage readable with native scrolling.
- With `prefers-reduced-motion: reduce`, the pinned scene is disabled and the same semantic stacked sequence is shown at every width.
- If JavaScript fails, the complete stacked route remains available and the primary RFQ mail link remains reachable.

## Asset generation

Regenerate the aligned part states after replacing the contact sheet:

```powershell
python scripts/process_part_sequence.py
```

The current six images are temporary, illustrative states rather than production-fidelity process evidence. The next asset pass must meet all of these requirements:

- Every state must use the same optical axis, perspective/camera direction, crop and lighting family.
- The raw and cut material envelopes must physically contain the finished component envelope.
- The cut blank must be long enough and large enough for the finished component.
- Machining stages must only remove material.
- The CAD, rough, finished and packed states must represent the same geometry.
- Inspection and packing states must preserve that exact component.
- Final desktop imagery must not rely on 512px source images when displayed near 800–950 CSS px.
- Final sources must support high-DPI displays through suitable responsive dimensions.
- Imagery remains illustrative unless its provenance permits stronger wording.

A higher-fidelity reel-like transformation additionally requires approximately 40–80 optimised frames of that same component under the controlled setup above, or a clean GLB/GLTF model with approved materials and camera direction. This asset constraint is the remaining blocker; it must not be disguised with invented tolerances, dimensions, machining data, certification marks, logos or machine specifications.

Any future frame sequence should use responsive AVIF/WebP sources, staged preloading, a measured transfer/decode budget and the current static sequence as its fallback. A 3D runtime should only be introduced when an approved model and a requirement for genuine camera or geometry control exist.

## Claims and imagery

`CLAIMS_REQUIRING_OWNER_CONFIRMATION.md` is the public-copy guardrail. Capability, inspection, records, manufacturing location and delivery terms remain quotation-specific. Process imagery is illustrative unless explicitly identified otherwise; do not infer certification, tolerance, lead time, machine envelope, factory ownership or sector approval from the presentation.

## QA

Install the dev-only QA dependency and run the self-hosting browser pass:

```powershell
npm ci
npm run qa:install
npm run qa
```

`npm run qa:install` installs Playwright's portable Chromium build once; `npm run qa` starts a temporary local static server and executes the assertions. `QA_URL` may be supplied to test an already-running preview instead. The package is a development tool only and is not part of the deployed website.

The assertions cover 375, 390, 430, 768, 780, 1024, 1440 and 1920 CSS-pixel widths; desktop cinematic activation; the mobile, reduced-motion and no-JavaScript eight-stage route; keyboard navigation and focus; interactive descendants inside `aria-hidden` subtrees; internal anchors; image loading; console and page errors; failed requests; and horizontal overflow. Screenshots and a machine-readable report are written to the ignored `qa-output/` directory.
