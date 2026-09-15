# QIN-BREAST-01-0023: human vs Astra

Fresh source-only prediction; human mask opened after prediction freeze.

| Metric | Full reference | Common field of view |
|---|---:|---:|
| breast_exclusive Dice | 0.8266 | 0.8266 |
| nipple Dice | 0.3419 | 0.3419 |
| breast_nipple_union Dice | 0.8288 | 0.8288 |
| Nipple centroid distance (original RAS mm) | 10.93 | See geometry notes |

## Differences

- Breast: Astra 1282.95 mL; human 1142.77 mL; signed volume bias +140.18 mL.
- Union: 16,063 human-labelled voxels missed; 30,956 Astra-only voxels. These are comparison differences, not automatic proof of anatomical error.
- Nipple: Astra 401 voxels vs human 1,278; status both_present.
- Nipple centroid Astra: [-97.5, 93.00250231892687, 12.666672825813293]; human: [-100.55555555555556, 87.79343562814552, 21.779870802154747]; delta Astra minus human: [3.055555555555557, 5.209066690781356, -9.113197976341453] mm.
- Largest union disagreements on reference slices: 1, 0, 19.
- Breast boundary HD95: 22.82 mm; average symmetric surface distance: 4.08 mm.

## Geometry and review

- Source (192, 192, 20); reference (192, 192, 20); encoding scalar.
- Human foreground outside source coverage: 0 voxels. Prediction foreground outside reference: 0.
- Actual Slicer slices reviewed: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]. Status: reviewed_frozen. Agent review is not user approval.
- Raw overlap is compared only when the human file preserves separate breast and nipple components. Scalar labels cannot recover that overlap.

## Source-only annotation notes

- Subtle local projection at k12-14. Internal dark region near inferior attachment retained within region outline; not thresholded out.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.


## Visual observations

- Astra includes substantially more posterior/inferior attachment tissue at the peripheral slices, especially k18-19, while the human superior slope extends farther anteriorly in places.
- Astra's nipple centroid is 9.11 mm inferior to the human centroid, and the local neighborhoods overlap only partially.

Images and masks remain in local storage. Full numeric data: [metrics.json](metrics.json).
