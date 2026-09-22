# Quantamorph Homepage — Redesign Plan

## Visual thesis

**A controlled production line in the browser.** The page begins with a finished component and its drawing intent. Scrolling moves the visitor through material, preparation, machining, optional operations, inspection, release and delivery. The interface borrows from engineering documentation—revision rails, stage IDs, crosshairs, measured spacing and restrained status red—without presenting invented engineering data.

## Audience and primary task

Primary visitors are design engineers, manufacturing engineers, procurement managers, operations managers and owner-managers with a component requirement. The page must answer, in order:

1. What does Quantamorph coordinate?
2. How does a requirement become a delivered component?
3. Which manufacturing routes can be considered?
4. How are inspection and documentation defined?
5. Why use a UK-facing coordinator?
6. What should I send for an RFQ?

## New homepage structure

### 01 — Hero: From drawing to delivered component

- Clear H1 and UK-facing manufacturing-coordination qualifier.
- Finished component on the right; subtle drawing grid and coordinate motifs.
- Primary CTA: **Send your drawing**.
- Secondary CTA: **Follow the production route**.
- Micro-interaction: **Scroll to start production**.

### 02 — Pinned manufacturing journey

Approximately 620vh desktop / 430vh mobile. A full-height scene stays pinned while a production rail advances through eight chapters:

0. **Requirement** — drawings, CAD models or samples establish the enquiry.
1. **Material** — grade, form and documentation needs are defined for the quotation.
2. **Preparation** — stock is prepared for the selected route.
3. **Machining** — geometry, interfaces and drawing-defined features take shape.
4. **Secondary operations** — optional routes appear around the part; the process adapts to the requirement.
5. **Inspection** — movement slows; agreed characteristics and records become the release gate.
6. **Finished component** — the visual resolves into a quiet premium product image.
7. **Delivery / accountability** — the route transitions into UK-facing communication and delivery coordination.

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

- Explain the commercial model directly: UK-facing communication plus coordinated manufacturing routes and one enquiry path.
- Avoid “Made in Britain” implications and avoid disparaging overseas factories.

### 08 — RFQ process

1. Send drawing / describe requirement.
2. Review material, quantity, revision and acceptance needs.
3. Define route and quotation.
4. Coordinate manufacture.
5. Inspect to the agreed scope.
6. Prepare documentation and delivery.

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
- Secondary processes orbit as brief supporting panels, then clear away.
- Inspection reduces velocity and contrast movement before the release state.
- Finished → delivery pulls back from product detail into packaged handover.
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
- Conservative title and meta description focused on drawing-led manufacturing coordination.
- Basic Open Graph title/description without an invented preview image.
- Registered-office wording and England/Wales registration disclosure.
- No ISO, tolerance, machine-axis, traceability, FAI, CMM, lead-time or sector-certification claims until confirmed.

## Success test

The redesign succeeds when a visitor can say: “I have a drawing. Quantamorph can review the requirement, coordinate an appropriate manufacturing route, define inspection and documentation with the quotation, and give me one UK-facing enquiry path.”
