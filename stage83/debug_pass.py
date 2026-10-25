from aura_external.agentsynth_adapter import AgentSynthAuraAdapter
from pathlib import Path
import shutil

p = Path('scratch_pass_debug')
if p.exists(): shutil.rmtree(p)
adapter = AgentSynthAuraAdapter('raise-ticket-priority', p)
adapter.execute_sql("UPDATE tickets SET priority='high' WHERE id=3")
adapter.set_agent_answer('Priority raised to high for ticket 3.')
res = adapter.run_aura_verification()
print('VERDICT:', res['aura_verdict'])
print('REASON_CODES:', res['cert'].get('reason_codes'))
for r in res['cert'].get('obligation_results', []):
    print('OBLIGATION:', r['obligation_id'], r['truth'], r.get('reason_code'))
