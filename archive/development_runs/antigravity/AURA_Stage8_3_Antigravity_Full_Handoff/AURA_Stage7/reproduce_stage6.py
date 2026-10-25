"""Stage 6 reproducible surface ablations and public contract-format checks.

Does NOT execute AppWorld or Agent-Diff agents; does NOT claim official scores.
Stage 5 reruns are explicitly modeled finite worlds + local controlled captures.
"""
from __future__ import annotations
import argparse,csv,json,hashlib,statistics
from pathlib import Path
from collections import Counter
from reproduce_stage5 import main as reproduce_stage5
from aura_evidence.util import save_json_atomic,read_json
from aura_baselines.surface import MODES,run_surface_ablation
from aura_external.agentdiff import parse_agentdiff_task,load_jsonl_tasks,evaluate_synthetic_diff
from aura_external.appworld import integration_status
from aura_external.fixtures import hypothetical_matching_diff

HERE=Path(__file__).resolve().parent
SCENARIOS={'clean':'PASS','missing_report':'FAIL','collateral':'FAIL','silent_noop':'FAIL','denied_readback':'UNCERTAIN','missing_validation':'FAIL'}

def csv_write(path,rows):
    if rows:
        with open(path,'w',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def main(out_dir,external_jsonl=None):
    out=Path(out_dir).resolve()
    if out.exists() and any(out.iterdir()): raise FileExistsError('refusing to overwrite nonempty result directory')
    out.mkdir(parents=True,exist_ok=True)
    reproduce_stage5(out/'stage5_reproduced')
    contract=read_json(HERE/'examples/reference/task_contract.json')
    probes=read_json(HERE/'examples/reference/probe_catalogue.json')
    records=[]
    for name,expected in SCENARIOS.items():
        root=out/'stage5_reproduced/local_captures'/name
        for mode in MODES:
            res=run_surface_ablation(root,contract,probes,mode,
                                     force_denied=('student_state',) if name=='denied_readback' else ())
            records.append({'scenario':name,'mode':mode,'expected':expected,
                'verdict':res['verdict'],'matched_expected':res['verdict']==expected,
                'decisive':res['verdict']!='UNCERTAIN',
                'num_probes':res['num_probes'],
                'actual_probe_ms':round(res['actual_probe_ms'],6),
                'common_snapshot_ms':round(res['capture_ms'],6),
                'actual_total_ms':round(res['actual_probe_ms']+res['capture_ms'],6),
                'information_matched':False})
    csv_write(out/'surface_ablation_results.csv',records)
    by_mode=[]
    for mode in MODES:
        subset=[x for x in records if x['mode']==mode]
        by_mode.append({'mode':mode,'runs':len(subset),'decisive':sum(r['decisive'] for r in subset),
                        'expected_label_matches':sum(r['matched_expected'] for r in subset),
                        'false_pass':sum(r['verdict']=='PASS' and r['expected']=='FAIL' for r in subset),
                        'false_fail':sum(r['verdict']=='FAIL' and r['expected']=='PASS' for r in subset),
                        'mean_total_ms':round(statistics.mean(r['actual_total_ms'] for r in subset),5)})
    csv_write(out/'surface_ablation_summary.csv',by_mode)

    source=HERE/'examples/external/agentdiff_public_contract_excerpt.jsonl'
    tasks=[parse_agentdiff_task(row) for row in load_jsonl_tasks(source)]
    external=[]
    for task in tasks:
        diff=hypothetical_matching_diff(task)
        mutations={'authored_complete':(diff,True),
                   'authored_missing_required':(diff[1:],True),
                   'authored_unlicensed_change':(diff+[{'diff_type':'added','entity':'other_entity','where':{},'after':{}}],True),
                   'authored_partial_scope':(diff,False)}
        for condition,(evidence,full) in mutations.items():
            r=evaluate_synthetic_diff(task,evidence,coverage_complete=full)
            external.append({'source_task_id':task.test_id,'service':task.service,
                             'condition':condition,'aura_subset_verdict':r['verdict'],
                             'reason':r['reason'],'source_contract_public':True,
                             'diff_fixture_authored':True,'real_agent_rollout':False,
                             'official_agentdiff_score':False})
    csv_write(out/'agentdiff_contract_format_checks.csv',external)
    supplied=None
    if external_jsonl:
        n=Counter();errors=[]
        for lineno,record in enumerate(load_jsonl_tasks(external_jsonl),1):
            try:
                t=parse_agentdiff_task(record)
                n['parsed_tasks']+=1
                n['unsupported_tasks']+=bool(t.unsupported)
                n['assertions']+=len(t.assertions)
                n['service_'+t.service]+=1
                n['unsupported_clauses']+=len(t.unsupported)
            except Exception as exc:
                n['unparsed_tasks']+=1
                if len(errors)<10:errors.append({'line':lineno,'type':type(exc).__name__})
        supplied={'counts':dict(n),'sample_errors':errors,'note':'Format validation only; no agent trajectories, initial/final states, or native benchmark scores.'}
        save_json_atomic(out/'agentdiff_optional_user_dataset_import.json',supplied)

    stage5_summary=read_csv(out/'stage5_reproduced/synthetic_policy_summary.csv')
    live_summary=read_csv(out/'stage5_reproduced/local_live_policy_results.csv')
    final={
       'stage':6,'status':'baseline_integration_and_public_contract_format_adaptation',
       'evidence_sources':['controlled Stage 2/5 local captures','authored finite-world models',
                           'five extracted public Agent-Diff assertion excerpts'],
       'public_agentdiff_contract_excerpt_count':len(tasks),
       'authored_external_diff_fixture_evaluations':len(external),
       'actual_external_benchmark_agent_trajectories':0,
       'official_agentdiff_evaluations':0,
       'official_appworld_evaluations':0,
       'appworld':integration_status(),
       'surface_ablation_runs':len(records),
       'information_matched_planning_runs':len(live_summary),
       'finite_world_policy_evaluations':int(sum(int(row['episodes']) for row in stage5_summary)),
       'matched_planning_methods':[row['policy'] for row in stage5_summary],
       'information_parity_note':'Stage 5 policy methods share probe catalogues; Stage 6 surface ablation methods intentionally do NOT share evidence.',
       'capture_cost_note':'Marginal cost units exclude common snapshot cost; local actual_total_ms includes common capture latency.',
       'evaluation_note':'No independent real agent outcome evaluation. External examples are schema compatibility, not benchmark performance.'
    }
    if supplied:final['optional_external_dataset_import']=supplied
    save_json_atomic(out/'run_manifest.json',final)
    return final

def read_csv(path):
    with open(path,encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True)
    p.add_argument('--agentdiff-jsonl',help='Optional locally downloaded upstream Agent-Diff JSONL; format analysis only')
    args=p.parse_args()
    result=main(args.out,args.agentdiff_jsonl)
    print(json.dumps(result,indent=2))
