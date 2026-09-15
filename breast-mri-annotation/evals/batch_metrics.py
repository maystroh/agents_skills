"""Geometry-aware metrics and reports for frozen agent predictions.

Reference files are read only after each manifest records a frozen prediction hash.
No automatic selection of the newest mask or channel guessing is performed.
"""
from pathlib import Path
from datetime import datetime
import argparse,json,html,shutil
from evaluate import np,nib,sha256,decode,dice,centroid
from scipy.ndimage import affine_transform,binary_erosion,label
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from case_visuals import render_comparison, write_case_report

def write_json(path,data):
    Path(path).write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf-8')

def map_array(array,source_affine,target_shape,target_affine):
    transform=np.linalg.inv(source_affine)@target_affine
    if np.allclose(transform,np.rint(transform),atol=1e-4,rtol=0):transform=np.rint(transform)
    out=affine_transform(array.astype(np.uint8),transform[:3,:3],offset=transform[:3,3],output_shape=target_shape,order=0,mode='grid-constant',cval=0,prefilter=False)
    return out,transform

def region_stats(p,g,affine,surface=True):
    p=np.asarray(p,bool);g=np.asarray(g,bool)
    tp=int(np.count_nonzero(p&g));fp=int(np.count_nonzero(p&~g));fn=int(np.count_nonzero(~p&g))
    pv=tp+fp;gv=tp+fn;vv=abs(float(np.linalg.det(affine[:3,:3])))
    pc,gc=centroid(p,affine),centroid(g,affine)
    delta=(np.array(pc)-gc).tolist() if pc is not None and gc is not None else None
    r={'dice':dice(p,g),'jaccard':tp/(tp+fp+fn) if tp+fp+fn else None,
       'precision':tp/pv if pv else None,'recall':tp/gv if gv else None,
       'true_positive_voxels':tp,'false_positive_voxels':fp,'false_negative_voxels':fn,
       'prediction_voxels':pv,'human_voxels':gv,'voxel_volume_mm3':vv,
       'prediction_volume_ml':pv*vv/1000,'human_volume_ml':gv*vv/1000,
       'false_positive_volume_ml':fp*vv/1000,'false_negative_volume_ml':fn*vv/1000,
       'volume_bias_ml':(pv-gv)*vv/1000,'volume_ratio':pv/gv if gv else None,
       'prediction_centroid_ras_mm':pc,'human_centroid_ras_mm':gc,
       'centroid_delta_ras_mm':delta,'centroid_distance_mm':float(np.linalg.norm(delta)) if delta is not None else None,
       'prediction_components_6_connected':int(label(p)[1]),'human_components_6_connected':int(label(g)[1]),
       'hd95_mm':None,'average_symmetric_surface_distance_mm':None,
       'status':'both_present' if pv and gv else 'missing_prediction' if gv else 'missing_human' if pv else 'both_empty'}
    if surface and pv and gv:
        ps=p&~binary_erosion(p,border_value=0);gs=g&~binary_erosion(g,border_value=0)
        pp=nib.affines.apply_affine(affine,np.argwhere(ps));gp=nib.affines.apply_affine(affine,np.argwhere(gs))
        pd=cKDTree(gp).query(pp)[0];gd=cKDTree(pp).query(gp)[0]
        r['hd95_mm']=float(max(np.percentile(pd,95),np.percentile(gd,95)))
        r['average_symmetric_surface_distance_mm']=float((pd.mean()+gd.mean())/2)
    return r

def format_number(x,places=4):return 'N/A' if x is None else f'{x:.{places}f}'

