"""Reproduce six *real local* and twelve *synthetic fixture* certificates."""
from pathlib import Path
import argparse
import csv
import json
import subprocess
import sys

from aura_evidence.util import save_json_atomic
from aura_verifier import verify_fixture_directory, verify_saved_run
from run_demo import run

SCENARIOS = {
    'clean':'PASS',
    'missing_report':'FAIL',
    'collateral':'FAIL',
    'silent_noop':'FAIL',
    'denied_readback':'UNCERTAIN',
    'missing_validation':'FAIL',
}
HERE=Path(__file__).resolve().parent


def reproduce(output):
    output=Path(output)
    if output.exists() and list(output.iterdir()):
        raise FileExistsError('output directory must not exist or be empty')
    output.mkdir(parents=True,exist_ok=True)
    results=[]
    for name,expected in SCENARIOS.items():
        root=output/'live_runs'/name
        run(name,root)
        cert=verify_saved_run(root)
        save_json_atomic(root/'certificate.json',cert)
        assert cert['verdict']==expected,(name,cert['verdict'],expected)
        results.append({'source_type':'real_local_capture','case':name,'verdict':cert['verdict'],
                        'decision_status':cert['decision_status'],'expected':expected,
                        'reproduced':True,'reason_codes':'|'.join(cert['reason_codes'])})
    for folder in sorted((HERE/'tests/fixtures/stage1_inputs').iterdir()):
        if not folder.is_dir():continue
        expected=json.loads((folder/'expected.json').read_text())
        cert=verify_fixture_directory(folder)
        save_json_atomic(output/'synthetic_reference'/folder.name/'certificate.json',cert)
        assert (cert['verdict'],cert['decision_status']) == (expected['expected_verdict'],expected['decision_status'])
        results.append({'source_type':'synthetic_reference','case':folder.name,'verdict':cert['verdict'],
                        'decision_status':cert['decision_status'],'expected':expected['expected_verdict'],
                        'reproduced':True,'reason_codes':'|'.join(cert['reason_codes'])})
    with (output/'verification_summary.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    report={'stage':'3','run_count':len(results), 'live_run_count':len(SCENARIOS),
            'synthetic_reference_count':len(results)-len(SCENARIOS),
            'matching_expected_verdicts':sum(r['reproduced'] for r in results),
            'description':'Only controlled local and preauthored reference acceptance tests; not external benchmark results.'}
    save_json_atomic(output/'verification_summary.json',report)
    print(json.dumps(report,indent=2))
    return report

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    reproduce(args.out)
