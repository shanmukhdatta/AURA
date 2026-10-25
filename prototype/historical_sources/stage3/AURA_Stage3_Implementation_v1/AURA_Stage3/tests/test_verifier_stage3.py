"""Stage 3 independently tests conservative AURA verdict semantics.

No hidden actual-world ground-truth or precomputed possible-world catalogue is
imported by the verifier. Expected outcome labels are read by tests ONLY.
"""
import copy
import json
from pathlib import Path

import pytest

from aura_evidence.capture import EvidenceSandbox, SnapshotError
from aura_evidence.util import digest, read_json
from aura_evidence.validation import observation_digest, validate_shape, ValidationError
from aura_verifier import verify, verify_fixture_directory, verify_saved_run, VerificationInputError
from run_demo import run

CASES = Path(__file__).parent/'fixtures/stage1_inputs'
CASE_IDS = sorted(p.name for p in CASES.iterdir() if p.is_dir())
LIVE_EXPECTED = {'clean':'PASS','missing_report':'FAIL','collateral':'FAIL',
                 'silent_noop':'FAIL','denied_readback':'UNCERTAIN',
                 'missing_validation':'FAIL'}


def inputs(case='01_complete_success'):
    src = CASES/case
    return (read_json(src/'task_contract.json'),
            read_json(src/'probe_catalogue.json'),
            read_json(src/'observations.json'))


def fixture_verdict(c,p,o):
    return verify(c,p,o,run_id=o[0]['run_id'],epoch_id=o[0]['epoch_id'],fixture_mode=True)


def seal(obs):
    for o in obs:
        o['payload_sha256']=observation_digest(o)
    return obs


@pytest.mark.parametrize('case',CASE_IDS)
def test_stage1_reference_verdicts(case):
    cert=verify_fixture_directory(CASES/case)
    expected=read_json(CASES/case/'expected.json')
    assert (cert['verdict'],cert['decision_status']) == (expected['expected_verdict'],expected['decision_status'])
    assert cert['mode']=='conservative'
    validate_shape(cert,'Certificate')
    assert {r['obligation_id'] for r in cert['obligation_results']} == {
        o['id'] for o in read_json(CASES/case/'task_contract.json')['obligations']}
    assert set(cert['unresolved_obligation_ids']) == {
        r['obligation_id'] for r in cert['obligation_results'] if r['truth']=='unknown'}
    assert cert['contract_sha256']==digest(read_json(CASES/case/'task_contract.json'))
    assert all(r in {o['observation_id'] for o in read_json(CASES/case/'observations.json')}
               for r in cert['evidence_refs'])


@pytest.mark.parametrize('scenario,expected',LIVE_EXPECTED.items())
def test_fresh_stage2_run_into_stage3(tmp_path,scenario,expected):
    root=tmp_path/scenario
    run(scenario,root)
    cert=verify_saved_run(root)
    assert cert['verdict']==expected
    assert cert['decision_status']=='normal'
    validate_shape(cert,'Certificate')
    assert cert['costs']['capture_latency_ms'] > 0
    assert cert['costs']['bytes_read'] > 0
    assert cert['contract_sha256']==digest(read_json(Path(__file__).parent.parent/'examples/reference/task_contract.json'))
    assert len(cert['inspection_ids'])==4


def test_fixture_missing_report_is_known_failure_not_unknown():
    c,p,o=inputs('02_missing_report'); cert=fixture_verdict(c,p,o)
    assert cert['verdict']=='FAIL'
    assert any(x['reason_code']=='required_report_absent' for x in cert['obligation_results'])


def test_failure_dominates_unknown():
    c,p,o=inputs('06_known_bad_and_unknown'); cert=fixture_verdict(c,p,o)
    assert cert['verdict']=='FAIL' and 'known_violation_dominates_unknown' in cert['reason_codes']


def test_conflict_overrides_even_otherwise_positive_facts():
    c,p,o=inputs('08_conflicting_evidence');cert=fixture_verdict(c,p,o)
    assert cert['decision_status']=='evidence_conflict' and cert['verdict']=='UNCERTAIN'
    assert next(x for x in cert['obligation_results'] if x['obligation_id']=='marks_correct')['truth']=='unknown'


def test_no_coverage_is_not_success():
    c,p,o=inputs('07_insufficient_frame_coverage'); cert=fixture_verdict(c,p,o)
    assert cert['verdict']=='UNCERTAIN' and cert['verified_frame_surfaces']==[]


def test_journal_required_for_transient_effect():
    c,p,o=inputs('10_unobservable_transient_effect');cert=fixture_verdict(c,p,o)
    assert next(x for x in cert['obligation_results'] if x['obligation_id']=='no_transient_unauthorized_mutation')['truth']=='unknown'


def test_self_report_fact_cannot_make_outcome_pass():
    c,p,o=inputs()
    # Allow a self-report probe to provide only marks, but remove the independent marks fact.
    p[0]['independence']='agent_self_report'
    o[0]['channel']='agent_self_report'
    seal(o)
    cert=fixture_verdict(c,p,o)
    assert cert['verdict']=='UNCERTAIN'
    assert next(x for x in cert['obligation_results'] if x['obligation_id']=='marks_correct')['truth']=='unknown'


def test_bool_does_not_satisfy_integer_count():
    c,p,o=inputs(); record=next(v for v in o if v['probe_id']=='student_state')
    next(f for f in record['facts'] if f['fact_key']=='student.101.matching_count')['value']=True
    seal(o)
    cert=fixture_verdict(c,p,o)
    assert cert['verdict']=='FAIL'
    assert 'record_multiplicity_violation' in cert['reason_codes']


