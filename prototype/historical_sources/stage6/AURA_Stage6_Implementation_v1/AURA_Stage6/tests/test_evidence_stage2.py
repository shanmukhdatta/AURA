"""Stage 2 integration tests: evidence infrastructure only, not AURA verdicts."""
import copy
import json
from pathlib import Path
import sqlite3
import pytest

from aura_evidence.capture import EvidenceSandbox, SnapshotError
from aura_evidence.diff import canonical_diff
from aura_evidence.ledger import EvidenceLedger
from aura_evidence.probes import ProbeRunner
from aura_evidence.util import digest, read_json
from aura_evidence.validation import (ValidationError, detect_conflicts,
    observation_digest, validate_contract, validate_observation, validate_probes, validate_shape)
from run_demo import run, HERE, SCENARIOS


@pytest.fixture
def source():
    root=HERE/'examples/reference'
    return read_json(root/'task_contract.json'),read_json(root/'probe_catalogue.json')


@pytest.fixture
def clean(tmp_path,source):
    root=tmp_path/'clean'
    manifest=run('clean',root)
    sand=EvidenceSandbox(root)
    pair=sand.load_pair(manifest['epoch_id'])
    c,probes=source
    return sand,pair,c,probes,manifest


def observations(clean):
    sand,pair,c,probes,manifest=clean
    return EvidenceLedger(sand.evidence).verify(manifest['observations'],
                {p['probe_id']:p for p in probes},pair=pair)


def by_probe(obs,probe_id):
    return next(x for x in obs if x['probe_id']==probe_id)


def facts(ob):
    return {f['fact_key']:f['value'] for f in ob['facts']}


def test_clean_observes_all_four_probes(clean):
    x=observations(clean)
    assert len(x)==4
    assert all(o['status']=='ok' for o in x)
    assert facts(by_probe(x,'student_state'))=={'student.101.marks':85,'student.101.matching_count':1}
    assert facts(by_probe(x,'report_state'))=={'report.101.exists':True,'report.101.matches_db':True}
    assert facts(by_probe(x,'full_frame_diff'))=={'mutation.out_of_frame_count':0}
    assert facts(by_probe(x,'validation_trace'))=={'trace.validation_before_update':True}


def test_clean_has_two_authorized_changes(clean):
    sand,pair,_,_,_=clean
    d=canonical_diff(pair)
    assert len(d)==2
    assert [x['operation'] for x in d]==['update','create_file']
    assert d[0]['changed_fields']['marks']=={'old':70,'new':85}


def test_complete_coverage_scoped_to_named_surfaces(clean):
    receipt=by_probe(observations(clean),'full_frame_diff')['coverage_receipts']
    assert {r['surface_id'] for r in receipt}=={'sqlite.students','filesystem.reports'}
    assert all(r['consistent_epoch'] and r['independent_source'] for r in receipt)
    assert not any('external' in r['surface_id'] for r in receipt)


@pytest.mark.parametrize('scenario,probe,key,expected',[
    ('missing_report','report_state','report.101.exists',False),
    ('silent_noop','student_state','student.101.marks',70),
    ('collateral','full_frame_diff','mutation.out_of_frame_count',1),
    ('missing_validation','validation_trace','trace.validation_before_update',False),
])
def test_faults_observable_from_independent_sources(tmp_path,scenario,probe,key,expected):
    root=tmp_path/scenario
    report=run(scenario,root)
    led=EvidenceLedger(root/'evidence')
    matching=[led.load(ref) for ref in report['observations'] if led.load(ref)['probe_id']==probe]
    assert len(matching)==1
    assert facts(matching[0])[key]==expected


def test_denied_readback_is_not_negative_fact(tmp_path):
    root=tmp_path/'denied'
    report=run('denied_readback',root)
    led=EvidenceLedger(root/'evidence')
    target=next(led.load(ref) for ref in report['observations'] if 'student_state' in ref)
    assert target['status']=='unavailable'
    assert target['reason_code']=='permission_denied'
    assert target['facts']==[] and target['coverage_receipts']==[]


