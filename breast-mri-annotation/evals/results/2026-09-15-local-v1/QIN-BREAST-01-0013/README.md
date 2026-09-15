# QIN-BREAST-01-0013: human vs Astra

Fresh source-only prediction; human mask opened after prediction freeze.

| Metric | Full reference | Common field of view |
|---|---:|---:|
| breast_exclusive Dice | 0.7794 | 0.7794 |
| nipple Dice | 0.3984 | 0.3984 |
| breast_nipple_union Dice | 0.7803 | 0.7803 |
| Nipple centroid distance (original RAS mm) | 24.87 | See geometry notes |

## Differences

- Breast: Astra 813.46 mL; human 717.94 mL; signed volume bias +95.52 mL.
- Union: 14,202 human-labelled voxels missed; 24,039 Astra-only voxels. These are comparison differences, not automatic proof of anatomical error.
- Nipple: Astra 429 voxels vs human 1,338; status both_present.
- Nipple centroid Astra: [82.5, 68.48446093767117, -11.66666066646576]; human: [73.53139013452915, 45.39387171498328, -13.895858540574181]; delta Astra minus human: [8.968609865470853, 23.090589222687896, 2.229197874108422] mm.
- Largest union disagreements on reference slices: 1, 2, 3.
- Breast boundary HD95: 28.30 mm; average symmetric surface distance: 5.46 mm.

## Geometry and review

- Source (192, 192, 20); reference (192, 192, 20); encoding scalar.
- Human foreground outside source coverage: 0 voxels. Prediction foreground outside reference: 0.
- Actual Slicer slices reviewed: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]. Status: reviewed_frozen. Agent review is not user approval.
- Raw overlap is compared only when the human file preserves separate breast and nipple components. Scalar labels cannot recover that overlap.

## Source-only annotation notes

- Clear local tip around k6-8. Exclude faint peripheral 0-1 and 19; inspect central posterior boundary against chest structures.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.
- Corrected visible anterior clipping on native slices 16-18 with new source-only boundary anchors.


## Visual observations

- At native k18 Astra includes substantially more posterior and inferior tissue than the human contour. Human labels include k19, which Astra left empty.
- The human nipple label contains a main anterior component of 1,022 voxels and a separate posterior component of 316 voxels, visible around native k12-15. The primary score retains both. Comparing Astra with only the largest human component gives a 4.86 mm centroid distance, versus 24.87 mm against the complete reference. This sensitivity result does not replace the ground-truth metric or change the reference.

Images and masks remain in local storage. Full numeric data: [metrics.json](metrics.json).
