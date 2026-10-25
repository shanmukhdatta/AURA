"""Explicit model templates for EDUCATIONAL/REFERENCE bounded-world evaluation.

Do not treat these domains as measured support, recovered database truth,
or operational coverage. A Stage 4 research model must be independently
reviewed before its conditional conclusions can support operational use.
"""
from __future__ import annotations
from aura_evidence.util import digest


def _distinct(vals):
    unique=[]
    for v in vals:
        if not any(type(u) is type(v) and u==v for u in unique):
            unique.append(v)
    return unique


def _candidate_for(pred):
    op=pred['operator']
    if op in ('true','false'):
        return [False,True]
    if op=='count_eq':
        n=pred['expected'];return _distinct([0,n,n+1])
    if op in ('eq','neq'):
        e=pred['expected']
        if type(e) is bool:return [False,True]
        if type(e) is int:return _distinct([e-1,e,e+1])
        if type(e) is float:return _distinct([e-1.0,e,e+1.0])
        if type(e) is str:return _distinct([e,e+'__alternative'])
        return [None,'not_null']
    return [None,0,1]


def make_reference_model(contract,probes,observations,*,model_id='model.reference.v1',max_worlds=8192):
    by_key={}
    for ob in contract['obligations']:
        pred=ob['predicate']
        by_key.setdefault(pred['fact_key'],[])
        by_key[pred['fact_key']].extend(_candidate_for(pred))
        if pred['operator']=='same_as':
            by_key.setdefault(pred['comparison_fact_key'],[])
            by_key[pred['comparison_fact_key']].extend(_candidate_for(pred))
    independents={p['probe_id'] for p in probes if p['independence']=='independent_verifier'}
    for ob in observations:
        if ob['probe_id'] in independents and ob['status']=='ok':
            for fact in ob['facts']:
                by_key.setdefault(fact['fact_key'],[])
                by_key[fact['fact_key']].insert(0,fact['value'])
    # For keys with a single independent observed value there is no reason to
    # explore different values: observation admission already fixes the value.
    observed={}
    for ob in observations:
        if ob['probe_id'] in independents and ob['status']=='ok':
            for f in ob['facts']:
                observed.setdefault(f['fact_key'],[]).append(f['value'])
    domains={}
    for key,values in sorted(by_key.items()):
        domains[key]=_distinct(observed[key]) if key in observed else _distinct(values)
    return {'schema_version':'1.0','model_id':model_id,
            'fact_domains':domains,'constraints':[],'max_worlds':max_worlds}