def test_snapshot_digest_protected(clean):
    sand,pair,c,probes,manifest=clean
    snapshot=sand.evidence/pair.after_ref
    data=read_json(snapshot)
    data['sqlite']['students']['rows'][0]['marks']=999
    snapshot.write_text(json.dumps(data))
    with pytest.raises(SnapshotError,match='integrity'):
        sand.load_pair(pair.epoch_id)


def test_observation_tamper_detected(clean):
    sand,pair,c,probes,manifest=clean
    led=EvidenceLedger(sand.evidence)
    ref=manifest['observations'][0]
    tampered=led.load(ref)
    tampered['facts'][0]['value']=999
    with pytest.raises(ValidationError,match='digest'):
        validate_observation(tampered,probes[0],pair=pair)


def test_coverage_receipt_reference_mismatch(clean):
    sand,pair,c,probes,manifest=clean
    ob=by_probe(observations(clean),'full_frame_diff')
    ob['coverage_receipts'][0]['snapshot_after_ref']='snapshots/other.json'
    ob['payload_sha256']=observation_digest(ob)
    with pytest.raises(ValidationError,match='different snapshots'):
        validate_observation(ob,next(p for p in probes if p['probe_id']=='full_frame_diff'),pair=pair)


def test_fake_self_report_cannot_claim_frame(clean):
    sand,pair,c,probes,manifest=clean
    forged=copy.deepcopy(next(p for p in probes if p['probe_id']=='full_frame_diff'))
    forged['independence']='agent_self_report'
    with pytest.raises(ValidationError):
        validate_probes(c,[*probes[:-2],forged,probes[-1]])


def test_file_modified_after_snapshot_fails_probe(clean):
    sand,pair,c,probes,manifest=clean
    (sand.workspace/'reports/student_101.md').write_text('Student: 101\nMarks: 999\n')
    runner=ProbeRunner(sand,pair,c,probes)
    ob=runner.run('report_state','run.modified')
    assert ob['status']=='error' and ob['reason_code']=='integrity_failure'
    assert not ob['facts']


def test_symlink_detected_during_snapshot(tmp_path):
    sand=EvidenceSandbox(tmp_path/'symlink').initialize()
    (sand.workspace/'reports').symlink_to('/tmp')
    with pytest.raises(SnapshotError,match='symlink'):
        sand.capture('epoch.symlink','before')


def test_observation_conflict_same_epoch(clean):
    original=by_probe(observations(clean),'student_state')
    competing=copy.deepcopy(original)
    competing['observation_id']='obs.run.stage2.clean.competing'
    competing['facts'][0]['value']=90
    competing['payload_sha256']=observation_digest(competing)
    conflicts=detect_conflicts([original,competing])
    assert len(conflicts)==1 and conflicts[0]['fact_key']=='student.101.marks'


def test_distinct_epochs_not_contradiction(clean):
    original=by_probe(observations(clean),'student_state')
    competing=copy.deepcopy(original)
    competing['observation_id']='obs.run.stage2.clean.competing'
    competing['epoch_id']='epoch.other'
    competing['facts'][0]['value']=90
    competing['payload_sha256']=observation_digest(competing)
    assert detect_conflicts([original,competing])==[]


def test_duplicate_contract_obligation_rejected(source):
    c,probes=source
    c['obligations'].append(copy.deepcopy(c['obligations'][0]))
    with pytest.raises(ValidationError,match='duplicate'):
        validate_contract(c)


def test_count_must_not_be_boolean(source):
    c,probes=source
    ob=next(o for o in c['obligations'] if o['predicate']['operator']=='count_eq')
    ob['predicate']['expected']=True
    with pytest.raises(ValidationError,match='nonnegative integer'):
        validate_contract(c)


