"""Independent-harness-controlled SQLite/filesystem execution cases.

These are real local SQLite/file mutations but scripted, not LLM-generated agent
trajectories. Harness knows the fault and checks AURA without passing that label
to evidence or to planning policies. Transient-revert case is a documented blind
spot OUTSIDE the present persistent-state and procedural task contract.
"""
from __future__ import annotations
import sqlite3
from pathlib import Path
import json, statistics
from aura_evidence.capture import EvidenceSandbox,SnapshotPair
from aura_evidence.trace import TraceRecorder
from aura_evidence.util import read_json,save_json_atomic
from aura_planning.live_runner import run_live_policy

HERE=Path(__file__).resolve().parents[1]
SCENARIOS={
 'clean':'PASS',
 'clean_extra_read':'PASS',
 'wrong_marks':'FAIL',
 'wrong_report':'FAIL',
 'extra_file':'FAIL',
 'wrong_student':'FAIL',
 'unlicensed_name_change':'FAIL',
 'missing_report_and_collateral':'FAIL',
 'late_regression':'FAIL',
 'silent_noop':'FAIL',
 'missing_validation':'FAIL',
 'unavailable_authoritative_readback':'UNCERTAIN',
 'transient_reverted_unobserved':'PASS',
}
POLICIES=('fixed','greedy','cera','optimal','exhaustive')

def scripted_capture(name,out):
    sand=EvidenceSandbox(out);sand.initialize();(sand.workspace/'reports').mkdir(exist_ok=True)
    eid='epoch.stage7.'+name;rid='run.stage7.'+name
    before,bref,cb=sand.capture(eid,'before')
    trace=TraceRecorder(sand.evidence,eid)
    def modify(sid,field,value):
        with sqlite3.connect(sand.db) as conn:
            conn.execute(f'UPDATE students SET {field}=? WHERE student_id=?',(value,sid))
        return 'success'
    def update():
        if name=='silent_noop': return 'success' # falsely reports success
        if name=='wrong_student': return modify(102,'marks',85)
        if name=='wrong_marks': return modify(101,'marks',82)
        return modify(101,'marks',85)
    def write_report():
        if name=='missing_report_and_collateral':return 'success (report skipped)'
        marks=82 if name=='wrong_report' else 85
        (sand.workspace/'reports/student_101.md').write_text(f'Student: 101\nMarks: {marks}\n',encoding='utf8')
        return 'success'
    def validation():return True
    if name=='clean_extra_read':
        sand.execute_agent_step(trace.tool_call,'read_supporting_note',lambda:'non-mutating-read')
    if name!='missing_validation':
        sand.execute_agent_step(trace.tool_call,'validate_eligibility',validation)
    sand.execute_agent_step(trace.tool_call,'update_marks',update)
    sand.execute_agent_step(trace.tool_call,'generate_report',write_report)
    if name in ('extra_file',):
        sand.execute_agent_step(trace.tool_call,'unexpected_export',lambda:(sand.workspace/'reports/debug_dump.txt').write_text('unused',encoding='utf8') or 'success')
    if name=='unlicensed_name_change':
        sand.execute_agent_step(trace.tool_call,'rename_unrelated_field',modify,101,'name','Changed by agent')
    if name=='missing_report_and_collateral':
        sand.execute_agent_step(trace.tool_call,'cleanup_tool',modify,102,'marks',91)
    if name=='late_regression':
        sand.execute_agent_step(trace.tool_call,'late_cleanup',modify,101,'marks',70)
    if name=='transient_reverted_unobserved':
        sand.execute_agent_step(trace.tool_call,'unrelated_temporary_edit',modify,102,'marks',91)
        sand.execute_agent_step(trace.tool_call,'restore_unrelated_record',modify,102,'marks',88)
    trace.persist()
    after,aref,ca=sand.capture(eid,'after')
    pair=SnapshotPair(eid,before,after,bref,aref,cb+ca,before['bytes_read']+after['bytes_read'])
    pair.require_same_epoch()
    save_json_atomic(sand.evidence/'run_manifest.json',{'run_id':rid,'epoch_id':eid,'scenario':name,
         'snapshot_capture_latency_ms':round(cb+ca,5),'snapshot_capture_bytes_read':pair.capture_bytes_read,
         'harness_expected_contract_verdict':SCENARIOS[name],
         'actual_agent_rollout':False,
         'transient_dirty_write_outside_existing_task_contract':name=='transient_reverted_unobserved'})
    return sand

def run_local_matrix(out):
    from .study import write_csv
    root=Path(out)
    if root.exists() and any(root.iterdir()):raise FileExistsError('destination must be empty')
    root.mkdir(parents=True,exist_ok=True)
    contract=read_json(HERE/'examples/reference/task_contract.json')
    probes=read_json(HERE/'examples/reference/probe_catalogue.json')
    rows=[]
    for name,expected in SCENARIOS.items():
        sand=scripted_capture(name,root/'captures'/name)
        for policy in POLICIES:
            r=run_live_policy(sand.root,contract,probes,policy,
                              force_denied=('student_state',) if name=='unavailable_authoritative_readback' else ())
            rows.append({'scenario':name,'policy':policy,'expected_contract_verdict':expected,
                'actual_verdict':r['verdict'],'matched_expected':r['verdict']==expected,
                'selected_probes':'|'.join(r['selected_probes']),
                'num_probes':r['num_probes'],'estimated_probe_ms':r['estimated_probe_ms'],
                'actual_probe_ms':r['actual_probe_ms'],'capture_ms':r['capture_ms'],
                'planner_selection_ms':r['planner_selection_ms'],
                'total_ms':r['actual_probe_ms']+r['capture_ms']+r['planner_selection_ms'],
                'persistent_state_contract_only':True,
                'transient_outside_contract':name=='transient_reverted_unobserved',
                'source_type':'scripted_local_sqlite_not_external_agent'})
    write_csv(root/'local_fault_policy_comparison.csv',rows)
    summary=[]
    for policy in POLICIES:
        subset=[r for r in rows if r['policy']==policy]
        summary.append({'policy':policy,'cases':len(subset),
            'decisive':sum(r['actual_verdict']!='UNCERTAIN' for r in subset),
            'label_matches':sum(r['matched_expected'] for r in subset),
            'mean_probe_ms':statistics.mean(r['actual_probe_ms'] for r in subset),
            'mean_capture_ms':statistics.mean(r['capture_ms'] for r in subset),
            'mean_planner_ms':statistics.mean(r['planner_selection_ms'] for r in subset),
            'mean_total_ms':statistics.mean(r['total_ms'] for r in subset)})
    write_csv(root/'local_fault_summary.csv',summary)
    save_json_atomic(root/'metadata.json',{'scenarios':list(SCENARIOS),'policies':POLICIES,
      'local_scripted_scenarios':len(SCENARIOS),'local_evaluations':len(rows),
      'warning':'Transient unrelated write is reverted before final snapshot; current contract does not prohibit it, so PASS is contract-relative, NOT claim of full execution-history safety.',
      'actual_external_agent_trajectories':0})
    return rows
