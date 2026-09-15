"""Create immutable run inputs and a snapshot of the skill; do not read mask voxels."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
from evaluate import sha256

def prepare(dataset, skill, case):
    root = Path(__file__).parent
    folder = Path(dataset)
    source = folder / (case+'.nii.gz')
    masks = list(folder.glob(case+'_mask*.nii.gz'))
    if not source.is_file() or len(masks) != 1:
        raise ValueError('Require exactly one source and one unambiguous reference')
    run = root / 'runs' / (datetime.now().astimezone().strftime('%Y%m%d_%H%M%S')+'_'+case)
    run.mkdir(parents=True)
    (run/'input').mkdir()
    shutil.copy2(source, run/'input'/source.name)
    snapshot = run/'skill_snapshot'
    snapshot.mkdir()
    hashes = {}
    for path in sorted(Path(skill).rglob('*')):
        if path.is_file() and path.suffix in ['.md', '.py', '.json'] and '__pycache__' not in path.parts:
            rel = path.relative_to(skill)
            dest = snapshot/rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            hashes[str(rel)] = sha256(dest)
    manifest = {'case':case, 'created':datetime.now().astimezone().isoformat(),
        'source':str(source), 'source_sha256':sha256(source), 'reference':str(masks[0]),
        'reference_sha256':sha256(masks[0]), 'skill_files_sha256':hashes,
        'annotation_status':'pending', 'slicer_reviewed_indices':[],
        'reference_voxels_viewed_before_prediction':False,
        'model':'GPT-6 (agent-guided session)', 'notes':[]}
    (run/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (root/'latest_run.txt').write_text(str(run.resolve()))
    print(run.resolve())

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset',default=r'<MRI_DATA>\sagitall_annotations\skill_evals\qin')
    p.add_argument('--skill',default=r'<INSTALLED_SKILL>')
    p.add_argument('--case',default='QIN-BREAST-01-0003')
    a=p.parse_args()
    prepare(a.dataset,a.skill,a.case)
