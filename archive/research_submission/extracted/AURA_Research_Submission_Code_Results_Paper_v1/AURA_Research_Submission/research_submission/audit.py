"""AURA research submission evidence audit, using archived outputs, not model claims.

Python stdlib only. Read-only ZIP validation, verified cohort extraction, derived tables.
Does not rerun agents and does not construct independent oracle labels.
"""
from __future__ import annotations
import argparse
import csv
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import zipfile

ARCHIVES = {
    'local_qwen3b': ('AURA_STAGE8_1_OUTPUTS.zip', 'FILE_MANIFEST_SHA256.json'),
    'appworld_v7': ('AURA_APPWORLD_STAGE8_1_v7_RESULTS.zip', 'FILE_MANIFEST.json'),
    'scripted_agent_synth': ('AURA_Stage8_2_External_SQL_Evidence_v1.zip', 'FILE_MANIFEST_SHA256.json'),
    'qwen05_agent_synth': ('AURA_STAGE8_3_CORRECTED_RESULTS.zip', 'stage83/results/SHA256SUMS.json'),
    'qwen3b_agent_synth': ('AURA_STAGE83_QWEN3B_PILOT_RESULTS.zip', 'results/FILE_MANIFEST_SHA256.json'),
}


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _entries(data: object, manifest_path: str) -> list[dict]:
    """Normalize several actual historical AURA manifest schemas."""
    if isinstance(data, list):
        return [{'path': r.get('path') or r.get('file'), 'sha256': r['sha256'], 'bytes': r.get('bytes')} for r in data]
    if isinstance(data, dict) and isinstance(data.get('files'), list):
        return [{'path': r['path'], 'sha256': r['sha256'], 'bytes': r.get('bytes')} for r in data['files']]
    if isinstance(data, dict):
        return [{'path': p, 'sha256': v if isinstance(v, str) else v['sha256'], 'bytes': None if isinstance(v, str) else v.get('bytes')} for p, v in data.items()]
    raise ValueError(f'Unrecognized manifest schema: {manifest_path}')


def archive_audit(path: Path, manifest: str) -> dict:
    issues = []
    if not path.is_file():
        return {'archive': path.name, 'status': 'MISSING', 'issues': ['file_missing']}
    try:
        with zipfile.ZipFile(path) as z:
            bad_member = z.testzip()
            if bad_member: issues.append(f'crc_failure:{bad_member}')
            names = z.namelist()
            bad_paths = [n for n in names if n.startswith('/') or '\\' in n or '..' in Path(n).parts]
            if bad_paths: issues.append(f'unsafe_archive_member_count:{len(bad_paths)}')
            mf = json.loads(z.read(manifest).decode('utf-8'))
            entries = _entries(mf, manifest)
            missing, mismatch, wrong_size = [], [], []
            for r in entries:
                p = r['path']
                if not p or p not in names:
                    # Corrected G4 manifest entries are relative to stage83/results.
                    if manifest.startswith('stage83/results/') and 'stage83/results/'+str(p) in names:
                        p = 'stage83/results/' + str(p)
                    elif manifest.startswith('results/') and 'results/'+str(p) in names:
                        p = 'results/' + str(p)
                    else:
                        missing.append(str(p)); continue
                b = z.read(p)
                if _digest(b) != r['sha256']: mismatch.append(str(p))
                if r['bytes'] is not None and len(b) != int(r['bytes']): wrong_size.append(str(p))
            if missing: issues.append('manifest_missing_members:'+','.join(missing[:5]))
            if mismatch: issues.append('hash_mismatches:'+','.join(mismatch[:5]))
            if wrong_size: issues.append('size_mismatches:'+','.join(wrong_size[:5]))
            return {'archive': path.name, 'status': 'PASS' if not issues else 'FAIL',
                    'zip_members': len(names), 'manifest_entries': len(entries),
                    'hashes_verified': len(entries)-len(missing)-len(mismatch),
                    'sha256': _digest(path.read_bytes()), 'issues': issues}
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as e:
        return {'archive': path.name, 'status':'ERROR', 'issues':[type(e).__name__+': '+str(e)]}


