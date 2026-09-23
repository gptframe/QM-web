# Quantamorph homepage

Premium, responsive homepage for Quantamorph Limited, built around a scroll-driven production line from enquiry to supplied component.

## Production website

The deployable static site is in `dist/`:

- `dist/index.html` - semantic homepage
- `dist/styles.css` - responsive design system
- `dist/script.js` - GSAP/ScrollTrigger journey and interactions
- `dist/assets/` - optimized AVIF and WebP imagery

The connected GitHub repository receives a browser-equivalent mirror at its root. `scripts/build_github_mirror.py` creates `github-dist/` using text-based SVG image wrappers so the repository copy retains the same imagery and interactions while the production Sites build keeps its smaller responsive assets.

## Production-story update

The pinned GSAP sequence now follows one representative cylindrical component through enquiry, technical review, quotation, approval, optional design, material, cutting, CNC/VMC machining, in-process checking, final inspection, packing and supply.

The homepage presents design, CNC turning, VMC milling, conventional toolroom, tools and dies, fabrication, special-purpose machines, inspection and supply as Quantamorph capabilities, based on the owner confirmation recorded in `CLAIMS_REQUIRING_OWNER_CONFIRMATION.md`.

The coherent part-state artwork is generated from `assets/part-evolution-master.png`; `scripts/process_part_sequence.py` produces the optimized animation states.

## Local preview

Serve the `dist` directory through a local HTTP server. Opening `index.html` directly may prevent some browser features and external animation libraries from loading correctly.
