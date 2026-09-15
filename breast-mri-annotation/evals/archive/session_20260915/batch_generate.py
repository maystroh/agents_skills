"""Rasterize this run's independently inspected source-only anchors. Not a trained model."""
from pathlib import Path
from datetime import datetime
import json,shutil
from evaluate import np,nib,sha256
from scipy.interpolate import CubicSpline
from matplotlib.path import Path as Polygon
root=Path(__file__).parent.resolve();batch=Path((root/'latest_batch.txt').read_text())
specs=json.loads((root/'batch_anchors.json').read_text())
for record in json.loads((batch/'batch.json').read_text())['cases']:
    run=Path(record['run']);m=json.loads((run/'manifest.json').read_text());spec=specs[m['case'][-4:]]
    if m.get('prediction_frozen_at'):raise ValueError('Refusing to change a frozen prediction')
    im=nib.load(next((run/'input').glob('*.nii.gz')))
    breast=np.zeros(im.shape,bool);ii,jj,kk=np.indices(im.shape)
    points=np.stack(np.meshgrid(np.arange(im.shape[0]),np.arange(im.shape[1]),indexing='ij'),-1).reshape(-1,2)
    anchors={int(k):np.array(v,float) for k,v in spec['anchors'].items()}; keys=sorted(anchors)
    # Resample each closed case-specific contour to an equal perimeter parameterization.
    def curve(p):
        p=np.vstack([p,p[0]]);d=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
        return CubicSpline(d/d[-1],p,bc_type='periodic')(np.linspace(0,1,400,endpoint=False))
    curves={k:curve(v) for k,v in anchors.items()}
    for k in range(spec['included_slices'][0],spec['included_slices'][1]+1):
        lo=max(t for t in keys if t<=k);hi=min(t for t in keys if t>=k)
        p=curves[lo] if lo==hi else curves[lo]+(curves[hi]-curves[lo])*(k-lo)/(hi-lo)
        breast[:,:,k]=Polygon(p).contains_points(points).reshape(im.shape[:2])
    c=spec['nipple_ijk'];r=spec['nipple_radii_mm'];spacing=im.header.get_zooms()
    nipple=sum(((axis-center)*sp/radius)**2 for axis,center,sp,radius in zip([ii,jj,kk],c,spacing,r))<=1
    labels=breast.astype('uint8');labels[nipple]=2
    stamp=datetime.now().astimezone().strftime('%Y%m%d_%H%M%S')
    out=run/(m['case']+'_mask_astra_'+stamp+'.nii.gz')
    h=im.header.copy();h.set_data_dtype('uint8');nib.save(nib.Nifti1Image(labels,im.affine,h),out)
    check=nib.load(out);assert np.array_equal(np.asanyarray(check.dataobj),labels) and np.allclose(check.affine,im.affine)
    np.savez_compressed(run/'segments.npz',breast=breast,nipple=nipple)
    (run/'anchors.json').write_text(json.dumps(spec,indent=2));(run/'prediction.txt').write_text(str(out))
    m.update(prediction=str(out),prediction_sha256=sha256(out),annotation_status='draft_pending_slicer_review',notes=[spec['notes']],generation_method='Fresh case-specific source-only contour anchors, perimeter interpolation, separate physical nipple neighborhood',source_slices_inspected=list(range(im.shape[2])))
    (run/'manifest.json').write_text(json.dumps(m,indent=2));print(m['case'],int(breast.sum()),int(nipple.sum()))
shutil.copy2(root/'batch_anchors.json',batch/'generation_anchors.json')
shutil.copy2(root/'batch_generate.py',batch/'generation_script.py')
