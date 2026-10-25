"""AURA Stage 6 import adapter for published Agent-Diff benchmark contracts.

Source schema in upstream datasets/agent-diff-bench/{train,test}.jsonl:
  {question, answer: JSON_STRING({assertions,ignore_fields}), test_id, service...}

This adapter evaluates *provided* finite diff fixtures under a documented
subset of the upstream DSL. It neither executes Agent-Diff nor claims official
benchmark score equivalence. Unrecognized clauses yield UNCERTAIN, never PASS.
"""
from __future__ import annotations
from dataclasses import dataclass
import json, re
from pathlib import Path

class ExternalContractError(ValueError):pass

VALID_DIFF_TYPES={'added','changed','deleted'}
VALID_OPS={'eq','ne','contains','regex'}

@dataclass(frozen=True)
class ParsedContract:
    test_id:str
    service:str
    assertions:tuple[dict,...]
    ignore_fields:dict
    unsupported:tuple[str,...]
    metadata:dict

def load_jsonl_tasks(path):
    """Import genuine published JSONL when supplied by the researcher (offline)."""
    with Path(path).open(encoding='utf-8') as f:
        for line_no,line in enumerate(f,1):
            if line.strip():
                try:yield json.loads(line)
                except json.JSONDecodeError as e:raise ExternalContractError(f'invalid JSONL at line {line_no}') from e

def parse_agentdiff_task(raw):
    if not isinstance(raw,dict) or not isinstance(raw.get('test_id'),str) or not isinstance(raw.get('service'),str):
        raise ExternalContractError('invalid task identifiers')
    answer=raw.get('answer')
    if isinstance(answer,str):
        try: answer=json.loads(answer)
        except json.JSONDecodeError as e:raise ExternalContractError('invalid answer JSON') from e
    if not isinstance(answer,dict) or not isinstance(answer.get('assertions'),list):
        raise ExternalContractError('missing assertions')
    assertions=[];unsupported=[]
    for index,a in enumerate(answer['assertions']):
        if not isinstance(a,dict):raise ExternalContractError('assertion is not object')
        if a.get('diff_type') not in VALID_DIFF_TYPES:unsupported.append(f'{index}:diff_type:{a.get("diff_type")}')
        if not isinstance(a.get('entity'),str):raise ExternalContractError('entity absent')
        for clause in (a.get('where',{}),a.get('expected_changes',{})):
            if not isinstance(clause,dict): raise ExternalContractError('conditions must be objects')
        for fld,rule in a.get('where',{}).items():
            if not isinstance(rule,dict) or len(rule)!=1 or next(iter(rule)) not in VALID_OPS:
                unsupported.append(f'{index}:where:{fld}')
        for fld,change in a.get('expected_changes',{}).items():
            if not isinstance(change,dict) or 'to' not in change or not isinstance(change['to'],dict) or len(change['to'])!=1 or next(iter(change['to'])) not in VALID_OPS:
                unsupported.append(f'{index}:expected_changes:{fld}')
        count=a.get('expected_count')
        if count is not None and (not(type(count) is int and count>=0) and not(isinstance(count,dict) and count and set(count)<={'min','max'} and all(type(v)is int and v>=0 for v in count.values()))):
            unsupported.append(f'{index}:expected_count')
        assertions.append(a)
    ignore=answer.get('ignore_fields',{})
    if not isinstance(ignore,dict):unsupported.append('ignore_fields')
    return ParsedContract(raw['test_id'],raw['service'],tuple(assertions),ignore if isinstance(ignore,dict) else {},tuple(unsupported),
       {'test_name':raw.get('test_name',''),'task_horizon':raw.get('task_horizon'), 'source':'public_agent_diff_contract', 'official_scorer':False})

def _matching_op(value,condition):
    op,expect=next(iter(condition.items()))
    if op=='eq':return type(value) is type(expect) and value==expect
    if op=='ne':return value!=expect
    if op=='contains':return isinstance(value,str) and isinstance(expect,str) and expect in value
    if op=='regex':
        if not isinstance(value,str) or not isinstance(expect,str) or len(expect)>512:return False
        try:return re.search(expect,value) is not None
        except re.error:return False
    raise ExternalContractError('unsupported comparison operator')

