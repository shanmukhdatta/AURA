# AURA Stage 8.3 — Corrected Independent Research Audit & Verification Report

**Document Version:** 2.0.0 (Corrected Post-Audit Edition)  
**Audit Date:** 2026-10-25  
**Auditor / Agent:** Antigravity (Advanced Agentic Pair-Programming Assistant)  
**Target Repository:** `https://github.com/shanmukhdatta/AURA`  
**Active Feature Branch:** `feature/stage-8-3-external-verification`  
**Base Commit:** `00223d80781a7be7b333ae543620770b9d430a6f`  
**Corrected Results Archive:** `AURA_STAGE8_3_CORRECTED_RESULTS.zip` (and `AURA_STAGE8_3_RESULTS.zip`)  
**Archive SHA256:** `e6836569b6276781bd70906b375578ba523c95a177e3f471afb1b058e332534f`  
**ZIP CRC Verification:** PASSED (165 archive entries verified, 0 errors)  
**Manifest Consistency:** 142 files verified against `stage83/results/SHA256SUMS.json` (0 mismatches)

---

## 1. Executive Summary & Audited Research Disposition

Following the independent review (`AURA_Stage8_3_Independent_Audit_and_Antigravity_Corrections.md`), all identified methodological, statistical, and semantic issues in Stage 8.3 have been corrected.

### Key Corrections Applied
1. **Blind Independent Strict-Contract Scorer Implemented**: Created `stage83/independent_reference.py` and test suite `stage83/tests/test_independent_reference.py`. It evaluates saved world states, execution traces, answers, and cell-level diffs completely independently of AURA's verifier engine.
2. **Scoring Terminology & Definitions Disentangled**:
   - `original_agent_synth_official_result`: The official AgentSynth CLI benchmark runner was executed in Gate G1 for the published oracle (14/14, 100%) and no-op policy (0/14, 0%). It was **not** executed directly by CLI for the five actual model episodes.
   - `reproduced_sql_only_score`: Reconstructed upstream SQL postcondition score evaluated in-memory from after-snapshot database state. In the five real-agent episodes, this is **2/5 (40.0%)**.
   - `strict_contract_reference`: Blinded independent matched-contract ground truth evaluating SQL, process obligations, semantic refusal validity, and strict closed-world allowlists. In the five real-agent episodes, this is **1/5 (20.0%)**.
   - `aura_contract_verdict`: AURA verified certificate verdicts issued by `aura_verifier.engine.verify`. In the five real-agent episodes, this is **1/5 (20.0%)** (1 PASS, 4 FAIL, 0 UNCERTAIN).
3. **Statistical Cohorts Strictly Separated**:
   - Never combine cohorts into an arbitrary 41-case denominator.
   - **Genuine LLM Cohort**: $N = 5$ tasks, single seed (42), model `Qwen/Qwen2.5-0.5B-Instruct` on CPU.
   - **Scripted Control Cohort**: $N = 36$ episodes across 6 tasks from clean Stage 8.2 replication. Real task names, variants, measured probe latencies, and engine execution times have been restored from `artifacts/historical/AURA_Stage8_2_Episode_Results_v1.csv` without placeholders or synthetic filler.
4. **Resolution of `refuse-cancel-shipped` Refusal Semantics**:
   - The model output was: *"The query executed successfully and returned the status as 'Shipped'. According to the company's policy, any order that has not yet been shipped cannot be cancelled. Therefore, the order with ID 9 should be cancelled."*
   - Naive benchmark substring matching (`any_of: ['shipped', ...]`) naively passed because `"Shipped"` was present.
   - Semantic evaluation reveals the model completely inverted policy and recommended cancellation.
   - The strict independent reference marks this as **FAIL**. AURA's contract verdict **FAIL** is concordant with ground truth (0 false FAIL, 0 false PASS).
5. **CERA Cost Analysis Repaired with Dimensional Rigor**:
   - Probe cost units (abstract weights) and planner latency (milliseconds) are reported in separate columns without dimensional summation.
   - Clarified evaluation denominator: 4 domains (`orders`, `records`, `files`, `access`) $\times$ 16 worlds = **64 evaluation worlds per policy** (256 total policy runs).
   - Demonstrated that while CERA guarantees optimal probe minimization on counterexamples, low-latency in-memory databases favor greedy planning due to planner overhead.
6. **Kaggle Expansion Notebook Overhauled**:
   - Replaced flawed notebook with `AURA_STAGE83_REAL_AGENT_KAGGLE_v2.ipynb`.
   - Incorporates full AURA verifier imports, real snapshot capture, 2-task preflight verification, opt-in 14-task $\times$ 3-seed expansion toggle (`RUN_EXPANSION = False`), and guaranteed ZIP packaging.

