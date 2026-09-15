"""Synthetic integration test: no real MRI data or external services."""
import json,tempfile,unittest
from pathlib import Path
from run_eval import run,CASES,np,nib,sha256,current

class RunnerTests(unittest.TestCase):
    def test_split_reference_preserves_overlap_and_scores_exact_prediction(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);data=root/'dataset';pred=root/'predictions';pred.mkdir()
            for sub in ['images','labels/breast_region','labels/nipples']:(data/sub).mkdir(parents=True)
            records=[]
            for case in CASES:
                breast=np.zeros((5,5,20),np.uint8);breast[1:4,1:4,5:10]=1
                nipple=np.zeros_like(breast);nipple[1,2,7]=1
                scalar=breast.copy();scalar[nipple>0]=2
                affine=np.diag([1.3,1.3,5,1])
                def save(a,p):
                    im=nib.Nifti1Image(a,affine);im.header.set_xyzt_units('mm');nib.save(im,p)
                for sub,a in [('images',breast*100),('labels/breast_region',breast),('labels/nipples',nipple)]:save(a,data/sub/(case+'.nii.gz'))
                file=pred/(case+'.nii.gz');save(scalar,file)
                records.append({'case':case,'prediction':str(file),'prediction_sha256':sha256(file),'prediction_frozen_at':'2026-01-01T00:00:00Z','reviewed_in_slicer':True,'reference_blind_annotation':True,'slicer_reviewed_indices':list(range(20)),'skill_sha256':current()['skill_sha256'],'model':'synthetic-test','reasoning_effort':'none'})
            manifest=root/'manifest.json';manifest.write_text(json.dumps(records));output=root/'output'
            run(data,manifest,output,'synthetic-test','none')
            m=json.loads((output/'metrics.json').read_text());self.assertEqual(m['totals']['case_count'],10)
            self.assertEqual(m['totals']['metrics']['full_reference_grid']['breast_exclusive']['mean_dice'],1)
            self.assertEqual(m['totals']['nipple_centroid_distance_mm']['mean'],0)
            for r in m['cases']:
                self.assertIsNone(r['raw_overlapping_breast_comparison'])
                self.assertIsNone(r['raw_overlap_voxels']['prediction'])
                self.assertEqual(r['raw_overlap_voxels']['human'],1)

if __name__=='__main__':unittest.main()
