"""Stage 1 schema compatibility plus Stage 2 cross-object invariants."""
from functools import lru_cache
from pathlib import Path
import json

from jsonschema import Draft202012Validator
from .util import digest


class ValidationError(ValueError):
    pass


@lru_cache(None)
def _schema(kind):
    loc = Path(__file__).resolve().parent.parent/'schemas'/f'{kind}.schema.json'
    return Draft202012Validator(json.loads(loc.read_text('utf-8')))


def validate_shape(data, kind):
    errors = sorted(_schema(kind).iter_errors(data), key=lambda e: tuple(str(s) for s in e.path))
    if errors:
        first = errors[0]
        raise ValidationError(f'{kind} schema: {list(first.path)}: {first.message}')
    return data


def _unique(keys, name):
    if len(keys) != len(set(keys)):
        raise ValidationError(f'duplicate {name}')


def validate_contract(c):
    validate_shape(c,'TaskContract')
    surfaces = {s['surface_id']:s for s in c['surfaces']}
    _unique([s['surface_id'] for s in c['surfaces']], 'contract surfaces')
    _unique([o['id'] for o in c['obligations']], 'contract obligations')
    mutable = {s['surface_id'] for s in c['surfaces'] if s['mutable']}
    frame = c['frame_policy']
    declared = set(frame['declared_mutation_surfaces'])
    if not declared.issubset(mutable):
        raise ValidationError('frame references undeclared or immutable surfaces')
    if frame['policy']=='closed_world' and frame['required_coverage_method']=='none':
        raise ValidationError('closed-world frame cannot disable required coverage')
    for effect in frame['allowed_effects']:
        if effect['surface_id'] not in declared:
            raise ValidationError('allowed effect outside declared frame surfaces')
        kind = surfaces[effect['surface_id']]['kind']
        if kind == 'filesystem' and effect['operation'] not in ('create_file','modify_file','delete_file','none'):
            raise ValidationError('invalid filesystem effect kind')
        if kind == 'sqlite' and effect['operation'] not in ('insert','update','delete','none'):
            raise ValidationError('invalid SQLite effect kind')
    for ob in c['obligations']:
        if ob['surface_id'] not in surfaces:
            raise ValidationError('obligation references unknown surface')
        if not set(ob['required_complete_coverage']).issubset(declared):
            raise ValidationError('obligation requires coverage outside declared mutation surfaces')
        p = ob['predicate']
        op = p['operator']
        if op in ('eq','neq','count_eq') and 'expected' not in p:
            raise ValidationError(f'{op} requires expected')
        if op == 'count_eq' and (type(p['expected']) is not int or p['expected'] < 0):
            raise ValidationError('count_eq requires nonnegative integer')
        if op in ('true','false') and 'expected' in p:
            raise ValidationError('true/false must not contain expected')
        if op == 'same_as' and 'comparison_fact_key' not in p:
            raise ValidationError('same_as requires comparison_fact_key')
        if op != 'same_as' and 'comparison_fact_key' in p:
            raise ValidationError('unexpected comparison_fact_key')
    return c


def validate_probes(c, probes):
    validate_contract(c)
    ids = [p['probe_id'] for p in probes]
    _unique(ids,'probe IDs')
    surfaces = {s['surface_id']:s for s in c['surfaces']}
    for p in probes:
        validate_shape(p,'ProbeSpec')
        if p['surface_id'] not in surfaces:
            raise ValidationError('probe references unknown surface')
        covered = set(p['covered_mutation_surfaces'])
        if not covered.issubset(set(surfaces)):
            raise ValidationError('probe covers unknown surface')
        if p['mutation_coverage']=='complete':
            if p['independence'] == 'agent_self_report' or p['coverage_method']=='none' or not covered:
                raise ValidationError('complete coverage requires independent source and covered surfaces')
            if not all(surfaces[s]['mutable'] for s in covered):
                raise ValidationError('coverage must target mutable surfaces')
        if p['coverage_method']=='snapshot_pair' and p['adapter']!='state_diff':
            raise ValidationError('snapshot pair receipts require the state_diff adapter')
        if p['adapter']=='state_diff' and p['coverage_method'] not in ('snapshot_pair','complete_journal'):
            raise ValidationError('state_diff requires snapshot_pair or complete_journal')
        if not p['read_only']:
            raise ValidationError('write-capable probe refused')
    available_keys = {key for p in probes for key in p['provides_fact_keys']}
    for ob in c['obligations']:
        if ob['predicate']['fact_key'] not in available_keys:
            raise ValidationError('unregistered obligation fact key: '+ob['predicate']['fact_key'])
        if ob['predicate']['operator']=='same_as' and ob['predicate']['comparison_fact_key'] not in available_keys:
            raise ValidationError('unregistered comparison fact key')
    return probes


def observation_digest(record):
    return digest({k:v for k,v in record.items() if k!='payload_sha256'})


def validate_observation(ob, probe, *, pair=None):
    validate_shape(ob,'Observation')
    if ob['probe_id'] != probe['probe_id']:
        raise ValidationError('observation/probe mismatch')
    if ob['channel'] != probe['independence']:
        raise ValidationError('observation channel mismatch')
    if ob['payload_sha256'] != observation_digest(ob):
        raise ValidationError('observation content digest mismatch')
    if ob['status']=='ok':
        if ob['reason_code']!='none':
            raise ValidationError('successful probe has error code')
    else:
        if ob['reason_code']=='none' or ob['facts'] or ob['coverage_receipts']:
            raise ValidationError('unavailable/error observation must carry no facts or receipts')
    fkeys = [f['fact_key'] for f in ob['facts']]
    _unique(fkeys, 'observation facts')
    if not set(fkeys).issubset(set(probe['provides_fact_keys'])):
        raise ValidationError('probe asserted an unregistered fact')
    for r in ob['coverage_receipts']:
        if (probe['mutation_coverage']!='complete' or r['surface_id'] not in probe['covered_mutation_surfaces'] or
            r['method'] != probe['coverage_method'] or r['independent_source'] != (probe['independence']=='independent_verifier')):
            raise ValidationError('unauthorized coverage receipt')
        if r['completeness']=='complete' and not r['consistent_epoch']:
            raise ValidationError('complete receipt with inconsistent epoch')
        if r['method']=='snapshot_pair':
            if pair is None:
                raise ValidationError('snapshot receipt requires independently verified pair')
            pair.require_same_epoch()
            if ob['epoch_id'] != pair.epoch_id:
                raise ValidationError('observation epoch differs from snapshot')
            if r.get('snapshot_before_ref') != pair.before_ref or r.get('snapshot_after_ref') != pair.after_ref:
                raise ValidationError('coverage receipt references different snapshots')
    return ob


def detect_conflicts(observations, registered_probes=None):
    """Report conflicting same-epoch authoritative facts; no verdict is issued."""
    registered_probes = registered_probes or {}
    seen = {}
    conflicts = []
    for ob in observations:
        if ob['status'] != 'ok' or ob['channel'] != 'independent_verifier':
            continue
        if registered_probes:
            p = registered_probes.get(ob['probe_id'])
            if p is None:
                continue
        for f in ob['facts']:
            key = (ob['run_id'],ob['epoch_id'],f['fact_key'])
            canonical = json.dumps(f['value'],sort_keys=True)
            if key in seen and seen[key][0]!=canonical:
                conflicts.append({'run_id':key[0],'epoch_id':key[1],
                                  'fact_key':key[2],'observation_a':seen[key][1],
                                  'observation_b':ob['observation_id']})
            else:
                seen[key]=(canonical,ob['observation_id'])
    return conflicts
