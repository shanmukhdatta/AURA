# AURA - Stage 2: Trusted Evidence Infrastructure

**Status:** working local evidence-capture prototype; no PASS/FAIL/UNCERTAIN engine yet. This package continues the Stage 0 research freeze and Stage 1 interface specification.

## What this implements
- A controlled task sandbox with an SQLite database and a file workspace.
- Read-only SQLite snapshot capture and whole-workspace file manifests with SHA-256 references.
- Canonical before/after diffs with row-key aware updates and file changes.
- Four independent, registered probe adapters (SQL fact readback, file check, state-diff, and tool-trace fact inspection).
- Shape + semantic checks against the **unchanged Stage 1 JSON Schemas**.
- Atomically written, verifier-owned evidence records and frame completeness receipts.
- A tool-boundary trace logger, denial and stale-read handling, and same-epoch fact-conflict detection.
- Controlled demonstrations and tests without access to benchmark-only hidden outcomes.

## How to run
Requirements: Python >=3.10, `jsonschema`, and `pytest` for testing. No GPU, API keys, network, cloud, or paid software.

```bash
python -m pip install -e '.[test]'
python run_demo.py --scenario clean --out ./demo_clean
python run_demo.py --scenario collateral --out ./demo_collateral
python verify_capture.py --run ./demo_clean
python -m pytest -q
```

Choose a **new or empty** directory after `--out`. This protects earlier evidence from being overwritten.

Available scenarios: `clean`, `missing_report`, `collateral`, `silent_noop`, `denied_readback`, `missing_validation`.

Inspect `demo_clean/evidence/run_manifest.json` and the referenced `snapshots/`, `traces/`, and `observations/`. The manifest separates capture costs from probe costs and does not contain a completion verdict.

## Example evidence from the clean run

- `student.101.marks = 85`, `student.101.matching_count = 1`
- `report.101.exists = true`, `report.101.matches_db = true`
- `mutation.out_of_frame_count = 0` **within the declared complete local snapshot scope**
- `trace.validation_before_update = true` according to the controlled trace proxy

**Do not interpret this as AURA PASS.** Stage 3 will implement contract/predicate evaluation, three-valued logic, and verification certificates.

## Package map

```
aura_evidence/
  capture.py       SQLite/file capture with explicit epoch boundaries
  diff.py          Persistent-state difference extraction
  probes.py        Four concrete local probe implementations
  validation.py    Shape, semantic, trust and epoch validation
  ledger.py        Protected evidence record persistence and readback
  trace.py         Instrumented tool proxy/event record
  util.py          Canonical JSON, hashes, atomic writes
schemas/           Unmodified Stage 1 Draft 2020-12 schemas
examples/reference Stage 1 example task and probe contract
run_demo.py        Deterministic sandbox workflow demonstrations
verify_capture.py   Revalidate exported evidence without task verdict
tests/             Unit and integration tests; Stage 1 input-shape fixtures
  fixtures/        DOES NOT include actual-world ground-truth files
docs/              Trust limits and stage-2 design decisions
```

## Design boundaries and research integrity

The local proof covers only explicitly declared SQLite and filesystem surfaces in a cooperatively controlled sandbox. It is not a secure container or distributed atomic snapshot. Agent bypass of the instrumented tool boundary, transient reverted changes, external side effects, incomplete/forged contracts, and a malicious verifier-host compromise are not generally detectable here. Hashes alone do not authenticate evidence from an untrusted source. See [`docs/STAGE2_DESIGN.md`](docs/STAGE2_DESIGN.md).

The Stage 1 12-case suite was drafted for future verifier behavior. Stage 2 validates its input structures but **does not claim to pass the twelve PASS/FAIL/UNCERTAIN cases**; those are Stage 3 requirements.

This is research infrastructure, not a production secure verifier and not evidence of publication novelty.