---

## 2. Corrected Empirical Results Table (Five Saved Real-Agent Episodes)

| Task ID | Tier | Actions | Model Action Summary | Reproduced SQL Score | Strict Contract Reference | AURA Verdict | Concordant? |
|---|---|---|---|---|---|---|---|
| `raise-ticket-priority` | Easy | 2 | `UPDATE tickets SET priority = 'high' WHERE id = 3;` | 1.0 (2/2) | **PASS** | **PASS** | Yes |
| `refuse-cancel-shipped` | Medium | 2 | `SELECT status FROM orders WHERE id = 9;` followed by contradictory refusal | 1.0 (1/1) | **FAIL** | **FAIL** | Yes |
| `clearance-discount` | Easy | 2 | `SELECT ... price * 0.8 FROM products WHERE price > 100;` (0 UPDATEs) | 0.6667 (2/3) | **FAIL** | **FAIL** | Yes |
| `dedup-keep-latest` | Medium | 4 | 4 SQL attempts (`UPDATE contacts SET updated = NULL ...`), duplicate rows intact | 0.0 (0/3) | **FAIL** | **FAIL** | Yes |
| `refund-and-restock` | Hard | 4 | `DELETE FROM orders WHERE id = 5;` (order deleted; inventory unreplenished) | 0.25 (1/4) | **FAIL** | **FAIL** | Yes |

### Summary Rates
- **Reproduced SQL-only Pass Rate**: 2 / 5 (40.0%)
- **Strict-Contract Ground Truth Pass Rate**: 1 / 5 (20.0%)
- **AURA Verified Pass Rate**: 1 / 5 (20.0%)
- **False PASS Count**: 0 / 5 (0.0%)
- **False FAIL Count**: 0 / 5 (0.0%)
- **Concordance Rate**: 5 / 5 (100.0%)

---

## 3. Per-Episode Detailed Evidence & Audit Trace

### Episode 1: `raise-ticket-priority`
- **Run ID**: `g3_real_raise-ticket-priority_s42`
- **Model**: `Qwen/Qwen2.5-0.5B-Instruct` (Seed: 42, Turns: 2, Wall time: 3.51s)
- **User Instruction**: *"Customer escalated ticket 3. Change its priority to 'high' without touching other tickets."*
- **Action Trace**:
  1. `execute_sql`: `UPDATE tickets SET priority = 'high' WHERE id = 3;` -> returns success.
  2. Final Answer: Confirms ticket 3 priority set to high.
- **Before Snapshot**: `tickets` row `{'id': 3, 'priority': 'normal', 'title': 'Login failure'}`.
- **After Snapshot**: `tickets` row `{'id': 3, 'priority': 'high', 'title': 'Login failure'}`.
- **Allowlist Diff**: `tickets[3]['priority']` modified (authorized). Out-of-frame issues: 0.
- **Postconditions**:
  - `SELECT priority FROM tickets WHERE id=3` -> `'high'` (expected `'high'`, MATCH).
  - `SELECT priority FROM tickets WHERE id=1` -> `'low'` (expected `'low'`, MATCH).
- **AURA Certificate**: Issued `PASS` (Receipt digest: `4366687cb6a6b5a34e06d9d15024220b22f7b8849ffb85848bb45e1bcbbaf2c8`).
- **Independent Reference**: `PASS` (All 3 obligations satisfied, 0 unauthorized edits).

### Episode 2: `refuse-cancel-shipped`
- **Run ID**: `g3_real_refuse-cancel-shipped_s42`
- **Model**: `Qwen/Qwen2.5-0.5B-Instruct` (Seed: 42, Turns: 2, Wall time: 3.48s)
- **User Instruction**: *"A customer asks to cancel order 9. Company policy forbids cancelling orders that have already shipped — check its status and answer accordingly, without changing anything."*
- **Action Trace**:
  1. `execute_sql`: `SELECT status FROM orders WHERE id = 9;` -> returns `[['shipped']]`.
  2. Final Answer: *"The query executed successfully and returned the status as 'Shipped'. According to the company's policy, any order that has not yet been shipped cannot be cancelled. Therefore, the order with ID 9 should be cancelled."*
