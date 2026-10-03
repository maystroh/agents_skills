# GPT-6.1 Sol (sol6.1): QIN human-ten evaluation

**Run:** `2026-10-03-sol6.1-local-v1` · **Date:** 2026-10-03 · **Model:** `gpt-6.1-sol` (sol6.1) · **Status:** evaluated local

Fresh agent-guided breast and nipple annotations using the installed breast MRI annotation skill. The agent generated masks from the source images, reviewed them in 3D Slicer, corrected them from source-image evidence and froze predictions before scoring against human masks.

## Benchmark

This run uses the same **ten human-from-scratch QIN cases** defined in the [project cohort](../../../README.md#dataset-and-evaluation-cohort). **0003 remains included; 0031 is excluded** as a development example. All ten source/reference pairs were verified against the published historical baseline.

These are the original local reference exports, before online split-label packaging. This is not a fresh evaluation against the current online packaged labels.

## Aggregate scores

Unweighted case means on the full human-reference grid. Higher Dice and lower nipple distance are better.

| Metric | sol6.1 (n=10) | Historical gpt-6-astra (n=10) |
| --- | ---: | ---: |
| Breast Dice (exclusive) | 0.8214 | 0.8214 |
| Breast + nipple union Dice | 0.8237 | 0.8249 |
| Nipple Dice | 0.3436 | 0.4062 |
| Nipple centroid distance (mm) | 12.59 | 11.69 |

Breast Dice rounds to the same four-decimal value as the baseline. Union and nipple Dice are lower; mean nipple position error is about 0.90 mm higher. These are single runs with their respective recorded instruction histories; the comparison does not isolate a causal effect of the model.

[Aggregate numerical results](metrics.json) · [Historical baseline](../2026-09-15-local-v1/README.md)

## Annotation and scoring protocol

- Fresh source-only annotations using case-specific anatomical contours, independently chosen posterior boundaries and nipple neighborhoods.
- Actual Slicer source-only and outline views were inspected for all **200 sagittal slices** in the ten-case benchmark, including empty slices. Source-based corrections preceded freezing and human-reference access.
- Breast Dice excludes nipple voxels consistently across label formats. Union Dice includes both breast and nipple.
- Labels were aligned using original physical geometry and nearest-neighbor mapping. Full-reference scoring retains labels outside source coverage; nipple distance uses original physical centroids in millimetres.
- Original human references were retained in full, including the extra source-coverage slice in 0003 and the disconnected nipple component in 0013. No ground-truth component was removed to improve the score.
- Exported masks were reloaded to check original geometry and labels. Frozen predictions were not changed after scoring.

## Model, execution and provenance

- **Model:** `gpt-6.1-sol`; output/run label **sol6.1**.
- **Reasoning effort:** not recorded in the available evaluation metadata.
- **Nb tokens:** unavailable (**—**). No token total was estimated or copied from another run.
- The annotation used a snapshotted installed local skill. This result does not claim a new run of the currently packaged skill or portable online-dataset scorer.
- The repository checks metric calculations and generated history consistency. CI does not generate new MRI annotations.
- Medical comparison images, case-level detailed artifacts, raw volumes, masks, editable segmentations and full review captures remain local. This page publishes aggregate statistical results and methodology.

## Interpretation

Agent review is separate from user approval. The skill includes learned preferences from earlier QIN corrections, so this cohort is not certified independent of all development history. Repeated comparable runs are needed before attributing differences to model or instruction changes.

[Evaluation history](../../../README.md#evaluation-history) · [Dataset and attribution](https://huggingface.co/datasets/h2thez3/breast-mri-sagitall-landmarks#breast-mri-sagittal-landmarks)
