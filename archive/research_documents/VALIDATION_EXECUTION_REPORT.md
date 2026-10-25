# AURA External Validation — Technical Execution Report

**Date**: 2026-10-25 18:21:57 UTC  
**Git Branch**: `feature/external-validation-pipeline`  
**Git Commit**: `2676ae6327c562d919cee7089764d679e9af186e`  
**Execution Mode**: Local CPU-Only Validation (Strict Software Engineering Standards)  

---

## 1. Executive Engineering Summary

This report documents the external validation of the **Agent Uncertainty and Residue Arbiter (AURA)** research system.
The validation was conducted strictly as an independent software verification effort: inspecting saved source, verifying certificates through live re-execution against raw evidence, evaluating four separate scoring concepts, and auditing immutable evidence integrity.

### Key Quantitative Findings

- **Total Episodes Validated**: `59` across 4 distinct cohorts.
- **Deterministic Certificate Replay**: `59/59` (**100.0%** match on verdicts, obligations, reason codes, and surfaces).
- **AURA Concordance with Independent Strict Reference**: `59/59` (**100.0%**).
- **AURA False Passes (Type I Errors)**: **0** across all genuine model rollouts and scripted fault injections.
- **AURA False Fails (Type II Errors)**: **0** across all genuine model rollouts and scripted fault injections.
- **Noninterference Audit**: **100.0%** verified (on-disk SQLite hashes match post-execution baseline hashes).

---

## 2. Cohort Separation and Verification Results

To prevent misleading research conclusions, experimental cohorts are partitioned strictly by their authentic execution context:

| Cohort | Execution Mode | Model ID | Episodes | Upstream SQL Score | Independent Strict Ref | AURA Certificate Verdict | Concordance | Replay Match |
|---|---|---|---|---|---|---|---|---|
| `stage7_local` | local_baseline | `none_scripted_local_sqlite` | 13 | 23.1% | 23.1% | 23.1% | 100.0% | 100.0% |
| `stage82_scripted_controls` | scripted_control | `none_scripted_control` | 36 | 75.0% | 16.7% | 16.7% | 100.0% | 100.0% |
| `stage83_qwen05b_genuine` | genuine_llm | `Qwen/Qwen2.5-0.5B-Instruct` | 5 | 58.3% | 20.0% | 20.0% | 100.0% | 100.0% |
| `stage83_qwen3b_genuine` | genuine_llm | `Qwen/Qwen2.5-3B-Instruct` | 5 | 75.0% | 60.0% | 60.0% | 100.0% | 100.0% |

### Critical Evaluation Disclosures
1. **Scripted Controls vs Genuine Agents**: Stage 8.2 (36 episodes) and Stage 7 (13 scenarios) represent scripted fault injection harnesses. They test the verifier's lower-bound bounds against synthetic omissions, dirty writes, and epistemic gaps. They are **never** combined with genuine LLM rollouts.
2. **Qwen2.5-0.5B vs Qwen2.5-3B Asymmetry**: The two Qwen models were run under divergent experimental configurations:
   - `Qwen2.5-0.5B`: Executed locally on CPU, 4-turn maximum, evaluating tasks `{raise-ticket-priority, refuse-cancel-shipped, clearance-discount, dedup-keep-latest, refund-and-restock}`.
   - `Qwen2.5-3B`: Executed on Kaggle T4 GPU, 6-turn maximum, evaluating tasks `{raise-ticket-priority, clearance-discount, dedup-keep-latest, cancel-and-void-payment, refund-and-restock}`.
   Because task selection and turn budgets differ, these cohorts are presented independently rather than as a controlled head-to-head comparison.

---

## 3. Four Distinct Evaluation Concepts

To ensure external scoring correctness, four separate concepts are tracked:

1. **Official AgentSynth CLI Benchmark**: Official benchmark score from upstream CLI runner (only applicable if official CLI was executed).
2. **Reproduced Benchmark SQL-Only Checker**: The native postcondition checker score reproduced directly from task SQL queries.
3. **Independent Strict Task-Contract Reference Judgment**: A blinded, independent evaluator that checks database states against frozen postconditions and cell-level frame allowlists without reading AURA certificates.
4. **AURA Verification Certificate Verdict**: The formal cryptographic certificate verdict emitted by `aura_verifier.engine.verify`.

### Key Empirical Insights from Scoring Separation

- **Semantic Refusal Correction (`refuse-cancel-shipped`)**:
  - The 0.5B agent answered that order 9 *should* be cancelled, contradicting company policy forbidding shipped order cancellations.
  - Upstream native SQL checker naively searched for the keyword `'shipped'` and awarded **1.0 (PASS)**.
  - Both AURA and the Independent Strict Reference detected the policy contradiction and certified **FAIL**.
  - This validates AURA's ability to prevent false passes induced by naive benchmark string matching.
- **Partial Credit vs Strict Verification (`refund-and-restock`)**:
  - Upstream checkers awarded **0.75** (0.5B) and **0.50** (3B) for completing only part of the multi-step transaction.
  - AURA and the Strict Reference strictly required all obligations and certified **FAIL**.

---

## 4. Integrity and Noninterference Audit

- **Closed-World Snapshots**: All before/after snapshots verified valid internal SHA256 digests matching canonical contents.
- **SQLite Binary Noninterference**: On-disk database file digests match post-execution and post-inspection hashes (`audit_receipt.json`), confirming zero evaluation-induced side effects.
- **Repository Manifest Audit**: Audited `stage83/results/SHA256SUMS.json`, verifying frozen artifact preservation.

---

## 5. Artifacts and Reproduction Commands

All validation artifacts were generated programmatically and saved in `validation_reports/`:

- `validation_summary.json`
- `external_episode_metrics.csv`
- `cohort_summary.csv`
- `certificate_replay_results.json`
- `integrity_check.json`
- `validation_failures.md`
- `VALIDATION_EXECUTION_REPORT.md`

### Exact Reproduction Command

```bash
python -m aura_validation.runner
```

### Automated Test Suite Command

```bash
pytest tests/test_validation_pipeline.py -v
```
