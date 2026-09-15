# Breast MRI annotation: skill and evaluation history

An agent-guided workflow for breast-region segmentation and nipple localization in sagittal MRI. This project keeps the instructions and evaluation code together so changes can be judged against measured human-label agreement and execution cost.

## Dataset and evaluation cohort

**The 10 cases annotated from scratch by a human in [Breast MRI sagittal landmarks on Hugging Face](https://huggingface.co/datasets/h2thez3/breast-mri-sagitall-landmarks#breast-mri-sagittal-landmarks) are the cases used to evaluate this skill.** Select `annotation_source=user` in the dataset metadata, rather than the 25 agent-assisted cases.

The exact cohort is `QIN-BREAST-01-0003`, `0007`, `0009`, `0013`, `0014`, `0019`, `0022`, `0023`, `0029`, and `0030` (each shares the `QIN-BREAST-01-` prefix). Case 0031 is an additional development example, excluded from the main benchmark. The earlier “10 new cases” continuation included 0031 and excluded pilot 0003; that is a different grouping.

The first baseline below was computed against the original local reference exports before Hugging Face split-label packaging. File hashes and full/common-field-of-view results are retained. It is not presented as a fresh evaluation of the current packaged skill or a byte-identical copy of the current online labels.

## Project layout

```text
breast-mri-annotation/
├── README.md                 # benchmark history and interpretation
├── skill/                    # install this folder as breast-mri-annotation
│   ├── SKILL.md
│   ├── README.md             # installation and usage
│   ├── references/
│   └── scripts/
└── evals/
    ├── README.md             # evaluation and versioning protocol
    ├── run_eval.py           # public split-label dataset scorer
    ├── evaluate.py           # strict geometry-aware metric primitives
    ├── batch_metrics.py      # reports and aggregate metrics
    ├── history.py            # append history and render this table
    ├── history.json          # append-only evaluated/pending entries
    ├── results/              # public numerical results and text reports
    └── archive/              # historical annotation helpers and decisions
```

[Install and use the skill](skill/README.md) · [Run evaluations](evals/README.md) · [Baseline metrics and per-case reports](evals/results/2026-09-15-local-v1/README.md)

## Evaluation history

Scores are unweighted means over the ten human cases. Breast Dice excludes nipple in both label encodings; union Dice includes both. Higher Dice and lower centroid distance are better. This table shows measured evaluations only. Infrastructure changes and pending evaluations remain in [the change history](evals/history.json).

<!-- evaluation-history:start -->

| Date / run | Change | Status | n | Breast Dice ↑ | Union Dice ↑ | Nipple Dice ↑ | Nipple distance mm ↓ |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| [2026-09-15-local-v1](evals/results/2026-09-15-local-v1/README.md) | Original local-reference baseline; human-user-10 cohort | evaluated historical | 10 | 0.8214 | 0.8249 | 0.4062 | 11.69 |

<!-- evaluation-history:end -->

### Reading the baseline

- The main cohort includes the previously evaluated pilot 0003; it was already visible before the continuation. The set is not certified independent of all skill development history.
- Case 0013 contains a disconnected 316-voxel human nipple component. Primary scores retain it: centroid distance is 24.87 mm. Largest-component-only sensitivity is 4.86 mm, reported separately rather than replacing ground truth.
- Pilot 0003 has 9,733 human-labelled voxels beyond the local source coverage. Full-reference scores penalize these; common-coverage scores are also available.
- The continuation consumed **7,362,686 recorded tokens**: 6,956,416 cached input, 361,073 uncached input and 45,197 output. This covers its annotation, corrections, review and reporting, includes development case 0031, and excludes the prior pilot work and calls after the saved checkpoint. It is not an exact cost for the human-ten cohort. Per-case token attribution and dollar cost are unavailable.
- This is evidence of agreement with one annotation convention on a small dataset. A baseline alone does not establish clinical validity, market superiority, or the causal benefit of a particular instruction change. Comparable repeated runs are needed to measure improvements and variability.

## Keeping changes measurable

Commit skill and eval code/text changes in Git. For each changed version, append a history entry describing the change and its measured result, or explicitly mark it pending. GitHub Actions tests the metrics and rejects a stale README table or missing entry for the current skill/evals fingerprints. CI does not perform agent annotation or fabricate results.

Before reporting an improvement, use the same case list, reference hashes, model/effort and review protocol. Freeze new predictions before opening the human masks. If references or the scorer change, re-score the old predictions as well and identify the new baseline; do not attribute a scoring change to the skill. Follow [the evaluation protocol](evals/README.md).

## Attribution

Dataset: [h2thez3/breast-mri-sagitall-landmarks](https://huggingface.co/datasets/h2thez3/breast-mri-sagitall-landmarks#breast-mri-sagittal-landmarks), derived from TCIA QIN-BREAST. The dataset card describes the original collection and CC BY 3.0 attribution requirements. Cite Li et al. (2016), *Data From QIN-BREAST (Version 2)*, [doi:10.7937/K9/TCIA.2016.21JUEBH0](https://doi.org/10.7937/K9/TCIA.2016.21JUEBH0) when using its data.

MRI volumes, labelmaps, screenshots and local environment files stay outside this Git repository; numerical results, methodology, instructions and code are versioned here.
