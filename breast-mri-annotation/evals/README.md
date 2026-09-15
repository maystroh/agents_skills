# Evaluating the breast MRI annotation skill

## Dataset

Use the **10 human-annotated cases** (`annotation_source=user`) from [Breast MRI sagittal landmarks](https://huggingface.co/datasets/h2thez3/breast-mri-sagitall-landmarks#breast-mri-sagittal-landmarks). The fixed case list is in `run_eval.py`. It includes pilot 0003 and excludes development example 0031.

Download the dataset separately, retaining its attribution and pinned revision. Expected local layout: `images/<case>.nii.gz`, `labels/breast_region/<case>.nii.gz`, `labels/nipples/<case>.nii.gz`. The breast file includes nipple; the nipple file is a separate binary mask. The scorer explicitly preserves both reference components and removes nipple only for the exclusive-breast metric.

## Setup and tests

Run from this directory with Python 3.12 or newer:

```bash
python -m venv .venv
# Activate .venv using your platform's activation command.
python -m pip install -r requirements.txt
python -m unittest test_metrics test_batch_metrics test_history test_run_eval -v
```

## Fresh skill evaluation

1. Pin the skill revision, dataset revision, model and reasoning effort. Record the skill fingerprint using `python -c "from history import current; print(current())"`.
2. In a fresh annotation task, supply only the ten MRI images and the skill instructions. Do not expose human masks, earlier results or the historical source-specific anchors. Ask the agent to generate new masks, inspect every sagittal slice in Slicer, correct visible defects and verify exports. This is agent-guided annotation, not a trained model inference script.
3. Freeze predictions and write `predictions.json` as a list of ten entries, one per case. Each entry has `case`, `prediction` (path relative to this manifest or absolute), `prediction_sha256`, `prediction_frozen_at` (ISO timestamp), `skill_sha256`, `model`, `reasoning_effort`, `reviewed_in_slicer: true`, `reference_blind_annotation: true`, and `slicer_reviewed_indices: [0,1,...,19]`. Set attestations only after that work actually occurred. The scorer checks these declarations and hashes; it cannot independently prove the annotation process.
4. Score the frozen outputs. Use a new output folder every time:

```bash
python run_eval.py --dataset /path/to/dataset --prediction-manifest /path/to/predictions.json --output /path/to/local-run-v2 --model gpt-6-astra --effort medium
```

5. Inspect reports. Keep the generated directory local: it contains images, masks and absolute paths. Publish only scrubbed numerical/text results in `results/<run-id>/metrics.json`, retaining `status`, `cohort`, `fingerprints`, `totals`, model, reference hashes and review provenance. Never copy MRI, labelmaps or screenshots into Git. Raw predicted breast/nipple overlap cannot be recovered from scalar NIfTI; those measurements are null, not inferred.
6. Append a measured entry and commit code, result and README together:

```bash
python history.py add --id 2026-09-16-v2 --change "Describe the tested change" --result results/2026-09-16-v2/metrics.json
python history.py check
```

For a code/text change without fresh annotation, use `python history.py add --id 2026-09-16-pending --change "Describe the untested change"`. This records **pending evaluation** with no scores. `history.py render` regenerates the README table from history. Do not edit or replace earlier entries. GitHub Actions enforces a matching current fingerprint and synchronized table; it runs mathematical tests, not costly agent annotation. No scheduled watcher is installed.

## Measurements and comparability

Dice, Jaccard, precision/recall, voxel TP/FP/FN, mL volume bias, HD95/ASSD, nipple RAS centroids and their Euclidean distance are reported per case. Full-reference and common-FOV scores are distinguished. Both-empty Dice and undefined distances are null; one-empty Dice is zero. Aggregates include explicit case counts, means, medians, spread and pooled Dice. Shape, affine and millimetre units are checked.

Measure repeated runs before attributing a difference to a prompt change. Re-score both old and new predictions whenever the evaluator or reference version changes. Do not mix the human-ten cohort with the historical ten-new-case continuation, which included 0031. A changed skill fingerprint cannot be presented as newly evaluated using an old run.

`token_usage.py` reads cumulative counters from an explicitly supplied Codex rollout. Its request marker is specific to the historical continuation; adapt it for another task. Cached input is a subset of input and reasoning output a subset of output. Reports identify the checkpoint, scope and missing per-case/dollar accounting.

## Historical artifacts

`results/2026-09-15-local-v1/` preserves the measured human-ten baseline and per-case text/numeric differences. `development-0031.json` is separate. The original local reference version predates the public split-label format; matching case IDs do not prove voxel equality. No new annotation or scoring against downloaded HF masks is claimed for the historical baseline.

`archive/session_20260915/` preserves the full evaluation session's code, text, case-specific contour decisions and evaluated instruction snapshot. Machine-specific paths are replaced with placeholders. These helpers are audit material, **not a portable predictor**: several have session-specific paths, slicing assumptions, Slicer setup or review attestations. Do not run historical freeze helpers to mark unseen images reviewed, or reuse their anchors when evaluating a changed skill. The active portable entry point is `run_eval.py`.
