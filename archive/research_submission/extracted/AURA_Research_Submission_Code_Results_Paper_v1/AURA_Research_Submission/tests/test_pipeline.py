"""Unit tests for independent, read-only paper-table assembly (no inference)."""
from pathlib import Path
import csv
import json
import tempfile
import unittest
import zipfile
from research_submission.audit import archive_audit,audit_and_export,ARCHIVES
from research_submission.tables import build_tables

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'evidence/source_archives'

class ResearchPipelineTests(unittest.TestCase):
    def test_archive_integrity(self):
        for key,(name,mf) in ARCHIVES.items():
            with self.subTest(archive=key):
                check=archive_audit(SOURCE/name,mf)
                self.assertEqual(check['status'],'PASS',check)
                self.assertGreater(check['manifest_entries'],0)
    def test_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'test.zip'
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('a.txt',b'fake changes')
                z.writestr('M.json',json.dumps({'a.txt':'0'*64}))
            result=archive_audit(path,'M.json')
            self.assertEqual(result['status'],'FAIL')
            self.assertIn('hash_mismatches', '|'.join(result['issues']))
    def test_episode_cohort_counts(self):
        with tempfile.TemporaryDirectory() as td:
            r=audit_and_export(SOURCE,Path(td))
            d={g['cohort']:g for g in r['cohorts']}
            self.assertEqual({k:v['n'] for k,v in d.items()}, {
                'stage8_1_local_qwen3b':4,'stage8_1_appworld':3,
                'stage8_2_scripted':36,'stage8_3_qwen05':5,'stage8_3_qwen3b_gpu':5})
            self.assertEqual((d['stage8_3_qwen3b_gpu']['pass'],d['stage8_3_qwen3b_gpu']['fail']),(3,2))
            self.assertEqual((d['stage8_2_scripted']['pass'],d['stage8_2_scripted']['fail'],d['stage8_2_scripted']['uncertain']),(6,24,6))
            self.assertEqual(d['stage8_1_appworld']['not_aura_evaluated'],3)
            with (Path(td)/'episode_registry.csv').open(encoding='utf-8',newline='') as f:
                rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),53)
            self.assertEqual(sum(r['execution_mode']=='real_llm_external_sql' for r in rows),10)
            self.assertEqual(sum(r['execution_mode']=='scripted_external_task_controls' for r in rows),36)
    def test_stage7_cost_tables_include_negative_regime(self):
        with tempfile.TemporaryDirectory() as td:
            counts=build_tables(SOURCE,Path(td))
            self.assertEqual(counts['stage7_local_policy_episodes'],65)
            with (Path(td)/'table_planner_prior_sensitivity.csv').open(encoding='utf-8',newline='') as f:
                rows=list(csv.DictReader(f))
            m={r['prior']:float(r['cera_minus_greedy_units']) for r in rows}
            self.assertLess(m['uniform'],0)
            self.assertGreater(m['clean_90'],0)
    def test_original_source_archives_preserved(self):
        self.assertEqual(len(ARCHIVES),5)
        self.assertTrue((SOURCE/'AURA_Stage7_Results_v1.zip').exists())

if __name__ == '__main__': unittest.main()
