# Phase 4B motion review

Review basis: the 4×4 contact sheet, all sixteen native masters, the local scrub/play preview, analytic parameter checks, sampled 3D containment, and the fixed-camera projection measurements in `motion-review-metrics.json`.

## Findings

### Feature direction

No geometric feature grows into the solid. The external envelope contracts, the edge-break removal increases, and the bore, counterbore, bolt holes, hole mouths and cross-hole only enlarge as subtractive volumes. The 15 higher-density 3D adjacent checks report zero containment violations.

The 400×400 diagnostic projection records 22 raw one-pixel boundary classifications across the complete sequence. All disappear with a one-pixel raster tolerance and are ray-march threshold/edge-sampling effects, not 3D containment failures.

### Camera, scale and registration

There is no camera, crop, field-of-view, component-transform, background or light change. The largest projected centroid change is 1.1549 pixels at the 400-pixel diagnostic resolution between frames 10 and 11, equivalent to approximately 4.6 pixels at master resolution. This is caused by the largest final outer-envelope cut and not by recentering.

The slight reduction in perceived component size across the sequence is the intended consequence of stock removal. At faster playback the frame 10–11 change can read as a small final settling movement; a longer sequence should allocate an extra in-between frame to that cut rather than compensate with camera motion.

### Hole progression

The central bore begins at frame 04 and grows through frame 15. Bolt holes and the cross-hole begin with small subtractive radii at frame 12 and reach final size over four frames. Hole-mouth and counterbore removal also grow across the final four frames. No hole appears at full size in one frame.

The final feature pass is the visually busiest interval. At 12 fps, frames 12–15 feel brisk because the bolt circle, counterbore and minor feature removals overlap. This is acceptable for proving continuity, but a longer production sequence should give the minor-feature pass more samples.

### Surface continuity

The rough turning pattern remains locked to component coordinates and contains no random term. Its amplitude and material response progress monotonically towards the Phase 4A finished treatment, so there is no stochastic texture flicker or one-frame material pop.

Fine highlights still shimmer slightly where changing geometry changes the surface normal. This is expected from the lightweight proof shader and is most visible in the early rough frames. It should be evaluated again if the final-metal shader or lighting rig changes.

### Removal versus dissolve

The transition reads as machining/removal rather than a dissolve. Silhouettes, bores and holes change through rendered SDF geometry; images are never crossfaded. Adjacent decoded-image changes remain small: the largest mean absolute channel delta is 0.8935 levels and the largest share of pixels changing by more than four levels is 2.8011%.

### Frame-count decision

Sixteen frames are sufficient for this pilot when mapped to a deliberate scroll interval or scrubbed manually. They establish geometric compatibility, fixed registration and a credible removal direction.

Sixteen frames are not sufficient for the final premium sequence at unrestricted playback speed. A longer sequence should add samples around frame 10–11 outer resolution and frames 12–15 minor-feature machining. It should not change the camera or reintroduce a dissolve.

## Recommendation

**Ready for longer-sequence development**, subject to preserving the validated parameter programme and adding temporal samples around the two dense intervals above. This is not approval to generate the 40–80-frame sequence, replace live assets or integrate the pilot into the public website.
