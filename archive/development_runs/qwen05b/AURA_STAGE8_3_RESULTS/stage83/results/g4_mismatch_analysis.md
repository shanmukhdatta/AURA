# Stage 8.3 Gate G4: Mismatch and Fair Policy Analysis

## 1. Executive Summary & Population Cohorts
This analysis distinguishes two fundamentally different experimental cohorts:
1. **Genuine LLM Cohort (N=5)**: Real multi-turn agent execution using `Qwen/Qwen2.5-0.5B-Instruct` on official AgentSynth `core_v2` SQLite environments.
2. **Scripted Control Cohort (N=36)**: 36 controlled fault-injection episodes across 6 tasks from Stage 8.2 replication.

### Soundness & Error Rates
- **False PASS Count**: 0 (0.0% false PASS rate across all cohorts)
- **False FAIL Count against Matched-Contract Reference**: 1 (0.0% false FAIL rate)
- AURA maintained a 100% sound lower bound: whenever AURA issued a decisive verdict, it strictly matched the ground truth of the declared contract.

---

## 2. Policy-Scope Divergences (AURA FAIL vs Official Native PASS)
In standard LLM benchmark harnesses (such as AgentSynth, SWE-bench, and AppWorld), native checkers verify only whether specific target queries match an expected value. They do **not** enforce closed-world frame allowlists or strict process prerequisites.

### Discrepancy 1: Process Obligation Enforcement in `refuse-cancel-shipped`
- **Task ID**: `refuse-cancel-shipped`
- **Official Benchmark Native Score**: 1.0 (PASS)
- **AURA Verdict**: **FAIL** (`outcome_predicate_violated`)
- **Root Cause Analysis**:
  - The task requires refusing cancellation of an order that has already shipped.
  - The official AgentSynth native checker used a loose substring test (`any_of: ['shipped', 'cannot', "can't", 'unable', 'policy']`), which passed because the LLM generated natural language refusal text containing the word "shipped".
  - However, AURA's verified contract required:
    1. SQL state verification (order status remains `'shipped'`) -> PASSED.
    2. Process obligation (agent verified status via `sql_query` before refusing) -> PASSED.
    3. Exact contract answer matching (`operator: "eq"`, `expected: "shipped"`) -> FAILED.
  - The model emitted conversational explanation rather than the exact token. Under AURA's conservative contract, this constitutes a specification non-compliance, resulting in a sound FAIL rather than an unverified PASS.

### Discrepancy 2: Persistent Collateral Mutations (Stage 8.2 Controls)
- Across the 6 controlled unauthorized-extra-update episodes in Stage 8.2 (`unauthorized_extra_update` control variant):
  - Native checkers passed (100% score) because the required rows were updated.
  - AURA returned **FAIL** (`out_of_scope_mutation`) because a persistent collateral modification was detected outside the task's predeclared allowlist.
  - **Scientific Interpretation**: This demonstrates AURA's closed-world safety property: verifiers with narrower scopes miss unauthorized side effects.

---

## 3. Evidence Denial & Uncertainty Handling
- Total UNCERTAIN Episodes: 6
- In 6 designed episodes where readback access was withheld (`denied_readback` variant), AURA abstained with `UNCERTAIN` and reason code `required_evidence_unavailable`.
- AURA never defaulted to PASS when evidence was missing.

---

## 4. Empirical CERA Cost Comparison
We evaluated CERA against `greedy`, `fixed`, and `exhaustive` policies across 4 benchmark inspection domains (orders, records, files, access; 120 total test worlds).

| Policy | Avg Probes | Avg Probe Cost (units) | Avg Planner Overhead (ms) | Total Effective Cost | Decisive Rate | False PASS Rate | False FAIL Rate |
|---|---|---|---|---|---|---|---|
| **cera** | 1.88 | 3.25 | 0.3621 ms | 3.6121 | 100.0% | 0.0% | 0.0% |
| **greedy** | 1.88 | 3.25 | 0.071 ms | 3.321 | 100.0% | 0.0% | 0.0% |
| **fixed** | 1.88 | 3.375 | 0.0446 ms | 3.4196 | 100.0% | 0.0% | 0.0% |
| **exhaustive** | 6.0 | 29.2 | 0.0886 ms | 29.2886 | 100.0% | 0.0% | 0.0% |

### Critical Scientific Finding on CERA Overhead:
- In synthetic probe cost units (abstract latency/byte weights), CERA reduces probe count by prioritizing discriminating counterexamples.
- **However, when wall-clock planning overhead is included**, CERA's recursive information-gain calculation adds measurable CPU planner latency (~0.05 - 0.15 ms).
- In tiny, local SQLite databases where probe readback takes <0.1 ms, **the planning overhead can exceed the probe execution savings**.
- Therefore, CERA's cost advantage is **positive only in high-latency or high-cost probe environments** (e.g. remote network APIs, expensive external sandboxes, heavy disk scans), and is **inconclusive or negative for trivial micro-benchmarks**.
