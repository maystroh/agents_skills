# Annotation preferences

Read [lessons from reviewed corrections](review1-learned-preferences.md) with these preferences. Apply them to the current anatomy and honor the user's project-specific definitions and corrected references.

## Breast region

The target is the breast region, including fatty and glandular tissue. Follow the visible external tissue/skin contour rather than leaving an unlabeled band inside the upper/anterior surface. Include anatomically supported superior and inferior extensions; do not truncate early at the breast mound. Delineate the posterior boundary separately from the external contour and avoid leaking into deeper chest tissue. Limits must be judged for each case, not transferred as fixed coordinates.

Retaining a posterior boundary in one reviewed example does not validate it as a general strategy. Review the breast/chest-wall interface independently on each case and slice.

## Nipple

For this workflow, nipple position takes priority over exact borders. A compact generous marker with some surrounding pixels is acceptable; label neighboring slices where supported. Do not deliberately expand to the whole areola. Avoid an unnecessarily tiny seed, arbitrary placement or a large patch that shifts the representative position. Uncertainty about borders alone is not a reason to stop; uncertainty about location may need a user hint.

## Corrected references

Keep case-specific corrected masks, before/after snapshots, audit manifests and images in the user's project data directory. Use matching corrected examples when available, preserving them exactly unless revision is requested. If references are unavailable, proceed from the documented preferences and current anatomy. Do not copy patient data into the skill or reuse case-specific polygon-generation scripts as a general segmentation model.