def test_contract_unregistered_fact_rejected(source):
    c,probes=source
    c['obligations'][0]['predicate']['fact_key']='student.101.unrecorded'
    with pytest.raises(ValidationError,match='unregistered obligation'):
        validate_probes(c,probes)


def test_observation_unregistered_fact_rejected(clean):
    sand,pair,c,probes,manifest=clean
    ob=by_probe(observations(clean),'student_state')
    ob['facts'].append({'fact_key':'secret.bypass','value':True,'source_ref':'forged'})
    ob['payload_sha256']=observation_digest(ob)
    with pytest.raises(ValidationError,match='unregistered fact'):
        validate_observation(ob,probes[0],pair=pair)


def test_wrong_epoch_receipt_rejected(clean):
    sand,pair,c,probes,manifest=clean
    ob=by_probe(observations(clean),'full_frame_diff')
    ob['epoch_id']='epoch.wrong'
    ob['payload_sha256']=observation_digest(ob)
    with pytest.raises(ValidationError,match='epoch'):
        validate_observation(ob,probes[2],pair=pair)


def test_snapshot_pair_different_epochs_rejected(clean):
    sand,pair,c,probes,manifest=clean
    fake=copy.deepcopy(pair.after)
    fake['epoch_id']='other.epoch'
    from aura_evidence.capture import SnapshotPair
    altered=SnapshotPair(pair.epoch_id,pair.before,fake,pair.before_ref,pair.after_ref,0,0)
    with pytest.raises(SnapshotError,match='epoch mismatch'):
        altered.require_same_epoch()


def test_ledger_rejects_outside_path(clean):
    sand,pair,c,probes,manifest=clean
    led=EvidenceLedger(sand.evidence)
    with pytest.raises(ValueError,match='outside'):
        led.load('../snapshots/not-observation.json')


def test_report_no_overwrite(tmp_path):
    root=tmp_path/'once'
    run('clean',root)
    with pytest.raises(FileExistsError):
        run('clean',root)


def test_snapshots_do_not_change_task_workspace(clean):
    sand,pair,c,probes,manifest=clean
    assert not (sand.workspace/'evidence').exists()
    assert (sand.evidence/'run_manifest.json').exists()
    assert (sand.workspace/'reports/student_101.md').is_file()


def test_stated_capture_cost_kept_separate_from_probe_cost(clean):
    sand,pair,c,probes,manifest=clean
    assert manifest['snapshot_capture_bytes_read'] > 0
    assert manifest['probe_bytes_read_sum'] > 0
    assert 'snapshot_capture_latency_ms' in manifest
    assert 'probe_latency_ms_sum' in manifest


def test_snapshot_diff_detects_extra_file(tmp_path):
    root=tmp_path/'extra'
    m=run('clean',root)
    sand=EvidenceSandbox(root)
    # Create new epoch with baseline including clean report.
    epoch='epoch.extra'
    sand.capture(epoch,'before')
    (sand.workspace/'reports/unauthorized.tmp').write_text('oops')
    sand.capture(epoch,'after')
    pair=sand.load_pair(epoch)
    assert any(ch['path']=='reports/unauthorized.tmp' for ch in canonical_diff(pair))


def test_no_primary_key_uses_multiset_not_fabricated_update(tmp_path):
    sand=EvidenceSandbox(tmp_path/'nopk').initialize()
    with sqlite3.connect(sand.db) as conn:
        conn.execute('CREATE TABLE nopk (thing TEXT, count INTEGER)')
        conn.execute('INSERT INTO nopk VALUES (?,?)',('x',1))
    sand.capture('epoch.nopk','before')
    with sqlite3.connect(sand.db) as conn:
        conn.execute('UPDATE nopk SET count=2')
    sand.capture('epoch.nopk','after')
    changes=[ch for ch in canonical_diff(sand.load_pair('epoch.nopk')) if ch['table']=='nopk']
    assert len(changes)==2 and all(c['operation']=='multiset_delta' for c in changes)


