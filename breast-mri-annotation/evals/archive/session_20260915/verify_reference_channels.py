from pathlib import Path
import json
from batch_metrics import np,nib,map_array,plt
b=Path('latest_batch.txt').read_text();b=Path(b);entries={};fig,ax=plt.subplots(4,2,figsize=(8,16));row=0
for item in json.loads((b/'batch.json').read_text())['cases']:
 r=Path(item['run']);m=json.loads((r/'manifest.json').read_text());assert m['prediction_frozen_at'];g=nib.load(m['reference']);a=np.asanyarray(g.dataobj)
 if a.ndim==3:entries[m['case']]={'encoding':'scalar','labels':{'0':'background','1':'breast','2':'nipple'}};continue
 assert a.shape[3:]==(1,2) and np.isin(a,[0,1]).all()
 src=nib.load(next((r/'input').glob('*.nii.gz')));k=int(round(json.loads((r/'anchors.json').read_text())['nipple_ijk'][2]))
 for c in range(2):
  mapped,_=map_array(a[:,:,:,0,c],g.affine,src.shape,src.affine)
  ax[row,c].imshow(src.get_fdata()[:,:,k].T,cmap='gray');ax[row,c].contour(mapped[:,:,k].T,levels=[.5],colors=['cyan']);ax[row,c].set_title(m['case'][-4:]+' channel '+str(c)+' k='+str(k));ax[row,c].axis('off')
 print(m['case'],'channel counts',a[:,:,:,0,:].sum(axis=(0,1,2)).tolist())
 entries[m['case']]={'encoding':'components','order':['breast','nipple'],'visual_verification':'pending'};row+=1
fig.tight_layout();fig.savefig(b/'reference_channels.png',dpi=130);(b/'reference_encodings.json').write_text(json.dumps(entries,indent=2))
