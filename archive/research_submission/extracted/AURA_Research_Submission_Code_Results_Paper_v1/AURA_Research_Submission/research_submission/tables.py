"""Rebuild paper tables from saved Stage 7 and Stage 8.3 original result archives."""
from __future__ import annotations
import csv
import io
import json
from pathlib import Path
import zipfile
from .audit import safe_write_csv


def rows_from_zip(z: zipfile.ZipFile, member: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(z.read(member).decode('utf-8-sig'))))


def build_tables(base: Path, out: Path) -> dict:
    stage7=base/'AURA_Stage7_Results_v1.zip'
    if not stage7.exists():raise FileNotFoundError(stage7)
    with zipfile.ZipFile(stage7) as z:
        raw=rows_from_zip(z,'AURA_Stage7_Results_v1/study/policy_summary.csv')
        paired=rows_from_zip(z,'AURA_Stage7_Results_v1/study/cluster_bootstrap_differences.csv')
        local=rows_from_zip(z,'AURA_Stage7_Results_v1/local/local_fault_policy_comparison.csv')
    assert len(raw)==15 and len([r for r in local if r['policy']=='cera'])==13
    summary=[]
    for regime in ('uniform','clean_50','clean_90'):
        x={r['policy']:float(r['mean_expected_cost']) for r in raw if r['prior_regime']==regime}
        summary.append({'prior':regime, 'fixed_units':round(x['fixed'],4),
            'greedy_units':round(x['greedy'],4),'cera_units':round(x['cera'],4),
            'optimal_units':round(x['optimal'],4),'exhaustive_units':round(x['exhaustive'],4),
            'cera_minus_greedy_units':round(x['cera']-x['greedy'],4),
            'cera_relative_vs_greedy_pct':round((x['greedy']-x['cera'])/x['greedy']*100,2)})
    safe_write_csv(out/'table_planner_prior_sensitivity.csv',summary)
    ci=[r for r in paired if r['comparison']=='cera_minus_greedy']
    safe_write_csv(out/'table_planner_template_bootstrap.csv',ci)
    local_by_policy=[]
    for p in ('fixed','greedy','cera','optimal','exhaustive'):
        data=[r for r in local if r['policy']==p]
        local_by_policy.append({'policy':p,'executions':len(data),
            'mean_total_ms':round(sum(float(r['total_ms']) for r in data)/len(data),4),
            'matched_contract_expected':sum(r['matched_expected'].lower()=='true' for r in data),
            'note':'controlled scripted, includes transient blind spot; not real LLM'})
    safe_write_csv(out/'table_local_policy_latency.csv',local_by_policy)
    with zipfile.ZipFile(base/'AURA_STAGE8_3_CORRECTED_RESULTS.zip') as z:
        cera=rows_from_zip(z,'stage83/results/g4_cost_corrected.csv')
    safe_write_csv(out/'table_stage83_modeled_planning.csv',cera)
    return {'stage7_prior_rows':len(summary),'stage7_model_cost_policy_rows':len(raw),
        'stage7_local_policy_episodes':len(local),'stage7_bootstrap_pair_rows':len(ci),
        'stage83_cera_rows':len(cera)}


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,default=Path(__file__).resolve().parents[1]/'evidence/source_archives')
    p.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'outputs');a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    print(json.dumps(build_tables(a.source_dir,a.out),indent=2))

if __name__=='__main__':main()
