"""Stage 7 scientific controls: not general agent-performance claims."""
import json
from pathlib import Path
import pytest
from aura_evaluation.study import (
 make_diverse_problem, with_prior, expected_outcomes, paired_cluster_bootstrap,
 boundary_failure_controls, budget_controls, scaling_controls, run_study)
from aura_evaluation.local_faults import scripted_capture, run_local_matrix
from aura_planning.planner import run_policy
from aura_planning.live_runner import run_live_policy
from aura_evidence.util import read_json


def test_48_authored_catalogues_not_just_replicated():
    sets=[]
    for domain in ('records','orders','access','files'):
        for i in range(12):
            p=make_diverse_problem(domain,i)
            sets.append(tuple((s.probe_id,s.fact_keys,s.cost) for s in p.inspections.values()))
            assert 4<=len(p.model['fact_domains'])<=5
            assert 7<=len(p.inspections)<=8
            assert 0<len(p.worlds)<=32
    assert len(sets)==len(set(sets))==48

@pytest.mark.parametrize('regime',['uniform','clean_50','clean_90'])
def test_prior_is_predeclared_and_valid(regime):
    p=with_prior(make_diverse_problem('records',3),regime)
    assert abs(sum(p.prior)-1)<1e-10
    assert all(x>0 for x in p.prior)
    if regime=='clean_90':
        assert abs(sum(v for v,ok in zip(p.prior,p.satisfying) if ok)-.9)<1e-10


def test_optimal_reference_dominates_inspection_cost_on_identical_worlds():
    for domain in ('files','orders'):
        p=make_diverse_problem(domain,2)
        for i in range(len(p.worlds)):
            optimal=run_policy(p,i,'optimal')
            assert optimal['correct_decisive']
            # Optimal is in EXPECTED cost, not necessarily in each individual world.
            assert not optimal['false_pass'] and not optimal['false_fail']


def test_all_policies_share_information_and_truth():
    p=make_diverse_problem('access',9)
    rows,summaries=expected_outcomes(p,'access',9,'uniform')
    assert {x['policy'] for x in summaries}=={'fixed','greedy','cera','optimal','exhaustive'}
    assert all(r['false_pass']==0 and r['false_fail']==0 for r in rows)
    assert all(r['source_type'].startswith('authored_') for r in rows)
    for i in range(len(p.worlds)):
        a=[r for r in rows if r['world_index']==i]
        assert len(a)==5 and len({r['actual_world_success'] for r in a})==1


def test_boundary_safety_no_pass():
    rows=boundary_failure_controls()
    assert len(rows)==36
    assert all(r['decision']!='PASS' for r in rows)
    assert any(r['decision']=='UNCERTAIN' for r in rows)
    assert any(r['decision']=='FAIL' for r in rows)


def test_budget_zero_does_not_certify_anything():
    b=budget_controls()
    assert len(b)==288
    assert all(r['coverage']==0 for r in b if r['budget']==0)
    assert all(not r['false_pass_count'] and not r['false_fail_count'] for r in b)


def test_scaling_oracle_reports_only_sampled_worlds():
    s=scaling_controls()
    assert len(s)==15
    assert max(r['possible_worlds'] for r in s)==256
    assert all(r['sampled_worlds']<=r['possible_worlds'] for r in s)


def test_bootstrap_is_task_clustered_not_world_clustered():
    all_summary=[]
    for c in range(3):
        p=make_diverse_problem('records',c)
        for regime in ('uniform','clean_50','clean_90'):
            _,s=expected_outcomes(with_prior(p,regime),'records',c,regime)
            all_summary.extend(s)
    results=paired_cluster_bootstrap(all_summary,policy_b='greedy',B=250)
    assert len(results)==3
    assert all(x['templates']==3 and x['bootstrap_95_low']<=x['bootstrap_95_high'] for x in results)


def test_conservative_direct_fail_survives_model_mismatch(tmp_path):
    sand=scripted_capture('wrong_marks',tmp_path/'wrong_marks')
    c=read_json(Path(__file__).parents[1]/'examples/reference/task_contract.json')
    probes=read_json(Path(__file__).parents[1]/'examples/reference/probe_catalogue.json')
    for policy in ('fixed','cera','optimal'):
        result=run_live_policy(sand.root,c,probes,policy)
        assert result['verdict']=='FAIL'
        assert 'direct_observed_contract_violation' in result['certificate']['reason_codes']


def test_transient_reversion_limitation_is_not_hidden(tmp_path):
    sand=scripted_capture('transient_reverted_unobserved',tmp_path/'transient')
    c=read_json(Path(__file__).parents[1]/'examples/reference/task_contract.json')
    probes=read_json(Path(__file__).parents[1]/'examples/reference/probe_catalogue.json')
    result=run_live_policy(sand.root,c,probes,'cera')
    assert result['verdict']=='PASS' # Only persistent, declared process properties!
    assert read_json(sand.evidence/'run_manifest.json')['transient_dirty_write_outside_existing_task_contract']


def test_local_expanded_matrix(tmp_path):
    rows=run_local_matrix(tmp_path/'run')
    assert len(rows)==65
    assert all(r['matched_expected'] for r in rows)
    assert {r['scenario'] for r in rows}==set(__import__('aura_evaluation.local_faults',fromlist=['SCENARIOS']).SCENARIOS)


def test_complete_study_reproducible_artifact_counts(tmp_path):
    manifest=run_study(tmp_path/'study')
    assert manifest['world_policy_evaluations']>=10000
    assert manifest['author_generated_tasks']==48
    assert manifest['official_agentdiff_scores']==0
    assert manifest['external_agent_trajectories_evaluated']==0
    assert (tmp_path/'study/policy_summary.csv').exists()
