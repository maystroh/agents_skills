"""Read only usage counters from an explicitly supplied Codex task rollout."""
import argparse,json
from datetime import datetime
from pathlib import Path

def extract(path, marker='run it on the rest of the cases'):
    previous=baseline=latest=None
    request_at=None
    for line in Path(path).open(encoding='utf-8'):
        try: event=json.loads(line)
        except ValueError: continue
        p=event.get('payload',{})
        if event.get('type')=='response_item' and p.get('role')=='user':
            content=' '.join(str(c.get('text','')) for c in p.get('content',[]) if isinstance(c,dict))
            if marker in content and request_at is None:
                baseline=previous;request_at=event.get('timestamp')
        if p.get('type')=='token_count' and p.get('info'):
            previous={'timestamp':event.get('timestamp'),'usage':p['info']['total_token_usage']}
            latest=previous
    delta=None
    if baseline and latest:
        delta={k:v-baseline['usage'].get(k,0) for k,v in latest['usage'].items()}
        if any(v<0 for v in delta.values()):raise ValueError('Counter reset; cannot subtract reliably')
        delta['uncached_input_tokens']=delta['input_tokens']-delta.get('cached_input_tokens',0)
    return {'scope':'This batch request, including infrastructure, annotation, review, reporting, and tool context',
        'status':'measured_so_far' if delta is not None else 'unavailable',
        'request_at':request_at,'baseline':baseline,'latest':latest,'delta':delta,
        'recorded_at':datetime.now().astimezone().isoformat(),
        'notes':['Cached input is a subset of input; reasoning output is a subset of output. Do not add them again.',
        'Token totals count repeated context across requests. This is not a unique-text count.',
        'The last response and subsequent calls are not included until a later counter event.',
        'Dollar cost is unavailable from these counters and is not inferred from subscription quota.'],
        'cost_usd':None}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rollout',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();r=extract(a.rollout);Path(a.output).write_text(json.dumps(r,indent=2));print(json.dumps({'status':r['status'],'delta':r['delta']}))
