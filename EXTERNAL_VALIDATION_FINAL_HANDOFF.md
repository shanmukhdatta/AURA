# AURA — External Validation Final Technical Handoff Report

**Date**: 2026-10-25  
**Role**: Python Software Engineer (External Validation, Testing & Reproducibility)  
**Git Branch**: `feature/external-validation-pipeline` (Dedicated feature branch pushed to GitHub)  
**Handoff Archive**: `AURA_EXTERNAL_VALIDATION_FINAL_HANDOFF.zip`  

---

## 1. Summary of Changes and Code Architecture

To validate AURA independently without modifying the core verifier or altering historical research evidence, a modular Python external validation package was constructed:

### Modules Implemented
1. **`aura_validation/models.py`**:
   - Strongly typed dataclasses: `CohortType`, `ExecutionMode`, `ScoringRecord`, `ReplayResult`, `IntegrityRecord`, `ValidationEpisode`.
   - Enforces strict separation of the four evaluation concepts and prevents conflation of scripted controls with genuine model rollouts.
2. **`aura_validation/reference_scorer.py`**:
   - Independent ground-truth evaluator operating without importing or reading AURA certificates.
   - Evaluates closed-world frame mutations via cell-level snapshot diffs against declared allowlists (`compute_frame_mutations`).
   - Implements semantic refusal parsing (`evaluate_refusal_semantics`) without rigid exact-string bias, correctly penalizing contradictory policy recommendations while accepting semantically sound refusals.
3. **`aura_validation/replayer.py`**:
   - Re-evaluates saved raw evidence (`contract.json`, `probes.json`, `observations.json`, `before.json`, `after.json`) through `aura_verifier.engine.verify` using live `SnapshotPair`.
   - Audits exact matching across verdicts, obligation results, reason codes, and declared frame surfaces.
4. **`aura_validation/integrity.py`**:
   - Validates snapshot internal canonical SHA256 digests.
   - Verifies SQLite on-disk database binary noninterference against post-execution baseline hashes (`audit_receipt.json`).
   - Audits repository file integrity manifests (`stage83/results/SHA256SUMS.json`).
5. **`aura_validation/cohorts.py`**:
   - Isolated cohort loaders for `stage7_local`, `stage82_scripted_controls`, `stage83_qwen05b_genuine`, and `stage83_qwen3b_genuine`.
   - Reads immutable evidence from `artifacts/historical/AURA_Stage8_2_External_SQL_Evidence_v1.zip` directly in memory without disk tampering.
6. **`aura_validation/runner.py`**:
   - Automated evaluation orchestrator generating all seven deliverable reports in `validation_reports/`.
7. **`tests/test_validation_pipeline.py`**:
   - 12 comprehensive automated test cases validating all external evaluation criteria.

---

## 2. Explanation of the 59 Episodes (vs. Earlier 53 Records)

### The Cohort Breakdown (59 Total Episodes)
1. **`stage7_local` (13 episodes)**:
   - *Mode*: Scripted local baseline scenarios (`local_baseline`).
   - *Environment*: Isolated local Python sandbox with cooperative quiescence SQLite capture.
   - *Model*: `none_scripted_local_sqlite`.
   - *Scenarios*: 13 canonical fault and clean cases (`clean`, `clean_extra_read`, `wrong_marks`, `wrong_report`, `extra_file`, `wrong_student`, `unlicensed_name_change`, `missing_report_and_collateral`, `late_regression`, `silent_noop`, `missing_validation`, `unavailable_authoritative_readback`, `transient_reverted_unobserved`).
   - *Results*: 3 PASS, 9 FAIL, 1 UNCERTAIN.
   - *Replay*: 13/13 MATCH (**100.0%**).
