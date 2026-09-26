# Codex task — Quantamorph cinematic manufacturing homepage

## Outcome
Upgrade the current Quantamorph homepage into a cinematic, scroll-led engineering experience inspired by premium interactive product websites, while keeping the site technically credible, fast, accessible and commercially useful to a UK B2B engineering buyer.

This is an original implementation. Do not copy third-party code, text, branding or media from the Instagram reference or any other site.

## Current repository
Repository: `gptframe/QM-web`
Base branch: `main`
Working branch: `codex/cinematic-manufacturing-v2`

Read the existing implementation first. In particular use:
- `index.html`
- `styles.css`
- `script.js`
- `README.md`
- `REDESIGN_PLAN.md`
- `CURRENT_SITE_AUDIT.md`
- `CLAIMS_REQUIRING_OWNER_CONFIRMATION.md`
- `IMAGE_SHOT_LIST.md`
- `assets/`

## Product decision
Do **not** migrate to React/Next.js for this phase. The current static HTML/CSS/JS + GSAP architecture is adequate and is easier to deploy on GitHub Pages. Introduce a new framework only if a verified requirement appears that cannot reasonably be met with the current stack.

Do **not** introduce Three.js in the first pass. First make the existing GSAP-based production journey feel like one continuous component transformation. Leave the code structured so a WebGL hero can be added later if a suitable 3D model becomes available.

## Design target
The page should feel like a controlled production line in the browser.

### Hero
- Full viewport.
- One dominant finished component / engineered object.
- Strong concise proposition on the left.
- Subtle technical grid and drawing motifs.
- Small motion tied to scroll, not distracting autoplay.
- Primary CTA: send drawing / manufacturing requirement.
- Secondary CTA: follow the manufacturing route.

### Signature interaction: one continuous manufacturing story
The manufacturing sequence is the centrepiece.

Use the existing pinned GSAP/ScrollTrigger structure, but redesign the choreography so the visitor perceives a **single part moving through production**, not an image carousel.

Recommended stages:
0. Requirement / CAD
1. Material
2. Preparation
3. Machining
4. Optional secondary route
5. Inspection
6. Released finished component
7. Packing / supply

The existing eleven-step commercial route in `REDESIGN_PLAN.md` can still be explained elsewhere, but the signature visual story should remain concise enough to understand while scrolling.

For each visual stage:
- keep the component focal point in approximately the same screen location;
- match scale and camera angle as closely as the existing assets permit;
- use masks, controlled cross-fades, depth/scale, line overlays and typography to bridge states;
- avoid large lateral jumps that make the visitor think it is a different object;
- use a single GSAP timeline for stage choreography;
- do not create new tweens continuously inside `ScrollTrigger.onUpdate`;
- JavaScript may update semantic status text and active-stage state, but the animation itself should be authored in the timeline.

### Text behaviour
During the cinematic pinned section, keep copy intentionally short:
- stage number / stage name;
- one strong two-line statement;
- one concise technical qualifier where needed.

Move long explanations below the visual story.

### After the cinematic section
The remainder should become a confident B2B conversion page:
- verified capabilities selector;
- component / tooling / fabrication scope;
- quality and documentation scope;
- representative sectors phrased cautiously;
- why Quantamorph / operating model;
- RFQ process;
- final CTA and company footer.

## Image-sequence readiness
Do not create a 100+ frame production sequence from unrelated images.

Instead:
1. Build an abstraction for a future frame-sequence hero (canvas or image layer) only if it simplifies later integration.
2. Keep the current coherent SVG part states as the production implementation for now.
3. Document exactly what additional assets would be needed for a true reel-like transformation: same component, same camera, consistent lighting, approximately 40–80 optimized frames or a suitable GLB/GLTF 3D model.

If you implement an image-sequence prototype, keep it optional behind a data/config flag and make sure the current SVG journey is the default fallback.

## Motion rules
- Scrolling remains native.
- Pinning may be used only for the manufacturing story.
- Use scrubbed motion rather than forced snap scrolling.
- No cursor-trailing gimmicks, excessive 3D tilts or unrelated floating particles.
- Use red accents to indicate status/progress.
- Use slower motion around inspection/release to communicate verification.
- Finish the production story with a clear visual resolution before returning to normal page flow.

## Mobile
Mobile is not a reduced desktop screenshot.
- Shorten the pinned distance.
- Reduce simultaneous overlays.
- Keep captions readable in a bottom/side tray.
- Preserve 20px+ gutters.
- Avoid large GPU-heavy filters.
- If pinning becomes unstable on mobile browsers, use a stacked stage fallback for narrow screens rather than forcing the desktop animation.

## Accessibility
- All core story copy must exist in semantic HTML.
- Decorative animation layers must not duplicate content for screen readers.
- Respect `prefers-reduced-motion` with a complete readable fallback.
- Keep focus-visible styling.
- All interactive targets should be approximately 44px minimum.
- The primary CTA must remain reachable without completing the animation.

## Commercial/claims guardrails
Do not add unsupported statements such as:
- ISO certification;
- guaranteed tolerances;
- guaranteed lead times;
- machine-axis counts;
- "Made in Britain" or UK manufacturing claims;
- named customer/OEM experience;
- CMM/FAI/PPAP/traceability promises;
- in-house/factory ownership claims;
- precise quantity capability unless already confirmed in repository evidence.

Use conditional language where appropriate: capability, inspection, documentation and delivery basis are defined for the quotation/order.

## Implementation milestones

### Milestone 1 — Audit and baseline
- Run the existing site locally.
- Record the current visual and technical baseline.
- Identify broken assets/console errors/layout overflow.
- Confirm GitHub Pages deployment constraints.

### Milestone 2 — Hero refinement
- Improve composition and responsive typography.
- Strengthen visual hierarchy and CTA.
- Keep current brand character.

### Milestone 3 — Manufacturing story v2
- Refactor current journey into the continuous-part choreography described above.
- Improve matched positioning and transition continuity.
- Simplify copy.
- Improve progress rail/status treatment.
- Preserve reduced-motion fallback.

### Milestone 4 — Supporting sections
- Refine capabilities, quality, operating model and RFQ sections so they feel consistent with the premium visual language without becoming over-animated.

### Milestone 5 — Mobile and performance
- Validate responsive layouts at 375, 390, 430, 768, 1024, 1440 and 1920 CSS px.
- Remove unnecessary eager media and expensive effects.
- Check transfer size and image loading.
- Ensure no horizontal overflow.

### Milestone 6 — QA and documentation
- Keyboard test.
- Reduced-motion test.
- Console and broken-link test.
- Update README with architecture, local preview, assets and future frame-sequence/3D upgrade path.
- Summarise changed files, tests run, remaining visual-asset limitations and recommended next asset-production step.

## Done when
The task is complete only when:
- the homepage works on GitHub Pages with no console errors;
- the hero clearly communicates what Quantamorph does and how to start an RFQ;
- the manufacturing section feels like one controlled continuous production story rather than a slideshow;
- current-stage progress is visually obvious;
- mobile has a deliberate usable experience;
- reduced-motion users receive all content without the cinematic pinning dependency;
- public copy contains no new unsupported capability/compliance claims;
- no horizontal overflow is present at the target widths;
- the final report lists the exact validation performed and any remaining limitations.

## Stop condition
If the desired reel-like effect cannot be achieved convincingly because the required same-part visual assets are missing, do not fake a finished result with unrelated images. Complete the strongest coherent GSAP implementation possible, document the blocker precisely, and provide the exact asset specification needed for the next pass.