def score_case(run,encoding,output=None):
    run=Path(run);output=Path(output or run);output.mkdir(parents=True,exist_ok=True)
    m=json.loads((run/'manifest.json').read_text())
    if not m.get('prediction_frozen_at'):raise ValueError('Prediction must be frozen before reference voxel access')
    prediction=Path(m['prediction']);reference=Path(m['reference'])
    if sha256(prediction)!=m['prediction_sha256'] or sha256(reference)!=m['reference_sha256']:
        raise ValueError('Source snapshot hash mismatch')
    p,g=nib.load(prediction),nib.load(reference)
    for im in [p,g]:
        if im.header.get_xyzt_units()[0]!='mm':raise ValueError('Millimetre units required')
        if not np.isfinite(im.affine).all() or abs(np.linalg.det(im.affine[:3,:3]))<1e-9:raise ValueError('Invalid affine')
    pb,pn=decode(p);gb,gn=decode(g,encoding)
    pu=pb|pn;gu=gb|gn
    mp,transform=map_array(np.asanyarray(p.dataobj),p.affine,g.shape[:3],g.affine)
    coverage,_=map_array(np.ones(p.shape,bool),p.affine,g.shape[:3],g.affine);coverage=coverage.astype(bool)
    pred_coverage,_=map_array(np.ones(g.shape[:3],bool),g.affine,p.shape,p.affine);pred_coverage=pred_coverage.astype(bool)
    classes={'breast_exclusive':(mp==1,gb&~gn),'nipple':(mp==2,gn),'breast_nipple_union':(mp>0,gu)}
    full={name:region_stats(a,b,g.affine) for name,(a,b) in classes.items()}
    common={name:region_stats(a&coverage,b&coverage,g.affine,surface=False) for name,(a,b) in classes.items()}
    # Localization uses original physical centroids, without resampling or FOV clipping.
    pc,gc=centroid(pn,p.affine),centroid(gn,g.affine)
    localization={'prediction_centroid_ras_mm':pc,'human_centroid_ras_mm':gc,
       'delta_ras_mm':(np.array(pc)-gc).tolist() if pc is not None and gc is not None else None,
       'distance_mm':float(np.linalg.norm(np.array(pc)-gc)) if pc is not None and gc is not None else None,
       'status':full['nipple']['status']}
    original=np.load(run/'segments.npz')
    raw_breast=None
    if encoding=='components' and m.get('raw_breast_overlap_available',True):
        rb,_=map_array(original['breast'],p.affine,g.shape[:3],g.affine)
        raw_breast=region_stats(rb>0,gb,g.affine)
    per_slice=[]
    for k in range(g.shape[2]):
        entry={'reference_k':k,'native_source_center_ijk':nib.affines.apply_affine(transform,[(g.shape[0]-1)/2,(g.shape[1]-1)/2,k]).tolist()}
        for name,(a,b) in classes.items():
            aa,bb=a[:,:,k],b[:,:,k]
            entry[name]={'dice':dice(aa,bb),'prediction_voxels':int(aa.sum()),'human_voxels':int(bb.sum()),'false_positive_voxels':int(np.count_nonzero(aa&~bb)),'false_negative_voxels':int(np.count_nonzero(~aa&bb))}
        per_slice.append(entry)
    r={'case':m['case'],'development_case':m.get('development_case',m['case'].endswith('0031')),
       'scored_at':datetime.now().astimezone().isoformat(),'annotation_status':m['annotation_status'],
       'source':m['source'],'source_sha256':m['source_sha256'],'prediction':str(prediction),'prediction_sha256':sha256(prediction),
       'human_reference':str(reference),'human_reference_sha256':sha256(reference),'human_encoding':encoding,
       'prediction_frozen_at':m['prediction_frozen_at'],'slicer_reviewed_indices':m['slicer_reviewed_indices'],
       'full_reference_grid':full,'common_field_of_view':common,'nipple_localization':localization,
       'raw_overlapping_breast_comparison':raw_breast,
       'raw_overlap_voxels':{'prediction':int(np.count_nonzero(original['breast']&original['nipple'])) if m.get('raw_breast_overlap_available',True) else None,'human':int(np.count_nonzero(gb&gn)) if encoding=='components' else None},
       'geometry':{'source_shape':p.shape,'reference_shape':g.shape[:3],'source_affine':p.affine.tolist(),'reference_affine':g.affine.tolist(),'reference_to_prediction_ijk':transform.tolist(),
       'method':'Prediction mapped to full reference grid by nearest neighbour; zero outside coverage. Centroids use original physical coordinates.',
       'human_foreground_outside_source':int(np.count_nonzero(gu&~coverage)),
       'human_nipple_outside_source':int(np.count_nonzero(gn&~coverage)),
       'prediction_foreground_outside_reference':int(np.count_nonzero(pu&~pred_coverage))},
       'notes':m.get('notes',[]),'per_slice':per_slice,'token_usage':None,
       'token_usage_note':'Shared agent batch; per-case tokens not separately metered. See batch token_usage.json.'}
    write_json(output/'metrics.json',r);write_json(output/'per_slice_metrics.json',per_slice)
    diff=np.zeros(g.shape[:3],np.uint8);diff[(mp>0)&~gu]=1;diff[gu&~(mp>0)]=2;diff[(mp>0)&gu]=3
    h=g.header.copy();h.set_data_shape(g.shape[:3]);h.set_data_dtype('uint8');h.set_intent('none')
    nib.save(nib.Nifti1Image(diff,g.affine,h),output/'union_difference.nii.gz')
    # Render overlays on ORIGINAL source grid; retain full-reference metrics independently.
    mg,_=map_array(gu,g.affine,p.shape,p.affine);mn,_=map_array(gn,g.affine,p.shape,p.affine)
    source=nib.load(next((run/'input').glob('*.nii.gz'))).get_fdata()
    counts=[int(np.count_nonzero((pu[:,:,k])^(mg[:,:,k]>0))) for k in range(p.shape[2])]
    render_comparison(source,pu,mg>0,pn,mn>0,output,m['case'])
    for group,indices in [('all_slice_differences',list(range(p.shape[2])))]:
        cols=min(5,len(indices));rows=(len(indices)+cols-1)//cols
        fig,axes=plt.subplots(rows,cols,figsize=(cols*3.2,rows*3.2),squeeze=False)
        for ax in axes.flat:ax.axis('off')
        for ax,k in zip(axes.flat,indices):
            ax.imshow(source[:,:,k].T,cmap='gray',origin='upper',vmin=np.percentile(source,1),vmax=np.percentile(source,99.8))
            overlays=[(pu[:,:,k],'lime'),(mg[:,:,k]>0,'cyan'),(pn[:,:,k],'red'),(mn[:,:,k]>0,'orange')]
            for mask,color in overlays:
                if mask.any():ax.contour(mask.T,levels=[.5],colors=[color],linewidths=.8)
            ax.set_title(f'Native k={k}; disagree={counts[k]} vox',fontsize=9)
        fig.suptitle(m['case']+' | Astra green / human cyan | nipples red / orange',fontsize=11)
        fig.tight_layout();fig.savefig(output/(group+'.png'),dpi=120);plt.close(fig)
    write_case_report(output,m['case'])
    return r

