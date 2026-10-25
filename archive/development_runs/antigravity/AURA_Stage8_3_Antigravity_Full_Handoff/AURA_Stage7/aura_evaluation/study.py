"""Paired experimental analysis of CERA and matched finite-world baselines.

This is a CONTROLLED SYNTHETIC STUDY. There are no agent-generated trajectories.
All algorithms receive exactly the same contract, candidate worlds, authorized
inspections and declared prior per episode. The simulator-only oracle reveals
hidden world values only after the policy has selected an inspection.

Statistical clusters are authored task templates, NOT individual worlds or seeds.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import replace
from pathlib import Path
import csv, hashlib, json, math, statistics, time, random
import numpy as np

from aura_planning.examples import make_problem
from aura_planning.planner import FiniteInspectionProblem, Inspection, run_policy

DOMAINS=('records','orders','access','files')
POLICIES=('fixed','greedy','cera','optimal','exhaustive')
REGIMES=('uniform','clean_50','clean_90')
CASES=12



def make_diverse_problem(domain,case):
    """48 different preregistered-authored probe catalogues and contract instances.

    Uses deterministic seed derived from domain/case, NOT from observed outcome.
    Synthetic exercise only; task labels are intentionally unrelated to real agents.
    """
    if domain not in DOMAINS or not 0<=case<CASES:raise ValueError('bad case')
    di=DOMAINS.index(domain)
    rng=random.Random(51420+1091*di+97*case)
    n=4+(case%2)
    labels={
        'records':('record_updated','report_saved','authorization_checked','report_consistent','mutation_clean'),
        'orders':('order_cancelled','stock_restored','refund_recorded','receipt_saved','mutation_clean'),
        'access':('role_assigned','ticket_approved','audit_logged','config_saved','mutation_clean'),
        'files':('files_moved','hashes_preserved','manifest_saved','index_updated','mutation_clean'),
    }[domain]
    keys=labels[:n-1]+(labels[-1],)
    contract={'obligations':[{'id':'ob_'+k,'category':'frame' if i==n-1 else 'outcome',
       'predicate':{'operator':'true','fact_key':k},
       'required_complete_coverage':['scope.main'] if i==n-1 else []}
       for i,k in enumerate(keys)],
       'frame_policy':{'policy':'closed_world','declared_mutation_surfaces':['scope.main']}}
    constraints=[]
    # Externally declared relationships, all valid under all-true clean world.
    if case%3==1:
        constraints.append({'op':'implies','if':{'op':'fact_eq','fact_key':keys[1],'value':True},
             'then':{'op':'fact_eq','fact_key':keys[0],'value':True}})
    if case%4==3:
        constraints.append({'op':'implies','if':{'op':'fact_eq','fact_key':keys[2],'value':True},
             'then':{'op':'fact_eq','fact_key':keys[1],'value':True}})
    model={'schema_version':'1.0','model_id':f'{domain}_heterogeneous_{case:02d}',
           'fact_domains':{k:[False,True] for k in keys},'constraints':constraints,'max_worlds':500}
    probes=[]
    for i,k in enumerate(keys):
        lo=3.0 if i==n-1 else .55
        hi=10.0 if i==n-1 else 4.2
        probes.append(Inspection(f'fact_{i}',(k,),('scope.main',) if i==n-1 else (),round(rng.uniform(lo,hi),3)))
    for j in range(2):
        chosen=tuple(keys[i] for i in sorted(rng.sample(range(n),rng.choice([2,3]))))
        # Joint inspector may cover frame if and only if it reads the mutation_clean fact.
        surface=('scope.main',) if keys[-1] in chosen else ()
        probes.append(Inspection(f'joined_{j}',chosen,surface,round(rng.uniform(1.3,8.5),3)))
    probes.append(Inspection('bulk_evidence',tuple(keys),('scope.main',),round(rng.uniform(7,22),3)))
    assert len(probes)<=9
    return FiniteInspectionProblem(contract,model,probes)

def prior_weights(problem, regime):
    n=len(problem.worlds)
    if regime=='uniform': return [1.0/n]*n
    p={'clean_50':0.50,'clean_90':0.90}[regime]
    clean=[i for i,s in enumerate(problem.satisfying) if s]
    if not clean or len(clean)==n:
        return [1.0/n]*n
    return [(p/len(clean) if i in clean else (1-p)/(n-len(clean))) for i in range(n)]


def expected_outcomes(problem, domain, case, regime):
    """Each policy uses the same world assignments and frozen declared prior."""
    prior=prior_weights(problem,regime)
    policy_results={}
    for policy in POLICIES:
        runs=[]
        for i in range(len(problem.worlds)):
            r=run_policy(problem,i,policy)
            assert not (r['false_pass'] or r['false_fail']), 'unexpected unsound decision'
            runs.append(r)
        policy_results[policy]=runs
    rows=[]; summary=[]
    task_id=f'{domain}_{case:02d}'
    for i in range(len(problem.worlds)):
        for policy in POLICIES:
            r=policy_results[policy][i]
            rows.append({'task_template':task_id,'domain':domain,'case':case,
                'prior_regime':regime,'world_index':i,'prior_weight':round(prior[i],12),
                'num_worlds':len(problem.worlds),'policy':policy,
                'actual_world_success':int(r['true_success']),
                'num_failed_obligations':sum(not v for v in problem.worlds[i].values()),
                'decision':r['verdict'],'cost_units':r['cost_units'],
                'probes':r['num_probes'],'false_pass':int(r['false_pass']),
                'false_fail':int(r['false_fail']),'correct_decisive':int(r['correct_decisive']),
                'selected_probes':'|'.join(x['probe_id'] for x in r['events']),
                'source_type':'authored_finite_world_not_agent_rollout'})
    for policy in POLICIES:
        runs=policy_results[policy]
        summary.append({'task_template':task_id,'domain':domain,'case':case,
            'prior_regime':regime,'policy':policy,'worlds':len(runs),
            'expected_cost':round(sum(prior[i]*r['cost_units'] for i,r in enumerate(runs)),9),
            'expected_probes':round(sum(prior[i]*r['num_probes'] for i,r in enumerate(runs)),9),
            'coverage':round(sum(prior[i]*(r['verdict']!='UNCERTAIN') for i,r in enumerate(runs)),9),
            'false_pass_probability':sum(prior[i]*r['false_pass'] for i,r in enumerate(runs)),
            'false_fail_probability':sum(prior[i]*r['false_fail'] for i,r in enumerate(runs))})
    return rows,summary


def with_prior(problem,regime):
    return FiniteInspectionProblem(problem.contract,problem.model,list(problem.inspections.values()),prior_weights(problem,regime))


def paired_cluster_bootstrap(summary,policy_a='cera',policy_b='greedy',seed=20261024,B=2500):
    """Template-cluster bootstrap descriptive sensitivity (NOT population CI)."""
    d=defaultdict(dict)
    for r in summary:
        d[(r['prior_regime'],r['task_template'])][r['policy']]=r['expected_cost']
    rng=np.random.default_rng(seed)
    out=[]
    for regime in REGIMES:
        diffs=np.array([v[policy_a]-v[policy_b] for (reg,task),v in sorted(d.items()) if reg==regime],dtype=float)
        n=len(diffs)
        inds=rng.integers(0,n,size=(B,n))
        boot=diffs[inds].mean(axis=1)
        out.append({'regime':regime,'comparison':f'{policy_a}_minus_{policy_b}',
                    'templates':n,'mean_cost_difference':float(diffs.mean()),
                    'bootstrap_95_low':float(np.quantile(boot,.025)),
                    'bootstrap_95_high':float(np.quantile(boot,.975)),
                    'fraction_templates_better':float(np.mean(diffs<0)),
                    'interpretation':'resampling authored templates, not population inference'})
    return out


def boundary_failure_controls():
    """Missing authoritative frame readback: no PASS, even on truly clean worlds."""
    rows=[]
    for domain in DOMAINS:
        source=make_problem(domain,0)
        probes=[replace(p,available=False) if p.surfaces else p for p in source.inspections.values()]
        p=FiniteInspectionProblem(source.contract,source.model,probes)
        clean=[i for i,s in enumerate(p.satisfying) if s]
        invalid=[i for i,s in enumerate(p.satisfying) if not s]
        assert clean and invalid
        for cls,ids in [('success',clean),('failure',invalid)]:
            for idx in ids[:2]:
                for policy in ('fixed','greedy','cera'):
                    r=run_policy(p,idx,policy)
                    rows.append({'domain':domain,'actual_world':cls,'policy':policy,
                                 'decision':r['verdict'],'false_pass':int(r['false_pass']),
                                 'false_fail':int(r['false_fail']),
                                 'frame_probe_available':False,
                                 'source_type':'authored_negative_control'})
                    assert r['verdict']!='PASS'
    return rows


def budget_controls():
    """Coverage/cost tradeoff under maximum probe budgets, same planner and catalogues."""
    rows=[]
    for domain in DOMAINS:
        for case in (0,1,2,3):
            p=make_problem(domain,case)
            for budget in (0,1,2,3,4,6):
                for policy in ('fixed','greedy','cera'):
                    runs=[run_policy(p,i,policy,max_probes=budget) for i in range(len(p.worlds))]
                    rows.append({'task_template':f'{domain}_{case:02d}','domain':domain,
                                 'budget':budget,'policy':policy,'worlds':len(runs),
                                 'mean_cost':statistics.mean(r['cost_units'] for r in runs),
                                 'coverage':sum(r['verdict']!='UNCERTAIN' for r in runs)/len(runs),
                                 'false_pass_count':sum(r['false_pass'] for r in runs),
                                 'false_fail_count':sum(r['false_fail'] for r in runs),
                                 'source_type':'authored_budget_control'})
    return rows


def scaling_controls():
    """Known assumptions; vary obligation count. No extrapolation to agent runtimes."""
    rows=[]
    for n in (4,5,6,7,8):
        keys=[f'outcome_{i}' for i in range(n-1)]+['frame_clean']
        obligations=[{'id':'ob_'+k,'category':'frame' if i==n-1 else 'outcome',
                      'predicate':{'operator':'true','fact_key':k},
                      'required_complete_coverage':['scope.main'] if i==n-1 else []} for i,k in enumerate(keys)]
        contract={'obligations':obligations,'frame_policy':{'policy':'closed_world','declared_mutation_surfaces':['scope.main']}}
        model={'schema_version':'1.0','model_id':f'scale_{n}',
               'fact_domains':{k:[False,True] for k in keys},'constraints':[],'max_worlds':500}
        probes=[Inspection(f'individual_{i}',(k,),('scope.main',) if i==n-1 else (),1.0+(i%3)) for i,k in enumerate(keys)]
        probes.append(Inspection('bulk',tuple(keys),('scope.main',),n*1.9))
        problem=FiniteInspectionProblem(contract,model,probes)
        indices=list(range(len(problem.worlds)))
        # All the fully-successful world, the all-fail world, plus deterministic sample.
        selected=list(dict.fromkeys([0,len(indices)-1]+[int(round(j*(len(indices)-1)/15)) for j in range(16)]))
        for policy in ('fixed','greedy','cera'):
            st=time.perf_counter_ns()
            res=[run_policy(problem,i,policy) for i in selected]
            elapsed=(time.perf_counter_ns()-st)/1e6
            rows.append({'facts':n,'possible_worlds':len(problem.worlds),'policy':policy,
                         'sampled_worlds':len(selected),'mean_probe_cost':statistics.mean(r['cost_units'] for r in res),
                         'false_passes':sum(r['false_pass'] for r in res),
                         'false_fails':sum(r['false_fail'] for r in res),
                         'total_policy_runtime_ms':round(elapsed,6),
                         'source_type':'author_generated_scale_study'})
    return rows


def write_csv(path,rows):
    if not rows:return
    with open(path,'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def run_study(out_dir):
    out=Path(out_dir)
    if out.exists() and any(out.iterdir()):raise FileExistsError('destination must be empty')
    out.mkdir(parents=True,exist_ok=True)
    rows=[];summaries=[]
    st=time.perf_counter()
    for domain in DOMAINS:
        for case in range(CASES):
            base=make_diverse_problem(domain,case)
            for regime in REGIMES:
                problem=with_prior(base,regime)
                r,s=expected_outcomes(problem,domain,case,regime)
                rows.extend(r);summaries.extend(s)
    write_csv(out/'paired_episode_results.csv',rows)
    write_csv(out/'task_level_summary.csv',summaries)
    boots=[]
    for baseline in ('fixed','greedy','optimal','exhaustive'):
        boots.extend(paired_cluster_bootstrap(summaries,policy_b=baseline))
    write_csv(out/'cluster_bootstrap_differences.csv',boots)
    boundary=boundary_failure_controls();write_csv(out/'observation_boundary_controls.csv',boundary)
    budgets=budget_controls();write_csv(out/'budget_ablation.csv',budgets)
    scaling=scaling_controls();write_csv(out/'scaling_stress.csv',scaling)
    aggregates=[]
    for regime in REGIMES:
        for policy in POLICIES:
            subset=[x for x in summaries if x['prior_regime']==regime and x['policy']==policy]
            aggregates.append({'prior_regime':regime,'policy':policy,'templates':len(subset),
                'mean_expected_cost':round(statistics.mean(x['expected_cost'] for x in subset),6),
                'mean_coverage':round(statistics.mean(x['coverage'] for x in subset),6),
                'mean_expected_probes':round(statistics.mean(x['expected_probes'] for x in subset),6),
                'false_pass_probability_sum':round(sum(x['false_pass_probability'] for x in subset),6),
                'false_fail_probability_sum':round(sum(x['false_fail_probability'] for x in subset),6)})
    write_csv(out/'policy_summary.csv',aggregates)
    manifest={
       'stage':7,'study':'controlled_paired_finite_world_inspection_study',
       'author_generated_tasks':len(DOMAINS)*CASES,
       'declared_prior_regimes':REGIMES,
       'world_policy_evaluations':len(rows),
       'task_policy_summaries':len(summaries),
       'observation_boundary_controls':len(boundary),
       'budget_ablation_points':len(budgets),
       'scaling_runs':len(scaling),
       'computational_cost_note':'Synthetic cost units for the 48-task policy study; actual measured planner runtime only in scaling_stress.csv. Shared snapshot expense excluded from synthetic costs and must be added for operational comparisons.',
       'prior_note':'Prior assumptions are authored for sensitivity testing and are NOT trained/calibrated from agent data.',
       'ground_truth_note':'The synthetic oracle knows the actual finite-world index; policies see only declared model and selected probe outcomes.',
       'external_agent_trajectories_evaluated':0,
       'official_agentdiff_scores':0,'official_appworld_scores':0,
       'bootstrap_note':'Templates are authored and correlated; bootstrap intervals reflect only this design set and are NOT external population confidence intervals.',
       'runtime_seconds':round(time.perf_counter()-st,3),
       'reproduction_command':'python reproduce_stage7.py --out ./new_stage7_results'
    }
    with open(out/'run_manifest.json','w',encoding='utf8') as f:json.dump(manifest,f,indent=2)
    return manifest
