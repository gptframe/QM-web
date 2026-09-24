# Quantamorph homepage

A static, GitHub Pages-compatible homepage for Quantamorph Limited. The central interaction follows one representative component from requirement through material, preparation, machining, inspection, release and protected supply.

## Architecture

- `index.html` contains the complete semantic page and the non-JavaScript/reduced-motion manufacturing route.
- `styles.css` contains the responsive design system, component layouts and motion fallbacks.
- `script.js` progressively enhances navigation, the capability tabs and the desktop manufacturing story.
- `assets/vendor/` contains pinned local copies of GSAP 3.12.5 and ScrollTrigger 3.12.5, removing the runtime dependency on a public CDN.
- `assets/part-*.avif|webp` are six aligned states of the same representative component. They are generated from `part-evolution-master.png` by `scripts/process_part_sequence.py`.

No build step or framework runtime is required. The page uses relative URLs and can be served directly from a GitHub Pages branch or repository root.

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

The current sequence is illustrative. A higher-fidelity reel-like transformation requires publication-approved imagery of the same component with:

- one fixed camera, focal length, crop and lighting setup;
- approximately 40–80 optimized frames spanning stock, preparation, machining, inspection, finished and packed states; or
- a clean GLB/GLTF model with approved materials and camera direction.

Any future frame sequence should use responsive AVIF/WebP sources, staged preloading, a measured transfer/decode budget and the current static sequence as its fallback. A 3D runtime should only be introduced when an approved model and a requirement for genuine camera or geometry control exist.

## Claims and imagery

`CLAIMS_REQUIRING_OWNER_CONFIRMATION.md` is the public-copy guardrail. Capability, inspection, records, manufacturing location and delivery terms remain quotation-specific. Process imagery is illustrative unless explicitly identified otherwise; do not infer certification, tolerance, lead time, machine envelope, factory ownership or sector approval from the presentation.

## QA

Run the automated browser pass while the local server is active:

```powershell
node scripts/browser_qa.mjs
```

The check covers 375, 390, 430, 768, 1024, 1440 and 1920 CSS-pixel widths, image and anchor failures, console/page errors, horizontal overflow, navigation behaviour, capability keyboard control, the desktop story and reduced motion.
