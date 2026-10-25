"""Sandbox-owned local evidence capture over SQLite and filesystem.

Guarantees apply ONLY to named surfaces inside a quiescent, cooperatively
controlled sandbox. SQLite backup is consistent; DB + filesystem together
are NOT an atomic distributed snapshot. The harness must stop writers.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import os
import sqlite3
import stat
import threading
import time
from urllib.parse import quote

from .util import canonical_json, digest, file_digest, read_json, save_json_atomic, utc_now


class SnapshotError(RuntimeError):
    pass


def _quote_table(name):
    return '"' + name.replace('"', '""') + '"'


def _value(x):
    if isinstance(x, bytes):
        return {"blob_sha256": hashlib.sha256(x).hexdigest(), "blob_length": len(x)}
    if isinstance(x, float) and not (float('-inf') < x < float('inf')):
        return {"nonfinite_float": repr(x)}
    return x


def capture_sqlite(db_path):
    db_path = Path(db_path)
    if not db_path.is_file() or db_path.is_symlink():
        raise SnapshotError("SQLite database missing or linked")
    uri = 'file:' + quote(str(db_path.resolve()), safe='/') + '?mode=ro'
    original = sqlite3.connect(uri, uri=True, timeout=3)
    mirror = sqlite3.connect(':memory:')
    total_bytes = 0
    try:
        original.execute('PRAGMA query_only=ON')
        original.backup(mirror)  # SQLite transaction-consistent snapshot
        tables = {}
        definitions = mirror.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
        for name, schema in definitions:
            cols = mirror.execute('PRAGMA table_info(' + _quote_table(name) + ')').fetchall()
            column_names = [c[1] for c in cols]
            pk = [c[1] for c in sorted(cols, key=lambda c: c[5]) if c[5] > 0]
            rows = [dict(zip(column_names, (_value(v) for v in row))) for row in mirror.execute('SELECT * FROM ' + _quote_table(name))]
            rows.sort(key=lambda r: canonical_json(r))
            tables[name] = {"schema": schema, "primary_key": pk, "columns": column_names, "rows": rows}
            total_bytes += len(canonical_json(tables[name]))
        return tables, total_bytes
    except (sqlite3.DatabaseError, OSError) as exc:
        raise SnapshotError(f"database capture unsuccessful: {type(exc).__name__}") from exc
    finally:
        mirror.close()
        original.close()


def capture_files(workspace):
    workspace = Path(workspace)
    if not workspace.is_dir() or workspace.is_symlink():
        raise SnapshotError('workspace directory missing or linked')
    manifest = {}
    total = 0
    for p in sorted(workspace.rglob('*')):
        rel = p.relative_to(workspace).as_posix()
        st = p.lstat()
        if stat.S_ISLNK(st.st_mode):
            raise SnapshotError(f'symlink is not an allowed observable workspace entry: {rel}')
        if stat.S_ISDIR(st.st_mode):
            manifest[rel] = {"kind": "dir"}
        elif stat.S_ISREG(st.st_mode):
            before = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)
            sha, size = file_digest(p)
            st2 = p.lstat()
            after = (st2.st_dev, st2.st_ino, st2.st_size, st2.st_mtime_ns)
            if before != after or size != st.st_size:
                raise SnapshotError(f'file changed while being captured: {rel}')
            manifest[rel] = {"kind": "file", "sha256": sha, "size": size}
            total += size
        else:
            raise SnapshotError(f'unsupported workspace entry: {rel}')
    return manifest, total


@dataclass(frozen=True)
class SnapshotPair:
    epoch_id: str
    before: dict
    after: dict
    before_ref: str
    after_ref: str
    capture_cost_ms: float
    capture_bytes_read: int

    def require_same_epoch(self):
        if self.before['epoch_id'] != self.after['epoch_id'] or self.epoch_id != self.before['epoch_id']:
            raise SnapshotError('snapshot epoch mismatch')
        if self.before['side'] != 'before' or self.after['side'] != 'after':
            raise SnapshotError('snapshot side mismatch')
        if self.before.get('consistency_basis') != 'cooperative_quiescence' or self.after.get('consistency_basis') != 'cooperative_quiescence':
            raise SnapshotError('unsupported consistency basis')
        for s in (self.before, self.after):
            if s['sha256'] != digest({k: v for k,v in s.items() if k != 'sha256'}):
                raise SnapshotError('snapshot integrity mismatch')
        return True


class EvidenceSandbox:
    """Only the harness should construct this object, not the agent.

    root/state.sqlite3 and root/workspace are task state. root/evidence is
    verifier-owned and MUST not be accessible from the agent's sandbox.
    """
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.db = self.root / 'state.sqlite3'
        self.workspace = self.root / 'workspace'
        self.evidence = self.root / 'evidence'
        self._lock = threading.RLock()

    def initialize(self):
        self.root.mkdir(parents=True, exist_ok=True)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.evidence.mkdir(parents=True, exist_ok=True)
        if not self.db.exists():
            with sqlite3.connect(self.db) as connection:
                connection.execute('PRAGMA foreign_keys=ON')
                connection.execute('CREATE TABLE students (student_id INTEGER PRIMARY KEY, name TEXT NOT NULL, marks INTEGER NOT NULL)')
                connection.executemany('INSERT INTO students VALUES (?,?,?)', [(101,'Sample Student',70),(102,'Other Student',88)])
                connection.commit()
        return self

    def capture(self, epoch_id, side):
        if side not in ('before', 'after') or not epoch_id or '/' in epoch_id or '\\' in epoch_id:
            raise ValueError('invalid epoch or snapshot side')
        with self._lock:
            start = time.perf_counter_ns()
            tables, bytes_sql = capture_sqlite(self.db)
            files, bytes_fs = capture_files(self.workspace)
            payload = {
                'schema_version': '1.0', 'epoch_id': epoch_id, 'side': side,
                'consistency_basis': 'cooperative_quiescence', 'captured_at': utc_now(),
                'sqlite': tables, 'files': files, 'bytes_read': bytes_sql + bytes_fs
            }
            payload['sha256'] = digest(payload)
            ref = 'snapshots/' + epoch_id + '.' + side + '.json'
            save_json_atomic(self.evidence / ref, payload)
            elapsed_ms = (time.perf_counter_ns()-start)/1e6
            return payload, ref, elapsed_ms

    def load_pair(self, epoch_id):
        def load(side):
            path = self.evidence / 'snapshots' / (epoch_id + '.' + side + '.json')
            if not path.is_file():
                raise SnapshotError(f'missing snapshot: {side}')
            return read_json(path)
        before, after = load('before'), load('after')
        pair = SnapshotPair(epoch_id, before, after,
                            'snapshots/' + epoch_id + '.before.json',
                            'snapshots/' + epoch_id + '.after.json',
                            0.0, before['bytes_read'] + after['bytes_read'])
        pair.require_same_epoch()
        return pair

    def execute_agent_step(self, operation, *args, **kwargs):
        """Cooperative writer gate. Uninstrumented external writers violate the assumption."""
        with self._lock:
            return operation(*args, **kwargs)
