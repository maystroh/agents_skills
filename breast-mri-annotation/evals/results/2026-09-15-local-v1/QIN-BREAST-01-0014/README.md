# QIN-BREAST-01-0014: human vs Astra

Fresh source-only prediction; human mask opened after prediction freeze.

| Metric | Full reference | Common field of view |
|---|---:|---:|
| breast_exclusive Dice | 0.8772 | 0.8772 |
| nipple Dice | 0.3475 | 0.3475 |
| breast_nipple_union Dice | 0.8795 | 0.8795 |
| Nipple centroid distance (original RAS mm) | 10.80 | See geometry notes |

## Differences

- Breast: Astra 1603.08 mL; human 1778.34 mL; signed volume bias -175.26 mL.
- Union: 33,295 human-labelled voxels missed; 12,778 Astra-only voxels. These are comparison differences, not automatic proof of anatomical error.
- Nipple: Astra 587 voxels vs human 1,387; status both_present.
- Nipple centroid Astra: [-77.1488265991211, 146.26661982162645, -8.055739402770996]; human: [-77.47687274187524, 144.2254415778866, 2.5494039077593698]; delta Astra minus human: [0.3280461427541468, 2.041178243739836, -10.605143310530366] mm.
- Largest union disagreements on reference slices: 13, 15, 10.
- Breast boundary HD95: 11.93 mm; average symmetric surface distance: 2.99 mm.

## Geometry and review

- Source (192, 192, 20); reference (192, 192, 20); encoding scalar.
- Human foreground outside source coverage: 0 voxels. Prediction foreground outside reference: 0.
- Actual Slicer slices reviewed: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]. Status: reviewed_frozen_low_confidence_nipple. Agent review is not user approval.
- Raw overlap is compared only when the human file preserves separate breast and nipple components. Scalar labels cannot recover that overlap.

## Source-only annotation notes

- Large smooth anterior surface; nipple candidate based on localized tissue convergence has low confidence. Breast and posterior attachment remain separately assessed.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.


## Visual observations

- Astra generally sits inside the human anterior skin envelope, including the superior and inferior slopes. Superior and inferior attachment endpoints also differ.
- Astra's nipple centroid is 10.61 mm inferior to the human centroid. Its location was flagged as low confidence before the reference was opened.

Images and masks remain in local storage. Full numeric data: [metrics.json](metrics.json).
