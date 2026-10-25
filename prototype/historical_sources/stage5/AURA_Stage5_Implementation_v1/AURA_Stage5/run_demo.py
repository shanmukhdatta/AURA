"""Run Stage 2 evidence capture. No task completion verdict is computed."""
import argparse
from pathlib import Path
import shutil
import sqlite3
import time

from aura_evidence.capture import EvidenceSandbox, SnapshotPair
from aura_evidence.diff import canonical_diff
from aura_evidence.ledger import EvidenceLedger
from aura_evidence.probes import ProbeRunner
from aura_evidence.trace import TraceRecorder
from aura_evidence.util import read_json, save_json_atomic, utc_now
from aura_evidence.validation import detect_conflicts, validate_probes

HERE = Path(__file__).resolve().parent
SCENARIOS=('clean','missing_report','collateral','silent_noop','denied_readback','missing_validation')


def run(scenario, out_dir):
    if scenario not in SCENARIOS:
        raise ValueError(f'unsupported scenario: {scenario}')
    out_dir=Path(out_dir).resolve()
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError('demo output root is nonempty; refusing to overwrite evidence')
    sand=EvidenceSandbox(out_dir)
    sand.initialize()
    (sand.workspace/'reports').mkdir(exist_ok=True)
    contract=read_json(HERE/'examples/reference/task_contract.json')
    probes=read_json(HERE/'examples/reference/probe_catalogue.json')
    validate_probes(contract,probes)
    epoch_id='epoch.stage2.'+scenario
    run_id='run.stage2.'+scenario
    before,before_ref,cost_before=sand.capture(epoch_id,'before')
    trace=TraceRecorder(sand.evidence,epoch_id)

    def validate_eligibility():
        return True

    def update_marks():
        if scenario=='silent_noop':
            return 'success'  # deliberately misleading tool return
        with sqlite3.connect(sand.db) as conn:
            conn.execute('UPDATE students SET marks=? WHERE student_id=?',(85,101))
        return 'success'

    def write_report():
        path=sand.workspace/'reports/student_101.md'
        path.write_text('Student: 101\nMarks: 85\n',encoding='utf-8')
        return 'success'

    def mutate_unrelated():
        with sqlite3.connect(sand.db) as conn:
            conn.execute('UPDATE students SET marks=? WHERE student_id=?',(91,102))
        return 'success'

    if scenario!='missing_validation':
        sand.execute_agent_step(trace.tool_call,'validate_eligibility',validate_eligibility)
    sand.execute_agent_step(trace.tool_call,'update_marks',update_marks)
    if scenario!='missing_report':
        sand.execute_agent_step(trace.tool_call,'generate_report',write_report)
    if scenario=='collateral':
        sand.execute_agent_step(trace.tool_call,'cleanup_tool',mutate_unrelated)
    trace_ref=trace.persist()
    after,after_ref,cost_after=sand.capture(epoch_id,'after')
    pair=SnapshotPair(epoch_id,before,after,before_ref,after_ref,cost_before+cost_after,
                      before['bytes_read']+after['bytes_read'])
    pair.require_same_epoch()

    runner=ProbeRunner(sand,pair,contract,probes)
    ledger=EvidenceLedger(sand.evidence)
    refs=[];obs=[]
    for p in probes:
        forced='permission_denied' if scenario=='denied_readback' and p['probe_id']=='student_state' else None
        result=runner.run(p['probe_id'],run_id,force_unavailable=forced)
        refs.append(ledger.add(result,p,pair=pair))
        obs.append(result)
    verified=ledger.verify(refs,runner.probes,pair=pair)
    report = {
        'stage':'2', 'run_id':run_id,'epoch_id':epoch_id,'scenario':scenario,
        'notice':'RAW EVIDENCE ONLY. These are NOT agent-task completion verdicts.',
        'snapshot_refs':[before_ref,after_ref], 'trace_ref':trace_ref,
        'snapshot_capture_latency_ms':round(cost_before+cost_after,5),
        'snapshot_capture_bytes_read':pair.capture_bytes_read,
        'probe_latency_ms_sum':round(sum(x['actual_cost']['latency_ms'] for x in obs),5),
        'probe_bytes_read_sum':sum(x['actual_cost']['bytes_read'] for x in obs),
        'observations':refs, 'independent_conflicts':detect_conflicts(verified,runner.probes),
        'canonical_diff':canonical_diff(pair),
        'created_at':utc_now()
    }
    save_json_atomic(sand.evidence/'run_manifest.json',report)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description='AURA Stage 2 trusted evidence capture demo')
    parser.add_argument('--scenario',choices=SCENARIOS,default='clean')
    parser.add_argument('--out',type=Path,required=True,help='new or empty sandbox folder')
    args=parser.parse_args()
    output=run(args.scenario,args.out)
    print(f"Saved {len(output['observations'])} evidence observations to {args.out}/evidence/")
    print('Capture bytes:',output['snapshot_capture_bytes_read'])
    print('Persistent diff entries:',len(output['canonical_diff']))
    print('No PASS/FAIL/UNCERTAIN verdict is computed in Stage 2.')
