"""Stage 4 acceptance and logical-refinement regression cases."""
from __future__ import annotations
import copy
from pathlib import Path
import pytest

from aura_evidence.util import read_json
from aura_evidence.validation import observation_digest, validate_shape
from aura_reasoning.model import (graph_for_contract, validate_model, enumerate_worlds,
                                  verify_bounded, ModelInputError)
from aura_reasoning.reference_models import make_reference_model
from aura_verifier.engine import verify

ROOT=Path(__file__).parent/'fixtures'/'stage1_inputs'
CASES=[p.name for p in ROOT.iterdir() if p.is_dir()]


def case(name='01_complete_success'):
    p=ROOT/name
    c=read_json(p/'task_contract.json')
    probes=read_json(p/'probe_catalogue.json')
    obs=read_json(p/'observations.json')
    return c,probes,obs


def run_bounded(c,p,o,m):
    return verify_bounded(c,p,o,m,run_id=o[0]['run_id'],epoch_id=o[0]['epoch_id'],fixture_mode=True)


def run_conservative(c,p,o):
    return verify(c,p,o,run_id=o[0]['run_id'],epoch_id=o[0]['epoch_id'],fixture_mode=True)


def reseal(observations):
    for ob in observations:
        ob['payload_sha256']=observation_digest(ob)


@pytest.mark.parametrize('name',CASES)
def test_stage1_reference_agreement(name):
    c,p,o=case(name)
    model=make_reference_model(c,p,o)
    bounded,ledger=run_bounded(c,p,o,model)
    reference=read_json(ROOT/name/'expected.json')
    assert bounded['verdict']==reference['expected_verdict'],name
    assert bounded['decision_status']==reference['decision_status'],name
    assert bounded['mode']=='bounded_exact'
    assert ledger['model_sha256'] and ledger['contract_sha256']
    validate_shape(bounded,'Certificate')


def test_dependency_graph_maps_schemas_and_cross_artifact_keys():
    c,p,o=case()
    graph=graph_for_contract(c,p)
    assert len(graph)==len(c['obligations'])
    assert next(x for x in graph if x['obligation_id']=='marks_correct')['probe_ids']==['student_state']
    assert next(x for x in graph if x['obligation_id']=='no_unauthorized_mutation')['required_coverage']==['sqlite.students','filesystem.reports']


def test_indistinguishable_external_effect_twins_are_uncertain():
    c,p,o=case('05_unobservable_notification')
    model=make_reference_model(c,p,o)
    cert,ledger=run_bounded(c,p,o,model)
    assert cert['verdict']=='UNCERTAIN'
    assert ledger['satisfying_world_count']>0 and ledger['failing_world_count']>0
    wgood=ledger['success_witness'];wbad=ledger['failure_witness']
    assert wgood['external.notify.confirmed'] is True
    assert wbad['external.notify.confirmed'] is False
    for f in ['student.101.marks','student.101.matching_count','trace.validation_before_update']:
        assert wgood[f]==wbad[f]


def test_strong_model_assumption_can_infer_missing_requirement_with_explicit_caveat():
    c,p,o=case('05_unobservable_notification')
    model=make_reference_model(c,p,o)
    # SYNTHETIC assumption ONLY: report existence causally guarantees notice.
    # It is NOT a real-world valid notification rule.
    model['constraints']=[{'op':'implies',
                           'if':{'op':'fact_eq','fact_key':'report.101.exists','value':True},
                           'then':{'op':'fact_eq','fact_key':'external.notify.confirmed','value':True}}]
    baseline=run_conservative(c,p,o)
    cert,ledger=run_bounded(c,p,o,model)
    assert baseline['verdict']=='UNCERTAIN'
    assert cert['verdict']=='PASS' and cert['mode']=='bounded_exact'
    assert ledger['satisfying_world_count']>=1 and ledger['failing_world_count']==0
    assert any('not ground truth' in txt for txt in cert['trust_assumptions'])
    assert next(x for x in cert['obligation_results'] if x['obligation_id']=='notification_confirmed')['reason_code']=='entailed_satisfaction_by_bounded_model'


