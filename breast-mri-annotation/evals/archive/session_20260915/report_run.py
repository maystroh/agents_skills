from pathlib import Path
from datetime import datetime
import json
from evaluate import np,nib,sha256
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
run=Path((Path(__file__).parent/'latest_run.txt').read_text())
m=json.loads((run/'manifest.json').read_text());r=json.loads((run/'metrics.json').read_text())
source=nib.load(next((run/'input').glob('*.nii.gz'))).get_fdata()
p=nib.load(m['prediction']).get_fdata()
g=nib.load(m['reference']).get_fdata()[:,:,19::-1]
fig,axes=plt.subplots(1,3,figsize=(14,5))
for ax,k in zip(axes,[0,10,19]):
    ax.imshow(source[:,:,k].T,cmap='gray',origin='upper',vmin=0,vmax=255)
    ax.contour((p[:,:,k]>0).T,levels=[.5],colors=['lime'],linewidths=1)
    ax.contour((g[:,:,k]>0).T,levels=[.5],colors=['cyan'],linewidths=1)
    if (p[:,:,k]==2).any():ax.contour((p[:,:,k]==2).T,levels=[.5],colors=['red'])
    if (g[:,:,k]==2).any():ax.contour((g[:,:,k]==2).T,levels=[.5],colors=['orange'])
    ax.set_title(f'Native slice {k}');ax.axis('off')
fig.suptitle('Breast union: prediction green / reference cyan; nipple: prediction red / reference orange')
fig.tight_layout();fig.savefig(run/'comparison.png',dpi=140)
m.update(annotation_status='agent_reviewed_pilot_with_uncertainty',slicer_reviewed_indices=list(range(20)),
    review_completed_at=datetime.now().astimezone().isoformat(),user_approved=False,
    notes=['All 20 original sagittal slices inspected in actual Slicer source and overlay captures, plus native closeup at k10.',
    'Source-only nipple candidate and posterior boundary were retained for unbiased scoring; no reference-driven prediction changes.',
    'Reference has one extra annotated slice beyond MRI coverage. Report full-reference and common-field-of-view metrics separately.',
    'Pilot uses five hand-drawn contour anchors with interpolation. Nipple marker is smaller than the reference; this is a skill execution weakness, not proof of instruction quality alone.'])
(run/'manifest.json').write_text(json.dumps(m,indent=2))
report=f'''# First pilot: QIN-BREAST-01-0003

| Metric | Full reference grid | Common MRI field of view |
|---|---:|---:|
| Breast Dice (exclusive label 1) | {r['breast_dice_exclusive']:.4f} | {r['common_field_of_view']['breast_dice_exclusive']:.4f} |
| Breast+nipple union Dice | {r['breast_nipple_union_dice']:.4f} | {r['common_field_of_view']['union_dice']:.4f} |
| Nipple Dice | {r['nipple_dice']:.4f} | {r['common_field_of_view']['nipple_dice']:.4f} |
| Nipple centroid distance (mm) | {r['nipple_centroid_distance_mm']:.2f} | {r['common_field_of_view']['nipple_centroid_distance_mm']:.2f} |

## Nipple centroids (RAS mm)

- Prediction: {r['nipple_centroid_prediction_ras_mm']}
- Reference: {r['nipple_centroid_reference_ras_mm']}

## Interpretation

The prediction has {r['prediction_voxels']['breast_exclusive']:,} breast voxels versus {r['reference_voxels']['breast_exclusive']:,} in the reference. The nipple marker has {r['prediction_voxels']['nipple']} voxels versus {r['reference_voxels']['nipple']}. This run underrepresents the reference region and produces a small, displaced nipple marker. Scores measure this particular agent's execution of the snapshotted skill. They cannot isolate the wording of the skill from the agent's choices.

The MRI has 20 slices; the reference has 21 with reversed K direction. Physical mapping is reference k = 19 - source k. The extra reference slice contains {r['geometry_mapping']['reference_foreground_outside_source']:,} foreground voxels outside MRI coverage. The primary score counts them as missed; the secondary score restricts comparison to observed MRI coverage. Original files were preserved.

## Protocol and provenance

Only the source MRI was viewed during prediction. Prediction and skill hashes were recorded before reference voxel scoring. All 20 slices were inspected in actual Slicer source/overlay captures. The working segmentation preserves overlap; scalar export uses nipple priority. No prediction edits were made after opening the reference. This is an agent-reviewed pilot, not user approval. The nipple location was a source-only candidate with residual uncertainty.

See `manifest.json`, `metrics.json`, `skill_snapshot/`, `contour_anchors.json`, and `slicer_review/`. Rerun the current skill with a fresh annotation after changes; do not reuse this pilot's case-specific generation script as a revised-skill predictor. The skill files were not modified.

![Comparison](comparison.png)
'''
(run/'report.md').write_text(report)
print(report)