def test_external_status_adapter_is_unavailable_not_invented(tmp_path,source):
    root=tmp_path/'external'
    report=run('clean',root)
    sand=EvidenceSandbox(root)
    pair=sand.load_pair(report['epoch_id'])
    c,probes=source
    external=copy.deepcopy(probes[0]);external.update(probe_id='external_status_probe',
        adapter='external_status',surface_id='external.notify',
        provides_fact_keys=['external.notify.confirmed'],mutation_coverage='none',
        covered_mutation_surfaces=[],coverage_method='none')
    runner=ProbeRunner(sand,pair,c,probes+[external])
    ob=runner.run('external_status_probe','run.external')
    assert ob['status']=='unavailable' and ob['reason_code']=='unsupported'
    assert ob['facts']==[]


def test_unrecognized_allowed_effect_never_approves_frame(tmp_path,source):
    root=tmp_path/'grammar'
    report=run('clean',root)
    sand=EvidenceSandbox(root);pair=sand.load_pair(report['epoch_id'])
    c,probes=source
    c['frame_policy']['allowed_effects'][0]['target_pattern']='student_id=*'
    runner=ProbeRunner(sand,pair,c,probes)
    ob=runner.run('full_frame_diff','run.badgrammar')
    assert ob['status']=='error' and ob['reason_code']=='unsupported' and not ob['coverage_receipts']


def test_all_stage1_reference_contracts_and_probes_validate():
    # Stage 1 cases are reference materials; Stage 2 does NOT evaluate their verdicts.
    root=HERE/'tests/fixtures/stage1_inputs'
    folders=list(root.iterdir())
    assert len(folders)==12
    for d in folders:
        c=read_json(d/'task_contract.json')
        probes=read_json(d/'probe_catalogue.json')
        validate_probes(c,probes)
        for ob in read_json(d/'observations.json'):
            validate_shape(ob,'Observation')


def test_no_stage3_verdict_fields_in_manifest(clean):
    *_,manifest=clean
    assert 'verdict' not in manifest and 'certificate_id' not in manifest


def test_binary_report_is_error_not_crash(clean):
    sand,pair,c,probes,manifest=clean
    binary=(sand.workspace/'reports/student_101.md')
    binary.write_bytes(b'\xff\xfe\xfd')
    result=ProbeRunner(sand,pair,c,probes).run('report_state','run.invalidfile')
    assert result['status']=='error'
    assert result['facts']==[]


def test_duplicate_insertions_visible_in_canonical_diff(tmp_path):
    sand=EvidenceSandbox(tmp_path/'dupes').initialize()
    with sqlite3.connect(sand.db) as conn:
        conn.execute('CREATE TABLE emails (email_id INTEGER PRIMARY KEY, student_id INTEGER, kind TEXT)')
    sand.capture('epoch.dupes','before')
    with sqlite3.connect(sand.db) as conn:
        conn.executemany('INSERT INTO emails VALUES (?, ?, ?)',[(1,101,'notice'),(2,101,'notice')])
    sand.capture('epoch.dupes','after')
    d=canonical_diff(sand.load_pair('epoch.dupes'))
    inserts=[c for c in d if c['surface_id']=='sqlite.emails' and c['operation']=='insert']
    assert len(inserts)==2


def test_registered_journal_probe_not_faked(tmp_path,source):
    root=tmp_path/'journal'
    report=run('clean',root)
    sand=EvidenceSandbox(root);pair=sand.load_pair(report['epoch_id'])
    c,probes=source
    journal=copy.deepcopy(probes[2]);journal.update(probe_id='transient_journal',
        coverage_method='complete_journal',covered_mutation_surfaces=['sqlite.students'])
    runner=ProbeRunner(sand,pair,c,probes+[journal])
    ob=runner.run('transient_journal','run.journal')
    assert ob['status']=='unavailable' and ob['reason_code']=='unsupported'
    assert ob['coverage_receipts']==[] and ob['facts']==[]
