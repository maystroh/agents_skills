"""Score externally generated, frozen predictions against the HF human-user-10 set.

Local dataset layout: images/, labels/breast_region/, labels/nipples/.
No downloading or annotation is performed. Prediction review is externally attested.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,shutil
from batch_metrics import np,nib,sha256,score_case,summarize,write_json
from history import current

CASES=['QIN-BREAST-01-'+x for x in ['0003','0007','0009','0013','0014','0019','0022','0023','0029','0030']]
DATASET='https://huggingface.co/datasets/h2thez3/breast-mri-sagitall-landmarks#breast-mri-sagittal-landmarks'

def run(dataset,prediction_manifest,output,model,effort):
    records=json.loads(prediction_manifest.read_text());assert len(records)==10
    assert {r['case'] for r in records}==set(CASES),'Require the exact ten human cases'
    output.mkdir(parents=True,exist_ok=False);results=[]
    # Validate and freeze every supplied prediction before reading any reference voxel.
    prepared=[]
    for item in records:
        case=item['case'];pred=Path(item['prediction']);pred=pred if pred.is_absolute() else prediction_manifest.parent/pred
        assert sha256(pred)==item['prediction_sha256'],'Prediction changed since external freeze'
        assert item['reviewed_in_slicer'] is True and item['reference_blind_annotation'] is True
        assert item['skill_sha256']==current()['skill_sha256'],'Prediction belongs to another skill version'
        assert item['model']==model and item['reasoning_effort']==effort
        assert item['prediction_frozen_at'] and item['slicer_reviewed_indices']==list(range(20))
        source=dataset/'images'/f'{case}.nii.gz';im=nib.load(source);p=nib.load(pred)
        assert p.shape==im.shape and np.allclose(p.affine,im.affine,atol=1e-4,rtol=0)
        labels=np.asanyarray(p.dataobj);assert labels.ndim==3 and np.isin(labels,[0,1,2]).all()
        r=output/case;(r/'input').mkdir(parents=True);shutil.copy2(source,r/'input'/source.name);shutil.copy2(pred,r/'prediction.nii.gz')
        np.savez_compressed(r/'segments.npz',breast=labels==1,nipple=labels==2)
        prepared.append((item,r,im))
    for item,r,im in prepared:
        case=item['case'];bpath=dataset/'labels/breast_region'/f'{case}.nii.gz';npath=dataset/'labels/nipples'/f'{case}.nii.gz'
        b,n=nib.load(bpath),nib.load(npath)
        for g in [b,n]:
            assert g.shape==im.shape and np.allclose(g.affine,im.affine,atol=1e-4,rtol=0)
            assert g.header.get_xyzt_units()[0]=='mm' and np.isin(np.asanyarray(g.dataobj),[0,1]).all()
        # Explicit components retain human overlap; predicted raw overlap is unavailable.
        data=np.stack([np.asanyarray(b.dataobj),np.asanyarray(n.dataobj)],axis=-1).astype('uint8')
        ref=r/'reference.nii.gz';nib.save(nib.Nifti1Image(data,im.affine,im.header),ref)
        m={'case':case,'prediction':str((r/'prediction.nii.gz').resolve()),'prediction_sha256':sha256(r/'prediction.nii.gz'),'reference':str(ref.resolve()),'reference_sha256':sha256(ref),
           'source':str((r/'input'/f'{case}.nii.gz').resolve()),'source_sha256':sha256(r/'input'/f'{case}.nii.gz'),'prediction_frozen_at':item['prediction_frozen_at'],'slicer_reviewed_indices':item['slicer_reviewed_indices'],
           'annotation_status':'externally_attested_reviewed_frozen','raw_breast_overlap_available':False,'notes':['Reference components explicitly ordered breast,nipple. Source-only review is attested by the supplied manifest, not performed by this scorer.']}
        write_json(r/'manifest.json',m);result=score_case(r,'components');result['reference_component_sha256']={'breast':sha256(bpath),'nipple':sha256(npath)};results.append(result)
    result={'status':'evaluated','cohort':'human-user-10','dataset_url':DATASET,'model':model,'reasoning_effort':effort,'fingerprints':current(),'created':datetime.now(timezone.utc).isoformat(),'cases':results,'totals':summarize(results),'token_usage':None}
    write_json(output/'metrics.json',result);print(output/'metrics.json')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dataset',required=True,type=Path);p.add_argument('--prediction-manifest',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--model',required=True);p.add_argument('--effort',required=True);a=p.parse_args()
    run(a.dataset,a.prediction_manifest,a.output,a.model,a.effort)
