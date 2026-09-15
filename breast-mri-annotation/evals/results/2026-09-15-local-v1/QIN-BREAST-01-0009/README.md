# QIN-BREAST-01-0009: human vs Astra

Fresh source-only prediction; human mask opened after prediction freeze.

| Metric | Full reference | Common field of view |
|---|---:|---:|
| breast_exclusive Dice | 0.7619 | 0.7619 |
| nipple Dice | 0.6087 | 0.6087 |
| breast_nipple_union Dice | 0.7641 | 0.7641 |
| Nipple centroid distance (original RAS mm) | 4.64 | See geometry notes |

## Differences

- Breast: Astra 1038.31 mL; human 1142.30 mL; signed volume bias -103.99 mL.
- Union: 35,113 human-labelled voxels missed; 23,084 Astra-only voxels. These are comparison differences, not automatic proof of anatomical error.
- Nipple: Astra 525 voxels vs human 855; status both_present.
- Nipple centroid Astra: [127.5, 103.32953201498304, 4.666665554046631]; human: [124.90350877192982, 104.44757159160591, 8.340739737616644]; delta Astra minus human: [2.596491228070178, -1.1180395766228628, -3.6740741835700135] mm.
- Largest union disagreements on reference slices: 18, 15, 16.
- Breast boundary HD95: 30.34 mm; average symmetric surface distance: 6.43 mm.

## Geometry and review

- Source (192, 192, 20); reference (192, 192, 20); encoding scalar.
- Human foreground outside source coverage: 0 voxels. Prediction foreground outside reference: 0.
- Actual Slicer slices reviewed: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]. Status: reviewed_frozen. Agent review is not user approval.
- Raw overlap is compared only when the human file preserves separate breast and nipple components. Scalar labels cannot recover that overlap.

## Source-only annotation notes

- Peripheral slices 0-1 are poorly supported and excluded. Local anterior projection around k7-9 selected; upper separate bulge is not used as nipple.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.


## Visual observations

- Human labels include native k1, which Astra left empty. At k8 and k19 the inferior attachment and posterior boundary differ; Astra extends lower, while the human superior/anterior contour is broader in places.
- The nipple neighborhoods substantially overlap; their remaining difference includes extent and a small centroid offset.

Images and masks remain in local storage. Full numeric data: [metrics.json](metrics.json).
