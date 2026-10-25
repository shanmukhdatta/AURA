# AURA — Stage 2 Implementation and Evidence Validation Report

**Project:** Agent Uncertainty and Residue Arbiter (AURA)  
**Stage:** 2 of 8 implementation/research stages after Stage 0  
**Date:** 24 October 2026  
**Status:** Implemented and tested as a controlled local evidence collector; not a task completion verifier

## Executive summary

AURA Stage 2 now contains a working Python/SQLite/filesystem evidence infrastructure built against the unchanged Stage 1 `TaskContract`, `ProbeSpec`, `Observation`, and `Certificate` JSON Schemas. It independently captures SQLite and filesystem state before and after a controlled workflow, builds canonical changes, records tool-boundary events, runs four explicit local read-only probes, and persists observations with integrity hashes and limited completeness receipts.

**Result:** **35 tests passed** in the local test suite. Six controlled workflow scenarios generated four inspectable observations each (24 total), including a forced readback denial. The evidence results were revalidated from saved artifacts. **No AURA PASS/FAIL/UNCERTAIN decisions have been calculated; Stage 3 implements those.**

## 1. Implemented modules

| Module | Implementation | Scope |
|---|---|---|
| `aura_evidence.capture` | SQLite read-only backup, file-hash manifests, epoch-tagged paired snapshots | Cooperative local sandbox |
| `aura_evidence.diff` | Persistent SQLite PK-aware row insert/update/delete, no-PK multiset changes, filesystem differences | Initial/terminal state only |
| `aura_evidence.probes` | SQL facts, report checks, state diff/frame accounting, trace-order facts | Controlled student/report contract |
| `aura_evidence.validation` | Stage 1 JSON Schemas and semantic registration, trust, digest, epoch and frame receipt checks | Core cross-object validation |
| `aura_evidence.ledger` | Atomic create-once evidence artifacts and independent readback | Hash-integrity references, not tamperproof signatures |
| `aura_evidence.trace` | Instrumented tool-event recording | Does not cover bypassed operations |
| `run_demo.py` | Six reproducible controlled scenarios | No LLM or paid services |
| `verify_capture.py` | Independent artifact-level evidence revalidation | No task verdict |

## 2. End-to-end evidence pipeline

`TaskContract + ProbeSpec -> Controlled local workflow -> (S0, trace, ST) -> Canonical state diff -> Read-only probes -> Observation ledger + completeness receipts -> Evidence manifest`

The implementation does not reinterpret tool status strings as proof of persisted effects. `state_diff` emits a complete-coverage receipt **only for named, locally captured mutable surfaces** backed by validated before/after artifacts and supported authorization rules.

## 3. Six evidence demonstration scenarios

| Scenario | Observed marks | Report exists | Report matches DB | Extra mutations | Required validation recorded | Readback |
|---|---:|---|---|---:|---|---|
| Clean | 85 | Yes | Yes | 0 | Yes | Available |
| Missing report | 85 | No | No | 0 | Yes | Available |
| Collateral mutation | 85 | Yes | Yes | 1 | Yes | Available |
| Silent tool no-op | 70 | Yes | No | 0 | Yes | Available |
| Readback denied | Unavailable | Yes | Yes | 0 | Yes | Denied for student probe |
| Missing validation | 85 | Yes | Yes | 0 | No | Available |

The `extra mutations` field is a **persistent final-state difference count restricted to the declared complete local frame surfaces**; it does not detect transient reverted changes or undeclared external services. The readback-denied scenario does not automatically make the whole task undecidable because other captured evidence may be available to a future verifier.

The six runs had 24 stored `Observation` records. One was deliberately marked `unavailable` with no asserted facts; the others were `ok`. The run manifests separately record capture and probe costs. These timing samples are smoke-test diagnostics, **not benchmark results or statistical performance claims**.

## 4. Test and integrity results

**Executed:** `python -m pytest -q`  
**Observed result:** 35 passed.

