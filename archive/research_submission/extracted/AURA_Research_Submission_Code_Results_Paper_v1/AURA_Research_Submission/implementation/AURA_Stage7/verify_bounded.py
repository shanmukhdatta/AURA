#!/usr/bin/env python3
"""Stage 4 bounded-world CLI. Requires explicit finite model assumptions."""
import argparse
from pathlib import Path

from aura_evidence.capture import EvidenceSandbox
from aura_evidence.ledger import EvidenceLedger
from aura_evidence.util import read_json, save_json_atomic
from aura_reasoning.model import verify_bounded


def load_input(fixture=None, run_dir=None, contract_path=None,probes_path=None):
    root=Path(__file__).resolve().parent
    if fixture is not None:
        directory=Path(fixture)
        contract=read_json(directory/'task_contract.json')
        probes=read_json(directory/'probe_catalogue.json')
        obs=read_json(directory/'observations.json')
        return contract,probes,obs,{
            'run_id':obs[0]['run_id'],'epoch_id':obs[0]['epoch_id'],
            'fixture_mode':True,
            'trust_assumptions':['Research fixture only. Authored facts and simulated coverage are not operational evidence.']}
    if run_dir is not None:
        sand=EvidenceSandbox(Path(run_dir))
        manifest=read_json(sand.evidence/'run_manifest.json')
        contract=read_json(contract_path or root/'examples/reference/task_contract.json')
        probes=read_json(probes_path or root/'examples/reference/probe_catalogue.json')
        pair=sand.load_pair(manifest['epoch_id'])
        obs=EvidenceLedger(sand.evidence).verify(manifest['observations'],{p['probe_id']:p for p in probes},pair=pair)
        return contract,probes,obs,{
            'run_id':manifest['run_id'],'epoch_id':manifest['epoch_id'],
            'pair':pair,'capture_latency_ms':manifest['snapshot_capture_latency_ms'],
            'capture_bytes_read':manifest['snapshot_capture_bytes_read'],
            'trust_assumptions':['Stage 2 controlled quiescent evidence sandbox; non-atomic across heterogeneous services.']}
    raise ValueError('specify fixture or run_dir')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--fixture',type=Path)
    group.add_argument('--run',type=Path)
    ap.add_argument('--model',required=True,type=Path)
    ap.add_argument('--contract',type=Path)
    ap.add_argument('--probes',type=Path)
    ap.add_argument('--out',required=True,type=Path)
    ns=ap.parse_args()
    if ns.out.exists():
        raise SystemExit('Output must be a NEW directory to avoid overwriting evidence')
    c,p,o,kw=load_input(ns.fixture,ns.run,ns.contract,ns.probes)
    cert,ledger=verify_bounded(c,p,o,read_json(ns.model),**kw)
    ns.out.mkdir(parents=True)
    save_json_atomic(ns.out/'certificate.json',cert)
    save_json_atomic(ns.out/'reasoning_ledger.json',ledger)
    print(f"{cert['verdict']} / {cert['decision_status']}")
    print(f"Certificate: {ns.out/'certificate.json'}")
    print(f"Reasoning ledger: {ns.out/'reasoning_ledger.json'}")

if __name__=='__main__':main()