def test_joint_failure_even_when_each_of_two_predicates_unresolved():
    c,p,o=case('05_unobservable_notification')
    # Remove authoritative marks observation while preserving valid hashes.
    data=next(x for x in o if x['probe_id']=='student_state')
    data['facts']=[f for f in data['facts'] if f['fact_key']!='student.101.marks']
    reseal(o)
    base=run_conservative(c,p,o)
    assert base['verdict']=='UNCERTAIN'
    model=make_reference_model(c,p,o)
    model['constraints']=[
        {'op':'implies','if':{'op':'fact_eq','fact_key':'trace.validation_before_update','value':True},
         'then':{'op':'not','arg':{'op':'and','args':[
             {'op':'fact_eq','fact_key':'student.101.marks','value':85},
             {'op':'fact_eq','fact_key':'external.notify.confirmed','value':True}]}}}
    ]
    cert,ledger=run_bounded(c,p,o,model)
    assert ledger['compatible_world_count']>0 and ledger['satisfying_world_count']==0
    assert cert['verdict']=='FAIL' and 'joint_unsatisfiable_completion' in cert['reason_codes']
    results={r['obligation_id']:r['truth'] for r in cert['obligation_results']}
    assert results['marks_correct']=='unknown' and results['notification_confirmed']=='unknown'


def test_conflicting_validated_evidence_remains_unknown():
    c,p,o=case('08_conflicting_evidence')
    cert,ledger=run_bounded(c,p,o,make_reference_model(c,p,o))
    assert cert['verdict']=='UNCERTAIN' and cert['decision_status']=='evidence_conflict'
    assert 'student.101.marks' in ledger['conflicted_fact_keys']


def test_evidence_model_contradiction_is_not_vacuous_pass():
    c,p,o=case()
    model=make_reference_model(c,p,o)
    model['constraints']=[{'op':'fact_eq','fact_key':'student.101.marks','value':70}]
    cert,ledger=run_bounded(c,p,o,model)
    assert ledger['compatible_world_count']==0
    assert cert['verdict']=='UNCERTAIN' and cert['decision_status']=='model_inconsistent'


def test_solver_cap_returns_unknown_not_pass():
    c,p,o=case('05_unobservable_notification')
    model=make_reference_model(c,p,o,max_worlds=1)
    cert,ledger=run_bounded(c,p,o,model)
    assert cert['verdict']=='UNCERTAIN' and cert['decision_status']=='solver_indeterminate'
    assert ledger['model_domain_size']>1


def test_frame_coverage_cannot_be_assumed_from_model():
    c,p,o=case('07_insufficient_frame_coverage')
    model=make_reference_model(c,p,o)
    # All concrete candidate values satisfy the positive predicates, but no
    # complete frame receipt exists. Bounded model does not replace receipt.
    cert,ledger=run_bounded(c,p,o,model)
    assert cert['verdict']=='UNCERTAIN' and cert['verified_frame_surfaces']==[]
    assert cert['unresolved_obligation_ids']


def test_fail_dominates_unobserved_external():
    c,p,o=case('06_known_bad_and_unknown')
    cert,_=run_bounded(c,p,o,make_reference_model(c,p,o))
    assert cert['verdict']=='FAIL'


def test_incomplete_model_domain_rejected():
    c,p,o=case()
    m=make_reference_model(c,p,o)
    del m['fact_domains']['student.101.marks']
    with pytest.raises(ModelInputError,match='omits obligated'):
        run_bounded(c,p,o,m)


def test_model_cannot_ignore_registered_extra_fact():
    c,p,o=case()
    m=make_reference_model(c,p,o)
    del m['fact_domains']['report.101.matches_db']
    with pytest.raises(ModelInputError):run_bounded(c,p,o,m)


