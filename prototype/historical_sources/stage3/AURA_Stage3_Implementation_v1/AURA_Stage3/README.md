# AURA — Stage 3: Core Task-Completion Verification Engine

**Status:** Runnable *controlled-local* Stage 3 prototype. **No adaptive CERA inspection planning yet.**

AURA's task is to establish whether **all declared multi-step workflow requirements** were met. It does **not** equate an agent's successful tool response with successful task completion.

## Quick start

Python 3.10+, `jsonschema`; `pytest` for tests. No GPU, LLM, paid APIs or network needed.

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python run_demo.py --scenario clean --out ./my_clean_run
python verify_task.py --run ./my_clean_run --out ./my_clean_run/certificate.json
python verify_task.py --fixture tests/fixtures/stage1_inputs/08_conflicting_evidence
python reproduce_stage3.py --out ./reproduced_stage3
```

Run each demo into a **fresh or empty** directory. Existing certificates are not overwritten.

Supported Stage 2 demonstration scenarios: `clean`, `missing_report`, `collateral`, `silent_noop`, `denied_readback`, `missing_validation`.

## Implemented now

- Reuses Stage 2's `aura_evidence` package and unmodified Stage 1 interface JSON Schemas.
- Validates observation digests, probe registration, run/epoch identity, and (for **real** runs) the independently captured snapshot pair and coverage receipts.
- Evaluates `eq`, `neq`, `true`, `false`, `count_eq`, and `same_as` contract predicates. Boolean values cannot masquerade as integer counts; unsupported predicates are rejected.
- Distinguishes observed contract violations (`FAIL`) from unavailable evidence (`UNCERTAIN`), while known failures dominate ordinary unknowns.
- Enforces a declared full-frame accounting prerequisite; state-diff checks cannot be certified without appropriate independent complete coverage. Transient-effect predicates require a complete journal rather than before/after snapshots.
- Detects same-epoch contradictory independent observations and returns `UNCERTAIN` with `evidence_conflict` rather than vacuously certifying PASS.
- Produces schema-validated JSON certificates with per-obligation results, evidence references, contract SHA-256, observation scope, reasons, and measured capture/probe/verifier times.

## Folder structure

- `aura_evidence/` — unchanged Stage 2 evidence collection implementation
- `aura_verifier/engine.py` — new Stage 3 task contract evaluator + certificate generator
- `schemas/` — unchanged Stage 1 machine-readable schemas
- `examples/reference/` — Stage 2 demonstration contract and probe catalogue
- `tests/fixtures/stage1_inputs/` — 12 **synthetic** reference inputs plus expected verdicts
- `tests/` — Stage 2 + Stage 3 unit/integration tests
- `docs/STAGE3_DESIGN.md` — decisions, limits, tests, and acceptance
- `docs/STAGE1_FIXTURE_HASH_COMPATIBILITY.json` — audit of corrected *test-only* fixture hashes
- `reproduce_stage3.py` — generates new six live runs and 12 synthetic fixture certificates

## Evidence distinction: real vs. synthetic

`verify_task.py --run` **requires** a real Stage 2 captured snapshot pair and validates all referenced evidence.

`verify_task.py --fixture` is a separate **reference-test** pathway. Its Stage 1 examples have pre-authored state facts and simulated snapshot receipts, **not actual captured database snapshots**. Such certificates are labeled `REFERENCE FIXTURE ONLY`; never treat them as real agent execution evidence. The verifier does not read the reference possible-world catalogue or the harness-only actual-world labels.

**Stage 1 checksum compatibility note:** The original Stage 1 synthetic `Observation.payload_sha256` values were not computed using Stage 2's canonical observation digest. To make fixture tests executable under the unchanged Stage 2 integrity algorithm, Stage 3 contains locally corrected *copies* of these test-only records (52 hashes). No observation payload facts, contract predicates, or expected verdicts were changed. The original Stage 1 archive remains unchanged. See the audit JSON for old and new digests.

## Demonstrated validation

- 12/12 Stage 1 authored reference verdicts and decision statuses matched the future-engine expectations.
- 6/6 **new real controlled-local** Stage 2-style demonstration runs produced their expected decisions.
- 76 automated tests passed at the time of Stage 3 packaging (35 Stage 2 regression tests; 41 Stage 3 tests), covering integrity attacks, missing coverage, false success, process violations and contradictory evidence.

These counts are **engineering acceptance tests** over known examples. They are **not** a generalization result, independent agent benchmark, confidence bound, or claim of research novelty.

## Trust and scientific limitations

1. Claims cover only explicit contract and inspection scope, *not all natural-language intent*.
2. The sandbox assumes cooperative quiescence; SQLite and filesystem captures are not a single distributed atomic snapshot. AURA cannot verify all external effects.
3. Stage 2's tool proxy is bypassable in a non-cooperative environment. A recorded read/order does not prove genuine data causation.
4. Trusted receipts require protected verifier-owned artifacts; SHA-256 hashes alone do not protect against a compromised host.
5. No global possible-world satisfiability solver, adaptive evidence-acquisition algorithm, in-flight enforcement or rollback is implemented in Stage 3.
6. A missing required fact results in `UNCERTAIN`; an unsupported or invalid contract/probe is rejected rather than silently certified.
7. Synthetic fixture digests were repaired transparently for test compatibility; do not treat fixture certificates as independently captured real evidence.
8. The conservative v1 evaluator treats atomic predicates individually and does not yet reason over correlated possible worlds; that's Stage 4.

**Next stage:** Stage 4 — obligation/evidence model and bounded logical reasoning. **No GitHub changes have been made.**
