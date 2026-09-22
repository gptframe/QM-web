# Quantamorph Homepage — Current Site Audit

Audit date: 6 September 2026  
Source reviewed: supplied `index.html`, content audit and eight 1536 × 1024 JPG assets.

## Executive assessment

The current page has the right dark-industrial ingredients, cautious copy and a basic pinned GSAP sequence, but it still reads as a conventional brochure site with a photograph carousel. It does not yet make the visitor feel that one requirement is being controlled through a manufacturing route. The redesign should preserve the brand tone and conservative claims posture, while replacing the page structure, hierarchy, motion system and image loading strategy.

## What should remain

- The Quantamorph name and restrained red accent.
- The near-black / charcoal / machined-metal visual language.
- Drawing-led enquiry positioning and a direct RFQ action.
- Broad, cautiously worded categories: engineering review, machining, tooling, fabrication, inspection and supply coordination.
- The supplied raw-material, milling, inspection, finished-component, turned-component and press-tool photography, subject to image rights and capability confirmation.
- Existing semantic foundations: one H1, landmarks, skip link, visible focus styles and a reduced-motion route.
- Conservative qualifiers that make capability, inspection and documentation subject to the agreed quotation.

## What should be removed

- The generic six-card services grid.
- The horizontal swipe gallery as the primary proof of capability.
- “Production examples” unless the images are confirmed as Quantamorph/customer-authorised work.
- “How we manufacture” where it implies that Quantamorph owns and operates every pictured process.
- The current five-photo crossfade as the main experience.
- Duplicate adjacent mailto actions that do the same job.
- Small red text at the current contrast level; the existing accent fails AA for small copy.
- Eager loading of every full-screen process image.

## What should be completely redesigned

- Hero: make the offer, audience and next action clear in the first viewport.
- Manufacturing story: eight connected stages from requirement to delivery, with one pinned production viewport, a continuous process rail and explicit acknowledgement that the route adapts to the part.
- Capabilities: an image-led indexed selector, not a card wall.
- Product scope: show component/tooling/fabrication types in procurement language.
- Quality: present drawing revision, acceptance criteria, inspection scope and records as a controlled release gate.
- Commercial model: explain the UK-facing interface and coordinated manufacturing route without disguising production location or implying “Made in Britain”.
- RFQ: show exactly what happens after an enquiry is sent.
- Navigation and mobile menu: persistent RFQ action, clearer active states, Escape/outside-click handling and robust contrast.

## Copy problems

- “Engineering Without Compromise” is usable as a brand line but does not explain the offer by itself.
- “Precision” is not substantiated with a process- and geometry-specific capability range.
- The current page repeatedly uses “agreed”, “drawing” and “scope” without turning those words into a distinctive value proposition.
- The current copy alternates between “coordinates” and “we manufacture”, leaving the operating model unclear.
- “Cut to size” is paired with a turning image, which is technically inaccurate.
- “Ready for assembly” overstates the universal delivered condition.
- The sectors read as completed sector experience even though no evidence has been supplied.

## Visual problems

- The current journey changes from a round dark billet to turning, then to a bright aluminium milled block, a different inspected part and a different finished part. It works as a representative route, not a literal same-part transformation.
- Four assets are studio packshots and four are documentary process images; interleaving them without a visual system creates discontinuity.
- The yellow robotic-welding image breaks the cool graphite/silver palette and contains prominent third-party branding.
- The inspection image contains visible instrument branding and plausible-looking numerical readouts that must not be presented as project data.
- Typography is large but not meaningfully integrated with the manufacturing movement.

## UX and conversion problems

- The primary value is not understood within five seconds; the page leads with a slogan rather than the concrete journey.
- The scroll story has no clear Stage 0 requirement moment and stops before commercial accountability/delivery.
- A visitor cannot easily distinguish a typical component route from optional secondary operations.
- Capabilities are generic descriptions rather than an answer to “can you handle my part?”.
- Mailto is the only conversion route and may be awkward for webmail users. No secure upload, accepted-format guidance or confidentiality workflow is described.
- The registered-office address can be mistaken for a manufacturing facility.
- No case study, machine/process envelope, material range, batch range, lead-time guidance or verified quality evidence is available.