def test_disallow_count_predicate_with_wrong_declared_expected_type():
    c,p,o=inputs()
    next(x for x in c['obligations'] if x['id']=='exact_record_count')['predicate']['expected']=True
    with pytest.raises(ValidationError,match='nonnegative integer'):
        fixture_verdict(c,p,o)


def test_frame_contract_requires_full_surface_accounting():
    c,p,o=inputs()
    next(x for x in c['obligations'] if x['category']=='frame')['required_complete_coverage']=[]
    with pytest.raises(VerificationInputError,match='zero-unaccounted-mutation'):
        fixture_verdict(c,p,o)


def test_frame_cannot_be_renamed_to_non_frame():
    c,p,o=inputs()
    next(x for x in c['obligations'] if x['category']=='frame')['category']='outcome'
    with pytest.raises(VerificationInputError,match='zero-unaccounted-mutation'):
        fixture_verdict(c,p,o)


def test_duplicate_observation_refused():
    c,p,o=inputs()
    with pytest.raises(VerificationInputError,match='duplicate'):
        fixture_verdict(c,p,o+[copy.deepcopy(o[0])])


def test_cross_epoch_refused():
    c,p,o=inputs()
    o[0]['epoch_id']='epoch.other'
    seal(o)
    with pytest.raises(VerificationInputError,match='cross-run or cross-epoch'):
        fixture_verdict(c,p,o)


def test_tampered_fixture_digest_refused():
    c,p,o=inputs()
    o[0]['facts'][0]['value']=999
    with pytest.raises(VerificationInputError,match='integrity'):
        fixture_verdict(c,p,o)


def test_agent_cannot_claim_full_mutation_coverage():
    c,p,o=inputs()
    diff=next(x for x in p if x['probe_id']=='full_frame_diff')
    diff['independence']='agent_self_report'
    with pytest.raises(ValidationError):
        fixture_verdict(c,p,o)


def test_forged_coverage_refs_refused_in_live_capture(tmp_path):
    root=tmp_path/'real';manifest=run('clean',root)
    from aura_evidence.ledger import EvidenceLedger
    sand=EvidenceSandbox(root); pair=sand.load_pair(manifest['epoch_id'])
    o=EvidenceLedger(sand.evidence).verify(manifest['observations'],{
        p['probe_id']:p for p in read_json(Path(__file__).parent.parent/'examples/reference/probe_catalogue.json')},pair=pair)
    target=next(x for x in o if x['probe_id']=='full_frame_diff')
    target['coverage_receipts'][0]['snapshot_before_ref']='snapshots/unknown.json'
    seal(o)
    c=read_json(Path(__file__).parent.parent/'examples/reference/task_contract.json')
    p=read_json(Path(__file__).parent.parent/'examples/reference/probe_catalogue.json')
    with pytest.raises(ValidationError,match='different snapshots'):
        verify(c,p,o,run_id=manifest['run_id'],epoch_id=manifest['epoch_id'],pair=pair)


def test_bad_real_snapshot_fails_closed(tmp_path):
    root=tmp_path/'real';manifest=run('clean',root)
    path=root/'evidence'/manifest['snapshot_refs'][1]
    data=read_json(path)
    data['sqlite']['students']['rows'][0]['marks']=900
    path.write_text(json.dumps(data))
    with pytest.raises(SnapshotError,match='integrity'):
        verify_saved_run(root)


def test_no_live_pair_is_rejected():
    c,p,o=inputs()
    with pytest.raises(VerificationInputError,match='validated snapshot pair'):
        verify(c,p,o,run_id=o[0]['run_id'],epoch_id=o[0]['epoch_id'])


def test_unsupported_operator_rejected():
    c,p,o=inputs()
    c['obligations'][0]['predicate']['operator']='execute_sql'
    with pytest.raises(ValidationError):
        fixture_verdict(c,p,o)


def test_equal_nulls_do_not_establish_cross_artifact_relation():
    c,p,o=inputs()
    # Construct comparison from trusted facts already in the student observation.
    ob=next(x for x in c['obligations'] if x['id']=='marks_correct')
    ob['predicate']={'operator':'same_as', 'fact_key':'student.101.marks',
                     'comparison_fact_key':'student.101.matching_count'}
    obs=next(x for x in o if x['probe_id']=='student_state')
    for f in obs['facts']:
        f['value']=None
    seal(o)
    cert=fixture_verdict(c,p,o)
    assert cert['verdict']!='PASS'
    assert next(x for x in cert['obligation_results'] if x['obligation_id']=='marks_correct')['truth']=='unknown'


def test_no_hidden_truth_or_world_catalogue_loaded_by_verifier():
    import inspect
    import aura_verifier.engine as eng
    code=inspect.getsource(eng)
    assert 'harness_hidden/' not in code
    assert "read_json(directory/'reference_possible_worlds.json')" not in code


def test_fixture_certificate_records_non_live_trust():
    cert=verify_fixture_directory(CASES/'01_complete_success')
    assert any('FIXTURE ONLY' in x for x in cert['trust_assumptions'])


def test_unknown_certificate_cites_failed_inspection():
    c,p,o=inputs('05_unobservable_notification')
    cert=fixture_verdict(c,p,o)
    item=next(x for x in cert['obligation_results'] if x['obligation_id']=='notification_confirmed')
    assert item['truth']=='unknown'
    failed_id=next(x['observation_id'] for x in o if x['probe_id']=='notification_status')
    assert failed_id in item['evidence_refs']


def test_conflict_certificate_cites_both_disagreeing_observations():
    c,p,o=inputs('08_conflicting_evidence')
    cert=fixture_verdict(c,p,o)
    item=next(x for x in cert['obligation_results'] if x['obligation_id']=='marks_correct')
    ids=[x['observation_id'] for x in o if x['probe_id']=='student_state']
    assert item['truth']=='unknown'
    assert set(ids).issubset(set(item['evidence_refs']))
