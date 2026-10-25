from aura_external.agentsynth_adapter import AgentSynthAuraAdapter, evaluate_native_checkers, take_snapshot
from pathlib import Path
import shutil

p = Path("scratch_debug")
if p.exists(): shutil.rmtree(p)
adapter = AgentSynthAuraAdapter("raise-ticket-priority", p)
adapter.execute_sql("UPDATE tickets SET priority='high' WHERE id=3")
after_snap = take_snapshot(adapter.db_path, adapter.epoch, "after")
print("DB tables after:", after_snap["sqlite"]["tickets"]["rows"])
checkers = adapter.scenario.get("checkers", [])
print("Checkers in scenario:", checkers)
results = evaluate_native_checkers(after_snap, checkers)
print("Results from evaluate_native_checkers:", results)
