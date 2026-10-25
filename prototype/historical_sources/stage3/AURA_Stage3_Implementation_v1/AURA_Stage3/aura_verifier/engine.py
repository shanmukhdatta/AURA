"""Independent AURA Stage 3 contract evaluator.

The verifier never imports harness actual-world labels. Its conservative semantics
are deliberately limited to observed, validated atomic facts. Possible-world
reasoning and adaptive probe selection are later stages.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import time

from aura_evidence.capture import EvidenceSandbox
from aura_evidence.ledger import EvidenceLedger
from aura_evidence.util import digest, read_json, utc_now
from aura_evidence.validation import (
    ValidationError, validate_shape, validate_probes,
    validate_observation, observation_digest,
)


class VerificationInputError(ValueError):
    """Malformed or unverifiable evidence. The engine refuses to certify PASS."""


_FAIL_REASONS = {
    'marks_correct': 'required_value_mismatch',
    'exact_record_count': 'record_multiplicity_violation',
    'report_exists': 'required_report_absent',
    'report_matches_database': 'cross_artifact_mismatch',
    'no_unauthorized_mutation': 'out_of_scope_mutation',
    'validation_before_update': 'process_precedence_violated',
    'notification_confirmed': 'required_external_effect_absent',
    'no_transient_unauthorized_mutation': 'transient_mutation_detected',
    'external_ledger_clean': 'out_of_scope_mutation',
}


def _check_predicate(pred, facts):
    """Return True/False/None using atomic trusted same-epoch facts only."""
    key = pred['fact_key']
    if key not in facts:
        return None
    value = facts[key]
    op = pred['operator']
    if op == 'eq':
        return type(value) is type(pred['expected']) and value == pred['expected']
    if op == 'neq':
        return type(value) is not type(pred['expected']) or value != pred['expected']
    if op == 'count_eq':
        return type(value) is int and value == pred['expected']
    if op == 'true':
        return value is True
    if op == 'false':
        return value is False
    if op == 'same_as':
        other = pred['comparison_fact_key']
        if other not in facts or value is None or facts[other] is None:
            return None
        return type(value) is type(facts[other]) and value == facts[other]
    raise VerificationInputError('unsupported predicate operator')


def _unknown_reason(ob, unavailable):
    if ob['id'] == 'no_transient_unauthorized_mutation' or 'transient' in ob['predicate']['fact_key']:
        return 'transient_mutation_unobserved'
    if ob['category'] == 'external' or ob['surface_id'].startswith('external.'):
        return 'unconfirmed_external_effect' if ob['category'] == 'external' else 'external_frame_unobserved'
    if ob['category'] == 'frame' and ob['surface_id'].startswith('external.'):
        return 'external_frame_unobserved'
    if ob['category'] == 'frame':
        return 'frame_coverage_incomplete'
    if ob['predicate']['fact_key'] in unavailable:
        return 'required_evidence_unavailable'
    return 'required_fact_unobserved'


def _fail_reason(ob):
    return _FAIL_REASONS.get(ob['id'], {
        'outcome': 'outcome_predicate_violated',
        'frame': 'frame_predicate_violated',
        'process': 'process_predicate_violated',
        'external': 'external_predicate_violated',
    }[ob['category']])


def _validate_fixture_record(record, p):
    """Pre-authored educational fixtures only: cannot substantiate snapshot refs.

    Production live paths *must* use validate_observation(pair=real_pair).
    """
    validate_shape(record, 'Observation')
    if record['probe_id'] != p['probe_id'] or record['channel'] != p['independence']:
        raise VerificationInputError('fixture observation registered identity mismatch')
    if record['payload_sha256'] != observation_digest(record):
        raise VerificationInputError('fixture observation integrity mismatch')
    if record['status'] == 'ok' and record['reason_code'] != 'none':
        raise VerificationInputError('fixture success cannot contain an error reason')
    if record['status'] != 'ok' and (record['reason_code'] == 'none' or record['facts'] or record['coverage_receipts']):
        raise VerificationInputError('fixture failed readback cannot contain facts/receipts')
    keys = [f['fact_key'] for f in record['facts']]
    if len(keys) != len(set(keys)) or not set(keys).issubset(set(p['provides_fact_keys'])):
        raise VerificationInputError('fixture fact outside registered probe')
    for rec in record['coverage_receipts']:
        if (p['mutation_coverage'] != 'complete' or p['independence'] != 'independent_verifier'
            or rec['surface_id'] not in p['covered_mutation_surfaces']
            or rec['method'] != p['coverage_method']
            or rec['completeness'] != 'complete' or not rec['consistent_epoch']
            or not rec['independent_source']):
            raise VerificationInputError('fixture receipt not registered as complete independent evidence')
        # The following labels are fixtures, NOT actual snapshot-file evidence.
        if (not rec.get('snapshot_before_ref','').startswith('snapshot_before:')
            or not rec.get('snapshot_after_ref','').startswith('snapshot_after:')):
            raise VerificationInputError('unsupported simulated coverage receipt identifiers')
    return record


def verify(contract, probes, observations, *, run_id, epoch_id,
           pair=None, fixture_mode=False, capture_latency_ms=0.0,
           capture_bytes_read=0, trust_assumptions=None):
    """Return a Stage-1-schema-compliant Certificate for immutable evidence.

    `fixture_mode` is FOR TEST FIXTURES ONLY. It does not inspect the backing state,
    and certificates produced under that mode cannot be used as operational proof.
    """
    start = time.perf_counter_ns()
    validate_probes(contract, probes)
    registered = {p['probe_id']: p for p in probes}
    # Schema v1 has no executable frame-rule DSL. Enforce the explicitly
    # supported atomic accounting grammar rather than certify a frame with
    # an arbitrary or vacuous predicate.
    frame_policy = contract['frame_policy']
    if frame_policy['policy'] == 'closed_world':
        frame_obs = [o for o in contract['obligations'] if o['category'] == 'frame'
                     and o['predicate']['operator'] == 'count_eq'
                     and o['predicate'].get('expected') == 0
                     and o['predicate']['fact_key'].startswith('mutation.')]
        frame_surfaces = set().union(*(set(o['required_complete_coverage']) for o in frame_obs)) if frame_obs else set()
        if not frame_obs or not set(frame_policy['declared_mutation_surfaces']).issubset(frame_surfaces):
            raise VerificationInputError('closed-world contract requires zero-unaccounted-mutation frame checks for every declared surface')
        for frame_ob in frame_obs:
            key = frame_ob['predicate']['fact_key']
            if not any(key in p['provides_fact_keys'] and p['adapter'] in ('state_diff','external_status')
                       and p['independence'] in ('independent_verifier','conditionally_trusted')
                       for p in probes):
                raise VerificationInputError('closed-world frame fact requires registered state-diff or external-status inspection')
    if not run_id or not epoch_id:
        raise VerificationInputError('run and epoch are mandatory')
    if fixture_mode and pair is not None:
        raise VerificationInputError('fixture mode and real capture are mutually exclusive')
    if not fixture_mode:
        if pair is None:
            raise VerificationInputError('live verification requires a validated snapshot pair')
        pair.require_same_epoch()
        if pair.epoch_id != epoch_id:
            raise VerificationInputError('requested epoch does not match actual snapshot')
    if capture_latency_ms < 0 or capture_bytes_read < 0:
        raise VerificationInputError('negative capture cost')

    obs_ids = set()
    accepted = []
    for ob in observations:
        if ob['observation_id'] in obs_ids:
            raise VerificationInputError('duplicate observation id')
        obs_ids.add(ob['observation_id'])
        if ob['run_id'] != run_id or ob['epoch_id'] != epoch_id:
            raise VerificationInputError('cross-run or cross-epoch observation')
        spec = registered.get(ob['probe_id'])
        if spec is None:
            raise VerificationInputError('unregistered probe observation')
        if fixture_mode:
            _validate_fixture_record(ob, spec)
        else:
            validate_observation(ob, spec, pair=pair)
        accepted.append(ob)

    # Scope/fact/provenance: only independently verified observations may
    # establish persistence, process or external outcomes in this version.
    facts = {}
    fact_refs = defaultdict(set)
    conflicts = []
    unavailable_keys = set()
    unavailable_refs = defaultdict(set)
    trusted_receipts = defaultdict(list)
    for ob in accepted:
        spec = registered[ob['probe_id']]
        if ob['status'] != 'ok':
            unavailable_keys.update(spec['provides_fact_keys'])
            for unavailable_key in spec['provides_fact_keys']:
                unavailable_refs[unavailable_key].add(ob['observation_id'])
            continue
        if spec['independence'] != 'independent_verifier':
            continue
        for fact in ob['facts']:
            key = fact['fact_key']
            if key in facts and (type(facts[key]) != type(fact['value']) or facts[key] != fact['value']):
                conflicts.append(key)
                fact_refs[key].add(ob['observation_id'])
            else:
                facts[key] = fact['value']
                fact_refs[key].add(ob['observation_id'])
        for receipt in ob['coverage_receipts']:
            if (receipt['completeness'] == 'complete' and receipt['consistent_epoch']
                and receipt['independent_source'] and receipt['method'] == spec['coverage_method']
                and spec['mutation_coverage'] == 'complete'
                and receipt['surface_id'] in spec['covered_mutation_surfaces']):
                trusted_receipts[receipt['surface_id']].append((receipt, ob['observation_id']))

    frame = contract['frame_policy']
    must_cover = set(frame['declared_mutation_surfaces']) if frame['policy'] == 'closed_world' else set()
    req_method = frame['required_coverage_method']
    def cover(surface, method=req_method):
        for receipt, evidence_id in trusted_receipts.get(surface, []):
            if method == 'either' or method == 'none' or receipt['method'] == method:
                return evidence_id
        return None

    covered = {surface for surface in must_cover if cover(surface)}
    global_frame_missing = must_cover - covered
    results = []
    conflicted_keys = set(conflicts)
    for ob in contract['obligations']:
        pred = ob['predicate']
        refs = set(fact_refs.get(pred['fact_key'],()))
        refs.update(unavailable_refs.get(pred['fact_key'],()))
        if pred['operator'] == 'same_as':
            refs.update(fact_refs.get(pred['comparison_fact_key'],()))
            refs.update(unavailable_refs.get(pred['comparison_fact_key'],()))
        missing = set(ob['required_complete_coverage'])
        # An explicit obligation for transient mutation safety cannot be
        # certified by final-state snapshots alone.
        transient = ('transient' in pred['fact_key'] or 'transient' in ob['id'])
        special_method = 'complete_journal' if transient else req_method
        for surface in list(missing):
            evidence = cover(surface, special_method)
            if evidence:
                refs.add(evidence)
                missing.remove(surface)
        has_conflict = bool(conflicted_keys.intersection(
            {pred['fact_key'], *([pred['comparison_fact_key']] if pred['operator']=='same_as' else [])}
        ))
        value = _check_predicate(pred, facts)
        if has_conflict:
            truth = 'unknown'
            reason = 'evidence_conflict'
        elif value is False:
            # A witnessed failure dominates missing coverage/other unknowns.
            truth = 'fail'
            reason = _fail_reason(ob)
        elif missing:
            truth = 'unknown'
            reason = ('transient_mutation_unobserved' if transient else
                      'external_frame_unobserved' if any(s.startswith('external.') for s in missing)
                      else 'frame_coverage_incomplete')
        elif value is None:
            truth = 'unknown'
            reason = _unknown_reason(ob, unavailable_keys)
        else:
            truth = 'pass'
            reason = 'predicate_supported'
        results.append({'obligation_id':ob['id'],'truth':truth,'reason_code':reason,
                        'evidence_refs': sorted(refs)})

    if frame['policy'] == 'closed_world':
        frame_obligations = [o for o in contract['obligations'] if o['category']=='frame']
        # Missing coverage affects global success even if other obligations
        # omitted required_complete_coverage (defense in depth).
        if global_frame_missing:
            for result in results:
                if result['truth'] == 'pass' and result['obligation_id'] in {o['id'] for o in frame_obligations}:
                    result['truth'] = 'unknown'; result['reason_code'] = 'frame_coverage_incomplete'

    any_fail = [x for x in results if x['truth']=='fail']
    unknown = [x for x in results if x['truth']=='unknown']
    decision_status = 'normal'
    if conflicts:
        # Even when another predicate seems false, contradictory authoritative
        # evidence invalidates the coherent fact set. No success certification.
        verdict = 'UNCERTAIN'
        decision_status = 'evidence_conflict'
        reasons = ['evidence_conflict']
    elif any_fail:
        verdict = 'FAIL'
        reasons = ['known_violation_dominates_unknown'] if unknown else [x['reason_code'] for x in any_fail]
    elif unknown or global_frame_missing:
        verdict = 'UNCERTAIN'
        reasons = [x['reason_code'] for x in unknown]
        if global_frame_missing:
            reasons.append('frame_coverage_incomplete')
    else:
        verdict = 'PASS'
        reasons = ['all_obligations_supported']
    reasons = sorted(set(reasons))
    unresolved = sorted(x['obligation_id'] for x in results if x['truth']=='unknown')
    # If no matching actual-world model is available, `mode` must be conservative.
    planner_ms = round((time.perf_counter_ns()-start)/1e6, 6)
    seen_obs = [x['observation_id'] for x in accepted]
    certificates = {
        'schema_version':'1.0',
        'certificate_id':f'cert.{run_id}',
        'run_id':run_id,
        'contract_id':contract['contract_id'],
        'contract_sha256':digest(contract),
        'epoch_id':epoch_id,
        'mode':'conservative',
        'verdict':verdict,
        'decision_status':decision_status,
        'reason_codes':reasons,
        'obligation_results':results,
        'inspection_ids':list(dict.fromkeys(x['probe_id'] for x in accepted)),
        'evidence_refs':seen_obs,
        'verified_frame_surfaces':sorted(covered),
        'unresolved_obligation_ids':unresolved,
        'costs':{
            'capture_latency_ms':float(capture_latency_ms),
            'inspection_latency_ms':round(sum(float(x['actual_cost']['latency_ms']) for x in accepted),6),
            'planner_latency_ms':planner_ms,
            'bytes_read':int(capture_bytes_read) + sum(x['actual_cost']['bytes_read'] for x in accepted),
        },
        'trust_assumptions':trust_assumptions if trust_assumptions is not None else [
            'Independent read-only evidence adapters; consistent named epoch; declared scope only.',
            'Contract adequacy and capture isolation are assumed, not proven.'
        ],
        'created_at':utc_now(),
    }
    validate_shape(certificates,'Certificate')
    return certificates


def verify_fixture_directory(directory):
    """Evaluate *preauthored, non-live* Stage 1 input fixtures.

    This entrypoint never reads reference_possible_worlds or hidden truth.
    """
    directory = Path(directory)
    contract = read_json(directory/'task_contract.json')
    probes = read_json(directory/'probe_catalogue.json')
    observations = read_json(directory/'observations.json')
    if not observations:
        raise VerificationInputError('fixtures require an explicit run/epoch record')
    return verify(contract,probes,observations,
                  run_id=observations[0]['run_id'],epoch_id=observations[0]['epoch_id'],
                  fixture_mode=True,
                  trust_assumptions=[
                      'REFERENCE FIXTURE ONLY: snapshot receipts are simulated and not verified against live state.',
                      'Preauthored facts serve specification testing; not evidence of real agent task completion.'
                  ])


def verify_saved_run(run_directory, *, contract_path=None, probes_path=None):
    """Verify a previously captured Stage 2 run with independent real snapshots.

    Validates digests and snapshot references before admitting any facts.
    """
    root = Path(run_directory)
    sand = EvidenceSandbox(root)
    manifest = read_json(sand.evidence/'run_manifest.json')
    package_root=Path(__file__).resolve().parent.parent
    contract = read_json(contract_path or package_root/'examples/reference/task_contract.json')
    probes = read_json(probes_path or package_root/'examples/reference/probe_catalogue.json')
    pair = sand.load_pair(manifest['epoch_id'])
    validate_probes(contract,probes)
    observations = EvidenceLedger(sand.evidence).verify(
        manifest['observations'], {p['probe_id']:p for p in probes}, pair=pair)
    return verify(contract,probes,observations,
                  run_id=manifest['run_id'],epoch_id=manifest['epoch_id'], pair=pair,
                  capture_latency_ms=manifest['snapshot_capture_latency_ms'],
                  capture_bytes_read=manifest['snapshot_capture_bytes_read'],
                  trust_assumptions=[
                      'Snapshot/trace evidence originates from the Stage 2 cooperative, quiescent sandbox.',
                      'Database+filesystem snapshot is not an atomic distributed-world snapshot.',
                      'Verifier-owned artifacts are assumed isolated; hashes alone are not authentication.',
                      'Only declared SQLite/filesystem/trace surfaces are covered.'
                  ])
