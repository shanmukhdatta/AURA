"""Stage 5: one-command deterministic synthetic benchmark + real local captures.

This is an engineering research pilot. It is not an independent SOTA benchmark.
No outcome labels are exposed to decision policies. Live oracle is Stage 2.
"""
import argparse,csv,hashlib,json,statistics,time
from pathlib import Path
from collections import defaultdict
from aura_evidence.util import read_json,save_json_atomic
from aura_planning.examples import make_problem
from aura_planning.planner import run_policy,FiniteInspectionProblem
from aura_planning.live_runner import run_live_policy
from run_demo import run as capture_demo,SCENARIOS

POLICIES=('fixed','greedy','cera','optimal','exhaustive')
DOMAINS=('records','orders','access','files')

def dump_csv(path,rows):
    if not rows:return
    with open(path,'w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def main(root):
    root=Path(root).resolve()
    if root.exists() and any(root.iterdir()):
        raise FileExistsError('Output directory must be new or empty; do not overwrite evidence')
    root.mkdir(parents=True,exist_ok=True)
    syn_rows=[];details=[]
    for domain in DOMAINS:
        for variation in range(4):
            p=make_problem(domain,variation)
            for idx in range(len(p.worlds)):
                for pol in POLICIES:
                    result=run_policy(p,idx,pol)
                    record={k:result[k] for k in ('policy','true_success','verdict','correct_decisive','false_pass','false_fail','cost_units','num_probes')}
                    record.update(domain=domain,variation=variation,world_index=idx,
                                  decision_coverage=int(result['verdict']!='UNCERTAIN'))
                    syn_rows.append(record)
                    details.append({'domain':domain,'variation':variation,'world_index':idx,
                                    'policy':pol,'inspection_trace':result['events']})
    dump_csv(root/'synthetic_episode_results.csv',syn_rows)
    save_json_atomic(root/'synthetic_inspection_traces.json',details)
    policy_sum=[]
    for pol in POLICIES:
        sample=[r for r in syn_rows if r['policy']==pol]
        policy_sum.append({'policy':pol,'episodes':len(sample),
            'mean_cost_units':round(statistics.mean(r['cost_units'] for r in sample),6),
            'median_cost_units':round(statistics.median(r['cost_units'] for r in sample),6),
            'mean_probes':round(statistics.mean(r['num_probes'] for r in sample),5),
            'decision_coverage':round(statistics.mean(r['decision_coverage'] for r in sample),6),
            'false_passes':sum(r['false_pass'] for r in sample),
            'false_fails':sum(r['false_fail'] for r in sample)})
    dump_csv(root/'synthetic_policy_summary.csv',policy_sum)


    # Distributional robustness: public prior explicitly varies clean-run
    # prevalence. Models are frozen before any synthetic observation.
    prior_stress=[]
    for domain in DOMAINS:
        for variation in (0,3):
            base=make_problem(domain,variation)
            good=[i for i,v in enumerate(base.satisfying) if v]
            bad=[i for i,v in enumerate(base.satisfying) if not v]
            for clean_prior in (0.5,0.9):
                prior=[(clean_prior/len(good) if i in good else (1-clean_prior)/len(bad))
                       for i in range(len(base.worlds))]
                problem=FiniteInspectionProblem(base.contract,base.model,list(base.inspections.values()),prior)
                for pol in POLICIES:
                    episodes=[run_policy(problem,i,pol) for i in range(len(problem.worlds))]
                    expected_cost=sum(problem.prior[i]*r['cost_units'] for i,r in enumerate(episodes))
                    decisive_prob=sum(problem.prior[i]*(r['verdict']!='UNCERTAIN') for i,r in enumerate(episodes))
                    prior_stress.append({'domain':domain,'variation':variation,'clean_prior':clean_prior,
                        'policy':pol,'expected_cost_units':round(expected_cost,6),
                        'decisive_probability':round(decisive_prob,6),
                        'false_pass_count':sum(r['false_pass'] for r in episodes),
                        'false_fail_count':sum(r['false_fail'] for r in episodes)})
    dump_csv(root/'prior_shift_stress_results.csv',prior_stress)
    # With a strict probe limit, evaluate whether abstention stays explicit.
    budget_rows=[]
    for domain in DOMAINS:
        problem=make_problem(domain,0)
        for max_probes in (1,2,3):
            for pol in POLICIES:
                episodes=[run_policy(problem,i,pol,max_probes=max_probes) for i in range(len(problem.worlds))]
                budget_rows.append({'domain':domain,'max_probes':max_probes,'policy':pol,
                    'coverage':round(sum(r['verdict']!='UNCERTAIN' for r in episodes)/len(episodes),6),
                    'mean_cost_units':round(statistics.mean(r['cost_units'] for r in episodes),6),
                    'false_pass_count':sum(r['false_pass'] for r in episodes),
                    'false_fail_count':sum(r['false_fail'] for r in episodes)})
    dump_csv(root/'probe_budget_stress_results.csv',budget_rows)

    contract=read_json(Path(__file__).parent/'examples/reference/task_contract.json')
    probes=read_json(Path(__file__).parent/'examples/reference/probe_catalogue.json')
    live_rows=[]
    for scenario in SCENARIOS:
        captured=root/'local_captures'/scenario
        capture_demo(scenario,captured)
        expected={ 'clean':'PASS','missing_report':'FAIL','collateral':'FAIL',
                   'silent_noop':'FAIL','denied_readback':'UNCERTAIN',
                   'missing_validation':'FAIL'}[scenario]
        for pol in POLICIES:
            result=run_live_policy(captured,contract,probes,pol,
                force_denied=('student_state',) if scenario=='denied_readback' else (),
                out_dir=root/'live_certificates')
            live_rows.append({'scenario':scenario,'policy':pol,'expected':expected,
                'verdict':result['verdict'],'matched':result['verdict']==expected,
                'num_probes':result['num_probes'],
                'estimated_probe_ms':result['estimated_probe_ms'],
                'actual_probe_ms':round(result['actual_probe_ms'],6),
                'capture_ms':round(result['capture_ms'],6),
                'selection_ms':result['planner_selection_ms']})
    dump_csv(root/'local_live_policy_results.csv',live_rows)
    description={
      'experiment':'AURA Stage 5 controlled engineering evaluation',
      'main_result_scope':'SIMULATED finite worlds + SIX controlled local task executions; no real LLM agent benchmark',
      'synthetic_cases':len(syn_rows), 'unique_synthetic_world_episodes':len(syn_rows)//len(POLICIES),
      'local_captures':len(SCENARIOS),'local_policy_evaluations':len(live_rows),
      'prior_shift_cells':len(prior_stress),'budget_stress_cells':len(budget_rows),
      'methods':list(POLICIES),
      'synthetic_costs':'pre-registered normalized estimated inspection cost units, NO capture overhead; this models marginal probe selection only',
      'live_costs':'reported captured snapshot cost is identical across policies per scenario; probe and planner latency separately measured',
      'truth':'synthetic labels kept inside simulation oracle; local run expectations set independently by authored scenario',
      'limitations':['same generator used for model and synthetic truth; not a blind study',
                     'repeat task templates across parameter variants; not independent samples',
                     'reference models and side-effect scope are small and authored',
                     'no statistically defensible novelty or generalization claim'],
    }
    save_json_atomic(root/'run_manifest.json',description)
    print('SYNTHETIC',len(syn_rows),'policy runs')
    for row in policy_sum:print(row)
    print('LOCAL',len(live_rows),'evaluations','mismatches',sum(not x['matched'] for x in live_rows))
    return description,policy_sum,live_rows

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();main(args.out)
