# QIN-BREAST-01-0007: human vs Astra

Fresh source-only prediction; human mask opened after prediction freeze.

| Metric | Full reference | Common field of view |
|---|---:|---:|
| breast_exclusive Dice | 0.7001 | 0.7001 |
| nipple Dice | 0.0249 | 0.0249 |
| breast_nipple_union Dice | 0.7165 | 0.7165 |
| Nipple centroid distance (original RAS mm) | 27.63 | See geometry notes |

## Differences

- Breast: Astra 387.62 mL; human 319.40 mL; signed volume bias +68.22 mL.
- Union: 7,961 human-labelled voxels missed; 14,978 Astra-only voxels. These are comparison differences, not automatic proof of anatomical error.
- Nipple: Astra 355 voxels vs human 1,013; status both_present.
- Nipple centroid Astra: [94.90218353271484, 33.14725579812493, 5.999998927116394]; human: [75.17365441129333, 46.83169836400174, -7.674236426113396]; delta Astra minus human: [19.728529121421516, -13.684442565876807, 13.67423535322979] mm.
- Largest union disagreements on reference slices: 3, 4, 5.
- Breast boundary HD95: 20.70 mm; average symmetric surface distance: 4.57 mm.

## Geometry and review

- Source (192, 192, 20); reference (192, 192, 20); encoding scalar.
- Human foreground outside source coverage: 0 voxels. Prediction foreground outside reference: 0.
- Actual Slicer slices reviewed: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]. Status: reviewed_frozen. Agent review is not user approval.
- Raw overlap is compared only when the human file preserves separate breast and nipple components. Scalar labels cannot recover that overlap.

## Source-only annotation notes

- Small breast. Exclude chest-only peripheral slices 0-1 and 17-19. Nipple candidate is the focal projection at k5-7; moderate confidence.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.


## Visual observations

- Largest nipple localization discrepancy. Astra marks native slices 4-8, while the human nipple region lies mainly on later slices. The human nipple region is one connected component; this is a localization disagreement, not a disconnected-reference effect.
- At native k16, Astra extends farther posteriorly and superiorly than the human breast contour, while missing part of the anterior skin band. Empty peripheral slices agree.

Images and masks remain in local storage. Full numeric data: [metrics.json](metrics.json).
