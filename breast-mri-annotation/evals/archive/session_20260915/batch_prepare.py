"""Stage only source images and skill snapshots. Never inspect reference voxels."""
from pathlib import Path
from datetime import datetime
import json,shutil
from evaluate import nib,np,sha256
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).parent.resolve()
dataset=Path(r'<MRI_DATA>\sagitall_annotations\skill_evals\qin')
skill=Path(r'<INSTALLED_SKILL>')
batch=root/'batches'/datetime.now().astimezone().strftime('%Y%m%d_%H%M%S')
batch.mkdir(parents=True)
records=[]
for source in sorted(dataset.glob('*.nii.gz')):
    if '_mask' in source.name or source.name=='QIN-BREAST-01-0003.nii.gz':continue
    case=source.name[:-7];masks=list(dataset.glob(case+'_mask*.nii.gz'))
    if len(masks)!=1:raise ValueError(f'Ambiguous references: {case}')
    run=batch/case; (run/'input').mkdir(parents=True)
    shutil.copy2(source,run/'input'/source.name)
    if not (batch/'skill_snapshot').exists():
        shutil.copytree(skill,batch/'skill_snapshot',ignore=shutil.ignore_patterns('__pycache__'))
    im=nib.load(source);a=im.get_fdata()
    if a.ndim!=3 or nib.aff2axcodes(im.affine)[2] not in ['L','R']:raise ValueError('Requires inspected scalar sagittal K source')
    geometry={'shape':a.shape,'affine':im.affine.tolist(),'spacing':list(map(float,im.header.get_zooms())),'orientation':nib.aff2axcodes(im.affine),'units':im.header.get_xyzt_units(),'range':[float(a.min()),float(a.max())]}
    manifest={'case':case,'source':str(source),'source_sha256':sha256(source),'reference':str(masks[0]),'reference_sha256':sha256(masks[0]),'source_geometry':geometry,'annotation_status':'pending','slicer_reviewed_indices':[], 'reference_voxels_viewed_before_prediction':False,'development_case':case.endswith('0031'),'skill_snapshot':'../skill_snapshot','created':datetime.now().astimezone().isoformat()}
    (run/'manifest.json').write_text(json.dumps(manifest,indent=2))
    for start in range(0,a.shape[2],10):
        fig,axes=plt.subplots(2,5,figsize=(15,6))
        for k,ax in zip(range(start,start+10),axes.flat):
            if k<a.shape[2]:
                ax.imshow(a[:,:,k].T,cmap='gray',origin='lower',vmin=np.percentile(a,1),vmax=np.percentile(a,99.8));ax.set_title(f'{case[-4:]} k={k}')
            ax.axis('off')
        fig.tight_layout();fig.savefig(run/f'source_{start}.png',dpi=120);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(12,4))
    for k,ax in zip([0,a.shape[2]//2,a.shape[2]-1],axes):
        ax.imshow(a[:,:,k].T,cmap='gray',origin='lower',vmin=np.percentile(a,1),vmax=np.percentile(a,99.8))
        ax.set_title(f'{case[-4:]} k={k}');ax.set_xticks(range(0,a.shape[0],20));ax.set_yticks(range(0,a.shape[1],20));ax.grid(alpha=.3)
    fig.tight_layout();fig.savefig(run/'source_axes.png',dpi=130);plt.close(fig)
    records.append({'case':case,'run':str(run),'status':'pending','development_case':manifest['development_case']})
    print(case,geometry)
hashes={str(p.relative_to(batch/'skill_snapshot')):sha256(p) for p in (batch/'skill_snapshot').rglob('*') if p.is_file()}
(batch/'skill_hashes.json').write_text(json.dumps(hashes,indent=2))
(batch/'batch.json').write_text(json.dumps({'created':datetime.now().astimezone().isoformat(),'dataset':str(dataset),'cases':records,'pilot_run':str(root/'runs'/'20260915_101634_QIN-BREAST-01-0003')},indent=2))
(root/'latest_batch.txt').write_text(str(batch))
print('BATCH',batch)
