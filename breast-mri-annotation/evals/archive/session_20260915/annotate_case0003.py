"""Case-specific source-only contour anchors from the first pilot; NOT a general predictor.

Do not reuse this script to evaluate a modified skill: create a fresh agent annotation.
Coordinates are native NIfTI I,J. No reference mask is read.
"""
from pathlib import Path
from datetime import datetime
import json
from evaluate import np, nib, sha256
from scipy.interpolate import CubicSpline
from matplotlib.path import Path as Polygon
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).parent
run=Path((root/'latest_run.txt').read_text())
source=next((run/'input').glob('*.nii.gz'))
im=nib.load(source); a=im.get_fdata()
anchors={
0:[[145,135],[127,126],[111,129],[93,141],[79,150],[65,150],[55,138],[50,122],[51,105],[58,90],[72,80],[91,75],[111,77],[129,78],[141,66],[146,87],[144,110]],
5:[[143,133],[128,125],[111,134],[95,150],[80,160],[64,160],[51,149],[43,133],[41,108],[47,88],[65,74],[90,67],[114,64],[136,56],[146,47],[143,83],[141,109]],
10:[[141,133],[125,129],[109,140],[96,155],[82,164],[64,161],[51,151],[43,136],[42,108],[44,90],[59,76],[80,65],[105,57],[124,51],[145,40],[143,79],[140,109]],
15:[[141,133],[127,129],[111,142],[96,156],[80,161],[65,157],[52,145],[45,129],[45,106],[52,89],[66,76],[86,68],[106,65],[125,57],[145,40],[146,77],[141,108]],
19:[[139,127],[124,125],[110,136],[97,145],[81,148],[66,143],[56,131],[51,117],[54,99],[63,85],[78,77],[97,73],[114,70],[127,58],[143,43],[148,79],[142,107]]}
grid=np.stack(np.meshgrid(np.arange(192),np.arange(192),indexing='ij'),-1).reshape(-1,2)
breast=np.zeros(a.shape,bool)
keys=sorted(anchors)
for k in range(a.shape[2]):
    lo=max(t for t in keys if t<=k); hi=min(t for t in keys if t>=k)
    p=np.array(anchors[lo],float)
    if hi!=lo: p=p+(np.array(anchors[hi])-p)*(k-lo)/(hi-lo)
    p=np.vstack([p,p[0]])
    smooth=CubicSpline(np.arange(len(p)),p,bc_type='periodic')(np.linspace(0,len(p)-1,400))
    breast[:,:,k]=Polygon(smooth).contains_points(grid).reshape(192,192)
# Source-only candidate: local anterior projection/tissue convergence across k=8..12.
# Physical ellipsoid dimensions chosen for this visible feature, not universal voxel radii.
ii,jj,kk=np.indices(a.shape)
nipple=(((ii-43)*im.header.get_zooms()[0]/5.5)**2+
        ((jj-128)*im.header.get_zooms()[1]/7.0)**2+
        ((kk-10)*im.header.get_zooms()[2]/11.0)**2)<=1
labels=breast.astype('uint8'); labels[nipple]=2
stamp=datetime.now().astimezone().strftime('%Y%m%d_%H%M%S')
out=run/(source.name[:-7]+'_mask_astra_'+stamp+'.nii.gz')
hdr=im.header.copy(); hdr.set_data_dtype('uint8')
nib.save(nib.Nifti1Image(labels,im.affine,hdr),out)
check=nib.load(out)
assert np.array_equal(np.asanyarray(check.dataobj),labels) and np.allclose(check.affine,im.affine)
np.savez_compressed(run/'segments.npz',breast=breast,nipple=nipple)
(run/'prediction.txt').write_text(str(out.resolve()))
(run/'contour_anchors.json').write_text(json.dumps(anchors,indent=2))
manifest=json.loads((run/'manifest.json').read_text())
manifest.update(prediction=str(out.resolve()),prediction_sha256=sha256(out),annotation_status='draft_pending_slicer_review',generation_method='Source-only agent-drawn case-specific spline anchors, interpolated and visually reviewed; separate nipple ellipsoid',notes=['Nipple candidate requires closeup review; posterior attachment convention uncertain.'])
(run/'manifest.json').write_text(json.dumps(manifest,indent=2))
for start in [0,10]:
    fig,axes=plt.subplots(2,5,figsize=(17,7))
    for k,ax in zip(range(start,start+10),axes.flat):
        ax.imshow(a[:,:,k].T,origin='lower',cmap='gray',vmin=0,vmax=255)
        ax.contour(breast[:,:,k].T,levels=[.5],colors=['lime'],linewidths=.7)
        if nipple[:,:,k].any(): ax.contour(nipple[:,:,k].T,levels=[.5],colors=['red'],linewidths=.8)
        ax.set_title(f'Native k={k}'); ax.axis('off')
    fig.tight_layout();fig.savefig(run/f'draft_{start}.png',dpi=140);plt.close(fig)
print(out)
