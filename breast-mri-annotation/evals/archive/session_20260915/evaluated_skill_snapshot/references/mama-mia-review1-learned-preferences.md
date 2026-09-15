# Mama-Mia user review: 2026-09-11

Use this as the latest calibration for this user's sagittal breast-region and nipple annotation. For continuing these cases, the mapped user-reviewed masks are authoritative references. For new cases, transfer the decisions below, not coordinates, brush shapes, slice ranges, or a uniform expansion/erosion. This is a task-specific ROI convention, not a universally validated anatomical segmentation definition.

## Verified evidence

Review folder: `<MRI_DATA>\annotation\mama_mia\dev_astra_review1`. Resolve reviewed files through `annotations.csv`; `stage_manifest.csv` names the exact seeded Astra exports from `<MRI_DATA>\datasets\sagittal_dataset\nifti\mama-mia\dev`. All 30 staged masks match those exports voxel-for-voxel, and physical geometry matches. The staged MRI copies are intensity-normalized and are not voxel-identical to the original MRI. Use original MRI for intensity-based analysis; do not reject an otherwise valid mask pairing solely because display-normalized source values differ.

All 1,734 slices were compared numerically; 981 changed. Selected source/before/after/difference panels were visually inspected for every case, plus focused nipple relocation views. This learning pass was not another complete live Slicer review. Immutable before/after files, hashes, geometry, per-slice counts and figures are under `<LOCAL_WORKSPACE>\mama_mia_corrections_20260911`: `comparison.json`, `per_slice_changes.csv`, `summary.json`, `correction_report.md`, and per-case `comparison.png` / `all_slice_differences.png`. Keep patient images outside the skill. If unavailable, use these documented lessons without fabricating access to examples.

Union masks gained 2,956,328 and lost 1,471,342 voxels; 17 cases became larger overall. These totals pool different voxel spacings and are descriptive, not target sizes. Twenty-four reviewed files contain two binary components, breast then nipple according to this folder's segment mapping; six are scalar 0/1/2. Preserve raw component overlap. Compare union and nipple separately so breast-to-nipple relabeling is not mistaken for tissue removal. Record original NIfTI K indices and map to Slicer physically, never by assumed array order.

## Extent: correct the previous bias toward trimming

Observed: large posterior, superior-posterior and inferior attachment additions recur in ISPY1_1049 (k31/40/56), 1056 (k20/47/49), 1098 (k34/45/46), 1104 (k22/48), 1150 (k42/48), 1168 (k18/21), 1179 (k11/15), 1183 (k21/32), 1198 (k33), 1199 (k28), 1207 (k39), 1230 (k22/24/25), and 1235 (k15). They replace short flat cutoffs or a straight posterior chord with a longer curved attachment. ISPY1_1230 has especially broad rounded additions beyond the obvious mound. Treat this as the user's region convention; do not falsely describe every added voxel as proven gland or fat.

Apply: assess the whole superior-to-inferior attachment, including the region behind the mound and below the fold. Do not end the mask at the mound's upper/lower extremum or trim inward merely because the interface is dark. Retain the case-supported attachment envelope while distinguishing it from clearly separate deep structures. On a new case, compare a relevant reviewed example with the same boundary problem; infer the curve from that case's anatomy and adjacent slices. Do not copy rounded brush lobes or add a fixed margin to every mask.

This supersedes a general reading of the older QIN lesson as 'posterior boundaries should move anteriorly.' Removals still occur: ISPY1_1128 k30 has a posterior strip trimmed; ISPY1_1185 k39 has a local posterior bulge removed. The correct rule is case-specific extent, with both under-inclusion and leakage checked. Several NACT central breast contours were largely retained. A straight edge is a warning cue, not automatically wrong.

## Coverage is a separate decision from contour shape

Observed: 162 previously nonempty slices were completely cleared in 28 cases. Many visibly contain peripheral tissue or artifact; do not claim they are all anatomically empty. Examples: ISPY1_1066 k5-8/55/56/58/59; 1164 k8-14; 1176 k0-7/42-48; 1179 k6-9/33-37; 1199 k43-50; 1236 k3-8/39/40; NACT_35 k53-58; NACT_53 k2-5/47-51. Exact lists, including nonconsecutive deletions, are in the comparison ledger. ISPY1_1049 k56 was instead added, so there is no universal endpoint deletion rule.

Apply: preserve the reviewed empty slices exactly in these cases. For new cases, inspect the onset/offset of the intended breast region with adjacent slices and distinguish substantial target anatomy from marginal tissue and artifact. Do not manufacture an explicit polygon on a barely supported slice merely to keep a nonempty sequence. Nor should artifact alone erase an otherwise supported central region. If the user's inclusion convention remains unclear, record that specific coverage uncertainty and request a hint while progressing elsewhere. Never infer that all visible tissue must be labeled, or skip a fixed number of slices.

## Nipple: a supported region, not a tiny seed

Observed: 29 nipple masks changed. All seven previously empty masks now have user-defined locations: ISPY1_1058, 1066, 1074, 1176, 1185, 1207, 1222. ISPY1_1124 remains exactly unchanged. All 22 changed masks that were already nonempty became larger; median voxel-volume ratio was 5.66. Examples: ISPY1_1056 287 to 1,882; 1199 671 to 3,493; 1236 1,355 to 12,202; NACT_25 325 to 2,941. These are evidence that the provisional markers were usually too small, not instructions to multiply future volumes by a constant. Some corrected spans shortened, so enlargement does not mean automatic extension in K.

ISPY1_1072 was relocated superiorly and across slices: all 287 old nipple voxels were removed, with 816 at the reviewed location. NACT_53 was moved inferiorly (269 of 287 old voxels removed; 792 reviewed). Focused same-slice comparisons confirm opposite directions. Therefore neither a superior shift nor the most anterior point is a universal locator. ISPY1_1183 also has a local positional adjustment, not just symmetric expansion.

Apply: identify the local surface feature and tissue convergence across adjacent slices, compare alternative candidates, and inspect a closeup. Cover the supported nipple projection and a generous local neighborhood rather than placing a tiny point in it. Use physical dimensions and this case's image spacing; the old fixed 3-voxel sagittal radius and 4-6-pixel in-plane ellipsoid were often inadequate. Do not clip the marker to the breast mask: reviewed markers can extend outside or overlap it. Preserve exact user geometry/overlap; use nipple priority only for a derived scalar export. Preserve new user nipple references during breast-only revisions.

## Quality gate that changes generation behavior

The previous all-slice viewing and geometry checks did not prevent systematic contour errors. Make review corrective:

- Inspect source-only and outline views around the full skin envelope and attachment, not only a filled green montage. Use closeups where the montage hides detail.
- Treat rectangular notches, thin detached strips, abrupt steps and flat caps as possible algorithm artifacts. Intensity clipping can remove low-signal fat; simply disabling it can fill background. Correct the actual boundary and recheck neighbors instead of accepting either failure.
- Use case-specific contour anchors as an initialization. Do not treat interpolated polygons or a single posterior x(y) curve as sufficient where a fold, oblique attachment or changing topology requires a full contour.
- Check coverage, posterior/upper/lower extent and nipple position/size independently. A connected mask or correct affine does not establish any of them.
- A recorded uncertainty does not excuse a visibly correctable defect. Fix known defects; reserve flags for uncertainty that remains after inspection. Keep agent review, user review and export verification separate.

Learning means updating these workflow rules and retaining the user's references, not model training. Do not silently rewrite existing reviewed masks or propagate their labels to other patients.
