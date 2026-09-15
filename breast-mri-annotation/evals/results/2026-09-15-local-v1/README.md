# QIN human-ten: historical baseline

[Dataset: Breast MRI sagittal landmarks](https://huggingface.co/datasets/h2thez3/breast-mri-sagitall-landmarks#breast-mri-sagittal-landmarks)

Original local references, before public split-label packaging. Model: gpt-6-astra, medium effort. This cohort includes pilot 0003 and excludes development example 0031.

| Case | Breast Dice | Union Dice | Nipple Dice | Nipple distance mm |
| --- | ---: | ---: | ---: | ---: |
| [QIN-BREAST-01-0003](QIN-BREAST-01-0003/README.md) | 0.7696 | 0.7739 | 0.1502 | 13.52 |
| [QIN-BREAST-01-0007](QIN-BREAST-01-0007/README.md) | 0.7001 | 0.7165 | 0.0249 | 27.63 |
| [QIN-BREAST-01-0009](QIN-BREAST-01-0009/README.md) | 0.7619 | 0.7641 | 0.6087 | 4.64 |
| [QIN-BREAST-01-0013](QIN-BREAST-01-0013/README.md) | 0.7794 | 0.7803 | 0.3984 | 24.87 |
| [QIN-BREAST-01-0014](QIN-BREAST-01-0014/README.md) | 0.8772 | 0.8795 | 0.3475 | 10.80 |
| [QIN-BREAST-01-0019](QIN-BREAST-01-0019/README.md) | 0.8742 | 0.8758 | 0.6200 | 3.92 |
| [QIN-BREAST-01-0022](QIN-BREAST-01-0022/README.md) | 0.8709 | 0.8721 | 0.6870 | 3.41 |
| [QIN-BREAST-01-0023](QIN-BREAST-01-0023/README.md) | 0.8266 | 0.8288 | 0.3419 | 10.93 |
| [QIN-BREAST-01-0029](QIN-BREAST-01-0029/README.md) | 0.8839 | 0.8860 | 0.4401 | 8.47 |
| [QIN-BREAST-01-0030](QIN-BREAST-01-0030/README.md) | 0.8707 | 0.8717 | 0.4438 | 8.72 |

Mean breast Dice: 0.8214. Mean nipple Dice: 0.4062. Mean centroid distance: 11.69 mm.

[Complete metrics and provenance](metrics.json). Reference and source hashes identify the historical files. Original machine-specific locations are redacted.

The archive preserves the evaluated instructions with local paths replaced by placeholders; original pre-redaction hashes remain in metrics.json. Packaged instruction hashes differ. No inference or scoring run against the current packaged instructions is implied.

Case 0013 retains its disconnected nipple-reference component. Pilot 0003 has an extra reference slice; see common-FOV metrics. The continuation token record includes development case 0031 and excludes prior pilot cost, so is not a cohort-specific token measurement.
