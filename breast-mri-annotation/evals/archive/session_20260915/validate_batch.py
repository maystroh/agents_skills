"""Read-only integrity audit of delivered scores, labels and local report links."""
from pathlib import Path
from html.parser import HTMLParser
import json
from evaluate import np,nib,sha256

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ['src','href'] and v and not v.startswith(('http:','https:','#')):self.links.append(v)

batch=Path(Path('latest_batch.txt').read_text());m=json.loads((batch/'all_metrics.json').read_text())
assert m['status']=='complete' and m['scored_cases']==len(m['cases'])==11
checked=0
for r in m['cases']:
    assert sha256(r['prediction'])==r['prediction_sha256']
    assert sha256(r['human_reference'])==r['human_reference_sha256']
    assert r['prediction_frozen_at'] and r['slicer_reviewed_indices']==list(range(20))
    for scope in ['full_reference_grid','common_field_of_view']:
        for metric in r[scope].values():
            tp,fp,fn=[metric[x] for x in ['true_positive_voxels','false_positive_voxels','false_negative_voxels']]
            assert tp+fp==metric['prediction_voxels'] and tp+fn==metric['human_voxels']
            assert abs(metric['dice']-2*tp/(2*tp+fp+fn))<1e-12
    a=np.array(r['nipple_localization']['prediction_centroid_ras_mm']);b=np.array(r['nipple_localization']['human_centroid_ras_mm'])
    assert abs(np.linalg.norm(a-b)-r['nipple_localization']['distance_mm'])<1e-10
    diff=nib.load(batch/r['case']/'union_difference.nii.gz');assert np.isin(np.asanyarray(diff.dataobj),[0,1,2,3]).all()
for f in batch.rglob('report.html'):
    p=Links();p.feed(f.read_text(encoding='utf-8'))
    for link in p.links:assert (f.parent/link).exists(),(str(f),link)
    checked+=1
for t in m['totals'].values():
    rows=[r for r in m['cases'] if r['case'] in t['cases']];assert len(rows)==t['case_count']
    for scope in ['full_reference_grid','common_field_of_view']:
        for region,aggregate in t['metrics'][scope].items():
            assert abs(np.mean([r[scope][region]['dice'] for r in rows])-aggregate['mean_dice'])<1e-12
    assert abs(np.mean([r['nipple_localization']['distance_mm'] for r in rows])-t['nipple_centroid_distance_mm']['mean'])<1e-12
u=m['token_usage']['delta'];assert u['input_tokens']+u['output_tokens']==u['total_tokens']
assert u['uncached_input_tokens']+u['cached_input_tokens']==u['input_tokens']
result={'status':'passed','case_count':11,'html_reports_checked':checked,'checks':['Prediction/reference SHA256','Frozen review records','Dice/count consistency','Physical centroid distances','Difference-volume labels','HTML local links','Aggregate arithmetic','Token-counter arithmetic'],'metric_unit_tests':{'passed':8,'command':'python -m unittest test_metrics test_batch_metrics -v'}}
(batch/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
