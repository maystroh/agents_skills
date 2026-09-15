# Breast MRI skill evaluations

Evaluate fresh agent annotations against the user's fixed masks. Scoring runs locally in Python; annotation review uses images shown to the agent. `runs/`, `batches/` and dependencies are excluded from Git.

## Setup

Use Python 3.12 or newer:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python test_metrics.py
```

## Run after modifying the skill

1. `python prepare.py --case QIN-BREAST-01-0003` creates a timestamped run, copies only the MRI to `input/`, and snapshots the skill and reference hashes. Override `--dataset` and `--skill` as needed.
2. Ask the agent: "Use the skill snapshot in this run to annotate only its input MRI. Do not view the reference mask or previous predictions. Review every sagittal slice in Slicer. Save a fresh scalar 0/1/2 prediction, an overlapping .seg.nrrd working copy, generation details, and reviewed original slice indices. Freeze the prediction before scoring."
3. Run `python evaluate.py --prediction PATH --reference PATH --output metrics.json`. For a binary component reference with verified breast,nipple channel order, add `--reference-encoding components`.
4. Save the result with the run. Compare the same cases across skill versions. Each revised skill requires new agent annotation; rerunning the scorer alone does not evaluate a skill change.

For a run manifest with a frozen scalar prediction path/hash, `python score_run.py --run RUN_FOLDER` explicitly maps the prediction onto the reference grid and reports both full-reference and common-coverage results. Use it only after verifying the image/reference pairing. This first pilot discovered reversed K direction and one extra annotated reference slice. `evaluate.py` remains strict and never resamples implicitly.

The first result is linked through `latest_run.txt`; its `report.md` contains the scores, centroids, geometry finding, and comparison image. In this desktop workspace the bundled Python is `<USER_HOME>\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`, with project-local packages under `.deps/`.

`annotate_case0003.py` preserves the first pilot's source-only decisions for audit. It is **not a reusable segmentation model or a runner for revised skills**. The annotation is agent-guided and can vary between runs. Keep the model, prompt, sample, and review protocol consistent and repeat runs to measure variation. No scheduled watcher has been installed.

## Metrics

- Breast Dice: `2 |P ∩ G| / (|P| + |G|)` for exclusive breast label 1, with nipple removed from both masks to handle component overlap consistently.
- Breast+nipple union Dice: same formula for the union; avoids penalizing breast-to-nipple relabeling as missing tissue.
- Nipple Dice: overlap of nipple masks.
- Nipple centroid distance: Euclidean distance between mean foreground coordinates transformed with each NIfTI affine into RAS millimetres. Reports both centroids.
- Both masks empty: Dice is `null`, not a perfect score. One empty: Dice 0. Missing nipple: distance `null` with an explicit status.
- Shapes, affines, units, finite values, and allowed labels are validated. Geometry mismatches fail instead of silently comparing or resampling. Component masks require an explicit channel encoding; no guessing.

The scalar export cannot retain breast/nipple overlap. Keep the `.seg.nrrd` for editing and raw overlap. Scores describe agreement with this user's annotation convention. One pilot does not estimate dataset-wide accuracy. Case 0031 was a skill development example; treat it as development data rather than an independent holdout. Check the other cases' history before calling the complete set held out.

## Completed batch: 15 September 2026

`latest_batch.txt` points to the 10-case continuation, with the original pilot included in the reports. Open `report.html` in that folder. Each case has an HTML/Markdown report, complete JSON metrics, per-slice metrics, comparison images and a NIfTI difference volume. `all_metrics.json` contains the full set plus totals, provenance, file hashes and recorded token usage. `metrics_per_case.json` and `totals.json` provide compact views.

The run used `gpt-6-astra` with medium reasoning effort. All 200 new native slices were reviewed in actual Slicer source/overlay captures. Drafts and corrections are preserved; each final prediction was frozen before human reference voxels were opened. Four references preserve separate breast/nipple channels, verified visually after freeze. Case 0014 retains low-confidence nipple localization. Case 0013 has a disconnected human nipple component; primary results retain it, with largest-component sensitivity reported separately.

### Regenerate scores and reports for these frozen predictions

```powershell
python -m unittest test_metrics test_batch_metrics -v
python batch_metrics.py --batch batches/20260915_151621
python publish_batch.py --batch batches/20260915_151621 --observations case_observations.json
```

This recomputes the existing run, not a revised skill evaluation. `publish_batch.py` enriches the master file with visual findings, component diagnostics, environment and usage. The scorer reports nearest-neighbour alignment explicitly, full-reference and common-coverage metrics, volumes, TP/FP/FN, precision/recall, surface distances, centroids, component counts and aggregate distributions. Undefined measurements remain null.

### Evaluate a revised skill

Create a new timestamped source-only run with `prepare.py` (single case) or `batch_prepare.py` (this QIN continuation set). Start fresh annotation using that run's skill snapshot, ideally in a fresh task with the same model and effort. Do not expose earlier masks, reports or human reference voxels to the annotating agent. Generate new case-specific decisions, review every slice, record the actual review and freeze hashes before scoring. Do not automatically reuse `batch_anchors.json`, correction helpers or `case_observations.json`: these preserve decisions and findings for this exact historical batch. The Slicer helper captures views; viewing them is a separate required agent action. `batch_freeze.py` records the completed review attestation for this batch and must not be used to assert an unseen review.

Use a new observations file after examining the new comparisons. Retain the same reference versions to compare skill versions fairly. If human labels are corrected, assign a new ground-truth version and re-score both old and new predictions against it; never silently replace the baseline. No watcher or automatic re-annotation service is installed.

### Token accounting

`token_usage.py --rollout PATH --output BATCH/token_usage.json` subtracts this task's cumulative counter immediately before the batch request from the latest recorded counter. Input includes repeated context; cached input is a subset of input, and reasoning output is a subset of output. This measures the whole shared batch request, including staging, failed attempts, corrections, review and reporting. It cannot attribute usage per case or infer a dollar charge. The report checkpoint excludes subsequent calls and the final reply. Re-run `publish_batch.py` after refreshing usage to embed the same checkpoint in `all_metrics.json` and HTML.