def test_finite_models_reject_embedded_hidden_labels():
    c,p,o=case()
    m=make_reference_model(c,p,o)
    m['actual_world']={'student.101.marks':85}
    with pytest.raises(ModelInputError,match='invalid model fields'):
        run_bounded(c,p,o,m)


def test_duplicate_typed_domain_rejected():
    c,p,o=case()
    m=make_reference_model(c,p,o)
    m['fact_domains']['student.101.marks']=[85,85]
    with pytest.raises(ModelInputError,match='duplicate typed'):
        run_bounded(c,p,o,m)


def test_boolean_and_integer_domain_are_different():
    c,p,o=case()
    m=make_reference_model(c,p,o)
    m['fact_domains']['student.101.matching_count']=[1,True]
    cert,_=run_bounded(c,p,o,m)
    assert cert['verdict']=='PASS' # observed integer 1 excludes boolean True


def test_trusted_additional_evidence_only_reduces_compatible_worlds():
    c,p,o=case('05_unobservable_notification')
    m=make_reference_model(c,p,o)
    world0,_,_=enumerate_worlds(m,{'student.101.marks':85})
    world1,_,_=enumerate_worlds(m,{'student.101.marks':85,'external.notify.confirmed':True})
    assert len(world0)>len(world1)
    assert all(w in world0 for w in world1)


def test_enumeration_does_not_use_actual_world_or_hidden_labels():
    c,p,o=case('05_unobservable_notification')
    m=make_reference_model(c,p,o)
    worlds,_,_=enumerate_worlds(m,{'trace.validation_before_update':True})
    assert {w['external.notify.confirmed'] for w in worlds}=={True,False}


def test_operator_validation_blocks_unknown_formula():
    c,p,o=case()
    m=make_reference_model(c,p,o)
    m['constraints']=[{'op':'python_eval','expr':'True'}]
    with pytest.raises(ModelInputError,match='unsupported'):
        run_bounded(c,p,o,m)


def test_model_mandatory_observed_fact_not_dropped_with_hidden_proxy():
    c,p,o=case()
    m=make_reference_model(c,p,o)
    m['fact_domains'].pop('mutation.out_of_frame_count')
    with pytest.raises(ModelInputError):run_bounded(c,p,o,m)


@pytest.mark.parametrize('scenario,expected',[('clean','PASS'),('missing_report','FAIL'),('collateral','FAIL'),('silent_noop','FAIL'),('denied_readback','UNCERTAIN'),('missing_validation','FAIL')])
def test_fresh_stage2_evidence_in_bounded_mode(tmp_path,scenario,expected):
    from run_demo import run
    from verify_bounded import load_input
    capture=tmp_path/scenario
    run(scenario,capture)
    c,p,o,kw=load_input(run_dir=capture)
    model=make_reference_model(c,p,o,model_id='model.test.'+scenario)
    cert,ledger=verify_bounded(c,p,o,model,**kw)
    assert cert['verdict']==expected
    assert cert['mode']=='bounded_exact'
    assert cert['decision_status']=='normal'
    assert cert['costs']['capture_latency_ms']>0
    validate_shape(cert,'Certificate')
    assert ledger['model_sha256']


@pytest.mark.parametrize('scenario',['01_complete_success','05_unobservable_notification','08_conflicting_evidence'])
def test_stage4_new_json_schemas(scenario):
    import jsonschema
    c,p,o=case(scenario)
    m=make_reference_model(c,p,o)
    cert,ledger=run_bounded(c,p,o,m)
    root=Path(__file__).parent.parent/'schemas'
    jsonschema.validate(m,read_json(root/'BoundedWorldModel.schema.json'))
    jsonschema.validate(ledger,read_json(root/'ReasoningLedger.schema.json'))
    assert ledger['stage4_reasoning_latency_ms']>0
    assert cert['costs']['planner_latency_ms']>=ledger['stage4_reasoning_latency_ms']
