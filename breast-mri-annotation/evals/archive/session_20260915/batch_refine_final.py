"""Source-only corrective pass for visible anterior boundary offsets in this batch.

The initial Slicer review showed missing skin bands and floating nipple neighborhoods.
Use localized image gradients within case-specific anterior row spans; keep manually
drawn posterior boundaries. This helper does not read any human reference voxels.
"""
from pathlib import Path
from datetime import datetime
import json,shutil
from evaluate import np,nib,sha256
from scipy.ndimage import gaussian_filter,gaussian_filter1d
root=Path(__file__).parent.resolve();batch=Path((root/'latest_batch.txt').read_text())
spans={'0007':(65,133),'0009':(50,121),'0013':(65,145),'0014':(53,148),'0019':(52,161),'0022':(60,158),'0023':(59,144),'0029':(54,150),'0030':(54,141),'0031':(64,149)}
for record in json.loads((batch/'batch.json').read_text())['cases']:
    run=Path(record['run']);m=json.loads((run/'manifest.json').read_text())
    if m.get('prediction_frozen_at'):raise ValueError('Already frozen')
    if m.get('final_correction'):continue
    im=nib.load(next((run/'input').glob('*.nii.gz')));a=im.get_fdata()
    archive=run/'before_correction'
    prior=run/'before_final_correction';prior.mkdir(exist_ok=True)
    for name in ['segments.npz','manifest.json']:
        shutil.copy2(run/name,prior/name)
    for name in ['slicer_review','slicer_capture_status.json']:
        if (run/name).exists() and not (prior/name).exists():(run/name).rename(prior/name)
    if not archive.exists():
        archive.mkdir()
        shutil.copy2(run/'segments.npz',archive/'segments.npz');shutil.copy2(run/'manifest.json',archive/'manifest.json')
        for name in ['slicer_review','slicer_capture_status.json']:
            origin=(run/name).resolve();target=(archive/name).resolve()
            assert origin.is_relative_to(batch.resolve()) and target.is_relative_to(batch.resolve())
            origin.rename(target)
    with np.load(archive/'segments.npz') as loaded:old={key:loaded[key].copy() for key in loaded.files}
    breast=old['breast'].copy();spec=json.loads((run/'anchors.json').read_text())
    low,high=spans[m['case'][-4:]]
    for k in range(a.shape[2]):
        if not breast[:,:,k].any():continue
        grad=np.gradient(gaussian_filter(a[:,:,k],.8),axis=0)
        shifts=np.zeros(a.shape[1]);left=np.full(a.shape[1],-1,int);right=np.full(a.shape[1],-1,int)
        for j in range(low,high+1):
            xs=np.flatnonzero(breast[:,j,k])
            if len(xs)<8:continue
            x=int(xs[0]);left[j]=x;gaps=np.flatnonzero(np.diff(xs)>1);right[j]=int(xs[gaps[0]]) if len(gaps) else int(xs[-1])
            search=np.arange(max(1,x-17),min(a.shape[0]-1,x+9))
            strength=np.maximum(grad[search,j],0)*np.exp(-.5*((search-x)/13)**2)
            if strength.max()>0:
                edge=int(search[np.argmax(strength)])
                # Include low-signal external skin rather than stopping at peak gradient.
                shifts[j]=min(0,edge-1-x)
        shifts=gaussian_filter1d(shifts,3.0)
        for j in range(low,high+1):
            if left[j]<0:continue
            taper=min(1,(j-low+1)/5,(high-j+1)/5)
            new=int(round(left[j]+shifts[j]*taper));new=max(0,min(right[j],new))
            breast[:right[j]+1,j,k]=False;breast[new:right[j]+1,j,k]=True
    # Track the supported surface across nipple-neighbour slices, without clipping the marker.
    ii,jj=np.indices(a.shape[:2]);nipple=np.zeros(a.shape,bool);cx,cy,ck=spec['nipple_ijk'];rx,ry,rz=spec['nipple_radii_mm'];spacing=im.header.get_zooms()
    centers=[]
    for k in range(a.shape[2]):
        factor=1-((k-ck)*spacing[2]/rz)**2
        if factor<=0:continue
        row=int(round(cy));xs=np.flatnonzero(breast[:,row,k])
        if not len(xs):continue
        actual=float(xs[0]+2)
        if abs(actual-cx)>24:continue
        nipple[:,:,k]=(((ii-actual)*spacing[0]/rx)**2+((jj-cy)*spacing[1]/ry)**2)<=factor
        centers.append([actual,cy,k])
    labels=breast.astype('uint8');labels[nipple]=2
    stamp=datetime.now().astimezone().strftime('%Y%m%d_%H%M%S');out=run/(m['case']+'_mask_astra_'+stamp+'.nii.gz')
    header=im.header.copy();header.set_data_dtype('uint8');nib.save(nib.Nifti1Image(labels,im.affine,header),out)
    assert np.array_equal(np.asanyarray(nib.load(out).dataobj),labels)
    np.savez_compressed(run/'segments.npz',breast=breast,nipple=nipple)
    (run/'prediction.txt').write_text(str(out))
    m.update(prediction=str(out),prediction_sha256=sha256(out),annotation_status='corrected_pending_slicer_review')
    m['notes'].append('Corrected visible anterior offsets using local source-gradient boundary fits in inspected case-specific row spans; re-centered neighboring nipple slices on supported surface. No human mask used.')
    m['final_correction']={'row_span':spans[m['case'][-4:]],'breast_changed_voxels':int(np.count_nonzero(breast!=old['breast'])),'nipple_centers_ijk':centers}
    (run/'manifest.json').write_text(json.dumps(m,indent=2));print(m['case'],m['final_correction']['breast_changed_voxels'])
shutil.copy2(root/'batch_refine_final.py',batch/'final_correction_script.py')
finished=batch/'slicer_batch_finished.txt'
if finished.exists():finished.unlink()
