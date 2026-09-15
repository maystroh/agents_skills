# Lessons from the user's Astra review, 2026-09-10

Historical QIN evidence: read the [subsequent Mama-Mia review](mama-mia-review1-learned-preferences.md) before applying these lessons. Its frequent posterior attachment additions qualify the trimming guidance below; its larger nipple regions and relocations in opposite directions qualify any size or directional generalization. Preserve these observations as case-specific evidence, not a global boundary rule.

Read this before generating or reviewing breast MRI annotations for this user. These are annotation preferences supported by a 25-case correction set, not a trained model or a guarantee of accuracy on a new patient. Use anatomy in the current case; never reuse these cases' pixel coordinates, slice indices, volumes, or numerical trim widths as defaults.

## Evidence and limits

The reviewed folder is `<MRI_DATA>\annotation\astra_review1`. `annotations.csv` explicitly maps all 25 sources to their timestamped edited exports. All 25 untimestamped staged masks equal the corresponding original Astra labelmaps voxel-for-voxel; source arrays and physical geometry also match. The audit compared all 500 slices and found changes on 320. Before/after/source/difference details were visually inspected for selected changed slices in every case; this correction-learning pass did not repeat a full live Slicer review.

Across breast-plus-nipple union masks, the user added 17,360 and removed 234,445 voxels; 23 of 25 cases became smaller overall. Label-specific counts differ because changing breast to nipple is a relabeling, not removal of the breast region. Nipple masks changed in seven cases and remained voxel-identical in 18. These descriptive totals are not target sizes or acceptance thresholds.

Local audit artifacts and immutable before/after snapshots are under `<LOCAL_WORKSPACE>\astra_corrections_20260910`:

- `comparison.json`: exact pairings, SHA-256 hashes, original geometry, encoding, centroids and per-slice counts.
- `per_slice_changes.csv`: breast, nipple and union additions/removals for all 500 slices.
- `correction_report.md`: case findings with before/after/difference image links.
- Each case folder: `before.nii.gz`, `after.nii.gz`, `comparison.png`, and `all_slice_differences.png`.

If local evidence is unavailable, use the documented principles here without inventing quantitative evidence or substituting another patient's mask. Keep patient images and masks outside the skill.

## Posterior boundary: the main recurring correction

Observed: the user repeatedly removed posterior strips and superior-posterior wedges, moving the boundary anteriorly relative to the Astra draft. Examples in original NIfTI K order: 0033 k15/18/19, 0036 k2-4, 0041 k0/3/6, 0045 k1/13, 0046 k1-3, 0047 k11-12, 0048 k4-6, 0054 k1/4, 0059 k16-18, and 0067 k9/12. The width and curve of removal vary within and between cases.

Apply: trace the breast/chest-wall interface separately from the outer skin. Where visible, follow the anterior surface of the pectoral/chest-wall structure and exclude the deeper slab that the drafts often included. Check the superior-posterior wedge and the inferior fold-to-chest transition explicitly. A long straight posterior closure is only acceptable where it follows the visible interface; a convenient polygon edge is not evidence of that boundary. Do not extend the mask to deep bright chest structures simply because their intensity resembles breast tissue. Compare adjacent slices to track the interface when it is subtle; record uncertainty instead of inventing a fixed inward offset.

This newer batch supersedes any inference that retaining the posterior border in the older 0031 example made the previous posterior strategy reliable. It does not imply that every posterior border should be shifted or every breast mask eroded.

## Outer contour: remove leakage and recover genuine tissue

Observed removals: jagged anterior spikes, small external islands, ghosted rims, and excess at superior/inferior transitions were trimmed (0037 k0/1/18, 0038 k2, 0040 k0, 0045 k19). Observed additions: real anterior tissue omitted by the draft was restored (0038 k1 and its upper transition at k18; 0044 k0/1/3; 0047 k17; 0052 k1/3; 0053 k1/2/15; 0057 k17/18).

