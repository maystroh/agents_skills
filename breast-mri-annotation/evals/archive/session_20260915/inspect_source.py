from pathlib import Path
import json
from evaluate import np, nib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).parent
run=Path((root/'latest_run.txt').read_text())
im=nib.load(next((run/'input').glob('*.nii.gz')))
a=im.get_fdata()
print(json.dumps({'shape':a.shape,'affine':im.affine.tolist(),'orientation':nib.aff2axcodes(im.affine),'units':im.header.get_xyzt_units(),'range':[float(a.min()),float(a.max())]}))
assert a.ndim==3
fig,axes=plt.subplots(4,5,figsize=(15,12))
for k,ax in enumerate(axes.flat):
    if k<a.shape[2]: ax.imshow(a[:,:,k].T,cmap='gray',origin='lower',vmin=0,vmax=np.percentile(a,99)); ax.set_title(f'k={k}')
    ax.axis('off')
fig.tight_layout(); fig.savefig(run/'source_montage.png',dpi=140)
