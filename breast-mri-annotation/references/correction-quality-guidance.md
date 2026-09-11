# Correction quality guidance

These portable lessons incorporate a subsequent manual correction review. Keep case-level evidence, images, hashes and exact edited masks in the user's project directory. For continuing a corrected case, its matched reviewed mask is authoritative. Transfer decisions to new cases, never coordinates, slice ranges, brush shapes or uniform margins. User ROI conventions are not universally validated anatomical definitions.

## Attachment extent

Review the entire superior-to-inferior attachment, including the region behind the mound and below the fold. Corrections may restore broad curved regions omitted by short flat or angular closures, or remove local posterior excess. Do not truncate at the mound's upper/lower extremum, trim inward merely because an interface is dark, or copy rounded additions as templates. Compare relevant reviewed examples with current anatomy and adjacent slices. A straight edge is a warning cue, not automatically wrong. Earlier posterior-trimming lessons do not establish a global inward offset.

## Slice coverage

Treat coverage separately from contour shape. Preserve deliberately empty user-corrected slices, even when some tissue remains visible. For new cases, inspect the first and last included slices and their neighbors to distinguish intended target from marginal tissue and artifact. Do not manufacture polygons to keep every slice nonempty, refill reviewed empty slices for continuity, or skip a fixed number of terminal slices. Artifact alone does not justify erasing a supported central region. Record a specific unresolved coverage ambiguity when necessary.

## Nipple position and extent

A generous supported local region is preferable to a tiny seed. Inspect the surface projection and tissue convergence in closeups across neighboring slices; consider alternative candidates. Corrections can relocate markers superiorly or inferiorly, so neither the most anterior point nor a universal upward shift is a reliable locator. Assess physical extent using current spacing rather than fixed voxel radii. A larger marker does not require a longer through-plane span. Avoid a fixed volume multiplier or deliberate whole-areola expansion. Preserve reviewed overlap and portions outside the breast mask; apply nipple priority only in derived scalar exports.

## Quality gate that changes generation behavior

- Inspect source-only and outline closeups around the full skin envelope and superior/inferior attachment, not only filled montages.
- Check rectangular notches, thin detached strips, abrupt steps and unsupported flat caps as potential algorithm artifacts. Intensity clipping may omit low-signal tissue; disabling clipping may fill background. Correct the actual contour and recheck neighbors.
- Treat case-specific anchors and interpolation as initialization. A single posterior x(y) curve is insufficient where folds, oblique attachment or changing topology require a full contour.
- Review coverage, attachment extent, outer envelope and nipple position/size independently. Correct geometry or a connected mask does not certify these decisions.
- Fix visibly correctable defects before acceptance. A review log or uncertainty flag does not substitute for correction. Keep agent review, user approval and export verification separate, and retain the requested every-slice Slicer review.

## Reliable correction comparisons

Resolve exact before/after pairings from explicit review mappings, not the newest filename or acceptance text. Verify baseline masks, physical geometry and segment encoding. Display-normalized staged MRI may differ in intensity while geometry and masks still match; use original MRI for intensity-based analysis. Preserve multicomponent overlap and compare union and nipple changes separately so relabeling is not mistaken for tissue removal. Map original slice indices to Slicer through physical geometry.

State which slices were numerically compared and which were visually inspected. Reconcile conflicting examples explicitly; do not turn the latest correction into a universal erosion, dilation, exclusion or relocation rule. Learning updates workflow guidance, not model weights. Do not silently rewrite reviewed masks or transfer their labels to other patients.
