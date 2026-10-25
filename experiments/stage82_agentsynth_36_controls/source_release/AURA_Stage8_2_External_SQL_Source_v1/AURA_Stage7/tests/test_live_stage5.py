from pathlib import Path
import pytest
from run_demo import run,SCENARIOS
from aura_evidence.util import read_json
from aura_evidence.capture import EvidenceSandbox
from aura_planning.live_runner import run_live_policy,frozen_preinspection_model
from aura_planning.planner import Inspection,FiniteInspectionProblem,PlanningError

@pytest.fixture(scope='module')
def catalog():
    root=Path(__file__).resolve().parents[1]
    return read_json(root/'examples/reference/task_contract.json'),read_json(root/'examples/reference/probe_catalogue.json')

@pytest.mark.parametrize('scenario,expected',[
 ('clean','PASS'),('missing_report','FAIL'),('collateral','FAIL'),
 ('silent_noop','FAIL'),('denied_readback','UNCERTAIN'),('missing_validation','FAIL')])
def test_all_policies_against_real_stage2_captures(tmp_path,catalog,scenario,expected):
    run(scenario,tmp_path/scenario)
    contract,probes=catalog
    for policy in ('fixed','greedy','cera','optimal','exhaustive'):
        res=run_live_policy(tmp_path/scenario,contract,probes,policy,
                            force_denied=('student_state',) if scenario=='denied_readback' else ())
        assert res['verdict']==expected
        assert all(x['probe_id'] in {p['probe_id'] for p in probes} for x in res['trace'])
        assert res['certificate']['costs']['bytes_read'] >= res['capture_bytes_read']

def test_prior_from_initial_state_not_silent_failure_truth(tmp_path,catalog):
    run('silent_noop',tmp_path/'run')
    pair=EvidenceSandbox(tmp_path/'run').load_pair('epoch.stage2.silent_noop')
    contract,probes=catalog
    prior=frozen_preinspection_model(contract,probes,pair)
    assert 70 in prior['fact_domains']['student.101.marks']
    assert 85 in prior['fact_domains']['student.101.marks']

def test_no_pass_on_unavailable_live_required_evidence(tmp_path,catalog):
    run('clean',tmp_path/'run')
    contract,probes=catalog
    for policy in ('fixed','greedy','cera','optimal'):
        res=run_live_policy(tmp_path/'run',contract,probes,policy,
                            force_denied=('full_frame_diff',))
        assert res['verdict']=='UNCERTAIN'

def test_empty_world_is_not_pass(tmp_path,catalog):
    run('silent_noop',tmp_path/'run')
    contract,probes=catalog
    pair=EvidenceSandbox(tmp_path/'run').load_pair('epoch.stage2.silent_noop')
    wrong=frozen_preinspection_model(contract,probes,pair)
    wrong['fact_domains']['student.101.marks']=[85]
    res=run_live_policy(tmp_path/'run',contract,probes,'cera',model=wrong)
    # Direct readback of 70 instead of 85 proves FAIL regardless of a bad model.
    assert res['verdict']=='FAIL'
    assert res['decision_status']=='model_inconsistent'
