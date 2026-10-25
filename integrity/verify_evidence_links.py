#!/usr/bin/env python3
"""Check record cardinality and original evidence registry existence without inventing missing files."""
import csv,pathlib,json,sys,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'evidence/experiment_registry.csv').open(encoding='utf-8-sig',newline='')))
cohorts=collections.Counter(r.get('cohort','') for r in rows)
expected={'stage7_local':13,'stage82_scripted_controls':36,'stage83_qwen05b_genuine':5,'stage83_qwen3b_genuine':5}
issues=[]
if cohorts!=expected:issues.append(f'Cohorts: actual={cohorts}, expected={expected}')
paths=['validation_reports/validation_summary.json','validation_reports/certificate_replay_results.json','validation_reports/integrity_check.json','tests/test_validation_pipeline.py','stage83/results/SHA256SUMS.json','test_execution_log.txt','experiments/stage81_local_qwen_4/README.md','experiments/stage81_appworld_3_native/README.md']
for rel in paths:
 if not (ROOT/rel).is_file():issues.append('Missing '+rel)
if len(rows)!=59:issues.append(f'Expected 59 validation registry rows, got {len(rows)}')
print('59-episode registry:',len(rows),'rows | cohorts',dict(cohorts));print('Required assets:',len(paths))
if issues:print('\n'.join(issues));sys.exit(1)
print('Registry structure PASS. NOTE: independent per-episode semantic validity and dataset licensing are not established by this structural checker.')