## Technical and performance problems

- In the supplied package all image URLs are broken: the HTML expects `assets/*.jpg`, while the attachments are flattened and renamed.
- CSS, content and JavaScript are combined in a 25 KB monolithic HTML file.
- The eight JPGs total approximately 16.7 MB. Hidden process images are still loaded eagerly.
- Five full-screen filtered images retain `will-change`, increasing GPU and memory pressure.
- Meaningful journey and gallery content is constructed in JavaScript, so no-JS users receive empty sections.
- External fonts and GSAP add availability/privacy cost; no fallback integrity strategy is present.
- There is no canonical URL, favicon or structured data. Open Graph text exists only partially and should not include unverified claims.

## Animation problems

- The current timeline is a competent crossfade, but the scene does not behave like one production line.
- Progress state is mutated in `onUpdate`; stage choreography is not authored as a single named sequence.
- Images and captions that are visually hidden remain exposed to assistive technology.
- The mobile pin is almost the desktop treatment at a smaller size, rather than a deliberately shorter journey.
- The sequence lacks a controlled inspection pause, branch behaviour for optional operations, a delivery/accountability handoff and visual continuity around a hero component.

## Image audit

| Supplied asset | Decision | Best use | Reason |
|---|---|---|---|
| `stage1_raw.jpg` | KEEP | Material stage | Strong raking light and useful billet texture. |
| `turned_gears.jpg` | KEEP | What we manufacture | High-quality product grouping; not part of the linear journey. |
| `stage2_cutting.jpg` | REPLACE | Temporary turning/preparation only | Coolant plus sparks feels theatrical and it is turning, not cutting-to-length. |
| `stage4_inspect.jpg` | KEEP | Inspection / quality | Clear human inspection moment; crop and overlays must de-emphasise readouts/brand. |
| `press_tool.jpg` | KEEP, CONDITIONAL | Tooling capability | Excellent packshot, but only if tooling is genuinely offered. |
| `stage5_finished.jpg` | KEEP | Hero and finished stage | Strongest premium component image. |
| `stage3_milling.jpg` | KEEP | Core machining stage | Credible, detailed CNC visual; closest tonal link to the finished part. |
| `welding.jpg` | REPLACE, OR REMOVE | Secondary fabrication | Colour outlier, prominent third-party branding and capability/ownership implications. |

## Claims requiring owner confirmation

1. Whether Quantamorph manufactures directly, coordinates approved partners, or uses a hybrid model.
2. Manufacturing locations and the wording permitted for the UK-facing commercial relationship.
3. Image ownership, licences and whether the images depict Quantamorph work/facilities.
4. ISO 9001 status, certified entity, scope, issuing body and expiry date.
5. Available CNC processes, axis counts, machine list and work envelopes.
6. Turning, milling, tooling, press-tool, fabrication and welding capability.
7. Supported materials and whether material certificates / certificates of conformity can be supplied.
8. Tolerance capability by process, material, geometry and feature.
9. Inspection equipment, calibration controls, sampling policy and CMM availability.
10. FAI, inspection-report, material-document and batch-traceability options.
11. Surface finishing, heat treatment, plating/coating and the parties responsible.
12. Prototype and production-volume ranges.
13. Standard lead-time and quotation-response expectations.
14. Countries served, Incoterms, customs responsibilities and delivery documentation.
15. NDA availability, drawing access, storage, retention, reuse and deletion controls.
16. Sector experience and any sector-specific certifications.
17. Company email, registered-office wording and owner-approved legal/privacy pages.

Until confirmed, homepage copy should stay process-specific but conditional: capabilities, inspection, records and delivery requirements are defined for each quotation.

## Administrative facts checked

The public [Companies House record](https://find-and-update.company-information.service.gov.uk/company/17389114) currently confirms the Quantamorph Limited name, company number 17389114, active private-company status and 71–75 Shelton Street registered office. It also lists agency/wholesale and engineering-design SIC activities, which supports using careful “manufacturing coordination” language rather than implying that the registered office is a factory. The footer now includes the registered number, registered-office label and place of registration in line with [GOV.UK website disclosure guidance](https://www.gov.uk/running-a-limited-company/signs-stationery-and-promotional-material).
