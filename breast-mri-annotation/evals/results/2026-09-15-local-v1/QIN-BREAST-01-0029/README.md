# QIN-BREAST-01-0029: human vs Astra

Fresh source-only prediction; human mask opened after prediction freeze.

| Metric | Full reference | Common field of view |
|---|---:|---:|
| breast_exclusive Dice | 0.8839 | 0.8839 |
| nipple Dice | 0.4401 | 0.4401 |
| breast_nipple_union Dice | 0.8860 | 0.8860 |
| Nipple centroid distance (original RAS mm) | 8.47 | See geometry notes |

## Differences

- Breast: Astra 1668.93 mL; human 1610.68 mL; signed volume bias +58.25 mL.
- Union: 18,249 human-labelled voxels missed; 24,025 Astra-only voxels. These are comparison differences, not automatic proof of anatomical error.
- Nipple: Astra 525 voxels vs human 1,302; status both_present.
- Nipple centroid Astra: [67.5, 126.97142734868186, -6.333337664604187]; human: [68.55990783410138, 122.41986551308597, 0.7275944454695491]; delta Astra minus human: [-1.0599078341013808, 4.551561835595891, -7.060932110073736] mm.
- Largest union disagreements on reference slices: 15, 10, 19.
- Breast boundary HD95: 13.00 mm; average symmetric surface distance: 2.82 mm.

## Geometry and review

- Source (192, 192, 20); reference (192, 192, 20); encoding components.
- Human foreground outside source coverage: 0 voxels. Prediction foreground outside reference: 0.
- Actual Slicer slices reviewed: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]. Status: reviewed_frozen. Agent review is not user approval.
- Raw overlap is compared only when the human file preserves separate breast and nipple components. Scalar labels cannot recover that overlap.

## Source-only annotation notes

- Nipple projection strongest around k13-15; central duct convergence helps separate it from the broad breast apex.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.


## Visual observations

- Breast overlap is the highest among the new cases. Residual differences concentrate at superior/inferior attachments and the posterior boundary; small holes in the human mask are retained in the comparison.
- Astra's nipple centroid is 7.06 mm inferior to the human centroid. Their marker extents also differ.

Images and masks remain in local storage. Full numeric data: [metrics.json](metrics.json).