2. **`stage82_scripted_controls` (36 episodes)**:
   - *Mode*: Scripted control scenarios (`scripted_control`).
   - *Environment*: Isolated AgentSynth SQLite benchmark environment (harness fault injection).
   - *Model*: `none_scripted_control`.
   - *Tasks*: 6 tasks (`cancel-and-void-payment`, `clearance-discount`, `dedup-keep-latest`, `raise-ticket-priority`, `refund-and-restock`, `store-credit-return`) across 6 controlled variants each (`oracle`, `no_op`, `silent_noop`, `partial`, `unauthorized_extra`, `denied_readback`) = 36 episodes.
   - *Results*: 6 PASS (oracle), 24 FAIL (faults), 6 UNCERTAIN (denied readbacks).
   - *Replay*: 36/36 MATCH (**100.0%**).
3. **`stage83_qwen05b_genuine` (5 episodes)**:
   - *Mode*: Genuine LLM model rollout (`genuine_llm`).
   - *Environment*: Local CPU execution, unquantized PyTorch/Transformers, max 4 turns.
   - *Model*: `Qwen/Qwen2.5-0.5B-Instruct` (Seed 42).
   - *Tasks*: `raise-ticket-priority`, `refuse-cancel-shipped`, `clearance-discount`, `dedup-keep-latest`, `refund-and-restock`.
   - *Results*: 1 PASS, 4 FAIL, 0 UNCERTAIN.
   - *Replay*: 5/5 MATCH (**100.0%**).
4. **`stage83_qwen3b_genuine` (5 episodes)**:
   - *Mode*: Genuine LLM model rollout (`genuine_llm`).
   - *Environment*: Kaggle T4 GPU execution, PyTorch/Transformers, max 6 turns.
   - *Model*: `Qwen/Qwen2.5-3B-Instruct` (Seed 42).
   - *Tasks*: `raise-ticket-priority`, `clearance-discount`, `cancel-and-void-payment`, `dedup-keep-latest`, `refund-and-restock`.
   - *Results*: 3 PASS, 2 FAIL, 0 UNCERTAIN.
   - *Replay*: 5/5 MATCH (**100.0%**).

### Why 59 Episodes (vs Earlier 53 Records)?
In earlier Stage 8.3 reports, `g4_metrics_corrected.csv` contained **53 rows**:
- 14 G1 benchmark sanity cases (7 oracle + 7 noop runs of the upstream AgentSynth CLI benchmark harness).
- 34 Stage 8.2 scripted control runs (two variants were omitted from the intermediate CSV import).
- 5 Stage 8.3 genuine Qwen2.5-0.5B local episodes.
*(14 + 34 + 5 = 53 rows).*

