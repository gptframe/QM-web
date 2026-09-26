# Quantamorph cinematic website — Start here in Codex

## Best workflow
Use the Codex app or Codex IDE extension with the GitHub repository `gptframe/QM-web` checked out locally. Keep the work isolated from `main` in a new branch or worktree.

Recommended branch name:

`codex/cinematic-manufacturing-v2`

Do not upload or commit the Instagram reel itself to the public repository. If you have a screen recording, attach it privately to the Codex thread or attach selected screenshots. The reel is a visual reference only; the implementation must use original code, copy and assets.

## Files to add before the first Codex run
1. Copy `AGENTS_QM.md` into the repository root and rename it to `AGENTS.md`.
2. Copy `CODEX_CINEMATIC_REDESIGN.md` into the repository root with that name.
3. Leave the existing audit, redesign plan, claims file and image shot list in place.

## First Codex instruction
Paste this into a fresh Codex thread after selecting the repository and the new branch/worktree:

> Read `AGENTS.md` and `CODEX_CINEMATIC_REDESIGN.md`, then inspect the current implementation before changing anything. Work through the milestones in the task brief in order. Start by running the current site locally and recording the baseline. Preserve all factual/claims guardrails. Do not migrate frameworks in this pass. Use the existing static HTML/CSS/JS + GSAP/ScrollTrigger architecture unless you find a concrete blocker. Make the manufacturing journey feel like one continuous part transformation, not a carousel. Validate desktop, mobile, reduced motion, keyboard navigation, console errors, broken assets and horizontal overflow. Keep working until the `Done when` criteria in `CODEX_CINEMATIC_REDESIGN.md` are either satisfied or you have a specific documented blocker.

## If Goal mode is available
After the first instruction, set this Goal:

> /goal Produce a production-ready cinematic Quantamorph homepage on the current feature branch, verified by a local browser preview and the validation checks in `CODEX_CINEMATIC_REDESIGN.md`, while preserving accessibility, GitHub Pages compatibility, performance and all claims guardrails. Use the existing GSAP architecture first. If missing same-part visual assets prevent a convincing reel-like transformation, complete the strongest coherent implementation possible and finish with the exact asset specification needed to remove that blocker.

## Give Codex the reel reference
The most reliable input is a private screen recording or 8–12 screenshots that show the key visual beats. Attach them to the Codex thread. Tell Codex:

> Use these only as interaction/pacing references. Do not copy branding, text, source code or proprietary assets. Identify the visual mechanics: camera/scale changes, pinned sections, masks, object continuity, typography timing, background treatment, progress UI and transitions. Map those mechanics onto the Quantamorph manufacturing story and existing brand.

If the reference cannot be attached, continue from the task brief. Do not ask Codex to scrape Instagram as a prerequisite.

## How to review Codex's first pass
Do not judge it only from the diff. Open the live local preview and scroll the whole page at least once on desktop and mobile.

The signature manufacturing section passes only if you can visually follow one object/part through the sequence. If it still feels like unrelated photographs fading between each other, tell Codex exactly that and ask it to improve matched position, scale, crop, transition masks and typography timing before adding more effects.

## Good follow-up prompts
Use one focused follow-up at a time:

- `The manufacturing story still reads like separate slides. Keep the current content, but make part position and scale visually continuous between stages. Reduce copy during the pin and improve the transition choreography before changing anything below it.`
- `Audit the mobile experience at 390px and 430px. Fix overflow, caption collisions and excessive pin length without weakening the desktop version.`
- `Run a performance pass. Reduce initial media weight and scroll-time GPU work without changing the approved visual design.`
- `Run an accessibility pass focused on reduced motion, keyboard navigation, focus visibility and duplicate screen-reader content.`
- `Compare the current result against the attached reference screenshots only for pacing and visual mechanics. List the three largest differences, then fix them without copying third-party creative assets.`

## What not to tell Codex
Avoid weak prompts such as:

- `make it like this reel`
- `make it more premium`
- `add cool animations`
- `make it 3D`
- `use Next.js`

Those describe taste or technology, not a verifiable outcome. The task brief already defines the outcome and the constraints.

## Framework decision
For this phase, keep the current static site and GSAP. A Next.js migration should be a separate project after the visual direction is approved, particularly if the site later adds multiple SEO landing pages, a secure RFQ upload workflow, server-side form handling, content management or authenticated customer features.

Mixing a framework migration with the cinematic redesign makes debugging, comparison and rollback unnecessarily difficult.

## Choosing 2D frame sequence vs 3D later
Use a frame sequence when you can produce a coherent set of the same component from the same camera with consistent lighting. It gives predictable art direction and is easy to scrub with scroll, but transfer/decode cost must be controlled.

Use Three.js/WebGL when you have a clean GLB/GLTF model and need true camera movement, rotation, exploded views or interactive geometry. It is more flexible but adds implementation, rendering and device-performance complexity.

Do not choose Three.js only because the reference feels cinematic. The current Quantamorph story can become substantially more cinematic with matched 2D assets and better GSAP choreography.

## The biggest visual dependency
The current repo already has strong interaction scaffolding. The main limitation is asset continuity. A near-reel-quality transformation needs one of these:

- approximately 40–80 optimized same-part frames with fixed camera/lighting; or
- a production-quality 3D model of the hero component plus approved materials/render direction.

Until that exists, Codex should not pretend unrelated photos form a literal transformation. It should use the existing SVG states as a representative controlled journey and keep the copy honest.

## Before merging
Require Codex to provide:
- changed files;
- screenshots or preview evidence;
- checks it ran;
- known limitations;
- media/performance impact;
- confirmation that no unsupported Quantamorph claims were introduced.

Then review the branch or pull request before merging to `main`.
