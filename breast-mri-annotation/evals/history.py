"""Append evaluation history and render its README table; never invent scores."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
HISTORY=ROOT/'evals/history.json'
BEGIN='<!-- evaluation-history:start -->'
END='<!-- evaluation-history:end -->'

def fingerprint(folder):
    entries=[]
    # Path ordering is case-insensitive on Windows, case-sensitive on Linux.
    # Sort normalized relative strings explicitly for identical fingerprints.
    for f in sorted(folder.rglob('*'),key=lambda p:p.relative_to(folder).as_posix()):
        rel=f.relative_to(folder)
        if not f.is_file() or any(x in rel.parts for x in ['__pycache__','.deps','.venv','results','runs','batches','archive','data']):continue
        if f.name=='history.json':continue
        if f.suffix not in ['.py','.md','.json','.txt']:continue
        entries.append((rel.as_posix(),hashlib.sha256(f.read_bytes().replace(b'\r\n',b'\n')).hexdigest()))
    return hashlib.sha256(json.dumps(entries,separators=(',',':')).encode()).hexdigest()

def current():
    extra=[]
    for file in [ROOT/'README.md',ROOT.parent/'.github/workflows/breast-mri-evals.yml']:
        if file.exists():
            content=file.read_text(encoding='utf-8')
            if BEGIN in content and END in content:
                content=content.split(BEGIN)[0]+BEGIN+END+content.split(END)[1]
            extra.append(content)
    digest=hashlib.sha256(json.dumps([fingerprint(ROOT/'evals'),extra]).encode()).hexdigest()
    return {'skill_sha256':fingerprint(ROOT/'skill'),'evals_sha256':digest}

def render(records):
    lines=['| Date / run | Change | Status | n | Breast Dice ↑ | Union Dice ↑ | Nipple Dice ↑ | Nipple distance mm ↓ |',
           '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for r in records:
        s=r.get('summary');vals=[str(s['case_count']),*[f'{s[k]:.4f}' for k in ['breast_dice','union_dice','nipple_dice']],f"{s['nipple_distance_mm']:.2f}"] if s else ['—']*5
        title=r['id'];title=f"[{title}]({r['result']})" if r.get('result') else title
        lines.append('| '+' | '.join([title,r['change'].replace('|','/').replace('\n',' '),r['status'],*vals])+' |')
    return '\n'.join(lines)

def update(check=False,base=None):
    records=json.loads(HISTORY.read_text());readme=ROOT/'README.md';text=readme.read_text(encoding='utf-8')
    a,b=text.split(BEGIN,1);_,c=b.split(END,1);new=a+BEGIN+'\n\n'+render(records)+'\n\n'+END+c
    if check:
        if base and set(base)!={'0'}:
            path='breast-mri-annotation/evals/history.json'
            old=subprocess.run(['git','show',f'{base}:{path}'],cwd=ROOT,capture_output=True,text=True)
            if old.returncode==0:
                prior=json.loads(old.stdout)
                assert records[:len(prior)]==prior,'Existing history entries must remain unchanged; append a new entry'
            else:
                valid=subprocess.run(['git','cat-file','-e',base+'^{commit}'],cwd=ROOT,capture_output=True)
                assert valid.returncode==0,'Cannot verify history: base commit is unavailable'
        assert new==text,'README metrics table is stale; run history.py render'
        assert any(all(r.get(k)==v for k,v in current().items()) for r in records),'Skill/evals changed without a matching history entry. Add a pending entry or a newly measured evaluation.'
    else:readme.write_text(new,encoding='utf-8')

def add(args):
    records=json.loads(HISTORY.read_text())
    if any(r['id']==args.id for r in records):raise ValueError('Run IDs are immutable; choose a new ID')
    r={'id':args.id,'date':datetime.now(timezone.utc).isoformat(),'change':args.change,'status':'pending evaluation',**current()}
    if args.result:
        path=args.result.resolve();path.relative_to((ROOT/'evals/results').resolve())
        data=json.loads(path.read_text());assert data['status']=='evaluated'
        assert data['cohort']=='human-user-10' and data['totals']['case_count']==10
        assert data['fingerprints']==current(),'Result belongs to another skill/evals version'
        t=data['totals'];f=t['metrics']['full_reference_grid']
        r.update(status='evaluated',result=path.relative_to(ROOT).as_posix(),summary={'case_count':10,'breast_dice':f['breast_exclusive']['mean_dice'],'union_dice':f['breast_nipple_union']['mean_dice'],'nipple_dice':f['nipple']['mean_dice'],'nipple_distance_mm':t['nipple_centroid_distance_mm']['mean']})
    records.append(r);HISTORY.write_text(json.dumps(records,indent=2)+'\n');update()

if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    c=sub.add_parser('check');c.add_argument('--base');sub.add_parser('render')
    a=sub.add_parser('add');a.add_argument('--id',required=True);a.add_argument('--change',required=True);a.add_argument('--result',type=Path)
    args=p.parse_args()
    if args.command=='add':add(args)
    else:update(args.command=='check',getattr(args,'base',None))
