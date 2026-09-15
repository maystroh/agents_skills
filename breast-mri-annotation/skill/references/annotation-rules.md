# User annotation preferences

Read [the latest 30-case Mama-Mia corrections](mama-mia-review1-learned-preferences.md) with these preferences, then [the earlier 25-case QIN review](review1-learned-preferences.md). Mama-Mia frequently restores broader posterior and upper/lower attachment regions, whereas QIN often trims posterior excess. Both are case-specific evidence: neither establishes a universal inward or outward offset.

## Breast region

The target is the breast region, including fatty and glandular tissue. Follow the visible external tissue/skin contour rather than leaving an unlabeled band inside the upper/anterior surface. Include the superior and inferior extensions demonstrated in the user's corrected examples; do not truncate early at the breast mound. Delineate the posterior boundary separately from the external contour and avoid leaking into deeper chest tissue. Limits must be judged for each case, not transferred as fixed coordinates.

The QIN-BREAST-01-0031 corrections expanded the upper/anterior border and superior extent on multiple slices, and the inferior extent on smaller-breast slices. The user largely retained the draft's posterior boundaries in those examples; this is not a universal posterior-boundary definition. The later 25-case QIN review repeatedly tightened posterior borders, while the subsequent Mama-Mia review often restored a broader curved attachment. Follow the current user's ROI convention and case anatomy; do not impose the anterior pectoral surface as an automatic cutoff or copy broad rounded additions as templates. Small external excess was removed on one 0031 slice.

## Nipple

The user explicitly prioritizes nipple **position** for the downstream task. Exact boundaries are not critical; extra surrounding pixels are acceptable. Use a generous local region centered on the supported nipple feature and label neighboring slices where supported. Mama-Mia corrections show that most previous markers were too small; assess physical extent rather than reusing fixed voxel radii. Do not deliberately expand to the whole areola. Avoid an unnecessarily tiny seed, arbitrary placement or a large patch that shifts the representative position. Corrections include both superior and inferior relocations; do not apply a universal directional shift. Preserve user-defined overlap and portions outside the breast mask. Uncertainty about borders alone is not a reason to stop; uncertainty about location may need a user hint.

## Local example (optional, never hard-coded input)

The original session's example artifacts are under:
`<LOCAL_WORKSPACE>\slicer-review\case0031`

- `QIN-BREAST-01-0031_corrected_reference.seg.nrrd`: user-corrected reference, saved before full-volume propagation.
- `corrections-review/`: before/after arrays, overlays and observed rules.
- `QIN-BREAST-01-0031_DRAFT_all_slices.seg.nrrd`: expanded draft, not evidence of user approval of every slice.

If these files are missing, proceed from these documented preferences and the current case. Do not copy patient data into the skill or reuse the case-specific polygon-generation scripts as a general segmentation model.
