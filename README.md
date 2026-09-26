# Quantamorph homepage

A static, GitHub Pages-compatible homepage for Quantamorph Limited. The central interaction follows one representative component from requirement through material, preparation, machining, inspection, release and protected supply.

## Architecture

- `index.html` contains the complete semantic page and the non-JavaScript/reduced-motion manufacturing route.
- `styles.css` contains the responsive design system, component layouts and motion fallbacks.
- `script.js` progressively enhances navigation, the capability tabs and the desktop manufacturing story.
- `assets/vendor/` contains pinned local copies of GSAP 3.12.5 and ScrollTrigger 3.12.5, removing the runtime dependency on a public CDN.
- `assets/cinematic/key-*.avif` are seven responsive key states of the same illustrative representative component.
- `assets/cinematic/machining/` contains the responsive 32-frame removal-only machining sequence. Review masters and validation evidence remain under `asset-lab/final-cinematic-production/`.

No build step, Node.js runtime or framework runtime is required for the production website. The page uses relative URLs and can be served directly from a GitHub Pages branch or repository root. Node.js is used only for local browser QA.

For Quantamorph design work, `.agents/skills/quantamorph-cinematic-design/SKILL.md` is the preferred project-specific Codex design guardrail. Generic third-party design skills must not override `AGENTS.md`, the claims constraints, the local-font policy or the existing static HTML/CSS/JavaScript and GSAP architecture.

## Local preview

Serve the repository root through HTTP:

```powershell
python -m http.server 4173 --bind 127.0.0.1
```

Then open `http://127.0.0.1:4173/`. Opening `index.html` directly is not the supported preview path.

## Motion and responsive behaviour

- At widths above 780px, one GSAP timeline owns the pinned production choreography. A 32-frame canvas sequence is scrubbed only through the machining interval; the part stays on a fixed optical axis while image state, aperture, inspection overlays, captions and the progress rail advance together.
- At 780px and below, the manufacturing route becomes a deliberate stacked sequence. This avoids fragile mobile pinning and keeps every stage readable with native scrolling.
- With `prefers-reduced-motion: reduce`, the pinned scene is disabled and the same semantic stacked sequence is shown at every width.
- If JavaScript fails, the complete stacked route remains available and the primary RFQ mail link remains reachable.
- Machining frames begin staged loading only when the manufacturing section approaches the viewport. Mobile and reduced-motion modes do not request them; a static rough-state image remains in place if sequence loading fails.

## Asset generation

Regenerate and validate the approved Variant B production family:

```powershell
python scripts/render_final_cinematic.py
python scripts/render_final_cinematic.py --verify-sampled
python scripts/render_final_cinematic.py --verify-existing
```

`--verify-sampled` independently rerenders both endpoints, the dense machining intervals and every distinct key-state context at all three media tiers. `--verify-existing` performs the exhaustive 118-file rerender when a full audit is required. The deterministic renderer enforces these requirements:

- Every state must use the same optical axis, perspective/camera direction, crop and lighting family.
- The raw and cut material envelopes must physically contain the finished component envelope.
- The cut blank must be long enough and large enough for the finished component.
- Machining stages must only remove material.
- The CAD, rough, finished and packed states must represent the same geometry.
- Inspection and packing states must preserve that exact component.
- Production review masters are native 1600×1600 PNGs, with responsive 1536×1536 and 960×960 AVIF delivery tiers.
- Imagery remains illustrative unless its provenance permits stronger wording.

The live sequence uses 32 deterministic frames with denser sampling around final feature operations. It is illustrative and must not be presented as measured process evidence or disguised with invented tolerances, dimensions, machining data, certification marks, logos or machine specifications. A 3D runtime should only be introduced if a future approved model and a genuine camera or geometry-control requirement justify it.

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

The assertions cover 375, 390, 430, 768, 780, 1024, 1440 and 1920 CSS-pixel widths; desktop cinematic activation; first/middle/final machining frames; responsive sequence tiers and staged loading; the static sequence-failure fallback; the mobile, reduced-motion and no-JavaScript eight-stage route; keyboard navigation and focus; interactive descendants inside `aria-hidden` subtrees; internal anchors; image loading; console and page errors; failed requests; and horizontal overflow. The detailed report is written to ignored `qa-output/`; committed release-review screenshots and runtime payload evidence are written under `asset-lab/final-cinematic-production/`.
