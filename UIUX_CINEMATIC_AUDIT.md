# Quantamorph cinematic UI/UX audit

Audit date: 25 September 2026  
Audited branch state: `codex/cinematic-manufacturing-v2` at `c00019772f2585a9ab28dd34ffa4a1d3f9e1157b`  
Audit branch: `codex/uiux-reference-audit`

## Scope and guardrails

This is a design audit, not a redesign. No production HTML, CSS, JavaScript, imagery or claims were changed. The review uses the repository instructions and evidence in `AGENTS.md`, `CURRENT_SITE_AUDIT.md`, `REDESIGN_PLAN.md`, `IMAGE_SHOT_LIST.md`, `CODEX_CINEMATIC_REDESIGN.md`, `CLAIMS_REQUIRING_OWNER_CONFIRMATION.md`, `CODEX_START_HERE.md`, the current implementation, and the existing browser-QA output.

The recommendations preserve the current static HTML/CSS/JavaScript architecture and its local GSAP/ScrollTrigger progressive enhancement. They also preserve the central claims rule: capability, inspection scope, records, lead time and route are confirmed per enquiry. Nothing in this audit should be read as evidence of a certification, tolerance, machine inventory, capacity, facility, customer relationship or guaranteed outcome.

No attached visual-reference files were available in this task's workspace. The audit therefore uses the repository's current screenshots and the supplied written direction. External premium-site patterns are discussed only as interaction and composition concepts; no third-party branding, text, source code or proprietary assets are proposed for copying.

## Evidence baseline

The existing Playwright report records **139/139 passing assertions across 10 scenarios**: 1920, 1440, 1024, 780, 768, 430, 390 and 375 CSS-pixel widths, plus reduced-motion and JavaScript-disabled modes. It records no console errors, page errors, failed requests, broken internal anchors, image failures or horizontal overflow. The desktop cinematic is asserted independently from the generic motion-ready class, and the mobile, reduced-motion and no-JavaScript routes are complete.

Representative evidence copied from that run:

