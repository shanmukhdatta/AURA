"""Stage 4 bounded-compatible-world reasoning.

Purpose: a finite, explicitly scoped research reference semantics. The model
may encode only public domain information and declared invariant rules, never
the hidden ground-truth world of the evaluated episode. This is NOT a general
agent/runtime model checker and it does not verify a model's assumptions.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import product
import time
from typing import Any

from aura_evidence.util import digest
from aura_evidence.validation import validate_shape
from aura_verifier.engine import verify, _check_predicate


class ModelInputError(ValueError):
    pass


def same_typed(a: Any, b: Any) -> bool:
    return type(a) is type(b) and a == b


def _primitive(v):
    return v is None or type(v) in (str, int, float, bool)


def _check_formula(formula, keys, depth=0):
    if depth > 16 or not isinstance(formula, dict):
        raise ModelInputError('invalid/deep constraint formula')
    op = formula.get('op')
    if op == 'fact_eq':
        if set(formula) != {'op','fact_key','value'} or formula['fact_key'] not in keys or not _primitive(formula['value']):
            raise ModelInputError('invalid fact_eq atom')
    elif op == 'fact_same':
        if set(formula) != {'op','left','right'} or formula['left'] not in keys or formula['right'] not in keys:
            raise ModelInputError('invalid fact_same atom')
    elif op == 'not':
        if set(formula) != {'op','arg'}:
            raise ModelInputError('invalid not formula')
        _check_formula(formula['arg'],keys,depth+1)
    elif op in ('and','or'):
        if set(formula) != {'op','args'} or not isinstance(formula['args'],list) or len(formula['args']) < 2:
            raise ModelInputError('invalid conjunction/disjunction')
        for f in formula['args']:
            _check_formula(f, keys, depth+1)
    elif op == 'implies':
        if set(formula) != {'op','if','then'}:
            raise ModelInputError('invalid implication')
        _check_formula(formula['if'],keys,depth+1)
        _check_formula(formula['then'],keys,depth+1)
    else:
        raise ModelInputError('unsupported constraint operator')


def _formula_eval(formula, world):
    op=formula['op']
    if op=='fact_eq':
        return same_typed(world[formula['fact_key']], formula['value'])
    if op=='fact_same':
        return same_typed(world[formula['left']],world[formula['right']])
    if op=='not':
        return not _formula_eval(formula['arg'],world)
    if op=='and':
        return all(_formula_eval(f,world) for f in formula['args'])
    if op=='or':
        return any(_formula_eval(f,world) for f in formula['args'])
    if op=='implies':
        return not _formula_eval(formula['if'],world) or _formula_eval(formula['then'],world)
    raise ModelInputError('unsupported constraint operator')


def validate_model(model, contract, probes, observations):
    """Check bounded-world model, domain coverage, and independent evidence compatibility.

    `constraints` are *trusted model assumptions*; they are not inferred from
    hidden fault labels and must be audited independently of test outcomes.
    """
    if not isinstance(model,dict) or set(model) != {'schema_version','model_id','fact_domains','constraints','max_worlds'}:
        raise ModelInputError('invalid model fields')
    if model['schema_version']!='1.0' or not isinstance(model['model_id'],str) or not model['model_id']:
        raise ModelInputError('invalid model version/identity')
    domains=model['fact_domains']
    if not isinstance(domains,dict) or not domains:
        raise ModelInputError('nonempty domains required')
    for k,values in domains.items():
        if not isinstance(k,str) or not k or not isinstance(values,list) or not values or len(values)>32:
            raise ModelInputError('invalid finite domain')
        if any(not _primitive(v) for v in values):
            raise ModelInputError('domains are restricted to scalar JSON facts')
        if any(same_typed(a,b) for i,a in enumerate(values) for b in values[i+1:]):
            raise ModelInputError('duplicate typed domain value')
    if type(model['max_worlds']) is not int or not 1<=model['max_worlds']<=100000:
        raise ModelInputError('invalid max_worlds')
    if not isinstance(model['constraints'],list) or len(model['constraints'])>128:
        raise ModelInputError('invalid constraint list')
    for formula in model['constraints']:
        _check_formula(formula,domains)
    required=set()
    for ob in contract['obligations']:
        pred=ob['predicate'];required.add(pred['fact_key'])
        if pred['operator']=='same_as':required.add(pred['comparison_fact_key'])
    missing=required-set(domains)
    if missing:
        raise ModelInputError(f'model omits obligated fact domains: {sorted(missing)}')
    # An evidence key not declared in the finite model is an error if it was
    # emitted by a registered independent probe. Prevent silent exclusion.
    independent_ids={p['probe_id'] for p in probes if p['independence']=='independent_verifier'}
    independently_observed={f['fact_key'] for o in observations if o['probe_id'] in independent_ids and o['status']=='ok' for f in o['facts']}
    missing_evidence=independently_observed-set(domains)
    if missing_evidence:
        raise ModelInputError(f'model omits trusted observed fact domains: {sorted(missing_evidence)}')
    return model


def enumerate_worlds(model, observed):
    """Enumerate in schema-defined order; return (worlds, candidates, capped).

    A hard cap is applied to the *raw Cartesian product* to avoid pathological
    enumeration masked by constraints. This baseline is deliberately simple.
    """
    keys=sorted(model['fact_domains'])
    vals=[model['fact_domains'][k] for k in keys]
    estimated=1
    for d in vals:
        estimated*=len(d)
    if estimated>model['max_worlds']:
        return [], estimated, True
    worlds=[]
    for values in product(*vals):
        world=dict(zip(keys,values))
        if not all(same_typed(world[k],v) for k,v in observed.items()):
            continue
        if all(_formula_eval(c,world) for c in model['constraints']):
            worlds.append(world)
    return worlds,estimated,False


def _total_success(contract, world):
    return all(_world_check(ob['predicate'],world) for ob in contract['obligations'])


def _world_check(pred,world):
    # In complete-world semantics, NULL in a relational comparison is *not*
    # proof of equality. Align with Stage 3's safe comparison treatment.
    result=_check_predicate(pred,world)
    return result is True


def graph_for_contract(contract,probes):
    """Immutable, auditable obligation-to-fact-to-probe dependency graph.

    This graph represents potential support, not proof that a probe has run.
    """
    by_key=defaultdict(list)
    for p in probes:
        for key in p['provides_fact_keys']:
            by_key[key].append(p['probe_id'])
    graph=[]
    for ob in contract['obligations']:
        pred=ob['predicate']
        keys=[pred['fact_key']]
        if pred['operator']=='same_as':keys.append(pred['comparison_fact_key'])
        graph.append({'obligation_id':ob['id'],'category':ob['category'],
                      'fact_keys':keys,
                      'probe_ids':sorted({p for k in keys for p in by_key[k]}),
                      'required_coverage':ob['required_complete_coverage']})
    return graph


def verify_bounded(contract,probes,observations,model,*,run_id,epoch_id,
                   pair=None,fixture_mode=False,capture_latency_ms=0.0,
                   capture_bytes_read=0,trust_assumptions=None):
    """Return (Stage-1 compliant bounded certificate, independent reasoning ledger).

    Calls full Stage 3 admission first: the bounded reasoner never accepts
    arbitrary input facts or actual-world labels. Additional constraints are
    explicit model assumptions and do not count as independent observations.
    """
    reasoning_start_ns=time.perf_counter_ns()
    conservative,ctx=verify(contract,probes,observations,run_id=run_id,epoch_id=epoch_id,
                            pair=pair,fixture_mode=fixture_mode,
                            capture_latency_ms=capture_latency_ms,
                            capture_bytes_read=capture_bytes_read,
                            trust_assumptions=trust_assumptions,return_context=True)
    validate_model(model, contract, probes, observations)
    ledger={
        'schema_version':'1.0',
        'reasoner':'finite_world_enumeration',
        'model_id':model['model_id'],
        'model_sha256':digest(model),
        'contract_sha256':conservative['contract_sha256'],
        'run_id':run_id,'epoch_id':epoch_id,
        'graph':graph_for_contract(contract,probes),
        'observed_fact_keys':sorted(ctx['facts']),
        'conflicted_fact_keys':ctx['conflicts'],
        'assumption_count':len(model['constraints']),
        'model_domain_size':None,
        'compatible_world_count':None,
        'satisfying_world_count':None,
        'failing_world_count':None,
        'success_witness':None,'failure_witness':None,
        'conservative_verdict':conservative['verdict'],
        'bounded_verdict':None,
        'limitation':'Finite explicitly authored model; cannot establish that model constraints are true in the external world.'
    }
    def finish(certificate, ledger_record):
        elapsed_ms=round((time.perf_counter_ns()-reasoning_start_ns)/1e6,6)
        ledger_record['stage4_reasoning_latency_ms']=elapsed_ms
        certificate['costs']['planner_latency_ms']=round(
            certificate['costs']['planner_latency_ms']+elapsed_ms,6)
        validate_shape(certificate,'Certificate')
        return certificate,ledger_record

    cert=dict(conservative)
    cert['costs']=dict(conservative['costs'])
    cert['mode']='bounded_exact'
    cert['trust_assumptions']=list(conservative['trust_assumptions'])+[
        f'Finite model {model["model_id"]} SHA256 {digest(model)} is reviewed external input, not ground truth.',
        'Bounded exactness holds only relative to complete declared finite domains and trusted assumptions.'
    ]
    if ctx['conflicts']:
        # Do not discard incoherent real observations to make a model satisfiable.
        cert['verdict']='UNCERTAIN';cert['decision_status']='evidence_conflict'
        cert['reason_codes']=['evidence_conflict']
        ledger['bounded_verdict']=cert['verdict']
        return finish(cert,ledger)

    worlds,domain_size,capped=enumerate_worlds(model,ctx['facts'])
    ledger['model_domain_size']=domain_size
    if capped:
        cert['verdict']='UNCERTAIN';cert['decision_status']='solver_indeterminate'
        cert['reason_codes']=['bounded_enumeration_limit']
        cert['unresolved_obligation_ids']=sorted(o['id'] for o in contract['obligations'])
        for r in cert['obligation_results']:
            r['truth']='unknown';r['reason_code']='solver_indeterminate'
        ledger['bounded_verdict']='UNCERTAIN'
        return finish(cert,ledger)
    ledger['compatible_world_count']=len(worlds)
    if not worlds:
        # Inconsistent models cannot establish PASS. However, direct independent
        # evidence may ALREADY prove a contract violation without any model.
        # A bad author-specified domain must not erase that observed FAIL.
        # Genuine evidence-vs-evidence conflicts were handled above and abstain.
        if conservative['verdict']=='FAIL':
            cert['verdict']='FAIL';cert['decision_status']='model_inconsistent'
            cert['reason_codes']=['direct_observed_contract_violation','model_inconsistent_with_observation']
            ledger['bounded_verdict']='FAIL'
            return finish(cert,ledger)
        cert['verdict']='UNCERTAIN';cert['decision_status']='model_inconsistent'
        cert['reason_codes']=['model_inconsistent_with_observation']
        cert['unresolved_obligation_ids']=sorted(o['id'] for o in contract['obligations'])
        for r in cert['obligation_results']:
            r['truth']='unknown';r['reason_code']='model_inconsistent'
        ledger['bounded_verdict']='UNCERTAIN'
        return finish(cert,ledger)
    success=[w for w in worlds if _total_success(contract,w)]
    failure=[w for w in worlds if not _total_success(contract,w)]
    ledger['satisfying_world_count']=len(success)
    ledger['failing_world_count']=len(failure)
    ledger['success_witness']=success[0] if success else None
    ledger['failure_witness']=failure[0] if failure else None
    old_by_id={r['obligation_id']:r for r in conservative['obligation_results']}
    out=[]
    for ob in contract['obligations']:
        values=[_world_check(ob['predicate'],w) for w in worlds]
        refs=list(old_by_id[ob['id']]['evidence_refs'])
        req_missing=(old_by_id[ob['id']]['truth']=='unknown' and
                     old_by_id[ob['id']]['reason_code'] in (
                         'frame_coverage_incomplete','transient_mutation_unobserved','external_frame_unobserved'))
        if not any(values):
            truth='fail';reason='entailed_violation_by_bounded_model'
        elif all(values) and not req_missing:
            truth='pass';reason=('predicate_supported' if old_by_id[ob['id']]['truth']=='pass'
                                  else 'entailed_satisfaction_by_bounded_model')
        else:
            truth='unknown';reason=('missing_required_coverage' if req_missing else 'mixed_compatible_worlds')
        out.append({'obligation_id':ob['id'],'truth':truth,'reason_code':reason,'evidence_refs':refs})
    cert['obligation_results']=out
    cert['unresolved_obligation_ids']=sorted(r['obligation_id'] for r in out if r['truth']=='unknown')
    coverage_missing=bool(ctx['missing_frame_surfaces']) or any(
        old_by_id[o['id']]['reason_code'] in (
            'frame_coverage_incomplete','transient_mutation_unobserved','external_frame_unobserved')
        and old_by_id[o['id']]['truth']=='unknown'
        for o in contract['obligations'] if o['category']=='frame')
    if not success:
        cert['verdict']='FAIL';cert['reason_codes']=['joint_unsatisfiable_completion' if not any(r['truth']=='fail' for r in out)
                                                      else 'bounded_entailed_violation']
    elif not failure and not coverage_missing and not cert['unresolved_obligation_ids']:
        cert['verdict']='PASS';cert['reason_codes']=['all_compatible_worlds_satisfy_contract']
    else:
        cert['verdict']='UNCERTAIN';cert['reason_codes']=['missing_required_coverage' if coverage_missing else 'mixed_compatible_worlds']
    cert['decision_status']='normal'
    ledger['bounded_verdict']=cert['verdict']
    return finish(cert,ledger)
