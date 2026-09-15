from pathlib import Path
from datetime import datetime
import json,shutil
from evaluate import np,nib,sha256
from scipy.interpolate import PchipInterpolator
b=Path('batches/20260915_151621').resolve();r=b/'QIN-BREAST-01-0013';m=json.loads((r/'manifest.json').read_text());assert not m.get('prediction_frozen_at')
a=r/'before_end_correction';a.mkdir(exist_ok=True)
for name in ['segments.npz','manifest.json']:shutil.copy2(r/name,a/name)
for name in ['slicer_review','slicer_capture_status.json']:
    if (r/name).exists() and not (a/name).exists():(r/name).rename(a/name)
with np.load(r/'segments.npz') as z:breast=z['breast'].copy();nipple=z['nipple'].copy()
anchors={16:[[65,91],[76,84],[88,64],[103,52],[115,49],[129,52],[136,63],[143,83]],17:[[65,93],[77,90],[89,67],[101,55],[112,51],[126,53],[135,63],[143,84]],18:[[65,94],[79,91],[88,77],[96,63],[108,57],[120,57],[131,64],[140,83]]}
for k,pts in anchors.items():
    pts=np.array(pts);curve=PchipInterpolator(pts[:,0],pts[:,1])
    for j in range(int(pts[0,0]),int(pts[-1,0])+1):
        xs=np.flatnonzero(breast[:,j,k]);new=int(round(float(curve(j))))
        if len(xs):breast[new:xs[0]+1,j,k]=1
im=nib.load(m['prediction']);labels=breast.astype('uint8');labels[nipple]=2
out=r/(m['case']+'_mask_astra_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.nii.gz');nib.save(nib.Nifti1Image(labels,im.affine,im.header),out)
np.savez_compressed(r/'segments.npz',breast=breast,nipple=nipple)
m.update(prediction=str(out),prediction_sha256=sha256(out));m['notes'].append('Corrected visible anterior clipping on native slices 16-18 with new source-only boundary anchors.');m['end_boundary_anchors_j_i']=anchors
(r/'manifest.json').write_text(json.dumps(m,indent=2));(r/'prediction.txt').write_text(str(out))
s=(Path('batch_slicer_review.py').read_text()).replace("for job in jobs:","for job in jobs:\n        if not job['case'].endswith('0013'):continue")
Path('slicer_review_0013.py').write_text(s)
