# Stage 2 - Trust Boundary, Invariants, and Evidence Semantics

## Status
Stage 2 implements independent **evidence collection** against the Stage 1 schemas. It does **not** implement final task certification, possible-world reasoning, an adaptive CERA planner, or an agent-self-report grader. Stage 3 is responsible for PASS/FAIL/UNCERTAIN decisions.

## Local topology

```
root/
  state.sqlite3               Task database, writable by controlled agent actions
  workspace/                  Task filesystem, writable by controlled agent actions
  evidence/                   Harness/verifier storage - outside agent workspace
    snapshots/<epoch>.before.json
    snapshots/<epoch>.after.json
    traces/<epoch>.json
    observations/<observation_id>.json
    run_manifest.json
```

## Capture and trust assumptions
1. This first version is a deterministic **cooperatively quiescent local harness**, not a hardened security boundary. All task writers are paused during capture, and the agent is assumed not to bypass the harness or write to `evidence/`.
2. SQLite capture uses a read-only connection and an in-memory SQLite backup. It yields a consistent SQLite database view at capture time.
3. Files are separately hashed and checked for changes during each read. The database and filesystem are **not atomically snapshotted together**; consistency across stores requires the stated quiescence assumption. Any external writer bypassing the harness invalidates the completeness guarantee.
4. Both snapshots of an epoch must be present, digest-verified, and labelled `before` and `after`.
5. Snapshot capture covers all user SQLite tables and all entries in the task workspace. Individual coverage receipts only attest to specifically named declared surfaces, such as `sqlite.students` and `filesystem.reports`.
6. Persisted state diffs cannot detect a temporary unauthorized write which was reversed before the terminal snapshot. Complete intermediate mutation journals are **not supported** yet.
7. Protected evidence is created with atomic create-once file writes and SHA-256 integrity references. This detects accidental alteration, **not malicious changes by an attacker with evidence-store write access**. The same OS user currently can access both roots; a production deployment requires real process/permission separation.
8. The tool proxy logs the calls executed through it, not uninstrumented direct actions. The event trace is not claimed to be complete mediation or strong causal provenance.
9. `bytes_read` for SQLite snapshots is the canonical-serialized logical byte count, not physical disk I/O; filesystem snapshot bytes represent hashed file bytes. Probe byte counts measure serialized data examined or files read, not necessarily OS read accounting. All latency figures are measured wall-clock values.
10. Read-only probes do not issue task-changing SQL. SQL facts are calculated from captured, immutable database rows; file reads are compared to captured hashes before facts are emitted.

## Source-to-observation security
- One probe can only emit `fact_key` values registered in its Stage 1 `ProbeSpec`.
- Source channels are fixed by the registered probe (`independent_verifier`, etc.). A caller cannot mint an independent observation simply by changing its field without violating semantic validation.
- Complete frame receipts require a verified snapshot pair and exact artifact references. A count of zero unsupported changes alone is never a completeness guarantee.
- Receipt coverage does not imply that undeclared external services were checked.
- A tool return of `success` does not establish persistence. Tool result events are trace data, not authoritative state data.
- Missing or denied readbacks create **unavailable observations with zero facts**, not assumed negative or successful results.
- Conflicting authoritative facts within the same run and consistency epoch are reported for later Stage 3 adjudication; cross-epoch differences are not automatically conflicts.
- `source_ref` is provenance metadata in the sealed snapshot namespace, not an independently authenticated signature.

## Supported Stage 2 adapter subset
- `sql_read`: whitelist of structured student facts from the `students` table (student ID, marks, matching row count).
- `file_read`: `reports/student_<id>.md` existence and comparison of a `Marks: <integer>` line with the captured database.
- `state_diff`: independent before/after snapshot comparison and out-of-frame mutation count for two declared local surfaces; frame allowed-effect grammar is deliberately restricted to `<pk_column>=<integer>, <column> only` database updates and exact safe relative file paths. Unsupported patterns produce `error`/`unsupported`, not a clean frame receipt.
- `trace_read`: recorded `validate_eligibility` successful response preceding a recorded successful `update_marks` call.
- `external_status`, `complete_journal`: registerable in the Stage 1 schema but **not implemented**; return `unavailable`/`unsupported` instead of invented facts.

## Out-of-scope behavior
No automatically inferred user-intent satisfaction, no full relational SQL expression evaluator, no generic parser of arbitrary `target_pattern`, no complete concurrent distributed snapshot, no recovery, no live agent orchestration, and no arbitrary-third-party API statuses.

## Demonstration contract
The demo adapts the Stage 1 `01_complete_success` TaskContract and four ProbeSpecs without importing hidden ground truth. Student 101 starts at marks 70, student 102 at marks 88, and the permitted actions are to update the marks for 101 and create `reports/student_101.md`. The task simulator can deliberately drop writes, skip reports, write unrelated rows, or omit validation.

## Stage 2 acceptance gate
- Independent SQLite/file before/after captures: demonstrated.
- Registered structured read-only probes: demonstrated for 4 local adapters.
- Immutable-by-convention observations and capture digests: demonstrated; not tamperproof.
- Cross-object validation for the Stage 1 interface: demonstrated for core constraints.
- Stale, conflicting, denied, missing, forged, and out-of-scope tests: covered by tests.
- Claims of complete journal, external verification, or cross-store atomicity: explicitly **not demonstrated**.
- Stage 3 completion verdicts: explicitly **not implemented**.
