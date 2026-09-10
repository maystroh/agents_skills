# Lessons from reviewed corrections

Read this before generating or reviewing annotations. This portable reference captures workflow lessons from manual corrections. It contains no case-level audit records or patient examples. These are annotation heuristics, not a trained model or a guarantee of accuracy on new patients. Use current anatomy and the user's project-specific corrected references; never transfer pixel coordinates, slice indices, target volumes or numerical trim widths between patients.

## Posterior boundary

Posterior strips and superior-posterior wedges are common places for a draft to include too much tissue. Trace the breast/chest-wall interface separately from the outer skin. Where visible, follow the anterior surface of the pectoral/chest-wall structure and exclude deeper tissue. Check the superior-posterior wedge and the inferior fold-to-chest transition explicitly. A long straight posterior closure is acceptable only where it follows the visible interface; a convenient polygon edge is not anatomical evidence. Similar intensity in deep chest structures is not a reason to include them.

Track the interface across adjacent slices when subtle, and record uncertainty instead of inventing a fixed inward offset. A retained posterior boundary in a single corrected example does not validate that boundary strategy for other cases. These checks do not imply that every posterior border should move or that every mask should be eroded.

## Outer contour

Both additions and removals may be necessary. Fit the visible continuous tissue/skin envelope. Remove jagged spikes, external islands and ghosted rims outside it, but restore real fatty/glandular tissue omitted by thresholding, including weak-signal tissue. Check superior/inferior transitions and folds explicitly.

Inspect source-only and outline views with useful contrast in low-signal and end slices. A connected sawtooth edge is not necessarily valid, and a threshold-excluded band is not necessarily background. Smoothness is a review cue, not permission to erase folds or apply blanket erosion/dilation. Inspect dark gaps before retaining or filling them; judge anatomical continuity rather than intensity alone.

## Slice coverage and empty references

Preserve deliberately empty user-corrected slices when continuing a case. A cleared slice may still visibly contain tissue, and neighboring terminal slices may be retained; saved masks alone do not establish the reason or a universal exclusion policy.

For new cases, assess first/last included slices and their neighbors explicitly. Distinguish target breast from chest-only tissue and uncertain marginal coverage. Do not propagate through an intentionally empty corrected slice or refill it merely to improve continuity. Do not infer a fixed number of skipped slices, a minimum volume or automatic removal of every terminal slice. Ask about a coverage convention only when unresolved ambiguity affects the current task.

## Nipple position and extent

Identify the actual local nipple feature across neighboring slices. The most anterior voxel, breast apex, midpoint of breast height and central slice are not reliable substitutes. Use a closeup and adjacent slices to examine a subtle surface projection or localized tissue convergence. Consider multiple plausible sites when needed, including a more superior candidate rather than assuming the most protruding inferior point is the nipple. This is a search cue, not an instruction to move every marker upward.

Keep a compact, generous marker around the supported location and extend it only onto supported neighboring slices. Both enlargement and trimming may be appropriate. Preserve the user's corrected nipple exactly during breast-only changes, including segment overlap. A corrected location supersedes an earlier provisional marker for the matching case.

## Review decisions and comparison mechanics

Before accepting a generated case, assess posterior depth, outer envelope, superior/inferior transitions, coverage endpoints and nipple position separately. Use actual source/overlay views rather than only the impression of a filled mask. Correct affected slices and recheck their neighbors. Geometry and connected-component checks cannot certify anatomical choices. Keep the requested every-slice Slicer review.

For saved corrections, resolve the reviewed filename from the explicit source/export mapping. A row containing both an acceptance label and an edit flag does not prove unchanged voxels; compare arrays against the matching baseline. Verify source identity, physical geometry and scalar versus multicomponent encoding. Some exports use scalar labels while others preserve overlapping binary segment channels. Establish the segment mapping before comparison; do not treat a channel axis as a spatial/time axis or assume its order across unrelated files.

Preserve original multicomponent references and overlap. Apply nipple priority only in a derived scalar comparison/export. Distinguish segment deletion from relabeling: breast-to-nipple changes do not remove tissue from their union. Store per-slice additions/removals, exact pairings, hashes and inspected before/after/difference evidence in the project, separately from portable skill instructions. Keep observations distinct from inferred rules and do not claim review of unseen slices.

Slicer may normalize handedness and reverse K relative to the original NIfTI despite identical array shapes. Map via physical geometry and record the slice-order convention. Compare geometry and voxels after reloading. Copying an array into a source header without this check can mirror corrections.
