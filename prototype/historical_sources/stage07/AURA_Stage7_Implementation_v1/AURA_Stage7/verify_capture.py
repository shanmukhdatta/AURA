"""Recheck a Stage 2 run's stored evidence without using simulator hidden truth.

Reports integrity and collected facts only; does not compute task verdicts.
"""
import argparse
from pathlib import Path
from aura_evidence.capture import EvidenceSandbox
from aura_evidence.ledger import EvidenceLedger
from aura_evidence.util import read_json
from aura_evidence.validation import detect_conflicts, validate_probes

ROOT = Path(__file__).resolve().parent


def verify(path):
    sand = EvidenceSandbox(Path(path))
    manifest = read_json(sand.evidence/'run_manifest.json')
    contract = read_json(ROOT/'examples/reference/task_contract.json')
    probes = read_json(ROOT/'examples/reference/probe_catalogue.json')
    validate_probes(contract, probes)
    pair = sand.load_pair(manifest['epoch_id'])
    obs = EvidenceLedger(sand.evidence).verify(manifest['observations'],
            {p['probe_id']:p for p in probes},pair=pair)
    if len(set(o['observation_id'] for o in obs)) != len(obs):
        raise ValueError('duplicate observation IDs')
    if any(o['run_id']!=manifest['run_id'] or o['epoch_id']!=manifest['epoch_id'] for o in obs):
        raise ValueError('cross-run or cross-epoch observation')
    return {
        'run_id':manifest['run_id'], 'validated_observations':len(obs),
        'status_counts':{status:sum(o['status']==status for o in obs)
                         for status in ('ok','unavailable','error')},
        'conflicting_facts':detect_conflicts(obs),
        'note':'Evidence integrity verified relative to protected local artifacts. No task verdict computed.'
    }


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run',type=Path,required=True)
    args=parser.parse_args()
    print(verify(args.run))
