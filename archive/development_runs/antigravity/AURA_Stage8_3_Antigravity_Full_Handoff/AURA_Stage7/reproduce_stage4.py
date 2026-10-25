#!/usr/bin/env python3
"""Reproduce Stage 4 reference and fresh local controlled evidence results.

Only software acceptance testing. Never use these authored cases as evidence
of benchmark superiority or claims of production correctness.
"""
import argparse
import csv
from pathlib import Path

from aura_evidence.util import read_json, save_json_atomic
from aura_reasoning.model import verify_bounded
from aura_reasoning.reference_models import make_reference_model
from aura_verifier.engine import verify
from run_demo import run
from verify_bounded import load_input

ROOT=Path(__file__).resolve().parent
EXPECTED_LIVE={'clean':'PASS','missing_report':'FAIL','collateral':'FAIL',
               'silent_noop':'FAIL','denied_readback':'UNCERTAIN','missing_validation':'FAIL'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    ns=parser.parse_args()
    if ns.out.exists():
        raise SystemExit('Output root already exists; evidence is never overwritten')
    ns.out.mkdir(parents=True)
    rows=[]
    for fi in sorted((ROOT/'tests/fixtures/stage1_inputs').iterdir()):
        if not fi.is_dir():continue
        c,p,o,kw=load_input(fixture=fi)
        m=make_reference_model(c,p,o,model_id='model.reference.'+fi.name)
        baseline=verify(c,p,o,**kw)
        cert,ledger=verify_bounded(c,p,o,m,**kw)
        exp=read_json(fi/'expected.json')
        assert (cert['verdict'],cert['decision_status'])==(exp['expected_verdict'],exp['decision_status']),fi.name
        d=ns.out/'synthetic_reference'/fi.name
        d.mkdir(parents=True)
        for name,datum in [('finite_model.json',m),('conservative_certificate.json',baseline),
                           ('bounded_certificate.json',cert),('reasoning_ledger.json',ledger)]:
            save_json_atomic(d/name,datum)
        rows.append({'source':'synthetic_reference','scenario':fi.name,
                     'conservative':baseline['verdict'],'bounded':cert['verdict'],
                     'status':cert['decision_status'],
                     'worlds':ledger['compatible_world_count'],
                     'success_worlds':ledger['satisfying_world_count'],
                     'failure_worlds':ledger['failing_world_count']})
    for scenario,expected in EXPECTED_LIVE.items():
        run_dir=ns.out/'live_runs'/scenario
        run_dir.parent.mkdir(parents=True,exist_ok=True)
        run(scenario,run_dir)
        c,p,o,kw=load_input(run_dir=run_dir)
        m=make_reference_model(c,p,o,model_id='model.local.'+scenario)
        baseline=verify(c,p,o,**kw)
        cert,ledger=verify_bounded(c,p,o,m,**kw)
        assert cert['verdict']==expected,(scenario,cert['verdict'])
        for name,datum in [('finite_model_stage4.json',m),('stage3_certificate.json',baseline),
                           ('stage4_certificate.json',cert),('stage4_reasoning_ledger.json',ledger)]:
            save_json_atomic(run_dir/name,datum)
        rows.append({'source':'real_local_capture','scenario':scenario,
                     'conservative':baseline['verdict'],'bounded':cert['verdict'],
                     'status':cert['decision_status'],
                     'worlds':ledger['compatible_world_count'],
                     'success_worlds':ledger['satisfying_world_count'],
                     'failure_worlds':ledger['failing_world_count']})
    # Controlled logical demonstrations use authored facts and explicit model
    # assumptions; they are deliberately separated from live captures.
    fixture=ROOT/'tests/fixtures/stage1_inputs/05_unobservable_notification'
    c,p,o,kw=load_input(fixture=fixture)
    m=make_reference_model(c,p,o,model_id='model.logical.synthetic_implied_notice')
    m['constraints']=[{'op':'implies',
                       'if':{'op':'fact_eq','fact_key':'report.101.exists','value':True},
                       'then':{'op':'fact_eq','fact_key':'external.notify.confirmed','value':True}}]
    cert,ledger=verify_bounded(c,p,o,m,**kw)
    d=ns.out/'logical_demonstrations'/'synthetic_inferred_success'
    d.mkdir(parents=True)
    for name,datum in [('model.json',m),('certificate.json',cert),('reasoning_ledger.json',ledger)]:
        save_json_atomic(d/name,datum)
    rows.append({'source':'synthetic_assumed_invariant','scenario':'synthetic_inferred_success',
                 'conservative':'UNCERTAIN','bounded':cert['verdict'],
                 'status':cert['decision_status'], 'worlds':ledger['compatible_world_count'],
                 'success_worlds':ledger['satisfying_world_count'], 'failure_worlds':ledger['failing_world_count']})
    with (ns.out/'stage4_verification_summary.csv').open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    print('Reference fixtures: 12/12')
    print('Fresh real local captures: 6/6')
    print('Additional synthetic logical demonstration: 1 (NOT a production claim)')
    print(f'Summary: {ns.out/"stage4_verification_summary.csv"}')

if __name__=='__main__': main()
