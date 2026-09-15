# QIN-BREAST-01-0030: human vs Astra

Fresh source-only prediction; human mask opened after prediction freeze.

| Metric | Full reference | Common field of view |
|---|---:|---:|
| breast_exclusive Dice | 0.8707 | 0.8707 |
| nipple Dice | 0.4438 | 0.4438 |
| breast_nipple_union Dice | 0.8717 | 0.8717 |
| Nipple centroid distance (original RAS mm) | 8.72 | See geometry notes |

## Differences

- Breast: Astra 1683.24 mL; human 1519.80 mL; signed volume bias +163.43 mL.
- Union: 14,178 human-labelled voxels missed; 32,226 Astra-only voxels. These are comparison differences, not automatic proof of anatomical error.
- Nipple: Astra 525 voxels vs human 863; status both_present.
- Nipple centroid Astra: [-92.5, 119.79491934730893, 11.666662573814392]; human: [-84.13383545770569, 122.10235490321008, 10.830818593709239]; delta Astra minus human: [-8.366164542294314, -2.307435555901151, 0.8358439801051532] mm.
- Largest union disagreements on reference slices: 0, 1, 2.
- Breast boundary HD95: 18.41 mm; average symmetric surface distance: 3.41 mm.

## Geometry and review

- Source (192, 192, 20); reference (192, 192, 20); encoding components.
- Human foreground outside source coverage: 0 voxels. Prediction foreground outside reference: 0.
- Actual Slicer slices reviewed: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]. Status: reviewed_frozen. Agent review is not user approval.
- Raw overlap is compared only when the human file preserves separate breast and nipple components. Scalar labels cannot recover that overlap.

## Source-only annotation notes

- Anterior focal nipple at k9-11. Dark inferior intrabreast area retained; posterior boundary assessed separately from its intensity.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.


## Visual observations

- Astra extends farther posteriorly and inferiorly than the human breast contour, especially on peripheral slices k0 and k19.
- The nipple centers overlap well within the displayed k10 plane, but their 3D centroids differ mainly along the left-right/slice direction (8.37 mm), showing why a single slice is insufficient.

Images and masks remain in local storage. Full numeric data: [metrics.json](metrics.json).
