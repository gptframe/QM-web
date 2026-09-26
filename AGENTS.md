# Quantamorph website — Codex instructions

## Purpose
Work on the Quantamorph Limited public website as a UK-facing B2B engineering/manufacturing supplier website. The site should feel premium, technical and cinematic without making claims that are not evidenced.

## Working principles
- Preserve factual caution. Do not invent certifications, machines, tolerances, capacity, lead times, locations, customers, sector approvals, quality standards or manufacturing ownership.
- Treat `CLAIMS_REQUIRING_OWNER_CONFIRMATION.md` as the source of truth for what may and may not be claimed.
- Use `REDESIGN_PLAN.md`, `CURRENT_SITE_AUDIT.md` and `IMAGE_SHOT_LIST.md` when the task concerns structure, copy, motion, imagery or accessibility.
- Keep the primary commercial action obvious: send a drawing / manufacturing requirement for review and quotation.
- Use UK English.

## Technical direction
- This repository is currently a static HTML/CSS/JavaScript site using GSAP + ScrollTrigger. Do not migrate frameworks merely for novelty.
- Prefer the smallest architecture that produces a reliable, high-performance result on GitHub Pages.
- Add Three.js/WebGL only if a task explicitly requires true 3D interaction that cannot be achieved credibly with the existing 2D/GSAP approach.
- Progressive enhancement is mandatory: the content and RFQ route must remain understandable if JavaScript or motion is unavailable.
- Respect `prefers-reduced-motion` and keep a non-pinned, readable fallback.
- Avoid scroll-jacking. Native scrolling must continue to work.
- Do not hide essential copy inside canvas-only content.
- Preserve keyboard navigation, focus visibility, semantic headings, skip link and mobile menu accessibility.

## Visual direction
The target is a cinematic engineering experience, not a generic agency website:
- near-black / graphite background;
- cool machined-metal imagery;
- restrained Quantamorph red as an accent, not a flood colour;
- large editorial typography;
- technical-grid, coordinate, crosshair and measurement motifs without fake numerical engineering data;
- one hero component should visually persist through the manufacturing story wherever assets allow;
- motion should communicate a production journey rather than decorative movement.

Do not copy third-party source code, branding, text, images or proprietary assets from reference websites or social media. Recreate interaction patterns and pacing with original implementation and original/authorised assets.

## Performance budgets
For the homepage target:
- no horizontal overflow at 375, 390, 430, 768, 1024, 1440 and 1920 CSS px widths;
- no persistent `will-change` on large full-screen layers;
- lazy-load below-fold media;
- preload only genuinely critical hero media;
- do not introduce a large image sequence without measuring transfer size and decode cost;
- if using a frame sequence, provide responsive frame sizes, staged preloading and a static fallback image;
- avoid blocking the main thread with per-scroll DOM work; prefer GSAP timelines and `requestAnimationFrame` where needed.

## Validation expectations
For meaningful frontend changes:
1. Serve the site through a local HTTP server, not only `file://`.
2. Check desktop and mobile layouts.
3. Check reduced-motion behaviour.
4. Check keyboard navigation and menu behaviour.
5. Check the browser console for errors.
6. Check broken links/assets.
7. Record any performance or accessibility compromise in the final summary.

## Change discipline
- Work on a feature branch; do not push experimental work directly to `main`.
- Keep commits focused and describe visual/behavioural changes in the commit message.
- Before replacing working code, inspect the existing implementation and preserve useful behaviour.
- If an implementation depends on a visual asset that does not exist, build the component/animation shell and use an explicit placeholder path or fallback rather than inventing customer work.
- Do not silently strengthen public claims to make copy sound more impressive.
