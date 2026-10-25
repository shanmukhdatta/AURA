import json
from pathlib import Path
import pytest
from aura_external.agentdiff import parse_agentdiff_task,load_jsonl_tasks,evaluate_synthetic_diff,ExternalContractError
from aura_external.appworld import integration_status
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'examples/external/agentdiff_public_contract_excerpt.jsonl'

def samples():return [parse_agentdiff_task(x) for x in load_jsonl_tasks(FIXTURE)]

def synthesize_present(contract):
    """Authored artificial diff instances, not official benchmark rollouts."""
    ans=[]
    for a in contract.assertions:
        n=a.get('expected_count',1)
        if isinstance(n,dict):n=n.get('min',1)
        for _ in range(n):
            where={key:(value['eq'] if 'eq' in value else 'synthetic_'+str(value.get('contains',value.get('regex','ok'))))
                for key,value in a.get('where',{}).items()}
            after={}
            for key,val in a.get('expected_changes',{}).items():
                op,exp=next(iter(val['to'].items()))
                after[key]=exp if op=='eq' else ('synthetic_other_value' if op=='ne' else exp)
            ans.append({'entity':a['entity'],'diff_type':a['diff_type'],'where':where,'after':after})
    return ans

def test_public_excerpt_count():
    s=samples();assert len(s)==5;assert all(not x.unsupported for x in s)
    assert {x.test_id for x in s}=={'box_145','box_125','box_146','box_119','box_126'}

@pytest.mark.parametrize('index',range(5))
def test_public_excerpt_fixture_positive_negative(index):
    contract=samples()[index];complete=synthesize_present(contract)
    assert evaluate_synthetic_diff(contract,complete,coverage_complete=True)['verdict']=='PASS'
    assert evaluate_synthetic_diff(contract,complete[1:],coverage_complete=True)['verdict']=='FAIL'
    assert evaluate_synthetic_diff(contract,complete,coverage_complete=False)['verdict']=='UNCERTAIN'
    assert evaluate_synthetic_diff(contract,complete+[{'entity':'other_entity','diff_type':'added','where':{},'after':{}}],coverage_complete=True)['verdict']=='FAIL'

def test_duplicate_without_expected_count_cannot_pass():
    contract=samples()[0];d=synthesize_present(contract)
    assert evaluate_synthetic_diff(contract,d+d,coverage_complete=True)['verdict']=='UNCERTAIN'

def test_invalid_clause_fails_closed():
    raw={'test_id':'bad','service':'box','answer':{'assertions':[{'diff_type':'added','entity':'x','where':{'id':{'near':'a'}}}]}}
    contract=parse_agentdiff_task(raw)
    assert evaluate_synthetic_diff(contract,[],coverage_complete=True)['verdict']=='UNCERTAIN'

def test_broken_task_rejected():
    with pytest.raises(ExternalContractError):parse_agentdiff_task({'test_id':'x','service':'box','answer':'{oops'})

def test_missing_benchmark_cannot_claim_executed():
    result=integration_status();assert result['official_evaluation_runs']==0

def test_partial_diff_cannot_prove_missing_required_change():
    assert evaluate_synthetic_diff(samples()[0],[],coverage_complete=False)['verdict']=='UNCERTAIN'

def test_extra_changed_field_is_not_silent_success():
    t=samples()[0];d=synthesize_present(t);d[0]['after']['unapproved_role']='admin'
    assert evaluate_synthetic_diff(t,d,coverage_complete=True)['verdict']=='FAIL'

def test_original_upstream_answer_json_string_encoding():
    raw=next(load_jsonl_tasks(FIXTURE))
    raw['answer']=json.dumps(raw['answer'])
    task=parse_agentdiff_task(raw)
    assert task.test_id=='box_145' and len(task.assertions)==1