def summarize(results):
    output={'case_count':len(results),'cases':[r['case'] for r in results],'metrics':{}}
    for scope in ['full_reference_grid','common_field_of_view']:
        output['metrics'][scope]={}
        for region in ['breast_exclusive','nipple','breast_nipple_union']:
            rows=[r[scope][region] for r in results];valid=[v['dice'] for v in rows if v['dice'] is not None]
            denom=sum(v['prediction_voxels']+v['human_voxels'] for v in rows)
            denom_mm=sum((v['prediction_voxels']+v['human_voxels'])*v['voxel_volume_mm3'] for v in rows)
            output['metrics'][scope][region]={'valid_dice_count':len(valid),'missing_dice_count':len(rows)-len(valid),
               'mean_dice':float(np.mean(valid)) if valid else None,'median_dice':float(np.median(valid)) if valid else None,
               'std_dice_sample':float(np.std(valid,ddof=1)) if len(valid)>1 else None,
               'min_dice':min(valid) if valid else None,'max_dice':max(valid) if valid else None,
               'pooled_voxel_dice':2*sum(v['true_positive_voxels'] for v in rows)/denom if denom else None,
               'pooled_volume_weighted_dice':2*sum(v['true_positive_voxels']*v['voxel_volume_mm3'] for v in rows)/denom_mm if denom_mm else None,
               'total_prediction_volume_ml':sum(v['prediction_volume_ml'] for v in rows),
               'total_human_volume_ml':sum(v['human_volume_ml'] for v in rows),
               'total_false_positive_volume_ml':sum(v['false_positive_volume_ml'] for v in rows),
               'total_false_negative_volume_ml':sum(v['false_negative_volume_ml'] for v in rows)}
    distances=[r['nipple_localization']['distance_mm'] for r in results if r['nipple_localization']['distance_mm'] is not None]
    output['nipple_centroid_distance_mm']={'valid_count':len(distances),'missing_count':len(results)-len(distances),
       'mean':float(np.mean(distances)) if distances else None,'median':float(np.median(distances)) if distances else None,
       'std_sample':float(np.std(distances,ddof=1)) if len(distances)>1 else None,
       'min':min(distances) if distances else None,'max':max(distances) if distances else None,
       'p95':float(np.percentile(distances,95)) if distances else None}
    return output

