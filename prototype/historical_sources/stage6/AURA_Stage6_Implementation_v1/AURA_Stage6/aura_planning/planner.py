"""CERA inspection strategies for explicitly bounded, model-relative scenarios.

IMPORTANT: `actual_world` is used ONLY by a synthetic observation oracle in tests
and benchmarking. Policies see `compatible_indices`, inspection specifications,
and past observations. It must never be passed to `plan_next` or `exact_value`.

No missing frame coverage may be inferred from apparent satisfaction of contract
predicates. Actual Stage 2 probes/certificates are handled by live_runner.py.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict
from functools import lru_cache
from typing import Any
import math

from aura_reasoning.model import enumerate_worlds, validate_model, _total_success
from aura_verifier.engine import _check_predicate

class PlanningError(ValueError):
    pass

def frozen_value(x):
    """JSON scalar tuple preserving types, including True vs 1."""
    if x is None:
        return ('null',None)
    if type(x) in (str,int,float,bool):
        return (type(x).__name__,x)
    raise PlanningError('only scalar declared fact values allowed')

@dataclass(frozen=True)
class Inspection:
    probe_id: str
    fact_keys: tuple[str,...]
    surfaces: tuple[str,...]
    cost: float
    available: bool=True

class FiniteInspectionProblem:
    """Frozen finite model, contract, catalogue and prior.

    `model` contains every possible world under *public pre-run assumptions*.
    In particular it must never be constructed from the hidden tested world.
    Outcome maps are computed from worlds but disclosed to a policy only after
    selecting a probe; learning the distribution of possible outcomes is allowed.
    """
    def __init__(self, contract:dict, model:dict, inspections:list[Inspection], prior=None):
        # Validate without synthetic test-world observations; empty probes sufficient.
        validate_model(model,contract,[],[])
        worlds, candidates,capped=enumerate_worlds(model,{})
        if capped or not worlds:
            raise PlanningError('frozen model is empty or exceeds declared enumeration limit')
        self.contract=contract
        self.model=model
        self.worlds=tuple(worlds)
        self.inspections={p.probe_id:p for p in inspections}
        if len(self.inspections)!=len(inspections):
            raise PlanningError('duplicate inspection id')
        if not inspections or len(inspections)>12:
            raise PlanningError('1..12 inspections allowed in small-instance reference')
        keys=set(model['fact_domains'])
        for p in inspections:
            if p.cost<=0 or not math.isfinite(p.cost):
                raise PlanningError('inspection costs must be positive and finite')
            if set(p.fact_keys)-keys:
                raise PlanningError('probe reads undeclared fact keys')
        self.required_surfaces=set(contract['frame_policy']['declared_mutation_surfaces']) if contract['frame_policy']['policy']=='closed_world' else set()
        covered=set().union(*(set(p.surfaces) for p in inspections if p.available))
        if self.required_surfaces-covered:
            # Such tasks may be provably FAIL but never PASS; do not reject.
            self.uncertifiable_surfaces=tuple(sorted(self.required_surfaces-covered))
        else:
            self.uncertifiable_surfaces=()
        self.satisfying=tuple(_total_success(contract,w) for w in worlds)
        if prior is None:
            prior=[1/len(worlds)]*len(worlds)
        if len(prior)!=len(worlds) or any(not math.isfinite(float(x)) or x<=0 for x in prior) or sum(prior)<=0:
            raise PlanningError('invalid prior')
        z=sum(prior)
        self.prior=tuple(float(p/z) for p in prior)
        self.initial_indices=tuple(range(len(worlds)))

    def outcome(self, probe_id, world_index):
        p=self.inspections[probe_id]
        if not p.available:
            return ('UNAVAILABLE',)
        return tuple(frozen_value(self.worlds[world_index][key]) for key in p.fact_keys)

    def partition(self, indices, probe_id):
        groups=defaultdict(list)
        for idx in indices:
            groups[self.outcome(probe_id,idx)].append(idx)
        return {k:tuple(v) for k,v in groups.items()}

    def verdict(self,indices,performed):
        if not indices:
            return 'UNCERTAIN'  # empty observational intersection cannot certify
        labels=[self.satisfying[i] for i in indices]
        if not any(labels):
            return 'FAIL'
        covered=set().union(*(set(self.inspections[p].surfaces) for p in performed
                              if self.inspections[p].available)) if performed else set()
        if all(labels) and self.required_surfaces.issubset(covered):
            return 'PASS'
        return 'UNCERTAIN'

    def mass(self,indices):
        return sum(self.prior[i] for i in indices)

def assess(problem, indices, performed):
    """Verdict, compatible-world count, and complete coverage information."""
    covered=set().union(*(set(problem.inspections[p].surfaces) for p in performed
                          if problem.inspections[p].available)) if performed else set()
    return {'verdict':problem.verdict(indices,performed),'compatible_worlds':len(indices),
            'missing_frame_surfaces':sorted(problem.required_surfaces-covered)}

def _remaining(problem,performed):
    return [p for p in problem.inspections.values() if p.probe_id not in performed and p.available]

def _counterexample_score(problem,indices,p):
    """Probability-mass of opposite-verdict pairs separated by a probe, per cost.

    A cross-class pair separated if its two worlds have distinct probe outcomes.
    If all worlds are successful but frame proof is missing, prefer a coverage probe.
    """
    successes=[i for i in indices if problem.satisfying[i]]
    failures=[i for i in indices if not problem.satisfying[i]]
    if not successes or not failures:
        return 0.0
    total=problem.mass(indices)
    # Distinguishing successful from failing states; not interested in splitting
    # worlds that share the same final success label.
    same=0.0
    part=problem.partition(indices,p.probe_id)
    for group in part.values():
        ps=sum(problem.prior[i] for i in group if problem.satisfying[i]);pf=sum(problem.prior[i] for i in group if not problem.satisfying[i])
        same+=ps*pf
    cross=sum(problem.prior[i] for i in successes)*sum(problem.prior[i] for i in failures)
    return max(0.,cross-same)/(total*total*p.cost)

def _greedy_score(problem, indices,performed,p):
    known=set().union(*(set(problem.inspections[r].fact_keys) for r in performed)) if performed else set()
    unknown_keys={o['predicate']['fact_key'] for o in problem.contract['obligations']}
    for o in problem.contract['obligations']:
        if o['predicate']['operator']=='same_as':unknown_keys.add(o['predicate']['comparison_fact_key'])
    covered=set().union(*(set(problem.inspections[r].surfaces) for r in performed)) if performed else set()
    missing=problem.required_surfaces-covered
    benefit=len((set(p.fact_keys)&unknown_keys)-known)+2*len(set(p.surfaces)&missing)
    return benefit/p.cost

def plan_next(problem,indices,performed,policy,*, fixed_order=None):
    """Choose an allowed probe without receiving hidden-world identity."""
    remain=_remaining(problem,performed)
    if not remain:
        return None
    if policy!='exhaustive' and problem.verdict(indices,performed)!='UNCERTAIN':
        return None
    if policy in ('fixed','exhaustive'):
        order=list(fixed_order or problem.inspections)
        return next((p for p in order if any(r.probe_id==p for r in remain)),None)
    if policy=='greedy':
        return max(remain,key=lambda p:(_greedy_score(problem,indices,performed,p),-p.cost,p.probe_id)).probe_id
    if policy=='cera':
        def score(p):
            covered=set().union(*(set(problem.inspections[r].surfaces) for r in performed)) if performed else set()
            coverage_gain=len((problem.required_surfaces-covered)&set(p.surfaces))
            s=_counterexample_score(problem,indices,p)
            # Prioritize counterexample discrimination when both outcomes plausible;
            # mandatory coverage when only successful worlds remain.
            mixed=any(problem.satisfying[i] for i in indices) and any(not problem.satisfying[i] for i in indices)
            return (s + (0.00001*coverage_gain/p.cost if mixed else coverage_gain/p.cost),
                    -p.cost,p.probe_id)
        return max(remain,key=score).probe_id
    if policy=='optimal':
        return exact_value(problem,indices,performed)['probe_id']
    raise PlanningError('unknown policy '+str(policy))

def exact_value(problem,indices=None,performed=()):
    """Bayes-optimal small finite reference, lexicographically:

    1. maximize probability of a decisive verdict, then
    2. minimize expected *additional* probe cost.

    Terminal UNCERTAIN is available when future observations cannot resolve
    uncertainty. It prevents optimizing cost by trivial abstention.
    """
    indices=tuple(sorted(problem.initial_indices if indices is None else indices))
    performed=frozenset(performed)
    if len(problem.inspections)>9 or len(problem.worlds)>500:
        raise PlanningError('exact policy intentionally limited to <=9 probes and <=500 worlds')
    @lru_cache(None)
    def solve(idx,used):
        v=problem.verdict(idx,used)
        if v!='UNCERTAIN':return (1.0,0.0,None)
        choices=_remaining(problem,used)
        best=(0.0,0.0,None)
        for p in choices:
            groups=problem.partition(idx,p.probe_id)
            mass=problem.mass(idx)
            coverage=0.0;future=0.0
            for g in groups.values():
                pr=problem.mass(g)/mass
                c,e,_=solve(tuple(g), used|frozenset({p.probe_id}))
                coverage+=pr*c;future+=pr*e
            totalcost=p.cost+future
            if coverage>best[0]+1e-12 or (coverage>0 and abs(coverage-best[0])<1e-12 and (best[2] is None or totalcost<best[1]-1e-12)):
                best=(coverage,totalcost,p.probe_id)
        return best
    cv,cost,p=solve(indices,performed)
    return {'decisive_probability':cv,'expected_remaining_probe_cost':cost,'probe_id':p,
            'cache_states':solve.cache_info().currsize}

def run_policy(problem,actual_world_index,policy,*,fixed_order=None,max_probes=None):
    """TEST-ONLY synthetic environment runner. Truth is used by oracle, not planner."""
    if not 0<=actual_world_index<len(problem.worlds):raise PlanningError('invalid synthetic world index')
    indices=problem.initial_indices
    seen=frozenset(); events=[]; cost=0.0
    while True:
        candidate=plan_next(problem,indices,seen,policy,fixed_order=fixed_order)
        if candidate is None or (max_probes is not None and len(events)>=max_probes):break
        actual_result=problem.outcome(candidate,actual_world_index)
        groups=problem.partition(indices,candidate)
        if actual_result not in groups:
            # Even test simulation must not certify if observation contradicts model.
            indices=()
        else:
            indices=groups[actual_result]
        seen=seen|frozenset({candidate})
        probe=problem.inspections[candidate];cost+=probe.cost
        events.append({'probe_id':candidate,'cost':probe.cost,'observation':list(actual_result),
                       'compatible_world_count':len(indices), 'verdict':problem.verdict(indices,seen)})
    status=assess(problem,indices,seen)
    true_success=problem.satisfying[actual_world_index]
    status.update({'policy':policy,'synthetic':True,'true_success':true_success,
                   'cost_units':round(cost,6),'num_probes':len(events),'events':events,
                   'correct_decisive':status['verdict']==('PASS' if true_success else 'FAIL'),
                   'false_pass':status['verdict']=='PASS' and not true_success,
                   'false_fail':status['verdict']=='FAIL' and true_success})
    return status
