# QIN-BREAST-01-0003: human vs Astra

Fresh source-only prediction; human mask opened after prediction freeze.

| Metric | Full reference | Common field of view |
|---|---:|---:|
| breast_exclusive Dice | 0.7696 | 0.7896 |
| nipple Dice | 0.1502 | 0.1502 |
| breast_nipple_union Dice | 0.7739 | 0.7940 |
| Nipple centroid distance (original RAS mm) | 13.52 | See geometry notes |

## Differences

- Breast: Astra 1326.20 mL; human 2081.82 mL; signed volume bias -755.63 mL.
- Union: 87,150 human-labelled voxels missed; 82 Astra-only voxels. These are comparison differences, not automatic proof of anatomical error.
- Nipple: Astra 195 voxels vs human 2,255; status both_present.
- Nipple centroid Astra: [89.4852104485035, 145.9170160293579, -43.333335876464844]; human: [83.36509664186882, 142.08538222982983, -31.905101980814123]; delta Astra minus human: [6.120113806634677, 3.8316337995280776, -11.42823389565072] mm.
- Largest union disagreements on reference slices: 20, 19, 18.
- Breast boundary HD95: 53.75 mm; average symmetric surface distance: 8.65 mm.

## Geometry and review

- Source (192, 192, 20); reference (192, 192, 21); encoding scalar.
- Human foreground outside source coverage: 9,733 voxels. Prediction foreground outside reference: 0.
- Actual Slicer slices reviewed: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]. Status: agent_reviewed_pilot_with_uncertainty. Agent review is not user approval.
- Raw overlap is compared only when the human file preserves separate breast and nipple components. Scalar labels cannot recover that overlap.

## Source-only annotation notes

- All 20 original sagittal slices inspected in actual Slicer source and overlay captures, plus native closeup at k10.
- Source-only nipple candidate and posterior boundary were retained for unbiased scoring; no reference-driven prediction changes.
- Reference has one extra annotated slice beyond MRI coverage. Report full-reference and common-field-of-view metrics separately.
- Pilot uses five hand-drawn contour anchors with interpolation. Nipple marker is smaller than the reference; this is a skill execution weakness, not proof of instruction quality alone.


## Visual observations

- Original pilot retained. The reference has an extra annotated slice outside the source MRI; full-reference and common-field-of-view scores are both reported. This case was already visible before the new batch.

Images and masks remain in local storage. Full numeric data: [metrics.json](metrics.json).
