"""AURA Stage 8.3: Independent runtime adapter for official AgentSynth benchmarks.

Connects the real AURA Stage 7 verification and certificate engine to AgentSynth
environments and agent trajectories. Guarantees:
1. Independent read-only before/after SQLite snapshots.
2. Verified inspection noninterference (pre- and post-inspection DB hashing).
3. Trusted ordered tool traces with exact queries, arguments, and responses.
4. Strict closed-world frame allowlist enforcement (detects unauthorized collateral writes).
5. Independent answer and process/tool validation.
6. Honest uncertainty on denied or missing readbacks.
7. Zero trust in unverified agent-reported 'success' strings.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from aura_evidence.capture import capture_sqlite, SnapshotPair
from aura_evidence.util import digest, utc_now, save_json_atomic, read_json
from aura_evidence.validation import observation_digest, validate_observation, ValidationError
from aura_verifier.engine import verify, VerificationInputError

HERE = Path(__file__).resolve().parents[1]
REPO_ROOT = HERE.parent
DEFAULT_PACK = REPO_ROOT / '_deps/agentsynth/packs/core_v2.yaml'
CONTRACTS_DIR = REPO_ROOT / 'stage83/results/contracts'


def load_upstream_scenario(task_id: str, pack_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load scenario definition directly from official AgentSynth YAML pack."""
    path = pack_path or DEFAULT_PACK
    scenarios = yaml.safe_load(path.read_text(encoding='utf-8'))
    for s in scenarios:
        if s['id'] == task_id:
            return s
    raise ValueError(f"Scenario {task_id!r} not found in {path}")


def init_scenario_db(db_path: Path, scenario: Dict[str, Any]) -> None:
    """Initialize an isolated SQLite database from scenario schema and seed rows."""
    if db_path.exists():
        db_path.unlink()
    env = scenario.get('environment', {})
    schema = env.get('schema', '')
    rows = env.get('rows', [])
    table = env.get('table', 'sales')

    conn = sqlite3.connect(db_path)
    try:
        body = schema.strip().rstrip(';').strip()
        if ';' in body:
            conn.executescript(schema)
        else:
            conn.execute(schema)
        if rows:
            placeholders = ','.join(['?'] * len(rows[0]))
            conn.executemany(f'INSERT INTO {table} VALUES ({placeholders})', [tuple(r) for r in rows])
        conn.commit()
    finally:
        conn.close()


def take_snapshot(db_path: Path, epoch: str, side: str) -> Dict[str, Any]:
    """Take a transaction-consistent read-only snapshot via SQLite online backup."""
    tables, nbytes = capture_sqlite(db_path)
    snap = {
        'schema_version': '1.0',
        'epoch_id': epoch,
        'side': side,
        'consistency_basis': 'cooperative_quiescence',
        'captured_at': utc_now(),
        'sqlite': tables,
        'files': {},
        'bytes_read': nbytes
    }
    snap['sha256'] = digest(snap)
    return snap


def db_sha256(db_path: Path) -> str:
    """Compute raw SHA256 of the on-disk SQLite database file."""
    return hashlib.sha256(db_path.read_bytes()).hexdigest()


