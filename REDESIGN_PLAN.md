# Quantamorph Homepage — Redesign Plan

## Visual thesis

**A controlled production line in the browser.** The page begins with the customer enquiry and a finished-component outcome. Scrolling follows one cylindrical part through review, quotation, approval, optional design, material, cutting, machining, checking, inspection, packing and supply. The interface borrows from engineering documentation—revision rails, stage IDs, crosshairs, measured spacing and restrained status red—without presenting invented engineering data.

## Audience and primary task

Primary visitors are design engineers, manufacturing engineers, procurement managers, operations managers and owner-managers with a component requirement. The page must answer, in order:

1. What does Quantamorph design and manufacture?
2. How does a requirement become a delivered component?
3. Which manufacturing routes can be considered?
4. How are inspection and documentation defined?
5. Why use one accountable Quantamorph engineering team?
6. What should I send for an RFQ?

## New homepage structure

### 01 — Hero: From enquiry to supplied component

- Clear H1 and an end-to-end design, manufacture, inspection and supply qualifier.
- Finished component on the right; subtle drawing grid and coordinate motifs.
- Primary CTA: **Send your drawing**.
- Secondary CTA: **Follow the production route**.
- Micro-interaction: **Scroll to start production**.

### 02 — Pinned manufacturing journey

Approximately 680vh desktop / 510vh mobile. A full-height scene stays pinned while a production rail advances through eleven chapters:

0. **Enquiry** — drawing, CAD file, sample or functional brief enters the route.
1. **Review** — geometry, material, quantity and acceptance requirements are assessed.
2. **Quotation** — process, scope, assumptions and delivery basis are defined.
3. **Approval & optional design** — design is added when required; drawing-ready work advances directly.
4. **Material** — the specified round stock enters production.
5. **Cut** — stock becomes a controlled machining blank.
6. **CNC/VMC machining** — the blank develops into the required geometry.
7. **In-process check** — key features are checked at the machine.
8. **Final inspection** — specified characteristics are checked before release.
9. **Packing** — the finished part is protected and identified.
10. **Supply** — documentation, packing and delivery complete the route.

The story is explicitly presented as a **representative route**, not a claim that every part receives every process.

### 03 — Capabilities: Select the route

- Numbered vertical index with a large changing image and one concise process note.
- Engineering review, machining, turned components, tooling/fixtures, fabrication and inspection.
- Capability availability, capacity and limits remain quotation-specific until verified.

### 04 — What we can help source and manufacture

- Large component-type matrix: machined components, turned components, tooling/fixtures, fabricated assemblies, prototypes and repeat-production parts.
- No vague benefit cards and no unsupported volume/tolerance figures.

### 05 — Quality: The release gate

- Inspection photography with drawing-grid overlay.
- Four controlled inputs: drawing revision, acceptance criteria, inspection scope and agreed records.
- Prominent qualifier: documentation is supplied where included in the agreed scope.

### 06 — Applications / sectors

- “Enquiries considered for” framing until delivered sector experience is confirmed.
- Restrained text rail rather than invented customer logos.

### 07 — Why Quantamorph

- Explain the operating model directly: design, CNC/VMC machining, conventional toolroom, fabrication, SPM capability, inspection and supply through one enquiry path.
- Avoid “Made in Britain” implications and avoid disparaging overseas factories.

### 08 — RFQ process

1. Send drawing / describe requirement.
2. Review material, quantity, revision and acceptance needs.
3. Define route and quotation.
4. Approve the order and complete design where required.
5. Manufacture.
6. Inspect and pack to the agreed scope.
7. Supply with the agreed documentation.

### 09 — Final CTA and footer

- “Have a part to manufacture? Send the requirement.”
- One primary mailto action plus a visible email fallback.
- Company name, registered number, registered office and “Registered in England and Wales”.
- Clear per-quotation capability qualifier.

## Motion system

- One `gsap.timeline()` owns the production journey; no nested `gsap.to()` calls are created inside `onUpdate`.
- Each stage uses overlapping image opacity, clip-path/aperture, scale and caption movement.
- The process rail is animated by the timeline; JavaScript updates only the accessible current-stage label.
- Requirement → material uses a CAD-grid dissolve.
- Material → preparation uses a vertical machine-door wipe.
- Preparation → machining uses a horizontal aperture and matched component scale.
- A matched part-state sequence remains centred through CAD, stock, blank, rough-turn, finished and packed states.
- Inspection introduces measured overlays and slower transitions before release.
- Finished → packing → supply resolves into a protected component handover.
- Below the story, reveal motion is sparse and batched.
- Reduced motion receives the full semantic sequence as stacked cards with no pinning or parallax.

## Responsive strategy

- Desktop: 100svh pinned viewport, left narrative / right component focal area, eight-step rail.
- Tablet: shortened pin, simplified masks, larger caption measure and horizontally scrollable stage labels only when necessary.
- Mobile: 430vh journey, bottom caption tray, dot-and-number progress, no heavy orbiting panels, no continuous pointer effects.
- Under 768px the navigation becomes a focus-managed disclosure menu.
- All target widths (430, 390 and 375px) retain at least 20px content gutters and prevent horizontal overflow.

## Accessibility

- Journey copy exists in HTML before JavaScript; motion is progressive enhancement.
- Decorative visual layers are `aria-hidden`; a live but non-intrusive stage status reports the current chapter.
- Semantic ordered lists describe both journey and RFQ process.
- Accent red is reserved for controls and large/status text; small labels use a lighter accessible red.
- Visible focus, skip link, Escape/outside-click menu handling, minimum 44px targets and high-contrast fallbacks.
- Motion-path-like movement, scale and pinning are disabled under `prefers-reduced-motion`.

## Performance

- Generate 1536px and 960px WebP/AVIF derivatives from supplied assets.
- Preload only the actual hero image; later journey imagery loads near the story via IntersectionObserver.
- Use responsive `picture` sources, explicit aspect ratios, `decoding="async"` and below-fold lazy loading.
- Remove persistent `will-change`; enable it only on active story layers.
- Split markup, styles and JavaScript into `index.html`, `styles.css` and `script.js`.
- Use a system font stack fallback immediately; remote display fonts remain optional.

## SEO and trust

- One descriptive H1, crawlable H2s and process copy.
- Specific title and meta description focused on design, manufacture, inspection and supply.
- Basic Open Graph title/description without an invented preview image.
- Registered-office wording and England/Wales registration disclosure.
- No ISO, tolerance, machine-axis, traceability, FAI, CMM, lead-time or sector-certification claims until confirmed.

## Success test

The redesign succeeds when a visitor can say: “I have a drawing or functional requirement. Quantamorph can review it, quote it, design where needed, manufacture it, inspect it, pack it and supply it through one accountable route.”
