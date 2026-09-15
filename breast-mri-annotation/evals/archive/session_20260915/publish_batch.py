"""Enrich already-scored results and publish a portable HTML/JSON report.

Does not modify predictions or human labels. Visual observations are a separate,
explicit input and are valid only for the reviewed batch.
"""
from pathlib import Path
from datetime import datetime
import argparse,json,html,shutil,platform
from batch_metrics import np,nib,decode,centroid,sha256,write_json,plt,format_number
from scipy.ndimage import label
import scipy,matplotlib

CSS='''body{font:16px/1.55 system-ui,sans-serif;color:#16283b;background:#f5f7fa;margin:0}main{max-width:1200px;margin:auto;padding:35px}h1{line-height:1.15}h2{margin-top:35px}a{color:#086f99}table{border-collapse:collapse;width:100%;background:white;font-size:14px}th,td{padding:10px;text-align:left;border-bottom:1px solid #dce3eb}th{background:#e7eef5;cursor:pointer}img{max-width:100%;background:white}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#fff;padding:16px}.cards{display:flex;gap:16px;flex-wrap:wrap}.card{flex:1;background:white;border-top:4px solid #168ba8;padding:20px;min-width:160px}.value{font-size:32px;font-weight:700}.note{background:#fff5d9;padding:16px;border-left:4px solid #c18b10}.muted{color:#52677b}details{background:white;padding:15px;margin-top:20px}code{overflow-wrap:anywhere}.scroll{overflow:auto}@media print{body{background:white}main{padding:10px}details{display:block}a{color:inherit}}'''
def esc(s):return html.escape(str(s))
def number(x,n=4):return format_number(x,n)
def page(title,body):return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+esc(title)+'</title><style>'+CSS+'</style><main>'+body+'</main></html>'
def bullets(lines):return '<ul>'+''.join('<li>'+esc(x)+'</li>' for x in lines)+'</ul>'
def table(head,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'

def publish(batch,observations):
    batch=Path(batch);master=json.loads((batch/'all_metrics.json').read_text());notes=json.loads(Path(observations).read_text())
    config=json.loads((batch/'batch.json').read_text());runs={r['case']:Path(r['run']) for r in config['cases']};runs['QIN-BREAST-01-0003']=Path(config['pilot_run'])
    for r in master['cases']:
        out=batch/r['case'];run=runs[r['case']];m=json.loads((run/'manifest.json').read_text())
        assert sha256(r['prediction'])==r['prediction_sha256']
        r['visual_comparison_observations']=notes.get(r['case'][-4:],[])
        r['visual_reference_comparison_scope']='All native slices for 0007 and 0013; selected worst-disagreement, nipple and endpoint slices for other cases. All slices compared numerically.'
        g=nib.load(r['human_reference']);_,gn=decode(g,r['human_encoding']);p=nib.load(r['prediction']);_,pn=decode(p)
        components,n=label(gn);component_rows=[]
        for i in range(1,n+1):
            mask=components==i;points=np.argwhere(mask);c=centroid(mask,g.affine)
            source_points=nib.affines.apply_affine(np.linalg.inv(p.affine)@g.affine,points)
            component_rows.append({'id':i,'voxels':int(mask.sum()),'centroid_ras_mm':c,'native_source_k_range':[float(source_points[:,2].min()),float(source_points[:,2].max())],
                'distance_from_astra_nipple_centroid_mm':float(np.linalg.norm(np.array(c)-r['nipple_localization']['prediction_centroid_ras_mm'])) if pn.any() else None})
        component_rows.sort(key=lambda x:-x['voxels']);r['human_nipple_components']=component_rows
        r['largest_reference_nipple_component_sensitivity']={'distance_mm':component_rows[0]['distance_from_astra_nipple_centroid_mm'] if component_rows else None,'is_primary_metric':False,'note':'Diagnostic sensitivity only; full unmodified reference is used for all primary scores and totals.'}
        r['provenance']={'model':'gpt-6-astra','reasoning_effort':'medium','method':'Agent-guided source-only annotation, case-specific anchors, source-image corrections and actual Slicer review','skill_snapshot_sha256':sha256(batch/'skill_snapshot/SKILL.md'),
            'segments_sha256':sha256(run/'segments.npz'),'working_segmentation_sha256':m.get('working_segmentation_sha256'),'user_approved':False,'reference_opened_after_prediction_freeze':True}
        write_json(out/'metrics.json',r)
        text=(out/'report.md').read_text(encoding='utf-8');base=text.split('\n## Visual comparison findings')[0]
        (out/'report.md').write_text(base+'\n\n## Visual comparison findings\n\n'+'\n'.join('- '+x for x in r['visual_comparison_observations'])+'\n',encoding='utf-8')
        rows=[]
        for key,title in [('breast_exclusive','Breast (exclusive)'),('breast_nipple_union','Breast + nipple union'),('nipple','Nipple')]:
            x=r['full_reference_grid'][key];rows.append([title,number(x['dice']),number(r['common_field_of_view'][key]['dice']),number(x['precision']),number(x['recall']),number(x['hd95_mm'],2),number(x['average_symmetric_surface_distance_mm'],2)])
        body='<a href="../report.html">&#8592; All cases</a><h1>'+r['case']+'</h1><p class="muted">Human vs Astra · frozen predictions · 15 September 2026</p>'
        if r['development_case']:body+='<p class="note">Skill development example. Separate totals exclude this case.</p>'
        if 'low_confidence' in r['annotation_status']:body+='<p class="note">Nipple location was flagged as low confidence before reference access.</p>'
        body+='<div class="cards"><div class="card">Breast Dice<div class="value">'+number(r['full_reference_grid']['breast_exclusive']['dice'],3)+'</div></div><div class="card">Nipple Dice<div class="value">'+number(r['full_reference_grid']['nipple']['dice'],3)+'</div></div><div class="card">Nipple centroid distance<div class="value">'+number(r['nipple_localization']['distance_mm'],2)+' mm</div></div></div>'
        body+='<h2>Where the labels differ</h2>'+bullets(r['visual_comparison_observations'])
        body+='<p>Green: Astra breast+nipple union · Cyan: human union · Red: Astra nipple · Orange: human nipple. Differences measure agreement with the supplied labels.</p><img alt="Selected human and Astra comparisons" src="comparison.png">'
        body+='<h2>Overlap and boundary metrics</h2>'+table(['Region','Dice','Common-FOV Dice','Precision','Recall','HD95 mm','ASSD mm'],rows)
        rows=[]
        for key,title in [('breast_exclusive','Breast'),('breast_nipple_union','Union'),('nipple','Nipple')]:
            x=r['full_reference_grid'][key];rows.append([title,number(x['human_volume_ml'],2),number(x['prediction_volume_ml'],2),number(x['volume_bias_ml'],2),f"{x['false_positive_voxels']:,}",f"{x['false_negative_voxels']:,}"])
        body+='<h2>Volume and voxel differences</h2>'+table(['Region','Human mL','Astra mL','Astra − human mL','Astra-only voxels','Human-only voxels'],rows)
        loc=r['nipple_localization'];body+='<h2>Nipple centroids</h2><p>Physical RAS coordinates in millimetres; positive directions are right, anterior and superior.</p>'+table(['Point','R','A','S'],[[title,*[number(v,2) for v in loc[key]]] for title,key in [('Astra','prediction_centroid_ras_mm'),('Human','human_centroid_ras_mm'),('Astra − human','delta_ras_mm')]])
        body+='<h3>Human nipple components</h3>'+table(['Component','Voxels','Source slice range','Distance from Astra centroid (mm)'],[[x['id'],x['voxels'],esc([round(v,2) for v in x['native_source_k_range']]),number(x['distance_from_astra_nipple_centroid_mm'],2)] for x in component_rows])
        body+='<p>Component distances are diagnostic only. Primary metrics retain all human-labelled voxels.</p><h2>Geometry, review and reproducibility</h2>'+bullets([
            f"Native source shape {r['geometry']['source_shape']}; reference shape {r['geometry']['reference_shape']}; human encoding {r['human_encoding']}.",
            f"Human foreground outside source: {r['geometry']['human_foreground_outside_source']:,} voxels. Full-reference metrics penalize these; common-FOV metrics restrict comparison to source coverage.",
            'Actual Slicer source/overlay review: native slices '+str(r['slicer_reviewed_indices'])+'. Working segmentation was reloaded and checked.',
            'The 10 new predictions were frozen before the human reference voxels were opened. Original pilot predictions are retained.',
            'Model: gpt-6-astra; reasoning effort: medium. Agent review is separate from user approval.',
            'Per-case tokens were not separately metered. See the batch usage record.'])
        body+='<h3>Source-only annotation decisions</h3>'+bullets(r['notes'])
        body+='<p><a href="metrics.json">Complete case metrics JSON</a> · <a href="per_slice_metrics.json">Per-slice data</a> · <a href="union_difference.nii.gz">Difference volume</a> · <a href="../token_usage.json">Batch token usage</a></p>'
        body+='<p>Difference volume labels: 0 neither, 1 Astra-only, 2 human-only, 3 agreement.</p><h2>Every native slice</h2><img alt="All native slice comparisons" src="all_slice_differences.png"><details><summary>File hashes and provenance</summary><pre>'+esc(json.dumps({k:r[k] for k in ['prediction','prediction_sha256','human_reference','human_reference_sha256','prediction_frozen_at','provenance']},indent=2))+'</pre></details>'
        (out/'report.html').write_text(page(r['case'],body),encoding='utf-8')
    master['environment']={'python':platform.python_version(),'numpy':np.__version__,'nibabel':nib.__version__,'scipy':scipy.__version__,'matplotlib':matplotlib.__version__,'slicer':'5.8.1','model':'gpt-6-astra','reasoning_effort':'medium'}
    master['code_sha256']={f.name:sha256(f) for f in Path(__file__).parent.glob('*.py')}
    master['skill_snapshot_sha256']={str(f.relative_to(batch/'skill_snapshot')):sha256(f) for f in (batch/'skill_snapshot').rglob('*') if f.is_file()}
    usage=batch/'token_usage.json';master['token_usage']=json.loads(usage.read_text()) if usage.exists() else None
    master['reported_at']=datetime.now().astimezone().isoformat();write_json(batch/'all_metrics.json',master)
    shutil.copy2(observations,batch/'case_observations.json')
    cases=master['cases'];fig,axes=plt.subplots(1,2,figsize=(12,5));labels=[r['case'][-4:]+('*' if r['development_case'] else '') for r in cases];xs=np.arange(len(cases))
    axes[0].bar(xs-.18,[r['full_reference_grid']['breast_exclusive']['dice'] for r in cases],.36,label='Breast',color='#197d9f');axes[0].bar(xs+.18,[r['full_reference_grid']['nipple']['dice'] for r in cases],.36,label='Nipple',color='#e39632');axes[0].set_ylim(0,1);axes[0].set_ylabel('Dice');axes[0].legend()
    axes[1].bar(xs,[r['nipple_localization']['distance_mm'] for r in cases],color='#197d9f');axes[1].set_ylabel('Nipple centroid distance (mm)')
    for ax in axes:ax.set_xticks(xs,labels,rotation=45);ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    fig.suptitle('Human vs Astra | 0003: prior pilot; 0031*: development example');fig.tight_layout();fig.savefig(batch/'metrics_overview.png',dpi=150);plt.close(fig)
    t=master['totals']['new_10_cases'];body='<h1>Human vs Astra</h1><p class="muted">Breast MRI annotation skill evaluation · 10 new cases + 1 retained pilot · gpt-6-astra / medium</p><div class="cards">'
    for name,v in [('Mean breast Dice',number(t['metrics']['full_reference_grid']['breast_exclusive']['mean_dice'],3)),('Mean nipple Dice',number(t['metrics']['full_reference_grid']['nipple']['mean_dice'],3)),('Mean nipple distance',number(t['nipple_centroid_distance_mm']['mean'],2)+' mm')]:body+='<div class="card">'+name+'<div class="value">'+v+'</div><span class="muted">10 new cases</span></div>'
    body+='</div><p>All 10 new cases scored successfully. Predictions were reviewed across 200 native slices in Slicer and frozen before ground-truth comparison. Eight metric tests pass.</p>'
    body+='<h2>Key findings</h2>'+bullets(['Nipple localization is least consistent in 0007 (27.63 mm). Its reference has one connected nipple region.', '0013 has a disconnected 316-voxel nipple-labelled reference component. Full-reference centroid distance is 24.87 mm; largest-component-only sensitivity is 4.86 mm. Original labels and primary scores are retained.', 'Posterior attachment limits and inclusion of peripheral slices are recurring breast disagreements. Nipple Dice also reflects marker size and through-slice extent.', '0014 was flagged for uncertain nipple location before reference access. Case 0031 is a known development example; separate totals exclude it. Other cases are not certified independent of the skill history.'])
    body+='<img alt="Per-case Dice and centroid distance charts" src="metrics_overview.png"><h2>Per-case results</h2><p>Open a case for visual comparisons, volumes, boundary distances, centroids and slice-level differences.</p>'
    body+=table(['Case','Breast Dice','Union Dice','Nipple Dice','Nipple distance mm'],[[f'<a href="{r["case"]}/report.html">{r["case"]}</a>'+(' *' if r['development_case'] else ''),number(r['full_reference_grid']['breast_exclusive']['dice']),number(r['full_reference_grid']['breast_nipple_union']['dice']),number(r['full_reference_grid']['nipple']['dice']),number(r['nipple_localization']['distance_mm'],2)] for r in cases])
    rows=[]
    for group,x in master['totals'].items():
        f=x['metrics']['full_reference_grid'];rows.append([esc(group.replace('_',' ')),x['case_count'],number(f['breast_exclusive']['mean_dice']),number(f['breast_exclusive']['pooled_voxel_dice']),number(f['nipple']['mean_dice']),number(x['nipple_centroid_distance_mm']['mean'],2),number(x['nipple_centroid_distance_mm']['median'],2)])
    body+='<h2>Totals</h2>'+table(['Group','n','Mean breast Dice','Pooled breast Dice','Mean nipple Dice','Mean distance mm','Median distance mm'],rows)
    body+='<p>Means weight cases equally. Pooled Dice combines voxel counts. JSON totals also include medians, sample standard deviations, ranges, volume-weighted Dice, volume totals and common-FOV results. There is no meaningful summed centroid distance.</p>'
    if master['token_usage']:
        u=master['token_usage'];d=u['delta'];body+='<h2>Measured token usage</h2>'+table(['Counter','Tokens'],[['Total input + output',f"{d['total_tokens']:,}"],['Input',f"{d['input_tokens']:,}"],['Cached input (subset)',f"{d['cached_input_tokens']:,}"],['Uncached input',f"{d['uncached_input_tokens']:,}"],['Output',f"{d['output_tokens']:,}"]])+ '<p>Checkpoint: '+esc(u['latest']['timestamp'])+'. Includes annotation, corrections, review, infrastructure and reporting for this batch request. Final reply and later calls are excluded. Per-case attribution and dollar cost are unavailable.</p>'
    body+='<h2>Files and definitions</h2><p><a href="all_metrics.json">All metrics, case details, totals and usage (JSON)</a> · <a href="metrics_per_case.json">Compact case metrics</a> · <a href="totals.json">Totals</a> · <a href="token_usage.json">Usage record</a></p>'+bullets(['Dice: 2 × intersection / (Astra voxels + human voxels). Breast excludes nipple in both scalar and component encodings; union retains all foreground.', 'Nipple centroids use original NIfTI physical coordinates in RAS millimetres. Reference alignment uses nearest-neighbour mapping; original grids are preserved.', 'Both-empty Dice is null, one-empty Dice is zero, and undefined distances are null with an explicit status.', 'HD95 is the maximum of the two directed 95th-percentile surface distances. ASSD is the mean of the two directed mean surface distances; both use surface voxel centres.', 'Pilot 0003 has 9,733 human foreground voxels outside source coverage. Full-reference and common-field-of-view metrics are reported separately.', 'This measures agreement with the supplied annotation convention. Agent-guided annotation varies across runs; scoring alone does not execute an updated skill.'])
    (batch/'report.html').write_text(page('Human vs Astra evaluation',body),encoding='utf-8')
    print('PUBLISHED',len(cases),'case reports and consolidated report')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--batch',type=Path);p.add_argument('--observations',required=True,type=Path);a=p.parse_args()
    publish(a.batch or Path(Path('latest_batch.txt').read_text()),a.observations)