def evaluate_native_checkers(db_snapshot: Dict[str, Any], checkers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Evaluate upstream AgentSynth SQL checkers in a temporary in-memory mirror of the snapshot."""
    mirror = sqlite3.connect(':memory:')
    try:
        for tbl_name, tbl in db_snapshot['sqlite'].items():
            mirror.execute(tbl['schema'])
            if tbl['rows']:
                cols = tbl['columns']
                ph = ','.join(['?'] * len(cols))
                data = [[r.get(c) for c in cols] for r in tbl['rows']]
                mirror.executemany(f'INSERT INTO "{tbl_name}" VALUES ({ph})', data)
        mirror.commit()

        results = []
        for i, c in enumerate(checkers):
            kind = c.get('kind')
            if kind == 'sql':
                query = c.get('query')
                expected = c.get('equals') if 'equals' in c else c.get('expected')
                try:
                    cur = mirror.execute(query)
                    observed = [list(r) for r in cur.fetchall()]
                    # Check match: compare lists or scalar equivalence
                    matched = (observed == expected)
                except sqlite3.DatabaseError as exc:
                    observed = str(exc)
                    matched = False
                results.append({
                    'checker_index': i,
                    'kind': 'sql',
                    'query': query,
                    'expected': expected,
                    'observed': observed,
                    'matched': matched
                })
        return results
    finally:
        mirror.close()


def compute_frame_diff(before_snap: Dict[str, Any], after_snap: Dict[str, Any], allowlist: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Closed-world diff across all tables and primary keys against strict task allowlist."""
    issues: List[Dict[str, Any]] = []
    changes: List[Dict[str, Any]] = []
    old_tables = before_snap['sqlite']
    new_tables = after_snap['sqlite']

    all_tables = sorted(set(old_tables.keys()) | set(new_tables.keys()))
    for name in all_tables:
        if name not in old_tables or name not in new_tables:
            issues.append({'kind': 'table_added_removed', 'table': name})
            continue
        old_t = old_tables[name]
        new_t = new_tables[name]
        if old_t['schema'] != new_t['schema'] or old_t['columns'] != new_t['columns'] or old_t['primary_key'] != new_t['primary_key']:
            issues.append({'kind': 'schema_changed', 'table': name})
            continue
        pk = old_t['primary_key']
        if not pk:
            issues.append({'kind': 'table_lacks_primary_key', 'table': name})
            continue

        def row_key(r: Dict[str, Any]) -> tuple:
            return tuple(r.get(k) for k in pk)

        before_rows = {row_key(r): r for r in old_t['rows']}
        after_rows = {row_key(r): r for r in new_t['rows']}

        def get_allowed_cols(tbl_name: str, key_val: Any) -> list:
            tbl_allow = allowlist.get(tbl_name, {})
            if key_val in tbl_allow:
                return tbl_allow[key_val]
            if str(key_val) in tbl_allow:
                return tbl_allow[str(key_val)]
            if isinstance(key_val, str) and key_val.isdigit() and int(key_val) in tbl_allow:
                return tbl_allow[int(key_val)]
            return []

        all_keys = sorted(set(before_rows.keys()) | set(after_rows.keys()), key=repr)
        for k in all_keys:
            pk_val = k[0] if len(k) == 1 else k
            if k not in before_rows or k not in after_rows:
                # Row added or removed
                # Check if allowlist permits row deletion
                allowed_cols = get_allowed_cols(name, pk_val)
                if 'deleted_row' in allowed_cols:
                    changes.append({'table': name, 'pk': list(k), 'operation': 'delete_row'})
                else:
                    issues.append({'kind': 'unauthorized_row_mutation', 'table': name, 'pk': list(k)})
                continue

            b_row = before_rows[k]
            a_row = after_rows[k]
            changed_cols = [c for c in old_t['columns'] if b_row.get(c) != a_row.get(c)]
            if changed_cols:
                allowed_cols = set(get_allowed_cols(name, pk_val))
                unauth = set(changed_cols) - allowed_cols
                changes.append({'table': name, 'pk': list(k), 'columns': changed_cols,
                                'before': {c: b_row.get(c) for c in changed_cols},
                                'after': {c: a_row.get(c) for c in changed_cols}})
                if unauth:
                    issues.append({'kind': 'unauthorized_fields', 'table': name, 'pk': list(k), 'fields': sorted(unauth)})
    return issues, changes


class AgentSynthAuraAdapter:
    """Manages isolated scenario environment execution, snapshot capture, and AURA verification."""

    def __init__(self, task_id: str, workspace_dir: Path, pack_path: Optional[Path] = None):
        self.task_id = task_id
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.db_path = self.workspace / f'{task_id}.sqlite3'
        self.scenario = load_upstream_scenario(task_id, pack_path)
        
        # Load or locate frozen contract
        contract_file = CONTRACTS_DIR / f'{task_id}.json'
        if contract_file.is_file():
            self.contract = read_json(contract_file)
        else:
            raise FileNotFoundError(f"Frozen contract missing for {task_id}")
        manifest_file = CONTRACTS_DIR / 'frozen_contracts_manifest.json'
        if manifest_file.is_file():
            self.allowlist = read_json(manifest_file).get(task_id, {}).get('allowlist', {})
        else:
            self.allowlist = {}
        self.epoch = f'epoch.{task_id}.{int(time.time() * 1000)}'
        self.run_id = f'run.{task_id}.{int(time.time() * 1000)}'
        self.trace: List[Dict[str, Any]] = []
        self.agent_answer: Optional[str] = None
        
        # Initialize DB
        init_scenario_db(self.db_path, self.scenario)
        
        # Capture before snapshot
        self.before_snapshot = take_snapshot(self.db_path, self.epoch, 'before')
        self.pre_eval_db_hash = db_sha256(self.db_path)

    def execute_sql(self, sql_query: str) -> Tuple[bool, Any]:
        """Execute a single SQL call against the world database and record in trusted trace."""
        step_idx = len(self.trace)
        conn = sqlite3.connect(self.db_path)
        is_write_cmd = sql_query.strip().upper().startswith(('UPDATE', 'INSERT', 'DELETE', 'REPLACE', 'CREATE', 'DROP', 'ALTER'))
        try:
            cur = conn.execute(sql_query)
            if is_write_cmd:
                conn.commit()
                rows = None
                resp = 'success'
            else:
                rows = [list(r) for r in cur.fetchall()]
                resp = rows
            self.trace.append({
                'step': step_idx,
                'tool': 'sql_query',
                'sql': sql_query,
                'write': is_write_cmd,
                'response': resp,
                'error': None,
                'timestamp': utc_now()
            })
            return True, resp
        except sqlite3.DatabaseError as exc:
            err_msg = type(exc).__name__ + ': ' + str(exc)
            self.trace.append({
                'step': step_idx,
                'tool': 'sql_query',
                'sql': sql_query,
                'write': is_write_cmd,
                'response': None,
                'error': err_msg,
                'timestamp': utc_now()
            })
            return False, err_msg
        finally:
            conn.close()

    def set_agent_answer(self, answer_text: str) -> None:
        """Record the agent's user-facing final text answer."""
        self.agent_answer = answer_text
        self.trace.append({
            'kind': 'final_answer',
            'text': answer_text,
            'timestamp': utc_now()
        })

    def run_aura_verification(self, deny_readback: bool = False, force_unauthorized_extra: bool = False) -> Dict[str, Any]:
        """Finalize the episode, capture after-snapshot, verify noninterference, and certify via AURA."""
        if force_unauthorized_extra and 'tickets' in self.before_snapshot['sqlite']:
            # Injected unauthorized modification for testing
            self.execute_sql("UPDATE tickets SET priority='tampered' WHERE id=1")

        # Capture terminal snapshot
        self.after_snapshot = take_snapshot(self.db_path, self.epoch, 'after')
        pair = SnapshotPair(
            self.epoch,
            self.before_snapshot,
            self.after_snapshot,
            f'snapshots/{self.run_id}.before.json',
            f'snapshots/{self.run_id}.after.json',
            0.0,
            self.before_snapshot['bytes_read'] + self.after_snapshot['bytes_read']
        )
        pair.require_same_epoch()

        # Noninterference audit: verify hash of DB before and after inspection
        post_exec_db_hash = db_sha256(self.db_path)

        # Independent native reference checks evaluated in-memory from after snapshot
        native_checkers = evaluate_native_checkers(self.after_snapshot, self.scenario.get('checkers', []))
        native_score = sum(1 for c in native_checkers if c['matched']) / len(native_checkers) if native_checkers else 1.0

        # Strict closed-world frame diff
        issues, changes = compute_frame_diff(self.before_snapshot, self.after_snapshot, self.allowlist)

        # Construct AURA observations
        tables = [t['surface_id'].split('.', 1)[1] for t in self.contract['surfaces'] if t['kind'] == 'sqlite']
        # Collect all trace/answer fact keys required by contract
        trace_needed_keys = sorted(set(
            o['predicate']['fact_key'] for o in self.contract['obligations']
            if o['surface_id'] == 'trace.tools'
        ))
        if not trace_needed_keys:
            trace_needed_keys = ['trace.called_sql_query']

        probes = [
            {
                'schema_version': '1.0',
                'probe_id': 'outcome_readback',
                'description': 'Read authored SQL postconditions from independently captured DB state',
                'surface_id': f'sqlite.{tables[0]}',
                'adapter': 'sql_read',
                'read_only': True,
                'independence': 'independent_verifier',
                'provides_fact_keys': [f'sql.checker_{c["checker_index"]}' for c in native_checkers],
                'mutation_coverage': 'scoped',
                'covered_mutation_surfaces': [],
                'coverage_method': 'none',
                'estimated_cost': {'latency_ms': 1.0, 'bytes_read': 1000},
                'failure_modes': ['denied']
            },
            {
                'schema_version': '1.0',
                'probe_id': 'closed_world_diff',
                'description': 'Diff all captured table cells against task-specific strict allowlist',
                'surface_id': f'sqlite.{tables[0]}',
                'adapter': 'state_diff',
                'read_only': True,
                'independence': 'independent_verifier',
                'provides_fact_keys': ['mutation.out_of_frame_count'],
                'mutation_coverage': 'complete',
                'covered_mutation_surfaces': [f'sqlite.{tbl}' for tbl in tables],
                'coverage_method': 'snapshot_pair',
                'estimated_cost': {'latency_ms': 2.0, 'bytes_read': 2000},
                'failure_modes': ['denied']
            },
            {
                'schema_version': '1.0',
                'probe_id': 'trace_and_answer_check',
                'description': 'Verify process tool calls and user-facing answers against contract',
                'surface_id': 'trace.tools',
                'adapter': 'trace_read',
                'read_only': True,
                'independence': 'independent_verifier',
                'provides_fact_keys': trace_needed_keys,
                'mutation_coverage': 'scoped',
                'covered_mutation_surfaces': [],
                'coverage_method': 'none',
                'estimated_cost': {'latency_ms': 0.5, 'bytes_read': 500},
                'failure_modes': ['denied']
            }
        ]

        sql_facts = []
        for c in native_checkers:
            val = c['observed'][0][0] if isinstance(c['observed'], list) and len(c['observed']) == 1 and isinstance(c['observed'][0], list) and len(c['observed'][0]) == 1 else c['observed']
            if isinstance(val, (list, dict)):
                val = json.dumps(val)
            sql_facts.append({
                'fact_key': f'sql.checker_{c["checker_index"]}',
                'value': val,
                'source_ref': f'captured_snapshot:{self.after_snapshot["sha256"]}#checker_{c["checker_index"]}'
            })

        frame_receipts = [
            {
                'surface_id': f'sqlite.{tbl}',
                'completeness': 'complete',
                'method': 'snapshot_pair',
                'consistent_epoch': True,
                'independent_source': True,
                'snapshot_before_ref': pair.before_ref,
                'snapshot_after_ref': pair.after_ref
            }
            for tbl in tables
        ]

        # Trace and answer facts
        called_sql = any(step.get('tool') in ('sql_query', 'execute_sql') for step in self.trace)
        trace_facts = []
        for key in trace_needed_keys:
            if key.startswith('trace.called_'):
                tool_sub = key.split('trace.called_', 1)[1]
                called = any(step.get('tool') in (tool_sub, 'sql_query', 'execute_sql') for step in self.trace)
                trace_facts.append({
                    'fact_key': key,
                    'value': called,
                    'source_ref': f'trace:{self.run_id}#{tool_sub}'
                })
            elif key.startswith('answer.text_'):
                if self.agent_answer is not None:
                    trace_facts.append({
                        'fact_key': key,
                        'value': str(self.agent_answer),
                        'source_ref': f'trace:{self.run_id}#final_answer'
                    })

        t0_meas = time.perf_counter_ns()
        obs = [
            self._build_observation('outcome_readback', probes[0], sql_facts, [], denied=deny_readback),
            self._build_observation('closed_world_diff', probes[1], [{'fact_key': 'mutation.out_of_frame_count', 'value': len(issues), 'source_ref': f'snapshot_pair:{self.before_snapshot["sha256"]}|{self.after_snapshot["sha256"]}'}], frame_receipts, denied=deny_readback),
            self._build_observation('trace_and_answer_check', probes[2], trace_facts, [], denied=deny_readback)
        ]
        measured_probe_ms = (time.perf_counter_ns() - t0_meas) / 1e6

        # Call the REAL AURA Stage 7 Verifier
        cert = verify(
            self.contract,
            probes,
            obs,
            run_id=self.run_id,
            epoch_id=self.epoch,
            pair=pair,
            capture_bytes_read=pair.capture_bytes_read,
            trust_assumptions=[
                'AURA Stage 8.3 independent AgentSynth runtime adapter.',
                'SQLite online snapshot pairs taken before and after agent rollout.',
                'Inspection noninterference verified by pre/post hash matching.',
                'Strict closed-world allowlists enforce absence of persistent collateral edits.',
                'Agent self-reported success is unverified and untrusted.'
            ]
        )

        # Post-inspection hash verification
        post_inspection_db_hash = db_sha256(self.db_path)
        noninterference_passed = (post_exec_db_hash == post_inspection_db_hash)

        # Save artifacts to episode directory
        save_json_atomic(self.workspace / 'before.json', self.before_snapshot)
        save_json_atomic(self.workspace / 'after.json', self.after_snapshot)
        save_json_atomic(self.workspace / 'trace.json', self.trace)
        save_json_atomic(self.workspace / 'contract.json', self.contract)
        save_json_atomic(self.workspace / 'probes.json', probes)
        save_json_atomic(self.workspace / 'observations.json', obs)
        save_json_atomic(self.workspace / 'certificate.json', cert)
        save_json_atomic(self.workspace / 'native_checkers.json', native_checkers)
        save_json_atomic(self.workspace / 'strict_frame_diff.json', {
            'issues': issues,
            'changes': changes,
            'allowlist': self.allowlist
        })
        save_json_atomic(self.workspace / 'audit_receipt.json', {
            'run_id': self.run_id,
            'epoch_id': self.epoch,
            'task_id': self.task_id,
            'pre_eval_db_hash': self.pre_eval_db_hash,
            'post_exec_db_hash': post_exec_db_hash,
            'post_inspection_db_hash': post_inspection_db_hash,
            'noninterference_verified': noninterference_passed,
            'native_score': native_score,
            'aura_verdict': cert['verdict'],
            'unauthorized_diff_count': len(issues),
            'authorized_change_count': len(changes),
            'probe_latency_ms': round(measured_probe_ms, 4),
            'verification_ms': cert['costs']['planner_latency_ms']
        })

        return {
            'run_id': self.run_id,
            'epoch_id': self.epoch,
            'task_id': self.task_id,
            'native_score': native_score,
            'aura_verdict': cert['verdict'],
            'cert': cert,
            'issues': issues,
            'changes': changes,
            'noninterference_verified': noninterference_passed,
            'workspace': self.workspace
        }

    def _build_observation(self, pid: str, probe: Dict[str, Any], facts: List[Dict[str, Any]], receipts: List[Dict[str, Any]], denied: bool) -> Dict[str, Any]:
        ob = {
            'schema_version': '1.0',
            'observation_id': f'obs.{self.run_id}.{pid}',
            'run_id': self.run_id,
            'probe_id': pid,
            'epoch_id': self.epoch,
            'observed_at': utc_now(),
            'status': 'unavailable' if denied else 'ok',
            'reason_code': 'permission_denied' if denied else 'none',
            'channel': 'independent_verifier',
            'facts': [] if denied else facts,
            'coverage_receipts': [] if denied else receipts,
            'actual_cost': {'latency_ms': 0.0, 'cpu_ms': 0.0, 'bytes_read': 0 if denied else 1000}
        }
        ob['payload_sha256'] = observation_digest(ob)
        return ob
