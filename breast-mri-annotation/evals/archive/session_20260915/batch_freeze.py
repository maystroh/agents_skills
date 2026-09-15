from pathlib import Path
from datetime import datetime
import json,shutil
from evaluate import np,nib,sha256
b=Path('latest_batch.txt').read_text();b=Path(b);cfg=json.loads((b/'batch.json').read_text())
for item in cfg['cases']:
 r=Path(item['run']);m=json.loads((r/'manifest.json').read_text());s=json.loads((r/'slicer_capture_status.json').read_text())
 assert s['prediction_sha256']==sha256(m['prediction'])==m['prediction_sha256']
 assert s['captured_native_k']==list(range(20)) and s['working_segmentation_reload_verified'] and s['allow_overlap_verified']
 p=nib.load(m['prediction']);src=nib.load(next((r/'input').glob('*.nii.gz')))
 assert p.shape==src.shape and np.allclose(p.affine,src.affine)
 with np.load(r/'segments.npz') as z:
  label=z['breast'].astype('uint8');label[z['nipple']]=2
  assert z['breast'].any() and z['nipple'].any()
  assert np.array_equal(label,np.asanyarray(p.dataobj))
  for name in ['breast','nipple']:assert np.array_equal(z[name],nib.load(r/(name+'_raw.nii.gz')).get_fdata()>0)
 m.update(prediction_frozen_at=datetime.now().astimezone().isoformat(),slicer_reviewed_indices=list(range(20)),annotation_status='reviewed_frozen_low_confidence_nipple' if m['case'].endswith('0014') else 'reviewed_frozen')
 m['working_segmentation_sha256']=sha256(r/(m['case']+'_ASTRA.seg.nrrd'));m['segments_sha256']=sha256(r/'segments.npz')
 (r/'manifest.json').write_text(json.dumps(m,indent=2));s.update(reviewed=True,reviewed_at=m['prediction_frozen_at'],reviewed_native_k=list(range(20)),source_only_and_nipple_closeup_reviewed=True);(r/'slicer_capture_status.json').write_text(json.dumps(s,indent=2))
 item['status']=m['annotation_status']
# Reference staging occurs after ALL predictions are frozen.
for item in cfg['cases']:
 r=Path(item['run']);m=json.loads((r/'manifest.json').read_text());origin=Path(m['reference']);assert sha256(origin)==m['reference_sha256']
 dest=r/'reference'/origin.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(origin,dest);assert sha256(dest)==m['reference_sha256']
 m['original_reference']=str(origin);m['reference']=str(dest);m['reference_first_voxel_access_after']=datetime.now().astimezone().isoformat();(r/'manifest.json').write_text(json.dumps(m,indent=2))
(b/'batch.json').write_text(json.dumps(cfg,indent=2));print('FROZEN AND VERIFIED',len(cfg['cases']))
