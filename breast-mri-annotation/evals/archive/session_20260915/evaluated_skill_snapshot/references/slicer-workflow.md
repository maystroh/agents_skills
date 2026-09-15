# Slicer connection and review

Use the installed `slicer` skill to find the server implementation and APIs. The known session used an MCP handler at `http://127.0.0.1:2026/mcp`, started inside Slicer. Discover/verify endpoint and process; do not assume this port, node IDs, version or session still exist.

The local bootstrap from the worked example is `<LOCAL_WORKSPACE>\connect_slicer.py`; inspect before reuse. It uses the installed skill's MCP handler with a loopback-only WebServer. The upstream server requires first-connection consent. Keep access local; do not expose an unauthenticated Python execution endpoint to the network. Follow tool policy for permission dialogs. A request timing out can mean the consent dialog is pending; inspect before retrying. Do not blindly replay a mutation after timeout—read state first.

For a running user session, preserve loaded data and unsaved edits. For folder batches, a separate review instance is preferable. Starting a separate instance does not connect to or recover unsaved content in the existing one. Do not clear an existing scene to load the next case. Remove only temporary nodes created by this workflow after saving and checking dependencies.

The user's setup script:
`<PROJECT_SETUP_SCRIPT>`

It discovers the visible editor, sets segment names/colors/order and source geometry, and binds `1` breast, `2` nipple, `3` fill/outline, `p` paint, `e` erase, `[`/`]` brush size, `r` reapply. Read it when needed; do not execute unexamined scripts or assume its visible-editor fallback selects the desired draft. Overall segmentation visibility needs a separate check.

## Geometry and export

Slicer array access uses KJI order; Slicer physical coordinates are RAS, while SimpleITK uses LPS. Never equate K with sagittal without inspecting directions. For untransformed source volume nodes, convert IJK-to-RAS to IJK-to-LPS with diag(-1,-1,1,1); derive origin, spacing and direction from that matrix. Account for parent transforms explicitly if present.

Prefer exporting arrays against the original source file geometry using the helper's `export_mask`. If the source has a nontrivial affine shear unsupported by SimpleITK, resolve this explicitly rather than silently orthogonalizing. Confirm NIfTI affine/header roundtrip using an appropriate library. For Slicer nodes modified/resampled relative to the source, map the mask to the original grid first.

Use `slicer.util.arrayFromSegmentBinaryLabelmap(segmentation, segmentID, sourceVolume)` and `updateSegmentBinaryLabelmapFromArray` with the same source node. Use independent copies for before snapshots. Segment arrays can overlap; NIfTI labels cannot, so label 2 takes precedence. Preserve the original segmentation instead of modifying it to resolve export overlap.

Visual review must inspect actual slice images and contours. Use Slicer MCP screenshots or supported computer-use tools. Programmatically selecting slice offsets is fine; inspect returned images before marking slices reviewed. Store case-specific review indices and findings. Automated pixel comparisons, connected-component counts, export success and screenshots that were never inspected are not visual review.
