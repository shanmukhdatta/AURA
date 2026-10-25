"""Stage 5 engineering acceptance, model-reference only."""
import itertools
import pytest
from aura_planning import FiniteInspectionProblem,Inspection,run_policy,plan_next,assess,exact_value
from aura_planning.examples import make_problem
from aura_planning.planner import PlanningError

@pytest.mark.parametrize('domain',('records','orders','access','files'))
def test_strict_pass_requires_coverage(domain):
    p=make_problem(domain)
    good=next(i for i,s in enumerate(p.satisfying) if s)
    assert p.verdict((good,),frozenset())=='UNCERTAIN'
    assert p.verdict((good,),frozenset({'frame_diff'}))=='PASS'

@pytest.mark.parametrize('domain',('records','orders','access','files'))
def test_failure_dominates_missing_frame(domain):
    p=make_problem(domain)
    bad=next(i for i,s in enumerate(p.satisfying) if not s)
    assert p.verdict((bad,),frozenset())=='FAIL'

@pytest.mark.parametrize('policy',('exhaustive','fixed','greedy','cera','optimal'))
def test_policies_sound_on_all_worlds(policy):
    p=make_problem('orders')
    for i in range(len(p.worlds)):
        r=run_policy(p,i,policy)
        assert not r['false_pass'] and not r['false_fail']
        if r['verdict']=='PASS':
            assert not r['missing_frame_surfaces']
            assert r['true_success']

@pytest.mark.parametrize('domain',('records','orders','access','files'))
def test_complete_evidence_decides(domain):
    p=make_problem(domain,1)
    for i in range(len(p.worlds)):
        r=run_policy(p,i,'exhaustive')
        assert r['verdict']==('PASS' if r['true_success'] else 'FAIL')
        assert r['num_probes']==len(p.inspections)

def test_exact_policy_no_trivial_abstention():
    p=make_problem('records')
    x=exact_value(p)
    assert x['decisive_probability']==pytest.approx(1)
    assert x['probe_id'] in p.inspections

def test_model_is_not_actual_world_conditioned():
    p=make_problem('files')
    assert plan_next(p,p.initial_indices,frozenset(),'cera')==plan_next(p,p.initial_indices,frozenset(),'cera')
    # Contrary actual hidden outcomes do not change the initial plan.
    r1=run_policy(p,0,'cera');r2=run_policy(p,len(p.worlds)-1,'cera')
    assert r1['events'][0]['probe_id']==r2['events'][0]['probe_id']

def test_frame_unobservable_prevents_success():
    p=make_problem('records')
    replacements=[Inspection(x.probe_id,x.fact_keys,(),x.cost,x.available) for x in p.inspections.values()]
    q=FiniteInspectionProblem(p.contract,{'schema_version':'1.0','model_id':'test',
                                'fact_domains':{k:[False,True] for k in p.worlds[0]},
                                'constraints':[],'max_worlds':500},replacements)
    good=next(i for i,s in enumerate(q.satisfying) if s)
    for policy in ('cera','greedy','optimal'):
        r=run_policy(q,good,policy)
        assert r['verdict']=='UNCERTAIN'

def test_invalid_probes_are_rejected():
    p=make_problem('records')
    with pytest.raises(PlanningError):
        FiniteInspectionProblem(p.contract,{'schema_version':'1.0','model_id':'x',
           'fact_domains':{k:[False,True] for k in p.worlds[0]},'constraints':[],'max_worlds':500},
           [Inspection('bad',('not_a_fact',),(),1)])

def test_all_policies_have_equal_available_catalogue():
    p=make_problem('records')
    for pol in ('fixed','greedy','cera','optimal','exhaustive'):
        r=run_policy(p,0,pol)
        assert set(x['probe_id'] for x in r['events'])<=set(p.inspections)

def test_explicit_resource_limit_keeps_uncertain():
    p=make_problem('files')
    successful=next(i for i,s in enumerate(p.satisfying) if s)
    r=run_policy(p,successful,'cera',max_probes=0)
    assert r['verdict']=='UNCERTAIN'

@pytest.mark.parametrize('domain',('records','orders','access','files'))
def test_exact_mean_cost_lower_bound_and_full_coverage(domain):
    p=make_problem(domain,2)
    scores={}
    for method in ('optimal','cera','greedy','fixed'):
        results=[run_policy(p,i,method) for i in range(len(p.worlds))]
        scores[method]=sum(p.prior[i]*v['cost_units'] for i,v in enumerate(results))
        assert all(r['verdict']!='UNCERTAIN' for r in results)
    assert scores['optimal']<=min(scores['cera'],scores['greedy'],scores['fixed'])+1e-9


def test_zero_probability_prior_not_accepted():
    p=make_problem('files')
    prior=[0]*(len(p.worlds)-1)+[1]
    with pytest.raises(PlanningError):
        FiniteInspectionProblem(p.contract,p.model,list(p.inspections.values()),prior)


def test_budgeted_case_does_not_silently_claim_success():
    p=make_problem('access')
    good=next(i for i,s in enumerate(p.satisfying) if s)
    for method in ('fixed','greedy','cera','optimal'):
        r=run_policy(p,good,method,max_probes=2)
        assert r['verdict']=='UNCERTAIN' and not r['false_pass']