- [Desktop hero, 1920 CSS px](https://github.com/gptframe/QM-web/blob/codex/uiux-reference-audit/audit-evidence/desktop-1920-hero.png)
- [Desktop manufacturing route, 1440 CSS px](https://github.com/gptframe/QM-web/blob/codex/uiux-reference-audit/audit-evidence/desktop-1440-process.png)
- [Desktop capability selector, 1440 CSS px](https://github.com/gptframe/QM-web/blob/codex/uiux-reference-audit/audit-evidence/desktop-1440-capabilities.png)
- [Mobile manufacturing route, 390 CSS px](https://github.com/gptframe/QM-web/blob/codex/uiux-reference-audit/audit-evidence/mobile-390-process.png)
- [Machine-readable browser-QA report](https://github.com/gptframe/QM-web/blob/codex/uiux-reference-audit/audit-evidence/browser-qa-report.json)

The evidence proves robust layout and fallback behaviour. It does not prove that the temporary imagery is physically continuous, production-resolution or licensed for stronger-than-illustrative presentation.

## UI/UX Pro Max upstream review

### Source, version and licence

The current upstream is [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill). The inspected `main` checkout was commit `dcc40ff5133ef78276117db0cc34e7b83cc8aeba` dated 21 September 2026. The [latest published GitHub release](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/releases) is `v2.15.0`, but the inspected main tree's root metadata still identifies skill version `2.13.0`, while the CLI package source declares version `2.5.0`. Those three identifiers should be reconciled against the exact npm tarball before installation rather than assuming they describe the same artefact.

The project is released under the [MIT License](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/LICENSE), copyright 2024 Next Level Builder. Project vendoring is therefore permitted provided the copyright and licence notice travel with copied or substantial portions. The repository also carries font-licence and data-provenance metadata. Those records are useful but do not transfer rights to unrelated third-party visual assets, and their presence is not a substitute for checking every asset introduced into Quantamorph.

### Codex compatibility and install locations

Codex is an explicit supported target. The [Codex platform template](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/src/ui-ux-pro-max/templates/platforms/codex.json) installs the orchestrator at `.agents/skills/ui-ux-pro-max/SKILL.md` and references `.agents/skills/ui-ux-pro-max/scripts/search.py`. The search runtime is Python 3 and otherwise uses local files and the standard library for ordinary queries.

The documented install is `npx ui-ux-pro-max-cli init --ai codex`; the project also documents a globally installed CLI (`npm install -g ui-ux-pro-max-cli`, then `uipro init --ai codex`). The [CLI documentation](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/cli/README.md) exposes `--dry-run`, `--force`, `--global`, `--offline` and a legacy installer path.

Without `--global`, the template installer writes below the current project directory. It does **not** edit Codex `config.toml` or another global Codex configuration file. With `--global`, it changes the target to the user's home directory and writes under `~/.agents`. The `update` command can execute a global `npm install -g`; it should not be used in a pinned repository workflow. The uninstaller recursively removes the installed skill and its bundled sibling-skill directories after an interactive confirmation.

### Files and scripts included

The upstream package contains:

- an orchestrator skill template and platform configurations, including Codex;
- Python search, scoring, design-system persistence and data-validation scripts;
- local CSV/JSON catalogues for interface styles, colours, typography, fonts and licence metadata, UX guidance, icons, GSAP motion, charts, landing-page patterns, product profiles and 22 implementation stacks;
- six bundled sibling skills in the inspected source (`banner-design`, `brand`, `design-system`, `design`, `slides`, and `ui-styling`), installed beside the orchestrator by the current template installer;
- TypeScript CLI sources for detection, template generation, GitHub release download, archive extraction, update and uninstall;
- tests and fixtures.

The normal template install copies local package assets. The legacy path can fetch a GitHub release ZIP, invokes platform archive/copy commands, and falls back to bundled assets. GitHub API calls can use `UI_PRO_MAX_GITHUB_TOKEN`, an explicit token, or the ambient `GITHUB_TOKEN`. Avoid the legacy path and avoid exposing a broad ambient Actions token to a tool that only needs public-repository access.

The reviewed Python search path does not fetch remote content. Plain searches read local data. Its `--persist` option intentionally creates or updates design-system files, so it should not be used casually in an established repository. The catalogue contains Google Fonts recommendations; Quantamorph's project rules must override those suggestions because the site deliberately has no remote-font dependency.

### Security and supply-chain assessment

No intentionally malicious behaviour was found in the inspected source. The material risks are scope and reproducibility, not a discovered exploit:

1. `npx` executes an npm-distributed build (`dist/index.js`) that is not tracked in the inspected Git source. Source review alone therefore does not establish byte-for-byte equivalence with the registry tarball.
2. The default command now installs seven skills, not only the UI/UX Pro Max orchestrator. That is unnecessary privilege and review surface for this audit.
3. `--force`, `update`, `uninstall`, `--global` and `--legacy` perform progressively more invasive writes, global package changes, recursive deletion or shell/archive operations.
4. Generic design recommendations can conflict with Quantamorph's evidence, font, performance and claims constraints unless the project-specific rules take precedence.
5. MIT allows vendoring, but its notice must be retained and upstream catalogue provenance should continue to be treated as metadata to verify, not blanket approval for downstream assets.

### Installation decision and safest route

**UI/UX Pro Max was audited but not installed or executed.** The current audit does not need its broad catalogue, and adding six sibling skills would exceed the smallest useful change. The project-specific proposal in `skills/quantamorph-cinematic-design/SKILL.md` is narrower and remains deliberately inactive pending review.

If Quantamorph later adopts UI/UX Pro Max, the safest supported sequence is:

1. Select and record an exact CLI version and upstream Git commit. Download the npm tarball without executing it, verify its integrity, inspect `dist`, `assets`, dependency lock information and licence notices, and reconcile the `2.13.0` skill / `2.5.0` CLI version mismatch.
2. From a disposable checkout, run the pinned package's `init --ai codex --dry-run` without `--global`, `--force` or `--legacy` and compare its announced paths with the reviewed source.
3. Prefer a least-privilege manual vendor of only the reviewed `ui-ux-pro-max` skill, required local data/scripts and MIT notice at the pinned revision. Do not copy the sibling skills unless each is separately required and reviewed.
4. Commit the vendored files so all contributors receive the same reviewed version. Keep Quantamorph's skill higher-priority for branding, accessibility, claims, fonts and architecture. Do not use automatic `uipro update` in the repository.

This route is project-local and avoids global Codex configuration changes. It also makes future upstream diffs reviewable.

## 1. What already feels premium

The strongest decision is the single-part narrative. The hero establishes the finished component as the protagonist; the manufacturing route keeps it centred; the capability selector continues to frame processes around a part rather than around generic service cards. That conceptual continuity is much stronger than the site's former page-of-sections structure.

The restrained near-black, graphite, cool-metal and red palette is credible for precision engineering. Fine rules, sparse red markers, the route rail and the large editorial display type create controlled tension without leaning on the familiar blue-corporate-manufacturing palette. The desktop process scene has a genuine focal point and uses scale well: the stage text, object and progress datum read in one glance.

The progressive enhancement is also premium in the less visible sense. The experience is not dependent on animation: mobile, reduced-motion, JavaScript-disabled and keyboard routes remain complete. The copy generally distinguishes consideration, coordination and confirmation from guaranteed delivery. That restraint supports trust.

## 2. What still feels like a conventional engineering website

Below the cinematic route, the page increasingly returns to familiar patterns: a large section heading, a supporting paragraph, a bordered card/list system, an image on one side, then another large heading. The capability selector is visually strong, but the repeated numbered rows still resemble a dressed-up services menu. The systems, quality, applications and why-us sections risk becoming a sequence of content modules rather than one procurement narrative.

The navigation is comprehensive but reads as a conventional corporate site index. The recurring all-caps labels, uppercase microcopy, outlined buttons and thin-rule boxes eventually become a visual template rather than meaningful hierarchy. On a long page, premium restraint depends on variation in density and silence; here, many sections announce themselves at the same volume.

The stock/illustrative machine imagery is the largest credibility gap outside the process route. It is appropriately labelled, but it shifts attention from the distinctive single-part story back to recognisable manufacturing-category imagery. The current temporary 512-pixel process sources also soften the intended object authority when enlarged near desktop hero scale.

## 3. Where animation should communicate manufacturing rather than decoration

Motion should answer one of four questions: what material exists now, what operation changes it, what evidence gates release, or where the component goes next. If a movement answers none of those questions, it should probably be removed.

Useful manufacturing motion includes:

- a drawing plane registering to the raw stock envelope;
- a cut datum reducing stock length before machining begins;
- controlled material removal or surface refinement while the camera and component registration remain fixed;
- a short inspection hold in which the route pauses rather than simply crossfades;
- a release transition from inspected component to preserved packed component;
- an optional-process branch that visibly rejoins the main route without implying every component receives every operation.

Decorative motion to avoid includes continuous object floating, ambient orbit for its own sake, unrelated text stagger on every section, looping scan lines, cursor followers and parallax that changes the apparent geometry. The stage-04 orbit labels are visually attractive but should become more explicitly conditional or quieter; otherwise they read as a sci-fi ornament around a mostly unchanged image.

Timing should reflect consequence. Preparation may be brisk; machining should feel progressive; inspection needs a deliberate dwell; release should be calm and final. Reduced motion should preserve those semantic state changes as discrete, legible steps without spatial travel.

## 4. Hero improvements

The hero has authority, but the headline currently competes with the part rather than introducing it. At 1920 pixels the five-line display block dominates the left half, while the component's darkest surfaces merge with the background. Improve the relationship before adding effects:

- give the component a slightly clearer rim/value separation and use a production-resolution source;
- tighten the headline's optical width or scale so the eye can move from proposition to object, not choose between them;
- retain the outlined final word only if it remains legible on lower-contrast and Windows font fallbacks;
- reduce the number of simultaneous orientation devices in the first viewport (route panel, vertical rail, scroll prompt, eyebrow, two CTAs and disclaimer);
- make the primary action remain dominant, with the route action visibly secondary and directly connected to the first manufacturing state;
- keep the claim-safe supporting sentence, but allow it more breathing room and a shorter measure.

A premium next step is not a more animated hero. It is a more physically convincing component, a calmer information hierarchy and a transition in which the hero part becomes the route part without a perceived camera reset.

## 5. Manufacturing journey improvements

The pinned route is the page's best interaction and should remain the spine. Its biggest limitation is asset truth: six temporary images represent eight stages, and the same-part continuity is suggested more than proved. Before increasing motion complexity, produce an aligned asset set in which every state uses the same optical axis, camera direction, crop and lighting family. The raw and cut stock must physically contain the finished geometry; machining can only remove material; CAD, rough, finished, inspected and packed states must preserve exactly the same component.

Then refine the route around production meaning:

- make the initial drawing-to-material registration explicit;
- show one unambiguous stock-reduction event during preparation;
- reserve the most continuous interpolation for machining, where transformation matters;
- present secondary operations as a conditional branch, not a universal stage;
- treat inspection as a gate with a short visual hold and evidence-oriented language, never fabricated readings;
- keep the component visible while packing changes around it;
- let the bottom stage rail carry actual route state and keyboard focus relationships, not only visual progress.

The current stage counter reads `04 / 07` while the accessible route includes stages 00 through 07. This is internally understandable but visually ambiguous. Prefer either `04 / 08`, or label it as an indexed route (`STAGE 04 · 8 STATES`) so the audience does not have to infer zero-based counting.

## 6. Typography improvements

The display system is forceful and now uses local system fallbacks, which protects performance and offline determinism. However, a narrow Arial-family fallback will not render identically across Windows, macOS and Linux. The design should be judged on all three fallback outcomes, not only on the development machine.

Near term, formalise fewer roles: display headline, section title, body, control label and technical annotation. Reduce all-caps outside controls and short annotations; sentence case body and explanatory headings will give the uppercase moments more authority. Keep body copy at a comfortable measure and avoid dropping mobile support text below a practical 16-pixel reading size.

Long term, if licensing and payload permit, bundle a self-hosted display family selected for condensed forms, numerals and broad platform consistency. Do not restore a remote Google Fonts dependency. Subset only the needed character set, provide `woff2`, declare responsible fallbacks, and measure layout shift and total transfer cost before adoption.

## 7. Spacing and composition improvements

The page's individual sections are spacious, but the macro rhythm is too even: very large heading, generous gap, bordered content, then repeat. Introduce contrast between cinematic space and compact evidence bands. A dense specification-like interval after a large visual scene can make the following open scene feel more deliberate.

Use one shared optical datum for the component, section indices and route connectors. The hero object, pinned process object and capability imagery should feel registered to the same invisible production line even when their containers differ. Align small labels to that datum instead of adding independent corner captions.

On desktop, reduce dead zones that do not contribute to anticipation, especially where a sticky visual persists beside short text. On mobile, avoid eight near-identical full-width image blocks at equal height; vary the vertical rhythm according to the significance of the state change. Preserve touch spacing and avoid making the condensed layout feel merely like the desktop scenes stacked one after another.

## 8. Capability-section improvements

The capability selector is the strongest supporting module because it asks the user to choose a process and updates one visual field. It can become more useful to a buyer without becoming a spec sheet:

- frame each option around the requirement it helps evaluate (define, shape, rotate, enable, verify, coordinate), as the current right-hand verbs begin to do;
- show concise input/decision/output context rather than generic marketing benefits;
- keep the selected state and focus state equally obvious;
- make image changes preserve a shared crop and perceived scale;
- distinguish illustrative process imagery from verified Quantamorph facility imagery;
- add no machine models, capacities, tolerances or lead times until confirmed by the owner.

The selector should not become a carousel. All choices should remain visible and keyboard reachable, with transitions subordinate to comparison. On mobile, an accordion or snap-free list with one active image is preferable to horizontal swipe controls that hide available routes.

## 9. Mobile-specific improvements

The 390-pixel evidence shows a clear fallback: the image precedes the stage label and body, and the navigation remains reachable. The main opportunity is compression without loss of route completeness.

- Add a quiet sticky route indicator or compact `03 / 08` label so users understand progress through the long stack.
- Reduce repeated image height when consecutive states share the same component appearance; preserve the complete text route, but do not force every state into an equal cinematic panel.
- Keep stage headings short enough to avoid narrow-line display-type fragmentation.
- Use 44 CSS-pixel minimum touch targets and maintain visible `:focus-visible` styling for the menu, route controls and capability selector.
- Avoid body or disclaimer text below 16 CSS pixels unless it remains demonstrably readable at 200% zoom.
- Test the open mobile menu, not only the closed screenshot, for focus trapping, escape behaviour, scroll lock and return focus.
- Maintain zero horizontal overflow at 320 pixels as an additional defensive check even though the required matrix begins at 375.

The mobile experience should feel like a concise traveller through the same factory route, not a reduced desktop animation and not a long product catalogue.

## 10. Microinteraction opportunities

Microinteractions should reinforce control and route state:

- animate the CTA arrow along the same horizontal datum used by the process rail;
- give navigation links a precise active-section marker rather than a generic underline;
- on capability focus/selection, register the label, verb and image with one short transition;
- let the process rail marker settle decisively at each stage, with no elastic overshoot;
- pause the inspection marker briefly before release;
- use a subtle mask or aperture action when packing closes around the unchanged part;
- acknowledge RFQ-link activation immediately while preserving normal link behaviour;
- expose hover and focus equivalently; never reserve explanatory content for hover.

Avoid magnetic buttons, pointer-chasing light, tilt cards, kinetic noise, autoplay sound, haptics on the web or custom cursors. They advertise the interface rather than the production process.

## 11. Patterns worth borrowing conceptually from premium modern websites

Borrow behaviours, not identities:

- product-centred continuity in which one object persists across sections;
- shared-element transitions that maintain camera and scale registration;
- editorial contrast between very large proposition type and quiet evidence text;
- a small, persistent progress datum that makes a long narrative legible;
- scene changes caused by masks, apertures or material boundaries rather than generic fades;
- intentional pauses before high-consequence states;
- dense technical interludes between open cinematic scenes;
- progressive disclosure that lets buyers inspect route detail without making the default view feel like a dashboard;
- purposeful image art direction with consistent optics and lighting.

Each borrowed pattern must survive keyboard, reduced-motion, mobile and no-JavaScript use. It must also work with Quantamorph's real evidence; a premium mechanic cannot compensate for an unsupported claim or an inconsistent part.

## 12. Patterns inappropriate for a B2B engineering supplier

- neon/glassmorphism or game-like sci-fi HUDs that imply fictional instrumentation;
- fake live counters, tolerances, inspection readings, machine telemetry or capacity figures;
- a bento-grid collage used as the default answer to every content problem;
- autoplay carousels, scroll-jacking, mandatory horizontal scrolling or hidden navigation;
- excessive 3D, particle fields, cursor trails, floating components or perpetual parallax;
- startup-style pricing tiers for enquiry-led work;
- unverified customer-logo walls, case-study metrics or certification badges;
- stock imagery presented as the Quantamorph facility or equipment;
- remote-font dependencies added only for fashion;
- interaction that makes it harder to reach the RFQ action or understand what is confirmed per enquiry.

## 13. Ranked implementation recommendations

### High impact / low complexity

1. Simplify the hero's information hierarchy and reduce simultaneous orientation devices while retaining the current copy and component.
2. Define five explicit typography roles, reduce repeated all-caps treatment, and verify the display fallback on Windows, macOS and Linux.
3. Clarify route counting so the zero-based `00–07` model cannot be mistaken for seven total stages.
4. Vary section density and spacing to break the repeated heading-plus-module rhythm.
5. Strengthen selected, hover and `:focus-visible` states in the capability selector and navigation with the existing red/rule language.
6. Add a visible note in development documentation that all temporary process sources are illustrative and unsuitable for final high-DPI desktop presentation.

### High impact / medium complexity

1. Refine ScrollTrigger timing so preparation, machining, inspection and release have different semantic pacing, with equivalent discrete reduced-motion states.
2. Recompose the capability section around one registered optical axis and consistent image crop; frame content as requirement inputs, route decisions and outputs.
3. Compress the mobile route with a compact progress indicator and significance-based image heights while preserving all eight stages.
4. Build one visual connector from hero component to process component and onward to capabilities, avoiding a camera reset between sections.
5. Turn the optional secondary-operation scene into an explicit branch-and-rejoin interaction without implying a universal operation.
6. Add cross-platform screenshot comparison and an open-menu keyboard test to the QA suite.

### High impact / high complexity

1. Produce the final same-component, same-camera, high-DPI asset system, including physically valid stock/cut envelopes, machining-only material removal, exact inspected geometry and preserved packed geometry.
2. If the asset plan justifies it, render a 40–80-frame controlled sequence for the desktop route and responsive high-density derivatives; measure decode, memory and transfer costs before shipping.
3. Consider true 3D only after a suitable source model exists and only if it materially improves spatial understanding, progressive loading and fallback remain excellent, and the static architecture can carry the cost.
4. Create verified facility/process photography only with provenance and owner approval, replacing illustrative machine scenes where factual presentation is desired.

Three.js is not recommended as a default next step. A disciplined image sequence will likely deliver the required continuity with lower interaction and maintenance risk. The decision should be made after the production asset test, not before it.

## 14. Preview evidence observations

The [1920-pixel hero](https://github.com/gptframe/QM-web/blob/codex/uiux-reference-audit/audit-evidence/desktop-1920-hero.png) shows the brand system at its strongest scale: confident type, a clear primary CTA and a large component. It also shows the hierarchy issue—the headline, object, route panel, vertical rail and scroll instruction all compete within one viewport, and the dark temporary component needs clearer separation.

The [1440-pixel process scene](https://github.com/gptframe/QM-web/blob/codex/uiux-reference-audit/audit-evidence/desktop-1440-process.png) demonstrates that the pinned composition succeeds. The part is central, the stage copy is readable and the progress rail gives the scene direction. It also exposes the temporary-asset and decorative-orbit limitations: the geometry appears persuasive, but the surrounding labels do not yet prove what changes at the stage.

The [1440-pixel capability selector](https://github.com/gptframe/QM-web/blob/codex/uiux-reference-audit/audit-evidence/desktop-1440-capabilities.png) is a strong, controlled alternative to a services-card grid. Its opportunity is to make each selection more decision-oriented and to ensure that process imagery is not mistaken for facility evidence.

The [390-pixel process route](https://github.com/gptframe/QM-web/blob/codex/uiux-reference-audit/audit-evidence/mobile-390-process.png) proves that the complete journey survives without the pinned cinematic. Its clarity is good; its future risk is repetitive length once all eight final high-resolution states are present.

## Top five recommendations

1. **Replace the temporary process imagery with one physically continuous, high-DPI component asset system before adding more motion.** This is the largest visual-quality and credibility gain.
2. **Make every transition explain material, operation, verification or release.** Remove or quiet motion that cannot answer one of those questions.
3. **Calm the hero hierarchy and carry the same registered component into the process route.** One object and one optical datum should organise the first two sections.
4. **Break the conventional section rhythm below the route.** Use alternating cinematic space and compact evidence bands, with fewer repeated giant headings and bordered lists.
5. **Formalise typography and mobile compression.** Reduce all-caps repetition, validate cross-platform fallbacks, and make the eight-stage mobile route concise without hiding any stage.

## Conclusion

The current branch has already crossed from a conventional engineering site into a recognisable cinematic system. Its structure, progressive enhancement and claims restraint are sound. The next leap will not come from adding a design framework or more generic animation. It will come from physically truthful same-part assets, more semantic timing, calmer hierarchy and a supporting-section rhythm that maintains the authority of the manufacturing route.
