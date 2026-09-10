# Slicer connection and review

Use the installed `slicer` skill to find the server implementation and APIs. The known session used an MCP handler at `http://127.0.0.1:2026/mcp`, started inside Slicer. Discover/verify endpoint and process; do not assume this port, node IDs, version or session still exist.

Discover a supported local Slicer connection or inspect a project-provided bootstrap before reuse. Keep Python execution endpoints loopback-only and follow the server's connection-consent requirements. A timeout may mean a consent dialog is pending; inspect state before retrying. Do not blindly replay a mutation after a timeout.

For a running user session, preserve loaded data and unsaved edits. For folder batches, a separate review instance is preferable. Starting a separate instance does not connect to or recover unsaved content in the existing one. Do not clear an existing scene to load the next case. Remove only temporary nodes created by this workflow after saving and checking dependencies.

If the project provides an editor setup script, read it before use and apply it after selecting the intended source and draft. Verify its target editor, segment names/order, geometry and shortcuts. Overall segmentation visibility needs a separate check; do not assume the script's fallback selects the intended draft.

## Geometry and export

Slicer array access uses KJI order; Slicer physical coordinates are RAS, while SimpleITK uses LPS. Never equate K with sagittal without inspecting directions. For untransformed source volume nodes, convert IJK-to-RAS to IJK-to-LPS with diag(-1,-1,1,1); derive origin, spacing and direction from that matrix. Account for parent transforms explicitly if present.

Prefer exporting arrays against the original source file geometry using the helper's `export_mask`. If the source has a nontrivial affine shear unsupported by SimpleITK, resolve this explicitly rather than silently orthogonalizing. Confirm NIfTI affine/header roundtrip using an appropriate library. For Slicer nodes modified/resampled relative to the source, map the mask to the original grid first.

Use `slicer.util.arrayFromSegmentBinaryLabelmap(segmentation, segmentID, sourceVolume)` and `updateSegmentBinaryLabelmapFromArray` with the same source node. Use independent copies for before snapshots. Segment arrays can overlap; NIfTI labels cannot, so label 2 takes precedence. Preserve the original segmentation instead of modifying it to resolve export overlap.

Visual review must inspect actual slice images and contours. Use Slicer MCP screenshots or supported computer-use tools. Programmatically selecting slice offsets is fine; inspect returned images before marking slices reviewed. Store case-specific review indices and findings. Automated pixel comparisons, connected-component counts, export success and screenshots that were never inspected are not visual review.