def _csv(z: zipfile.ZipFile, name: str) -> list[dict[str,str]]:
    return list(csv.DictReader(io.StringIO(z.read(name).decode('utf-8-sig'))))


def _bool(s: object) -> bool:
    return str(s).strip().lower() in ('true','1','yes')


def collect_cohorts(base: Path) -> tuple[list[dict], list[dict]]:
    """Extract actual recorded episode rows into non-pooled, labeled cohorts."""
    records, cohorts = [], []
    with zipfile.ZipFile(base/ARCHIVES['local_qwen3b'][0]) as z:
        data=_csv(z,'track_A/summary.csv')
        assert len(data)==4, f'Unexpected local track A length: {len(data)}'
        for r in data:
            records.append({'cohort':'stage8_1_local_qwen3b','task_id':r['episode'],
                'execution_mode':'real_llm_local_controlled','model':'Qwen2.5-3B-Instruct',
                'seed':'20261025','aura_verdict':r['aura_verdict'],
                'reference_label':('PASS' if _bool(r['oracle_success']) else 'FAIL'),
                'reference_kind':'scripted_local_expected_outcome',
                'score_kind':'AURA certificate vs local reference',
                'tool_calls':r['actual_tool_calls'], 'notes':'Self-authored task family; no external benchmark.'})
        cohorts.append({'cohort':'stage8_1_local_qwen3b','n':len(data), 'scope':'real LLM local-controlled workflows'})
    with zipfile.ZipFile(base/ARCHIVES['appworld_v7'][0]) as z:
        data=_csv(z,'track_B/summary.csv')
        assert len(data)==3
        for r in data:
            records.append({'cohort':'stage8_1_appworld','task_id':r['task_id'],
                'execution_mode':'real_llm_official_appworld','model':'Qwen2.5-3B-Instruct',
                'seed':'not_available','aura_verdict':'NOT_EVALUATED',
                'reference_label':'PASS' if _bool(r['official_success_field']) else 'FAIL',
                'reference_kind':'official_native_AppWorld_dev',
                'score_kind':'AppWorld success, NOT AURA verification',
                'tool_calls':'not_comparable', 'notes':'AURA adapter NOT evaluated on AppWorld.'})
        cohorts.append({'cohort':'stage8_1_appworld','n':len(data),'scope':'AppWorld native agent evaluation; no AURA certificates'})
    with zipfile.ZipFile(base/ARCHIVES['scripted_agent_synth'][0]) as z:
        data=_csv(z,'episode_results.csv'); assert len(data)==36
        for r in data:
            records.append({'cohort':'stage8_2_scripted','task_id':r.get('task_id', ''),
                'execution_mode':'scripted_external_task_controls','model':'NONE_SCRIPTED',
                'seed':'not_applicable','aura_verdict':r['aura_verdict'],
                'reference_label':r.get('expected_verdict') or r.get('expected') or r.get('reference_verdict') or 'CONTROL_DESIGN',
                'reference_kind':'predefined_fault_variant',
                'score_kind':'AURA contract outcome; upstream SQL-only predicates separately',
                'tool_calls':'not_model_generated','notes':'Six externally authored tasks x 6 author-scripted variants; NOT real model episodes.'})
        cohorts.append({'cohort':'stage8_2_scripted','n':len(data),'scope':'6 tasks x 6 scripted oracle/fault/denial controls'})
    with zipfile.ZipFile(base/ARCHIVES['qwen05_agent_synth'][0]) as z:
        data=_csv(z,'stage83/results/g4_metrics_corrected.csv')
        selected=[r for r in data if r['execution_cohort']=='genuine_llm']
        controls=[r for r in data if r['execution_cohort']=='scripted_control']
        assert len(selected)==5 and len(controls)==36, (len(selected),len(controls))
        for r in selected:
            records.append({'cohort':'stage8_3_qwen05','task_id':r['task_id'],
                'execution_mode':'real_llm_external_sql','model':r['model_id'],
                'seed':r['seed'],'aura_verdict':r['aura_verdict'],
                'reference_label':r['strict_contract_reference'],
                'reference_kind':'independent_scorer_shared_frozen_contract',
                'score_kind':'reproduced_SQL_only:'+r['reproduced_sql_only_score']+'; official_cli:'+r['original_agent_synth_official_result'],
                'tool_calls':'see_traces','notes':'AURA vs matched contract; complete official CLI not run on LLM tasks.'})
        cohorts.append({'cohort':'stage8_3_qwen05','n':len(selected),'scope':'Qwen2.5-0.5B; AgentSynth SQL environment; 1 seed'})
    with zipfile.ZipFile(base/ARCHIVES['qwen3b_agent_synth'][0]) as z:
        data=_csv(z,'results/pilot_results.csv'); assert len(data)==5
        for r in data:
            records.append({'cohort':'stage8_3_qwen3b_gpu','task_id':r['task_id'],
                'execution_mode':'real_llm_external_sql','model':'Qwen2.5-3B-Instruct',
                'seed':'42','aura_verdict':r['aura_verdict'],
                'reference_label':('PASS' if _bool(r['reproduced_full_published_checker_pass']) else 'FAIL'),
                'reference_kind':'reproduced_published_checker_not_official_cli',
                'score_kind':'reproduced SQL predicate checks; NOT AgentSynth CLI',
                'tool_calls':r['sql_tool_calls'], 'notes':'Archive feature branch differs from corrected Qwen0.5 evaluation; incomparable task selection.'})
        cohorts.append({'cohort':'stage8_3_qwen3b_gpu','n':len(data),'scope':'Qwen2.5-3B on Kaggle GPU; 5 tasks; 1 seed'})
    return records, cohorts


