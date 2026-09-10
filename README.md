# Agent Skills

Reusable skills from my everyday AI-assisted workflows. Each skill combines instructions, reference guidance and small utilities so an agent can carry out a specialized task consistently.

## Available skills

| Skill | What it helps with |
| --- | --- |
| [Breast MRI annotation](breast-mri-annotation/SKILL.md) | Create breast-region and nipple masks, inspect every sagittal slice in 3D Slicer, preserve image geometry, and incorporate lessons from manual corrections. |

## Breast MRI annotation: what it does

This skill guides an AI agent through annotating sagittal breast MRI volumes in `.nii` or `.nii.gz` format, individually or in a folder batch.

The workflow covers:

- **Input checks:** identify source images, inspect orientation and geometry, and keep existing masks separate.
- **Draft annotation:** create editable `breast_region` and `nipple` segments using the current case's anatomy.
- **Slice-by-slice review:** inspect source images and overlays in Slicer, correct contours, and record unresolved uncertainties.
- **Export checks:** save timestamped masks, reload them, and verify voxel labels and original physical geometry.
- **Learning from corrections:** compare matching before/after masks and update reusable annotation guidance while preserving the user's corrected references.

This is an agent-guided workflow, **not a pretrained segmentation model or a one-command automatic segmenter**. Installing it supplies instructions and an export utility; the agent still needs the tools and setup below to perform annotation and visual review.

## Who it helps and why

It is useful for researchers preparing breast MRI datasets, annotators reviewing draft masks, and developers building imaging workflows around 3D Slicer.

| Common problem | How the skill helps |
| --- | --- |
| Repeating setup and export steps for each case | Defines a repeatable batch workflow with recorded progress. |
| Masks extending into the chest wall or missing the outer tissue edge | Provides separate checks for posterior boundaries, skin contours, folds and coverage endpoints. |
| Nipple markers placed at the wrong part of the breast | Emphasizes local anatomy and neighboring slices rather than assuming the breast apex is the nipple. |
| Masks appearing flipped or misaligned after export | Requires physical-geometry mapping and reload verification. |
| The same mistakes returning after manual review | Turns supported corrections into future guidance, without copying patient coordinates between cases. |

These checks aim to reduce repeated work and make results easier to audit. They do not establish clinical validity or guarantee accuracy on a new dataset.

## Requirements

- **A local agent that supports skills**, such as Codex, with access to the MRI files and permission to run local scripts.
- **3D Slicer** for the requested live visual review.
- **A working agent-to-Slicer connection** capable of running Slicer Python and returning actual view images. The skill references a separate `slicer` skill for API and connection guidance; that skill and a connection/bootstrap are **not included in this repository**. Configure them separately before requesting a full Slicer review. See the [Slicer workflow notes](breast-mri-annotation/references/slicer-workflow.md).
- **Python 3 with NumPy and SimpleITK** in the environment used for labelmap export. The inventory command uses only the Python standard library. For a separate Python environment, install the export dependencies with:

  ```bash
  python -m pip install numpy SimpleITK
  ```

Slicer uses its own Python environment; packages installed in another environment are not automatically available there. Additional libraries may be needed for the annotation approach chosen by the agent.

## Install in Codex

### Option 1: ask the skill installer

Paste this into Codex:

```text
$skill-installer install the breast-mri-annotation skill from https://github.com/maystroh/agents_skills/tree/main/breast-mri-annotation
```

The installer supports skills from GitHub repositories. If the skill does not appear after installation, restart Codex. See the [official skill installation and discovery documentation](https://learn.chatgpt.com/docs/build-skills).

### Option 2: copy the skill folder manually

Clone this repository, then copy the **whole** `breast-mri-annotation` folder into your personal skills directory. The following commands use the user-level `.agents/skills` location documented for Codex. Use one installation method to avoid duplicate copies of the same skill.

**Windows — PowerShell**

```powershell
git clone https://github.com/maystroh/agents_skills.git
$skillsDir = Join-Path $HOME '.agents\skills'
$skillDest = Join-Path $skillsDir 'breast-mri-annotation'
if (Test-Path -LiteralPath $skillDest) { throw 'Skill already exists; back up local changes before updating.' }
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
Copy-Item -LiteralPath '.\agents_skills\breast-mri-annotation' -Destination $skillDest -Recurse
```

**macOS / Linux — Bash**

```bash
git clone https://github.com/maystroh/agents_skills.git
mkdir -p "$HOME/.agents/skills"
if [ -e "$HOME/.agents/skills/breast-mri-annotation" ]; then
  echo "Skill already exists; back up local changes before updating."
else
  cp -R agents_skills/breast-mri-annotation "$HOME/.agents/skills/"
fi
```

For a project-specific installation, place the folder under `<project>/.agents/skills/` instead. Other agents may use different locations; follow their skill-loading instructions. Copying this folder does not install Slicer or configure its connection.

## Use it

### Annotate a folder

Replace the example path with a folder your agent can access:

```text
Use $breast-mri-annotation on /path/to/mri-folder.
Generate breast-region and nipple masks, review every sagittal slice in 3D Slicer,
and save timestamped labelmaps and editable segmentations beside the source images.
Report any cases that still need review.
```

The same prompt works with a Windows folder path. Start with a small batch to check that your connection, annotation conventions and exports work as expected.

### Incorporate your corrections

Keep the original drafts and save your edited masks separately, then ask:

```text
Use $breast-mri-annotation to compare my corrected masks in /path/to/reviewed
with the matching original drafts in /path/to/drafts.
Show before/after differences and per-slice changes, then update the annotation
guidance with recurring corrections. Preserve my edited masks.
```

This updates instructions and project references; it does not retrain a model. Case-specific choices, such as deliberately empty slices, should not become universal rules without supporting evidence.

### Inventory files without Slicer

From a clone of this repository:

```bash
python breast-mri-annotation/scripts/batch_io.py inventory /path/to/mri-folder
```

This lists candidate source volumes and excludes common mask/segmentation filenames. It **does not generate annotations or perform visual review**. The same module exposes `export_mask(...)` for programmatic export once binary breast and nipple arrays are already mapped to the original source grid.

## Expected outputs

For each completed case, the workflow saves a NIfTI labelmap and an editable Slicer segmentation:

```text
case001_mask_astra_YYYYMMDD_HHMMSS.nii.gz
case001_mask_astra_YYYYMMDD_HHMMSS.seg.nrrd
```

| Label | Meaning |
| --- | --- |
| `0` | Background |
| `1` | Breast region |
| `2` | Nipple; takes priority where segments overlap in the labelmap |

A batch manifest should record source/output paths, reviewed slices, export checks and remaining uncertainties. Agent visual review, user approval and clinical validation are separate states. If Slicer review could not be performed, it must remain explicitly pending.

## Repository contents

```text
breast-mri-annotation/
├── SKILL.md
├── references/
│   ├── annotation-rules.md
│   ├── review1-learned-preferences.md
│   └── slicer-workflow.md
└── scripts/
    └── batch_io.py
```

The public package contains portable guidance and code. Keep patient images, masks and case-level review records in your own project data storage. Adapt the annotation conventions to your study and have outputs reviewed by appropriately qualified people before clinical use.
