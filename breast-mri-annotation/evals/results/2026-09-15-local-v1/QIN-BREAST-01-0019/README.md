# QIN-BREAST-01-0019: human vs Astra

Fresh source-only prediction; human mask opened after prediction freeze.

| Metric | Full reference | Common field of view |
|---|---:|---:|
| breast_exclusive Dice | 0.8742 | 0.8742 |
| nipple Dice | 0.6200 | 0.6200 |
| breast_nipple_union Dice | 0.8758 | 0.8758 |
| Nipple centroid distance (original RAS mm) | 3.92 | See geometry notes |

## Differences

- Breast: Astra 1419.52 mL; human 1426.24 mL; signed volume bias -6.72 mL.
- Union: 20,519 human-labelled voxels missed; 19,416 Astra-only voxels. These are comparison differences, not automatic proof of anatomical error.
- Nipple: Astra 541 voxels vs human 888; status both_present.
- Nipple centroid Astra: [-85.87307739257812, 95.22797334502673, 1.8315385580062866]; human: [-87.9451494646502, 92.42661275130672, 0.04024721333036041]; delta Astra minus human: [2.072072072072075, 2.8013605937200055, 1.7912913446759262] mm.
- Largest union disagreements on reference slices: 4, 3, 0.
- Breast boundary HD95: 14.24 mm; average symmetric surface distance: 3.00 mm.

## Geometry and review

- Source (192, 192, 20); reference (192, 192, 20); encoding components.
- Human foreground outside source coverage: 0 voxels. Prediction foreground outside reference: 0.
- Actual Slicer slices reviewed: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]. Status: reviewed_frozen. Agent review is not user approval.
- Raw overlap is compared only when the human file preserves separate breast and nipple components. Scalar labels cannot recover that overlap.

## Source-only annotation notes

- Distinct anterior projection at k8-12 with converging tissue. Retain curved inferior attachment while excluding deeper chest.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.


## Visual observations

- Outer breast contours agree more closely than the attachment boundaries. At k15 Astra misses some superior and posterior human-labelled tissue; endpoint differences appear at k0 and k19.
- Nipple neighborhoods overlap substantially. Similar total breast volumes conceal local added and missed regions, so volume bias alone is insufficient.

Images and masks remain in local storage. Full numeric data: [metrics.json](metrics.json).