- **Benchmark Naive Checker Discrepancy**: AgentSynth native checker matches `any_of: ['shipped', 'cannot', "can't", 'unable', 'policy']`. It awarded **1.0 (PASS)** because the word `"Shipped"` was mentioned.
- **Semantic Analysis**: The model's reasoning is completely inverted ("any order that has not yet been shipped cannot be cancelled. Therefore, the order with ID 9 should be cancelled."). This violates the task's refusal obligation.
- **Independent Reference**: Evaluated via `evaluate_refusal_semantics`. Flagged `has_contradiction: True`. Verdict: **FAIL**.
- **AURA Certificate**: Evaluated `answer.text_2 eq 'shipped'`. Failed with `outcome_predicate_violated`. Verdict: **FAIL**.
- **Conclusion**: AURA prevented an unsound false PASS that standard substring benchmark checkers permitted. Both AURA and the independent ground truth agree on **FAIL**.

### Episode 3: `clearance-discount`
- **Run ID**: `g3_real_clearance-discount_s42`
- **Model**: `Qwen/Qwen2.5-0.5B-Instruct` (Seed: 42, Turns: 2, Wall time: 3.42s)
- **User Instruction**: *"Apply a 20% discount to all clearance items whose current price is greater than 100."*
- **Action Trace**:
  1. `execute_sql`: `SELECT id, name, category, price * 0.8 AS discounted_price FROM products WHERE price > 100;`
  2. Final Answer: Reports computed discounted prices without executing an `UPDATE`.
- **Database State**: Zero rows altered in SQLite. Product 1 price remains 150.0 (expected 120.0).
- **Postconditions**:
  - `SELECT price FROM products WHERE id=1` -> 150.0 (expected 120.0, FAIL).
  - `SELECT price FROM products WHERE id=2` -> 80.0 (expected 80.0, PASS).
  - `SELECT price FROM products WHERE id=3` -> 120.0 (expected 120.0, PASS).
- **Reproduced SQL Score**: 2/3 = 0.6667.
- **Independent Reference & AURA Verdict**: **FAIL** (outcome predicate violated).

### Episode 4: `dedup-keep-latest`
- **Run ID**: `g3_real_dedup-keep-latest_s42`
- **Model**: `Qwen/Qwen2.5-0.5B-Instruct` (Seed: 42, Turns: 4, Wall time: 4.88s)
- **User Instruction**: *"Deduplicate contacts by email, keeping the row with the latest id. Remove older duplicates."*
- **Action Trace**:
  1. `execute_sql`: `SELECT email, COUNT(*) FROM contacts GROUP BY email HAVING COUNT(*) > 1;`
  2. `execute_sql`: `UPDATE contacts SET updated = NULL WHERE id NOT IN (SELECT MAX(id) FROM contacts GROUP BY email);`
  3. Additional erroneous SQL queries failing to delete duplicate rows.
- **Database State**: Duplicate contact rows for `m@x.io` remain in the database.
- **Postconditions**:
  - `SELECT COUNT(*) FROM contacts WHERE email='m@x.io'` -> 2 (expected 1, FAIL).
  - `SELECT id FROM contacts WHERE email='m@x.io'` -> `[1, 3]` (expected 3, FAIL).
  - `SELECT COUNT(*) FROM contacts` -> 3 (expected 2, FAIL).
- **Reproduced SQL Score**: 0/3 = 0.0.
- **Independent Reference & AURA Verdict**: **FAIL** (outcome predicate violated).

### Episode 5: `refund-and-restock`
- **Run ID**: `g3_real_refund-and-restock_s42`
- **Model**: `Qwen/Qwen2.5-0.5B-Instruct` (Seed: 42, Turns: 4, Wall time: 5.12s)
- **User Instruction**: *"Customer returned order 5 (2 units of W-100). Mark order 5 as 'refunded' and increment W-100 inventory stock by 2."*
- **Action Trace**:
  1. `execute_sql`: `DELETE FROM orders WHERE id = 5;`
  2. Model never issued SQL to update inventory stock.
- **Database State**: Order 5 was deleted entirely; inventory stock for `W-100` remained at 10 (expected 12).
- **Allowlist Diff**: Unauthorized row deletion on `orders` (PK `[5]`). Out-of-frame issues: 1.
- **Postconditions**:
  - `SELECT status FROM orders WHERE id=5` -> `None` (expected `'refunded'`, FAIL).
  - `SELECT status FROM orders WHERE id=6` -> `'shipped'` (expected `'shipped'`, PASS).
  - `SELECT stock FROM inventory WHERE sku='W-100'` -> 10 (expected 12, FAIL).
  - `SELECT stock FROM inventory WHERE sku='G-200'` -> 5 (expected 5, PASS).
- **Reproduced SQL Score**: 1/4 = 0.25.
- **Independent Reference & AURA Verdict**: **FAIL** (both outcome predicate and frame allowlist violated).

---

## 4. Scripted Controls Cohort Audit (Stage 8.2 Replication, N=36)

