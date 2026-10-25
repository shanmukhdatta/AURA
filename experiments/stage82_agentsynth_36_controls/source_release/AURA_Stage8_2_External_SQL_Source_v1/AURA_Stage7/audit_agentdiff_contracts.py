"""Static coverage audit for upstream published Agent-Diff JSONL contracts.

Usage (network-accessible computer; download JSONL yourself from upstream GitHub):
 python audit_agentdiff_contracts.py --jsonl all_numbered.jsonl --out audit.json

NO agent execution, no state snapshots, no native benchmark scoring.
"""
from __future__ import annotations
import argparse, json, hashlib
from collections import Counter
from pathlib import Path
from aura_external.agentdiff import load_jsonl_tasks,parse_agentdiff_task

def audit(path):
    data=Path(path).read_bytes(); counts=Counter();examples=[]
    for row in load_jsonl_tasks(path):
        counts['total_tasks']+=1
        try:
            task=parse_agentdiff_task(row)
            counts['parsed_tasks']+=1
            counts['service_'+task.service]+=1
            counts['assertions']+=len(task.assertions)
            if task.unsupported:
                counts['unsupported_tasks']+=1
                for code in task.unsupported: counts['unsupported_clause_'+code.split(':',2)[-1]]+=1
                if len(examples)<12:examples.append({'id':task.test_id,'service':task.service,'unsupported':task.unsupported})
            else:
                counts['syntactically_supported_tasks']+=1
        except Exception as exc:
            counts['invalid_or_unparsed_tasks']+=1
            if len(examples)<12: examples.append({'id':row.get('test_id'), 'error_type':type(exc).__name__})
    return {'source_file':Path(path).name,'source_sha256':hashlib.sha256(data).hexdigest(),
      'metrics':dict(counts),'example_unsupported':examples,
      'warning':'Parsing and static syntax support only; not a native Agent-Diff task run or verified score.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--jsonl',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();result=audit(a.jsonl)
    Path(a.out).write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result['metrics'],indent=2))
