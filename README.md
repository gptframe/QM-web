# Quantamorph homepage

Premium, responsive homepage for Quantamorph Limited, built around a scroll-driven manufacturing journey from drawing to delivered component.

## Production website

The deployable static site is in `dist/`:

- `dist/index.html` - semantic homepage
- `dist/styles.css` - responsive design system
- `dist/script.js` - GSAP/ScrollTrigger journey and interactions
- `dist/assets/` - optimized AVIF and WebP imagery

The connected GitHub repository receives a browser-equivalent mirror at its root. `scripts/build_github_mirror.py` creates `github-dist/` using text-based SVG image wrappers so the repository copy retains the same imagery and interactions while the production Sites build keeps its smaller responsive assets.

## Fort Automation profile update

The partner-supported engineering section adds carefully attributed capability evidence for CAD development, reverse engineering, special-purpose machines, checking/application fixtures, press tools and metrology workstations.

See `FORT_PROFILE_INTEGRATION.md` and `CLAIMS_REQUIRING_OWNER_CONFIRMATION.md` before strengthening any public capability claim.

## Local preview

Serve the `dist` directory through a local HTTP server. Opening `index.html` directly may prevent some browser features and external animation libraries from loading correctly.