def _matches(diff_entry,assertion):
    if diff_entry.get('diff_type')!=assertion['diff_type'] or diff_entry.get('entity')!=assertion['entity']:
        return False
    where=diff_entry.get('where',{})
    after=diff_entry.get('after',{})
    if not isinstance(where,dict) or not isinstance(after,dict):return False
    for key,condition in assertion.get('where',{}).items():
        if key not in where or not _matching_op(where[key],condition):return False
    for key,changes in assertion.get('expected_changes',{}).items():
        if key not in after or not _matching_op(after[key],changes['to']):return False
    return True

def evaluate_synthetic_diff(task, diff_entries, *, coverage_complete, strict_frame=True):
    """Illustrative AURA-side judgment on supplied diff fixtures.

    Not the Agent-Diff native scorer. Only returns PASS with full declared
    coverage, fully supported clauses, and no unaccounted changes.
    """
    if not isinstance(task,ParsedContract):raise ExternalContractError('parsed contract required')
    if not isinstance(diff_entries,list) or any(not isinstance(d,dict) for d in diff_entries):
        raise ExternalContractError('diff_entries must be objects')
    if task.unsupported:
        return {'verdict':'UNCERTAIN','reason':'unsupported_contract_semantics', 'unsupported':list(task.unsupported)}
    failing=[]; matched_indices=set(); ambiguous=False;counts=[];field_violations=[]
    for i,a in enumerate(task.assertions):
        matches=[j for j,d in enumerate(diff_entries) if _matches(d,a)]
        unique=[j for j in matches if j not in matched_indices]
        # Disallow one mutation satisfying multiple unrelated assertions.
        if len(unique)!=len(matches):ambiguous=True
        n=len(unique);counts.append(n)
        target=a.get('expected_count')
        if target is None:
            # A missing cardinality is ambiguous when multiple matching mutations exist.
            # Do not treat a duplicate as certified by an existential predicate.
            if n>1:ambiguous=True
            passed=n>=1
        elif type(target) is int:
            passed=n==target
        else:
            passed=n>=target.get('min',0) and n<=target.get('max',10**9)
        if not passed:failing.append({'assertion':i,'matched':n,'expected_count':target})
        matched_indices.update(unique)
        if a.get('diff_type')=='changed':
            allowed=set(a.get('expected_changes',{})) | set(task.ignore_fields.get('global',[]))
            for j in unique:
                extras=set(diff_entries[j].get('after',{}))-allowed
                if extras: field_violations.append({'assertion':i,'diff_index':j,'extra_fields':sorted(extras)})
    residue=sorted(set(range(len(diff_entries)))-matched_indices)
    # Known unsupported assert overlapping is not a sound proof.
    if ambiguous:
        return {'verdict':'UNCERTAIN','reason':'overlapping_assertions_need_exact_matching','matched_counts':counts}
    # Positive witnesses of illegal mutations or excess cardinality establish FAIL.
    # Missing mutations cannot prove FAIL when only an incomplete diff was inspected.
    excess=[f for f in failing if f['matched']> (f['expected_count'] if type(f['expected_count']) is int else f['expected_count'].get('max',10**9) if isinstance(f['expected_count'],dict) else 10**9)]
    if field_violations or (strict_frame and residue) or excess or (coverage_complete and failing):
        return {'verdict':'FAIL','reason':'assertion_or_frame_violation','failed_assertions':failing,'unaccounted_mutations':residue,'unexpected_changed_fields':field_violations,'matched_counts':counts}
    if not coverage_complete:
        return {'verdict':'UNCERTAIN','reason':'incomplete_mutation_scope','matched_counts':counts,'possible_residue':residue,'unconfirmed_missing_assertions':failing}
    return {'verdict':'PASS','reason':'supported_subset_with_complete_diff','matched_counts':counts,'unaccounted_mutations':[]}
