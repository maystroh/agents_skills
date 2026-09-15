"""Freeze the prediction, explicitly map to the reference grid, and score a run."""
import argparse
from pathlib import Path
from datetime import datetime
import json
from evaluate import np,nib,sha256,compare,decode,dice,centroid
from scipy.ndimage import affine_transform

def main(run):
    manifest=json.loads((run/'manifest.json').read_text())
    pred=Path(manifest['prediction']); ref=Path(manifest['reference'])
    if sha256(ref)!=manifest['reference_sha256'] or sha256(pred)!=manifest['prediction_sha256']:
        raise ValueError('Reference or prediction changed since recorded snapshot')
    manifest['prediction_frozen_at']=datetime.now().astimezone().isoformat()
    (run/'manifest.json').write_text(json.dumps(manifest,indent=2))
    p,g=nib.load(pred),nib.load(ref)
    decode(p);decode(g) # this pilot uses scalar encoding
    if p.header.get_xyzt_units()[0]!='mm' or g.header.get_xyzt_units()[0]!='mm':
        raise ValueError('Expected mm units')
    transform=np.linalg.inv(p.affine)@g.affine
    # Snap numerical NIfTI round-off for grids related by integer flip/translation.
    rounded=np.rint(transform)
    if np.allclose(transform,rounded,atol=1e-4,rtol=0): transform=rounded
    mapped=affine_transform(np.asanyarray(p.dataobj),transform[:3,:3],offset=transform[:3,3],output_shape=g.shape,order=0,mode='grid-constant',cval=0,prefilter=False)
    coverage=affine_transform(np.ones(p.shape,np.uint8),transform[:3,:3],offset=transform[:3,3],output_shape=g.shape,order=0,mode='grid-constant',cval=0,prefilter=False)>0
    aligned=run/'prediction_on_reference_grid.nii.gz'
    header=g.header.copy();header.set_data_dtype('uint8')
    nib.save(nib.Nifti1Image(mapped,g.affine,header),aligned)
    result=compare(aligned,ref)
    gd=np.asanyarray(g.dataobj)
    pc=centroid(np.asanyarray(p.dataobj)==2,p.affine)
    gc=centroid(gd==2,g.affine)
    result['nipple_centroid_prediction_ras_mm']=pc
    result['nipple_centroid_distance_mm']=float(np.linalg.norm(np.array(pc)-gc)) if pc is not None and gc is not None else None
    common_gc=centroid((gd==2)&coverage,g.affine)
    result['common_field_of_view']={
        'breast_dice_exclusive':dice((mapped==1)&coverage,(gd==1)&coverage),
        'union_dice':dice((mapped>0)&coverage,(gd>0)&coverage),
        'nipple_dice':dice((mapped==2)&coverage,(gd==2)&coverage),
        'nipple_centroid_distance_mm':float(np.linalg.norm(np.array(pc)-common_gc)) if pc is not None and common_gc is not None else None,
        'reference_nipple_voxels_outside_source':int(np.count_nonzero((gd==2)&~coverage))}
    result.update(original_prediction=str(pred),original_prediction_sha256=sha256(pred),
        geometry_mapping={'method':'nearest-neighbour; zero outside source; full reference grid scored',
        'reference_to_prediction_ijk':transform.tolist(),'source_shape':p.shape,'reference_shape':g.shape,
        'reference_foreground_outside_source':int(np.count_nonzero((np.asanyarray(g.dataobj)>0)&~coverage))})
    (run/'metrics.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    manifest['scored_at']=datetime.now().astimezone().isoformat()
    manifest['metrics']='metrics.json'
    (run/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',type=Path)
    args=parser.parse_args()
    main(args.run or Path((Path(__file__).parent/'latest_run.txt').read_text()))