Apply: fit the visible continuous tissue/skin envelope. Remove threshold-derived protrusions outside it, but include real fatty/glandular tissue up to that envelope even where signal is weak. Inspect source-only and outline views with useful contrast in low-signal and end slices. Do not accept a sawtooth edge merely because it is connected, or a missing band merely because thresholding excluded it. Smoothness is a review cue, not permission to erase real folds or to apply blanket erosion/dilation. Inspect internal dark gaps before retaining or filling them; judge anatomical continuity rather than intensity alone.

## Slice coverage and deliberately empty references

Observed: the user cleared entire previously labeled slices in nine cases: 0039 k0/1/2/18/19; 0042 k1; 0049 k3; 0052 k0; 0054 k0; 0055 k3/4/17; 0058 k1; 0067 k2; 0068 k2/3. These are original NIfTI K indices, not portable Slicer indices. Some cleared slices visibly contain tissue, and some neighboring terminal slices were retained. The files alone do not establish the user's reason or a universal first/last-slice exclusion policy.

Apply: preserve those empty slices when continuing these corrected cases. For new cases, assess first/last included slices and their neighbors explicitly; distinguish target breast from chest-only tissue and uncertain marginal coverage. Do not propagate contours through an intentionally empty corrected slice or refill it to improve continuity. Do not turn these observations into a fixed number of skipped slices, a minimum volume, or automatic removal of every terminal slice. Ask about a coverage convention only if an unresolved ambiguity affects the current task.

## Nipple position and local extent

Observed: the user replaced the nipple locations in 0036, 0039 and 0040 with markers higher on the anterior surface in these sagittal images, rather than at the draft's more inferior/anterior extremum. They enlarged/extended markers in 0033 (235 to 438 voxels) and 0050 (167 to 440). Changes in 0038 (212 to 175) and 0043 (167 to 165) were trims, not comparable relocations. Eighteen nipple masks were unchanged.

Apply: identify the actual local nipple feature across neighboring slices; neither the most anterior voxel, breast apex, midpoint of breast height nor the central slice reliably locates it. Inspect a closeup and adjacent slices for a subtle surface projection or localized tissue convergence, considering more than one plausible site when needed. The three upward corrections motivate checking the superior candidate, not universally moving markers upward. Keep a compact, generous marker around the supported location and extend only onto supported neighboring slices. Preserve the user's corrected nipple exactly during breast-only changes, including its segment overlap; do not replace a corrected location with the old provisional marker. The corrected 0036 marker is now a user reference, replacing the earlier unresolved provisional location for that case.

## Checks that should change future behavior

Before accepting each generated case, review posterior depth, outer envelope, superior/inferior transitions, coverage endpoints and nipple position as separate decisions. Do this on actual source/overlay views, not only the combined impression of a green filled mask. Correct affected slices and recheck their neighbors. Geometry and connected-component checks cannot certify these anatomical choices. Keep the every-slice Slicer review requirement when requested.

For correction comparisons, resolve the reviewed filename from the review mapping, not the newest-looking name alone. A row saying both `Acceptable with no changes` and `Mask edited` is not proof of unchanged voxels. Compare arrays. The 0036 and 0039 reviewed NIfTI files store two binary components (breast then nipple in this folder's segment order), including overlap, whereas the others are scalar labels 0/1/2. Verify encoding and segment mapping before comparison; do not treat a channel axis as a spatial/time axis or assume the same order for unrelated files. Preserve the original multicomponent reference and overlap; use nipple priority only in an explicit derived scalar comparison/export. Distinguish actual segment deletion from label reassignment.

Slicer may normalize handedness and reverse K relative to the original NIfTI despite identical shapes. Map via physical geometry and record the slice-order convention. Preserve reviewed masks in their original geometry and compare geometry and voxels after reloading; copying an array into a source header without this check can mirror corrections.
