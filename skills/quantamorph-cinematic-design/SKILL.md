---
name: quantamorph-cinematic-design
description: Audit or design Quantamorph public-site interfaces and motion while preserving its controlled-production visual identity, static HTML/CSS/JavaScript and GSAP architecture, accessibility, performance, asset provenance, and claims guardrails. Use for Quantamorph website UI/UX, cinematic manufacturing journeys, imagery, typography, responsive layout, interaction, or frontend review; do not use for unrelated brands.
---

# Quantamorph cinematic design

This is a project proposal. Do not move it into `.agents/skills`, install it globally, or treat it as active until a human reviewer approves it.

## Read before acting

Read the current versions of:

1. `AGENTS.md`
2. `README.md`
3. `CLAIMS_REQUIRING_OWNER_CONFIRMATION.md`
4. `CURRENT_SITE_AUDIT.md`
5. `REDESIGN_PLAN.md`
6. `IMAGE_SHOT_LIST.md`
7. `CODEX_CINEMATIC_REDESIGN.md`
8. `CODEX_START_HERE.md`

Inspect the current implementation and establish a browser baseline before proposing changes. Treat repository evidence and the user's current task as authoritative. Never infer a capability or factual claim from a visual reference.

## Design thesis

Present Quantamorph as a controlled route from requirement to released component. The protagonist is one component moving through production, not a sequence of unrelated slides, service cards or stock photographs.

Use motion to explain one of four things:

- the material state;
- the operation changing it;
- the evidence gating release;
- the component's next route state.

If motion explains none of these, remove it or make it static.

## Visual identity

- Use near-black and graphite foundations, cool metallic surfaces, white/off-white type, and restrained Quantamorph red for state, emphasis and action.
- Prefer strong editorial scale, asymmetric but registered composition, fine rules, route markers and sparse technical notation.
- Keep technical graphics abstract and truthful. Never create fake dimensions, tolerances, telemetry, inspection values, certification marks, machine specifications or production data.
- Avoid generic corporate blue, colourful gradients, glassmorphism, neon sci-fi HUDs, bento-grid excess, floating particles, custom cursors and decorative parallax.
- Borrow interaction mechanics and compositional principles from references, never their branding, copy, code or proprietary assets.

## Component continuity

Every manufacturing state must represent the same component and preserve:

- optical axis;
- camera direction and perspective;
- crop and perceived scale;
- lighting family;
- stable registration between frames.

The raw and cut stock envelopes must physically contain the finished component envelope. The cut blank must be long and large enough for the final part. Machining stages may only remove material. CAD, rough, finished, inspected and packed states must retain exactly the same geometry. Inspection and packing change evidence or context, not the component.

Treat imagery as illustrative unless documented provenance allows stronger wording. Do not present stock machine imagery as the Quantamorph facility or equipment.

For final desktop scenes displayed near 800–950 CSS pixels, do not rely on 512-pixel sources. Provide responsive high-DPI dimensions and verify decoding, transfer size and memory cost.

## Architecture rules

- Preserve the existing static HTML/CSS/JavaScript architecture and local GSAP/ScrollTrigger progressive enhancement unless a concrete blocker is demonstrated.
- Do not migrate frameworks for design novelty.
- Build a complete semantic document first. Animation may enhance it but must not own access to content.
- Keep local fallbacks when a third-party library fails or JavaScript is unavailable.
- Do not add remote font dependencies. Prefer the current deterministic stacks; propose self-hosted fonts only with clear licensing, measured payload and cross-platform fallback testing.
- Use existing tokens, component patterns and route data before adding new abstractions.

## Claims and evidence

Use conservative verbs such as `considered`, `reviewed`, `coordinated`, `planned` and `confirmed per enquiry`. Do not introduce or imply:

- ISO or other certification;
- guaranteed tolerance, lead time, capacity or outcome;
- owned machine models, facility details or inspection equipment;
- named materials, processes or sectors not already evidenced;
- customer relationships, metrics or testimonials without approval;
- automatic quoting or secure file handling that is not implemented.

Keep the qualification that capability, inspection scope, required records, route and lead time are confirmed against the specific enquiry.

## Typography and composition

- Use no more roles than needed: display headline, section title, body, control label and technical annotation.
- Reserve all-caps for short controls and annotations; do not make every heading and paragraph shout.
- Keep body copy readable, with practical line length and at least 16 CSS pixels for important mobile content.
- Align hero object, process object, capability imagery, indices and route rails to a shared optical datum.
- Alternate cinematic space with compact evidence bands. Avoid repeating the same large-heading-plus-bordered-module composition for every section.
- Use the red accent to indicate state or action, not as ambient decoration.

## Interaction and motion

- Use shared-element continuity so the hero component appears to enter the manufacturing route without a camera reset.
- Give preparation, machining, inspection and release different semantic pacing.
- Present optional operations as branches that rejoin the main route; never imply every enquiry receives every process.
- Let inspection pause deliberately before release. Never fill that pause with fabricated readings.
- Keep hover and keyboard focus equivalent. Do not hide essential information behind hover.
- Avoid scroll-jacking, mandatory horizontal navigation, autoplay carousels, elastic overshoot, perpetual loops and motion that changes perceived geometry.
- Honour `prefers-reduced-motion` with discrete state changes and no loss of content.

## Responsive behaviour

- Use the cinematic pinned route only at the intended desktop breakpoint and only when GSAP/ScrollTrigger are available.
- At 780 CSS pixels and below, provide the complete stacked eight-stage route.
- Reduced-motion and JavaScript-disabled modes must receive the complete route.
- Keep mobile navigation keyboard-operable with visible focus, escape behaviour, appropriate scroll handling and returned focus.
- Use at least 44 CSS-pixel touch targets.
- Avoid horizontal overflow at every tested width.
- Compress repetitive mobile imagery according to the significance of state change; never remove a route stage to shorten the page.

## Working method

1. Record the current branch, commit and working-tree state.
2. Read the required documents and map any claim in the task to its evidence.
3. Run the current site locally and capture desktop, mobile, reduced-motion and no-JavaScript baselines.
4. Identify the buyer task and the production state that each proposed interaction communicates.
5. Prefer the smallest implementation that strengthens component continuity and procurement clarity.
6. Keep visual-reference influence conceptual and document any asset provenance assumptions.
7. Test before/after at 375, 390, 430, 768, 1024, 1440 and 1920 CSS pixels.
8. Verify keyboard-only navigation, focus, reduced motion, JavaScript disabled, internal anchors, image loading, failed requests, console/page errors and horizontal overflow.
9. Report files changed, evidence, performance/media impact, remaining assets, limitations and claims confirmation.

## Decision tests

Before accepting a design change, answer yes to all applicable questions:

- Does it make the single-component route clearer?
- Does its motion communicate production rather than decorate the page?
- Is the geometry and asset provenance credible?
- Is the copy within repository claims guardrails?
- Does it work without motion and without JavaScript?
- Is keyboard use complete and focus visible?
- Is the mobile version intentional rather than merely stacked?
- Is the performance cost proportionate to the visual gain?
- Does it fit the existing architecture without unnecessary framework or dependency churn?

If evidence is missing, label the proposal as illustrative or stop and request the specific asset/owner confirmation. Never fake fidelity with invented data.