def safe_write_csv(path:Path,rows:list[dict]):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows: raise ValueError('No rows')
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction='ignore')
        writer.writeheader();writer.writerows(rows)


def audit_and_export(base: Path, out: Path) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    checks={k:archive_audit(base/name, mf) for k,(name,mf) in ARCHIVES.items()}
    rows,groups=collect_cohorts(base)
    cohort_table=[]
    for g in groups:
        subset=[r for r in rows if r['cohort']==g['cohort']]
        counts=Counter(r['aura_verdict'] for r in subset)
        cohort_table.append({**g,'pass':counts['PASS'],'fail':counts['FAIL'],
            'uncertain':counts['UNCERTAIN'],'not_aura_evaluated':counts['NOT_EVALUATED']})
    assert sum(int(r['n']) for r in cohort_table)==len(rows)==53
    assert all(v['status']=='PASS' for v in checks.values()), 'Evidence integrity audit failed; inspect JSON and do not publish tables'
    safe_write_csv(out/'episode_registry.csv',rows)
    safe_write_csv(out/'cohort_summary.csv',cohort_table)
    report={'schema_version':'1.0','study':'AURA preliminary research consolidation',
        'archive_integrity':checks,'cohorts':cohort_table,
        'model_episode_count_across_four_distinct_cohorts':17,
        'model_episode_count_excluding_appworld':14,
        'controlled_case_count':36,
        'important_limitations':[
          '53 registry rows are 17 model episodes plus 36 scripted controls; not 53 independent agent episodes.',
          'AppWorld has no AURA certificates.',
          'The 5 Qwen0.5 AgentSynth tasks were scored with reproduced SQL state predicates and a matched-contract scorer, not native CLI.',
          'The 5 Qwen3B Kaggle tasks were scored with reproduced checkers, not native CLI.',
          'Model cohorts differ in tasks, prompt, code revision and hardware: NOT a controlled model-comparison experiment.',
          'Zero mismatches on small test-designed controls is not general accuracy.',
          'Finite-model CERA cost units do not equal milliseconds; under some priors greedy outperforms CERA.',
          'Terminal before/after snapshots cannot detect transient writes that are fully reverted.'
        ]}
    (out/'derived_audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-dir',type=Path,default=Path(__file__).resolve().parents[1]/'evidence/source_archives')
    parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'outputs')
    args=parser.parse_args()
    result=audit_and_export(args.source_dir,args.out)
    print('PASS: source archives verified, records reconstructed:',sum(g['n'] for g in result['cohorts']))
    for g in result['cohorts']:print(g)

if __name__=='__main__':main()
