"""Stage 3 CLI: produce schema-validated certificates from captured evidence."""
import argparse
import json
from pathlib import Path
from aura_evidence.util import canonical_json, save_json_atomic
from aura_verifier import verify_saved_run, verify_fixture_directory


def main():
    parser=argparse.ArgumentParser(description='AURA task-completion verification')
    sources=parser.add_mutually_exclusive_group(required=True)
    sources.add_argument('--run',type=Path,help='Captured Stage 2 run with trusted evidence')
    sources.add_argument('--fixture',type=Path,help='Stage 1 synthetic reference case (NOT operational evidence)')
    parser.add_argument('--out',type=Path,help='Optional new certificate JSON output path')
    parser.add_argument('--contract',type=Path,help='Optional contract for --run')
    parser.add_argument('--probes',type=Path,help='Optional probe catalogue for --run')
    a=parser.parse_args()
    cert = (verify_fixture_directory(a.fixture) if a.fixture else
            verify_saved_run(a.run,contract_path=a.contract,probes_path=a.probes))
    if a.out:
        save_json_atomic(a.out,cert)
    print(json.dumps({'run_id':cert['run_id'],'verdict':cert['verdict'],
                      'decision_status':cert['decision_status'],
                      'reason_codes':cert['reason_codes'],
                      'unresolved_obligation_ids':cert['unresolved_obligation_ids']},indent=2))

if __name__=='__main__':
    main()