def batch_report(batch):
    batch=Path(batch);config=json.loads((batch/'batch.json').read_text());encodings=json.loads((batch/'reference_encodings.json').read_text())
    results=[];failures=[]
    for item in config['cases']:
        try:
            r=score_case(item['run'],encodings[item['case']]['encoding']);results.append(r)
            print(r['case'],r['full_reference_grid']['breast_exclusive']['dice'],r['nipple_localization']['distance_mm'],flush=True)
        except Exception as e:failures.append({'case':item['case'],'error':str(e)})
    pilot=Path(config['pilot_run']);pm=json.loads((pilot/'manifest.json').read_text())
    # Existing pilot freeze and review are preserved. Report into the batch, not over original outputs.
    try:results.append(score_case(pilot,'scalar',batch/'QIN-BREAST-01-0003'))
    except Exception as e:failures.append({'case':'QIN-BREAST-01-0003','error':str(e)})
    results.sort(key=lambda r:r['case'])
    totals={'all_11_cases':summarize(results),'new_10_cases':summarize([r for r in results if not r['case'].endswith('0003')]),
        'excluding_development_0031':summarize([r for r in results if not r['development_case']]),
        'new_cases_excluding_development_0031':summarize([r for r in results if not r['development_case'] and not r['case'].endswith('0003')])}
    result={'status':'complete' if not failures and len(results)==11 else 'partial','requested_cases':11,'scored_cases':len(results),'failures':failures,'cases':results,'totals':totals,
        'metric_definitions':{'breast_exclusive':'breast minus nipple in both encodings','nipple':'nipple segment','breast_nipple_union':'breast OR nipple','mean_dice':'unweighted arithmetic mean across nonempty comparisons','pooled_voxel_dice':'2*sum(TP)/(sum prediction voxels + sum human voxels)','hd95':'maximum of directed 95th-percentile nearest surface-voxel-centre distances','ASSD':'mean of the two directed mean distances; surface voxel centres in RAS mm'},
        'notes':['Case 0031 is a skill development example, not held out.','Pilot case 0003 was scored before this batch; its results were already visible to the agent.','All aggregate groups report explicit denominators; missing metrics are not replaced with zero.']}
    write_json(batch/'all_metrics.json',result);write_json(batch/'totals.json',totals)
    rows=[]
    for r in results:
        rows.append({'case':r['case'],'development_case':r['development_case'],
          'breast_dice':r['full_reference_grid']['breast_exclusive']['dice'],'union_dice':r['full_reference_grid']['breast_nipple_union']['dice'],
          'nipple_dice':r['full_reference_grid']['nipple']['dice'],'nipple_centroid_distance_mm':r['nipple_localization']['distance_mm'],
          'breast_dice_common_fov':r['common_field_of_view']['breast_exclusive']['dice'],
          'human_outside_source_voxels':r['geometry']['human_foreground_outside_source'],'report':r['case']+'/report.html'})
    write_json(batch/'metrics_per_case.json',rows)
    body=['# Human vs Astra: evaluation batch','',f'Status: {result["status"]}. Scored {len(results)}/11 cases.','',
      '| Case | Breast Dice | Union Dice | Nipple Dice | Nipple distance mm |','|---|---:|---:|---:|---:|']
    for r in rows:body.append(f'| [{r["case"]}]({r["report"]}) | {format_number(r["breast_dice"])} | {format_number(r["union_dice"])} | {format_number(r["nipple_dice"])} | {format_number(r["nipple_centroid_distance_mm"],2)} |')
    body+=['','## Aggregate results','']
    for name,t in totals.items():
        body += [f'### {name} (n={t["case_count"]})','',f'- Mean breast Dice: {format_number(t["metrics"]["full_reference_grid"]["breast_exclusive"]["mean_dice"])}',
          f'- Mean nipple Dice: {format_number(t["metrics"]["full_reference_grid"]["nipple"]["mean_dice"])}',f'- Mean nipple centroid distance: {format_number(t["nipple_centroid_distance_mm"]["mean"],2)} mm','']
    body += ['## Interpretation and limitations','',*['- '+n for n in result['notes']],
      '- Full-reference results penalize human labels outside source coverage; common-field-of-view scores are also provided.',
      '- See per-case reports for volume bias, false positives/negatives, boundary distances, centroids, geometry and every-slice comparisons.',
      '- Token usage is recorded in token_usage.json; per-case token attribution is unavailable because this is one shared agent batch.',
      '- all_metrics.json contains every case, per-slice data and aggregate statistics. totals.json and metrics_per_case.json are compact views.']
    (batch/'report.md').write_text('\n'.join(body),encoding='utf-8')
    table='<table><tr><th>Case</th><th>Breast Dice</th><th>Nipple Dice</th><th>Centroid mm</th></tr>'
    for r in rows:table+=f'<tr><td><a href="{r["report"]}">{r["case"]}</a></td><td>{format_number(r["breast_dice"])}</td><td>{format_number(r["nipple_dice"])}</td><td>{format_number(r["nipple_centroid_distance_mm"],2)}</td></tr>'
    table+='</table>'
    (batch/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Astra evaluation</title><style>body{font:16px system-ui;max-width:1100px;margin:32px auto;padding:20px;color:#142333}td,th{text-align:left;padding:10px;border-bottom:1px solid #ccd}pre{white-space:pre-wrap}a{color:#096b9e}</style><h1>Human vs Astra evaluation</h1>'+table+'<pre>'+html.escape('\n'.join(body[17:]))+'</pre>',encoding='utf-8')
    print('STATUS',result['status'],failures)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--batch',type=Path);a=parser.parse_args()
    batch_report(a.batch or Path((Path(__file__).parent/'latest_batch.txt').read_text()))
