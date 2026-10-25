# AURA - Stage 4: Evidence Model and Logical Reasoning

**Project:** AURA (Agent Uncertainty and Residue Arbiter)  
**Scope:** Python/SQLite local research prototype; Stage 4 adds bounded compatible-world reasoning over independently validated Stage 2 evidence and Stage 3 contract checks.

## What is new

- Obligation -> fact -> registered probe dependency graph.
- Explicit bounded finite-domain models with restricted declarative constraints.
- Conservative Stage 3 verdicts and model-relative exact verdicts in parallel.
- Logical UNKNOWN on observationally indistinguishable success/failure worlds.
- Guardrails for conflicting evidence, model inconsistency, incomplete mutation coverage and solver caps.
- Schema-compliant verification certificates plus a separate auditable reasoning ledger.
- Captured reasoning cost (included in certificate), reproducible 12 fixture + 6 local runs.

**Important:** Stage 4 does not run additional probes dynamically and does not implement Stage 5 CERA. Model assumptions are authored inputs and are **not independently established truths**. A bounded-model PASS is only sound *conditional on* domain completeness, trust and correctness of those assumptions. No benchmark superiority is claimed.

## Install and test

```bash
python -m pip install -e '.[test]'
python -m pytest -q
```

Expected current acceptance: **115 tests passed**.

## Reproduce fresh local and synthetic results

```bash
python reproduce_stage4.py --out ./fresh_stage4_results
```

This creates new controlled SQLite runs, snapshots, trace observations, certificates, model files, per-case reasoning ledgers, and CSV summary. Use an output directory that does not exist.

## Run a single existing fixture with an explicit model

```bash
python verify_bounded.py \
  --fixture tests/fixtures/stage1_inputs/05_unobservable_notification \
  --model examples/models/external_uncertainty_reference.json \
  --out ./my_bounded_certificate
```

## Run a real local capture

```bash
python run_demo.py --scenario clean --out ./clean_workspace
python verify_bounded.py \
  --run ./clean_workspace \
  --model examples/models/clean_local_reference.json \
  --out ./clean_bounded_result
```

Note that `clean_local_reference.json` is a **demo-specific reference**. For new runs, a new independently justified bounded model is required. A model that fixes the observed values after the fact is not valid for a rigorous verification-effectiveness comparison.

## Code overview

- `aura_evidence/`: Stage 2 SQLite, filesystem, read-only probes, capture and verification ledger.
- `aura_verifier/`: Stage 3 conservative deterministic task-completion verifier.
- `aura_reasoning/`: Stage 4 finite models, constraints, support graph, conditional verdicts.
- `schemas/`: Stage 1 contract/probe/observation/certificate, plus Stage 4 model and reasoning ledger.
- `tests/`: inherited Stage 2 and 3 tests plus Stage 4 logic/negative/real-run tests.
- `examples/models/`: reproducible research-fixture models.
- `docs/STAGE4_DESIGN.md`: formal semantics, limits, and recorded acceptance results.

## Scientific limitations

The 115 tests and 18 reference/local runs are **software acceptance**, not SOTA benchmarking. Model-relative results do not prove that the contract captures real user intent, that model relations are true, that all external side effects are observable, or that we have a sound distributed snapshot. This version uses complete finite enumeration; it does not include a general SMT solver or adaptive evidence acquisition.

**Next:** Stage 5 - CERA Adaptive Inspection Planner.

**Repository status:** No GitHub changes made.
