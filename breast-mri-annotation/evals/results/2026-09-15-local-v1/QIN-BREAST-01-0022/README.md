# QIN-BREAST-01-0022: human vs Astra

Fresh source-only prediction; human mask opened after prediction freeze.

| Metric | Full reference | Common field of view |
|---|---:|---:|
| breast_exclusive Dice | 0.8709 | 0.8709 |
| nipple Dice | 0.6870 | 0.6870 |
| breast_nipple_union Dice | 0.8721 | 0.8721 |
| Nipple centroid distance (original RAS mm) | 3.41 | See geometry notes |

## Differences

- Breast: Astra 1964.81 mL; human 1777.16 mL; signed volume bias +187.65 mL.
- Union: 16,618 human-labelled voxels missed; 37,430 Astra-only voxels. These are comparison differences, not automatic proof of anatomical error.
- Nipple: Astra 587 voxels vs human 886; status both_present.
- Nipple centroid Astra: [105.91964721679688, 144.79926960655126, -12.835128545761108]; human: [103.04718672018288, 144.12285061143592, -11.124067546686263]; delta Astra minus human: [2.8724604966139964, 0.6764189951153412, -1.7110609990748458] mm.
- Largest union disagreements on reference slices: 17, 1, 14.
- Breast boundary HD95: 17.03 mm; average symmetric surface distance: 3.70 mm.

## Geometry and review

- Source (192, 192, 20); reference (192, 192, 20); encoding components.
- Human foreground outside source coverage: 0 voxels. Prediction foreground outside reference: 0.
- Actual Slicer slices reviewed: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]. Status: reviewed_frozen. Agent review is not user approval.
- Raw overlap is compared only when the human file preserves separate breast and nipple components. Scalar labels cannot recover that overlap.

## Source-only annotation notes

- Large breast with local anterior indentation/projection around k11-13 at the converging ducts; exclude poorly supported initial 0-1.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.
- Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.


## Visual observations

- Astra includes native k2 where the human reference is empty. At k12 and k19 Astra extends farther posteriorly and inferiorly. The inferior fold remains represented by both contours.
- The nipple locations agree relatively closely; the residual mismatch includes differences in marker extent.

Images and masks remain in local storage. Full numeric data: [metrics.json](metrics.json).