Tests cover: clean capture, authorized state changes, generated reports, complete local coverage receipts, missing report, silent write drop, unrelated mutation, skipped validation, denied readback, snapshot tampering, mismatched snapshot refs, fake self-report coverage, stale file detection, symlink rejection, fact conflicts, distinct observation epochs, invalid predicates, unregistered facts, incorrect epoch evidence, observation tampering, atomic create-once artifacts, capture cost accounting, extra files, no-primary-key multiset diffs, duplicate inserts, unsupported external and journal probes, and validation of all 12 Stage 1 contract/probe structural inputs.

**Important distinction:** Validating all twelve Stage 1 input fixtures does not mean that Stage 2 has executed the twelve reference PASS/FAIL/UNCERTAIN decisions. Stage 3 has not yet been implemented.

## 5. Evidence and trust limitations

1. **Sandbox assumptions:** Workflows use cooperative quiescence; the prototype is not a secure process/container boundary. External writers or an agent that bypasses the harness invalidate complete-observation assumptions.
2. **Cross-store atomicity:** SQLite's backup is consistent, but the database and filesystem are not snapshotted as one atomic distributed transaction.
3. **External and intermediate effects:** Complete-journal and external-status adapters are interfaces only; they currently produce `unavailable/unsupported` rather than fabricated evidence.
4. **Capture scope:** No claim about unregistered database tables as approved task frame surfaces, arbitrary directories outside the sandbox, irreversible external effects, or hidden user intent.
5. **Digest semantics:** SHA-256 helps detect changed files and artifacts under a protected-harness assumption; it does not authenticate a compromised evidence store.
6. **Schema extensions:** The Stage 1 schemas remain unchanged. The current demonstration adapter supports a deliberately restricted authorization grammar, not arbitrary free-text rules or SQL contracts.
7. **Cost accounting:** Capture time and logical snapshot byte volume are recorded separately from probe latency and logical inspected bytes. Disk I/O counters and general overhead scaling are future evaluation work.

## 6. Stage 2 exit criteria

- [x] Controlled SQLite database and filesystem workspace.
- [x] Initial/terminal independent snapshot capture and canonical persistent diffs.
- [x] Four local read-only probe adapters with registered fact names.
- [x] Schema and semantic validation, coverage receipts, epoch checks and evidence integrity checks.
- [x] Six independent demonstration scenarios and evidence samples.
- [x] 35 automated tests passing, including negative controls.
- [x] Documented unimplemented interfaces, trust assumptions, and hidden-ground-truth separation.
- [ ] Hardened isolation from a hostile agent (not required for the current controlled sandbox, but necessary for deployment claims).
- [ ] Complete journal and external status verification (future expansion, not falsely claimed complete).
- [ ] Advisor/research-team review (not yet performed).

**Stage 2 engineering status:** Complete for the declared **cooperatively controlled local pilot**. Not production-secure or externally validated.

## 7. Next stage

**Stage 3 — Core AURA Verification Engine** will consume the saved Stage 2 evidence and Stage 1 contracts, evaluate required postconditions, exact multiplicity, cross-artifact agreement, declared frame coverage, process rules and uncertainty, and generate structured PASS/FAIL/UNCERTAIN certificates. Its first acceptance gate will be the twelve Stage 1 reference-world scenarios and new integration cases derived from the actual Stage 2 artifacts. The future CERA planning algorithm remains Stage 5, not Stage 3.

## Deliverables

- `AURA_Stage2_Implementation_v1.zip` — runnable source code, unchanged Stage 1 schemas, tests, demo and technical design.
- `AURA_Stage2_Evidence_v1.zip` — six captured run workspaces/evidence ledgers, verification manifests, and CSV summary.
- `AURA_Stage2_Report_v1.md` / `.pdf` — implementation and limitation report.

**Research integrity note:** These outputs are local engineering checks, not evidence of novel algorithm superiority, agent success-rate improvement, or publication acceptance. No GitHub commit or push was made.