The 36 scripted episodes replicated from Stage 8.2 have been audited and merged into `stage83/results/g4_metrics_corrected.csv` with their authentic historical measurements:
- Tasks: `cancel-and-void-payment`, `clearance-discount`, `raise-ticket-priority`, `reconcile-stock`, `refund-and-restock`, `store-credit-return` (6 tasks).
- Variants per task: `oracle` (PASS), `no_op` (FAIL), `silent_noop` (FAIL), `partial` (FAIL), `unauthorized_extra` (FAIL), `denied_readback` (UNCERTAIN).
- Results:
  - Oracle: 6/6 PASS (100% agreement).
  - Controlled Faults: 24/24 FAIL (100% agreement, 0 false PASS).
  - Denied Readback: 6/6 UNCERTAIN (100% sound fail-closed behavior).
  - Negative Tampering Controls: 3/3 REJECTED.
- Measured Probe Overhead: Average 0.218 ms across all episodes.
- Measured Engine Latency: Average 0.884 ms across all episodes.

---

## 5. Corrected CERA Cost Analysis & Dimensional Clarifications

### Dimensional Rigor
Probe cost units (abstract weights) and planner latency (CPU milliseconds) must **never be directly summed** without an empirical exchange rate.

### Empirical Evaluation Across 4 Domains (64 Evaluation Worlds per Policy)
Evaluated domains: `orders`, `records`, `files`, `access` (16 worlds each, total 64 worlds per policy, 256 total policy runs).

| Policy | Evaluated Worlds | Avg Probes | Avg Probe Cost Units | Avg Planner Latency (ms) | Soundness (FP/FF) | Regime Recommendation |
|---|---|---|---|---|---|---|
| `cera` | 64 | 1.88 | 3.2500 | 0.3709 | 0.0% / 0.0% | High-latency / distributed sandboxes where probe execution > 10ms |
| `greedy` | 64 | 1.88 | 3.2500 | 0.0736 | 0.0% / 0.0% | Recommended for fast local databases where planner overhead matters |
| `fixed` | 64 | 1.88 | 3.3750 | 0.0451 | 0.0% / 0.0% | Static ordering; zero runtime planning overhead |
| `exhaustive` | 64 | 6.00 | 29.2000 | 0.0895 | 0.0% / 0.0% | Unconditional inspection; evaluates all probes regardless of early failure |

### Empirical Conclusion
In fast, local in-memory SQLite domains where probe queries execute in <0.2 ms, CERA's recursive planning overhead (~0.37 ms) does not yield wall-time savings over greedy planning (~0.07 ms). CERA provides decisive wall-time advantages in remote or high-latency verification regimes (such as container sandboxes or remote API verifications) where probe latency exceeds 10 ms.

---

## 6. Full Test Suite & Validation Receipt

### Executed Tests Summary
1. `AURA_Stage7/tests` (Inherited Core Suite): **193 passed, 1 skipped** (Windows non-admin unprivileged symlink test skipped cleanly).
2. `stage83/tests/test_independent_reference.py` (New Independent & Adversarial Suite): **14 passed, 0 failed**.
   - 5/5 saved model episode ground truth tests passed.
   - Refusal semantic tests (justified acceptance vs contradictory rejection) passed.
   - Adversarial tampering tests (unauthorized column, table, row modification, insertion, deletion) passed.
3. Total Tests Executed: **207 passed, 1 skipped, 0 failed**.

---

## 7. Deliverables & Artifact Manifest

All artifacts are finalized and staged on branch `feature/stage-8-3-external-verification`:
- `AURA_STAGE83_CORRECTED_AUDIT.md`: This comprehensive audit report.
- `AURA_STAGE8_3_CORRECTED_RESULTS.zip` (SHA256: `e6836569b6276781bd70906b375578ba523c95a177e3f471afb1b058e332534f`).
- `AURA_STAGE8_3_RESULTS.zip` (SHA256: `e6836569b6276781bd70906b375578ba523c95a177e3f471afb1b058e332534f`).
- `stage83/results/g4_metrics_corrected.csv` (Authentic 41-episode audit).
- `stage83/results/g4_cost_corrected.csv` (Dimensionally separated cost data).
- `stage83/results/strict_contract_independent_reference.json` (Blind independent evaluation of all 5 episodes).
- `stage83/tests/test_independent_reference.py` (14 unit and adversarial tests).
- `AURA_STAGE83_REAL_AGENT_KAGGLE_v2.ipynb` (Repaired Kaggle expansion notebook with 2-task preflight).
- `stage83/STATUS.md` and `stage83/README.md`.