**Distinctions in Current Validation (59 Episodes)**:
1. **Benchmark CLI checks vs. AURA Certificate Episodes**: The G1 runs (14 cases) were upstream benchmark sanity checks evaluating whether AgentSynth's test runner worked; they were not AURA-certified execution episodes with full snapshots and certificates. They are excluded from the certificate episode inventory.
2. **Complete Authentic Archive Restoration (36 vs 34)**: The authentic immutable archive `AURA_Stage8_2_External_SQL_Evidence_v1.zip` contains all 36 episodes (6 tasks x 6 variants). All 36 are verified directly from the archive.
3. **Stage 7 Local Baseline Integration (+13)**: The 13 canonical Stage 7 local controlled scenarios (which establish AURA's foundational contract semantics on SQLite/files) are included as a distinct cohort.
4. **Qwen2.5-3B GPU Pilot Integration (+5)**: The 5 genuine Qwen2.5-3B Kaggle pilot episodes (`stage83/results/qwen3b_pilot/`) are fully verified and audited.
*(13 + 36 + 5 + 5 = 59 total certified episodes).*

All 59 episodes possess complete before/after snapshots, probes, observations, and AURA certificates, and all 59 have been deterministically replayed through `verify()`.

---

## 3. Four Separate Scoring Concepts

| Cohort | Execution Mode | Model ID | Episodes | Upstream SQL Score | Strict Contract Reference | AURA Verified Verdict | Concordance | Replay Match Rate |
|---|---|---|---|---|---|---|---|---|
| `stage7_local` | Local Baseline | `none_scripted_local_sqlite` | 13 | 23.1% | 23.1% | 23.1% | **100.0%** | **100.0%** |
| `stage82_scripted_controls` | Scripted Control | `none_scripted_control` | 36 | 75.0% | 16.7% | 16.7% | **100.0%** | **100.0%** |
| `stage83_qwen05b_genuine` | Genuine LLM | `Qwen/Qwen2.5-0.5B-Instruct` | 5 | 58.3% | 20.0% | 20.0% | **100.0%** | **100.0%** |
| `stage83_qwen3b_genuine` | Genuine LLM | `Qwen/Qwen2.5-3B-Instruct` | 5 | 75.0% | 60.0% | 60.0% | **100.0%** | **100.0%** |

### Key Empirical Findings
- **Zero False Passes (Type I Error)**: 0 across all 59 episodes.
- **Zero False Fails (Type II Error)**: 0 across all 59 episodes.
- **Semantic Refusal Correction (`refuse-cancel-shipped`)**:
  - The Qwen2.5-0.5B agent observed that order 9 was shipped, but stated that order 9 *should* be cancelled, contradicting company policy.
  - Upstream native checker looked only for `'shipped'` and awarded **1.0 (PASS)**.
  - AURA and the Independent Reference caught the contradiction and certified **FAIL**.
- **Model Non-Comparability**:
  - Qwen2.5-0.5B and Qwen2.5-3B are reported as independent cohorts due to divergent environments (local CPU vs Kaggle GPU) and different task sets (`refuse-cancel-shipped` vs `cancel-and-void-payment`).

---

## 4. Automated Test Suite Execution Results

Full test suite execution command:
```bash
pytest AURA_Stage7/tests stage83/tests tests/test_validation_pipeline.py -v
```

**Results**:
- **Passed**: 224
- **Failed**: 0
- **Skipped**: 1 (`AURA_Stage7/tests/test_evidence_stage2.py::test_capture_files_symlink_privilege_boundary` cleanly skipped on Windows when running unprivileged)
- **Total Duration**: 133.75s (0:02:13)
- **Execution Log**: `test_execution_log.txt`

---

## 5. Evidence Package Contents

The evidence package `AURA_EXTERNAL_VALIDATION_FINAL_HANDOFF.zip` contains:
1. `aura_validation/`: Complete modular validation source (`models.py`, `reference_scorer.py`, `replayer.py`, `integrity.py`, `cohorts.py`, `runner.py`).
2. `tests/test_validation_pipeline.py`: Automated validation test suite.
3. `validation_reports/`:
   - `validation_summary.json`
   - `external_episode_metrics.csv`
   - `cohort_summary.csv`
   - `certificate_replay_results.json`
   - `integrity_check.json`
   - `validation_failures.md`
   - `VALIDATION_EXECUTION_REPORT.md`
4. `EXPERIMENT_INVENTORY_FINAL.csv`: One row per unique experiment execution across all 59 episodes.
5. `test_execution_log.txt`: Raw pytest output log (224 passed, 1 skipped).
6. `git_review_evidence.txt`: Full `git status`, branch, log, and diff against `main`.
7. `REPRODUCTION_COMMANDS.md`: Exact commands to regenerate all validation results.
8. `CHANGED_FILES.txt`: Complete inventory of added and modified files.

---

## 6. Git Review & Branch Status

```bash
git branch --show-current
# Output: feature/external-validation-pipeline

git status
# On branch feature/external-validation-pipeline
# nothing to commit, working tree clean
```

The feature branch `feature/external-validation-pipeline` has been pushed to GitHub:
- **Branch URL**: https://github.com/shanmukhdatta/AURA/tree/feature/external-validation-pipeline
- **Draft Pull Request**: Opened targeting `main` (unmerged).
All original evidence, historical archives, and repository files remain preserved.

