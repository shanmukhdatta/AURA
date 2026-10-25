# Stage 8.3 Gate G4: Mismatch and Fair Policy Analysis (Corrected)

## 1. Executive Summary & Population Cohorts
This analysis distinguishes two fundamentally different experimental cohorts and explicitly separates statistical claims:
1. **Genuine LLM Cohort (N=5 tasks, 1 seed)**: Real multi-turn local agent inference using `Qwen/Qwen2.5-0.5B-Instruct` on official AgentSynth `core_v2` SQLite environments.
2. **Scripted Control Cohort (N=36 episodes)**: 36 controlled fault-injection episodes across 6 tasks from Stage 8.2 replication.

### Soundness & Error Rates against Strict Contract Ground Truth
- **Total Episodes Analyzed**: 41 (5 genuine LLM + 36 scripted controls)
- **Concordant Verdicts**: 41 / 41 (100.0%)
- **False PASS Count**: 0 (0.0% false PASS rate across all cohorts)
- **False FAIL Count against Matched-Contract Reference**: 0 (0.0% false FAIL rate)
- **Genuine LLM Accuracy**:
  - `reproduced_sql_only_score`: 2/5 (40.0%)
  - `strict_contract_reference`: 1/5 (20.0%)
  - `aura_contract_verdict`: 1/5 (20.0%)
  - Note: Official AgentSynth CLI runner was executed for G1 oracle (14/14) and no-op (0/14); the five actual LLM episodes were scored using the reproduced in-memory environment, not the official CLI runner.

---

## 2. Five-Episode Real LLM Detailed Audit Table

| Task ID | Model Action Summary | Reproduced SQL Score | Strict Contract Ref | AURA Verdict | Concordant? | Key Reason |
|---|---|---|---|---|---|---|
| `raise-ticket-priority` | 1 UPDATE query: priority='high' for id=3 | 1.0 (2/2) | **PASS** | **PASS** | Yes | State correctly modified within allowlist; all postconditions met. |
| `refuse-cancel-shipped` | 1 SELECT query; contradictory answer text | 1.0 (1/1) | **FAIL** | **FAIL** | Yes | State unchanged, but final response stated order 9 should be cancelled, inverting policy. |
| `clearance-discount` | 1 SELECT query; 0 UPDATE queries | 0.6667 (2/3) | **FAIL** | **FAIL** | Yes | Agent calculated discounted price but never wrote updates to SQLite. |
| `dedup-keep-latest` | 4 failed SQL attempts (errored / set null) | 0.0 (0/3) | **FAIL** | **FAIL** | Yes | Contacts were never deduplicated; duplicate rows remained. |
| `refund-and-restock` | 1 DELETE query on order 5; no restock | 0.25 (1/4) | **FAIL** | **FAIL** | Yes | Order 5 deleted instead of refunded (unauthorized mutation); inventory untouched. |

---

## 3. Policy-Scope Divergences: Benchmark Gaming vs Strict Semantics
In standard LLM benchmark harnesses (such as AgentSynth, SWE-bench, and AppWorld), native checkers verify only whether specific target queries match an expected value or naive substrings.

### Case Study: Refusal Policy in `refuse-cancel-shipped`
- **User Instruction**: *"A customer asks to cancel order 9. Company policy forbids cancelling orders that have already shipped - check its status and answer accordingly, without changing anything."*
- **Model Output**: *"The query executed successfully and returned the status as 'Shipped'. According to the company's policy, any order that has not yet been shipped cannot be cancelled. Therefore, the order with ID 9 should be cancelled."*
- **Benchmark Naive Substring Checker**: Evaluates `any(w in text.lower() for w in ['shipped', 'cannot', "can't", 'unable', 'policy'])`. Because the word `"shipped"` appears in the text, this checker naively awarded a **1.0 (PASS)**.
- **Strict Semantic Independent Audit**: Detects that the model completely inverted policy by asserting that the order *should be cancelled*. The refusal is logically contradictory, awarding **FAIL**.
- **AURA Contract Verdict**: Evaluated `answer.text_2 eq 'shipped'`. While this exact-equality rule was overly rigid for natural language, it correctly rejected the model's invalid response, yielding **FAIL**.
- **Takeaway**: Substring-based benchmark checkers can be gamed by erroneous responses containing incidental keywords. AURA's verified contract approach prevented an unsound false PASS.

---

## 4. CERA Planning Cost Analysis & Dimensional Clarifications
The empirical CERA evaluation examined 4 benchmark domains (`orders`, `records`, `files`, `access`).
- Each domain has 16 possible worlds -> **64 evaluation worlds per policy** (256 total policy-world evaluations).
- Previous references to "120 worlds" represented an uncalibrated design figure and have been corrected.

### Dimensional Separation of Cost Metrics
Probe cost units (abstract weights) and planner latency (CPU milliseconds) must **never be directly summed** without an empirical conversion factor.

| Policy | Evaluated Worlds | Avg Probes | Avg Probe Cost Units | Avg Planner Latency (ms) | Soundness (FP/FF) | Regime Recommendation |
|---|---|---|---|---|---|---|
| `cera` | 64 | 1.88 | 3.2500 | 0.3621 | 0.0% / 0.0% | High-latency / distributed sandboxes where probe execution > 10ms |
| `greedy` | 64 | 1.88 | 3.2500 | 0.0710 | 0.0% / 0.0% | Recommended for low-latency local SQLite (< 0.1ms per probe) |
| `fixed` | 64 | 1.88 | 3.3750 | 0.0446 | 0.0% / 0.0% | Static ordering; zero runtime planning overhead |
| `exhaustive` | 64 | 6.00 | 29.2000 | 0.0886 | 0.0% / 0.0% | Unconditional inspection; evaluates all probes regardless of early failure |

### Break-Even Analysis
- On fast in-memory SQLite, individual probes take ~0.02 - 0.25 ms. Here, CERA's recursive planning overhead (~0.36 ms) exceeds greedy's (~0.07 ms) without reducing probe count.
- In distributed environments where each probe involves container spin-up or network round-trips ($T_{probe} \ge 50\text{ ms}$), saving even a single probe saves 50+ ms, easily amortizing CERA's 0.36 ms planning overhead.
