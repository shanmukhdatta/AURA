import yaml, json
from pathlib import Path

yaml_path = Path('_deps/agentsynth/packs/core_v2.yaml')
scenarios = yaml.safe_load(yaml_path.read_text(encoding='utf-8'))

task_analysis = []
for s in scenarios:
    sid = s['id']
    meta = s.get('metadata', {})
    tier = meta.get('tier', 'unknown')
    multi_table = bool(meta.get('multi_table', False))
    env = s.get('environment', {})
    schema = env.get('schema', '')
    tables = [line.split()[2].strip('("`') for line in schema.splitlines() if line.strip().upper().startswith('CREATE TABLE')]
    checkers = s.get('checkers', [])
    
    kinds = [c.get('kind') for c in checkers]
    is_sql_only = all(k == 'sql' for k in kinds)
    is_refusal = 'refuse' in sid
    has_answer = 'answer' in kinds
    has_called = 'called_tool' in kinds
    
    # Classify whether task has multi-row mutations
    plan_lines = [q.strip() for q in schema.split(';') if q.strip()]
    
    task_analysis.append({
        'id': sid,
        'tier': tier,
        'tables': tables,
        'multi_table': multi_table,
        'check_count': len(checkers),
        'check_kinds': kinds,
        'sql_state_only': is_sql_only,
        'has_called_tool_check': has_called,
        'has_answer_check': has_answer,
        'is_refusal_task': is_refusal,
        'in_stage82_subset': sid in [
            'raise-ticket-priority', 'clearance-discount', 'refund-and-restock',
            'cancel-and-void-payment', 'store-credit-return', 'reconcile-stock'
        ],
        'task': s.get('task', '').strip()
    })

print(json.dumps(task_analysis, indent=2))
with open('stage83/results/core_v2_task_taxonomy.json', 'w', encoding='utf-8') as f:
    json.dump(task_analysis, f, indent=2)
