# AURA: Verified Postcondition Arbiters and Frame Soundness for Autonomous Software and Database Agents

**Authors:** AURA Research Collective  
**Repository:** [https://github.com/shanmukhdatta/AURA](https://github.com/shanmukhdatta/AURA)  
**Pull Request:** [Draft PR #1](https://github.com/shanmukhdatta/AURA/pull/1)  
**Date:** October 2026 (Research Publication Edition)

---

## Abstract
Evaluating autonomous LLM agents by inspecting execution transcripts or self-reported success introduces severe grade inflation: recent audits show that agents frequently report success despite failing the task, modifying unauthorized persistent state, or gaming naive string-matching checkers. In this work, we introduce **AURA** (**A**gent **U**ncertainty and **R**esidue **A**rbiter), an independent verification framework that enforces postcondition soundness and closed-world frame policies across live database and software environments. AURA captures deterministic pre- and post-execution snapshot pairs, evaluates declared contract obligations via noninterfering probes, and proves the absence of unauthorized collateral mutations using cell-level allowlists. Under epistemic gaps or incomplete observations, AURA fails closed with explicit uncertainty rather than misattributing success.

To minimize verification overhead, we develop **CERA** (**C**ounterexample-guided **E**valuation with **R**isk **A**mortization), an observation-planning algorithm that sequentially chooses probes to minimize expected inspection costs while identifying failures early. We validate AURA against the official **AgentSynth** `core_v2` benchmark across two distinct open-weight LLM agent scales (`Qwen2.5-0.5B-Instruct` on CPU and `Qwen2.5-3B-Instruct` on GPU) alongside 36 replicated adversarial fault-injection episodes. AURA achieves a **100% sound lower bound** (zero false PASS, zero false FAIL against strict ground truth). Furthermore, we expose a critical vulnerability in standard benchmark checkers, where an agent inverting company policy was mistakenly awarded a 1.0 pass rate by naive substring matching, whereas AURA soundly identified the failure. All verification contracts, replayable certificates, and raw SQLite snapshots are published for independent third-party reproducibility.

---

## 1. Introduction

Autonomous agents powered by Large Language Models (LLMs) are increasingly deployed to execute complex, multi-turn software workflows: modifying databases, invoking APIs, and generating patch scripts. Evaluating whether an agent actually completed its assigned objective remains a foundational open challenge. Standard evaluation methodologies typically rely on one of two flawed mechanisms:
1. **Transcript-Based LLM Judges**: An evaluator prompt reviews the conversation trace or the agent's self-reported summary. Because agents routinely hallucinate or overlook execution errors, self-reported success correlates poorly with actual environment state.
2. **Ad-Hoc Benchmark Checkers**: Upstream benchmarks execute isolated post-queries (e.g., verifying whether an updated row matches an expected value). Crucially, these checkers do not audit whether the agent modified other sensitive rows, dropped tables, or satisfied prerequisite process constraints.

These limitations represent an instance of the classical **Frame Problem** in artificial intelligence: verifying that a desired postcondition holds does not guarantee that other aspects of the world remained uncorrupted. An agent tasked with cancelling an order that instead drops the entire customer database can pass an ad-hoc checker if the cancelled order row is absent.

### Key Contributions
- **AURA Architecture**: A formal contract-driven verification arbiter that pairs online environment snapshots with closed-world frame allowlists, ensuring that persistent modifications outside predeclared boundaries are soundly detected.
- **CERA Observation Planning**: An information-theoretic observation planner that minimizes verification latency and probe costs by prioritizing decisive counterexamples.
- **Empirical Multi-Scale Evaluation**: Rigorous real-agent execution across `Qwen2.5-0.5B` and `Qwen2.5-3B` agents on AgentSynth SQLite tasks, demonstrating 100% sound verification and exposing benchmark gaming vulnerabilities in naive substring evaluation.
- **Full Reproducibility**: Complete release of all SQLite binary states, tool execution trajectories, and cryptographically verifiable certificates.

---

## 2. The AURA Verification Architecture

### 2.1 Formal Problem Formulation
Let $W$ be an execution environment consisting of mutable state surfaces (e.g., SQLite tables). An agent executes a sequence of actions $a_1, \dots, a_T$, inducing a state transition from $w_{\text{before}}$ to $w_{\text{after}}$.

```
                     +---------------------------------------+
                     |         Task Contract C               |
                     |  - Surfaces (sqlite, trace)           |
                     |  - Closed-World Allowlists            |
                     |  - Obligations (outcome, process)     |
                     +-------------------+-------------------+
                                         |
                                         v
+------------------+         +-----------+-----------+         +------------------+
| w_before Snapshot| ------> |    AURA Verifier      | <------ |  w_after Snapshot|
| (Pre-Execution)  |         |   (Engine verify)     |         | (Post-Execution) |
+------------------+         +-----------+-----------+         +------------------+
                                         |
                                         v
                     +---------------------------------------+
                     |       Cryptographic Certificate       |
                     |  - Verdict (PASS / FAIL / UNCERTAIN)  |
                     |  - Verified Frame Surfaces            |
                     |  - Hash Noninterference Receipt       |
                     +---------------------------------------+
```

**Definition 1 (Task Contract):** A task contract $\mathcal{C} = \langle \mathcal{S}, \mathcal{F}, \mathcal{O} \rangle$ consists of:
1. **Surfaces** $\mathcal{S}$: Observable consistency domains (e.g., specific tables, tool execution traces).
2. **Frame Policy** $\mathcal{F}$: A closed-world allowlist specifying permissible modifications:
   $$\mathcal{F} = \{ (tbl, pk, cols) \mid tbl \in \mathcal{S}, pk \in \text{PK}(tbl), cols \subseteq \text{Cols}(tbl) \}$$
3. **Obligations** $\mathcal{O}$: A set of predicates $\{ \phi_1, \dots, \phi_m \}$ over observed facts categorised into *outcome*, *process*, and *frame* constraints.

**Definition 2 (Frame Soundness):** A state transition from $w_{\text{before}}$ to $w_{\text{after}}$ satisfies frame soundness under allowlist $\mathcal{F}$ if and only if for all tables $T$ and rows $r$:
$$\Delta(w_{\text{before}}, w_{\text{after}})[T, r] \neq \emptyset \implies (T, \text{PK}(r), \text{changed\_cols}(r)) \in \mathcal{F}$$

### 2.2 Online Snapshot Pairs and Noninterference
To verify frame soundness without modifying the environment, AURA captures an online byte-level snapshot before the agent begins and immediately upon agent termination. A noninterference check verifies that the evaluation probe suite does not alter the underlying database:
$$\text{SHA256}(w_{\text{post\_exec}}) = \text{SHA256}(w_{\text{post\_inspection}})$$

If this equality fails, the verification run fails closed with an `INTERFERENCE_DETECTED` error.

### 2.3 CERA: Counterexample-Guided Risk-Amortized Planning
In complex environments, evaluating all possible state assertions can incur substantial I/O overhead. We propose CERA, which formulates inspection as a sequential decision process over a set of available probes $\mathcal{P}$. Given prior distribution $P(w)$ over candidate worlds and observed outcomes $e_{1:k}$, CERA selects the probe $p^* \in \mathcal{P}$ that maximizes information gain per unit cost:
$$p^* = \arg\max_{p \in \mathcal{P} \setminus \text{seen}} \frac{\mathcal{H}(\text{Verdict} \mid e_{1:k}) - \mathbb{E}[\mathcal{H}(\text{Verdict} \mid e_{1:k}, p)]}{\text{Cost}(p)}$$

When a probe outcome decisively establishes a failure condition, CERA halts inspection immediately, avoiding wasteful readback costs.

---

## 3. Empirical Evaluation

### 3.1 Experimental Setup
We evaluate AURA against the official AgentSynth `core_v2` SQLite benchmark suite across three cohorts:
1. **Genuine LLM (0.5B)**: Local CPU inference using `Qwen/Qwen2.5-0.5B-Instruct` across 5 preregistered tasks (seed 42).
2. **Genuine LLM (3B)**: Kaggle T4 GPU inference using `Qwen/Qwen2.5-3B-Instruct` across 5 tasks (seed 42).
3. **Scripted Control Baseline**: 36 controlled fault-injection episodes across 6 tasks from Stage 8.2 replication, evaluating positive oracles, silent omissions, collateral mutations, and epistemic denials.

### 3.2 Main Benchmark Verification Results

| Evaluation Cohort | Model / System | Hardware | Evaluated Tasks | Tool Calls (Avg) | Reproduced SQL Pass | Strict Ground Truth | AURA Verified | False PASS | False FAIL | Concordance |
|---|---|---|---|---|---|---|---|---|---|---|
| **Genuine LLM (0.5B)** | Qwen2.5-0.5B-Instruct | CPU (x86_64) | 5 | 2.6 | 2/5 (40.0%) | 1/5 (20.0%) | **1/5 (20.0%)** | **0 / 5 (0.0%)** | **0 / 5 (0.0%)** | **100.0%** |
| **Genuine LLM (3B)** | Qwen2.5-3B-Instruct | T4 GPU (CUDA) | 5 | 3.0 | 3/5 (60.0%) | 3/5 (60.0%) | **3/5 (60.0%)** | **0 / 5 (0.0%)** | **0 / 5 (0.0%)** | **100.0%** |
| **Scripted Controls** | Deterministic Fault Harness | CPU | 36 | 2.0 | 6/36 (16.7%) | 6/36 (16.7%) | **6/36 (16.7%)** | **0 / 36 (0.0%)** | **0 / 36 (0.0%)** | **100.0%** |

#### Key Insights
- **Perfect Soundness**: Across all 46 evaluated episodes (10 genuine LLM runs + 36 scripted controls), AURA produced **0 false PASS** and **0 false FAIL** outcomes against strict independent ground truth.
- **Model Capacity Scaling**: Moving from `Qwen2.5-0.5B` to `Qwen2.5-3B` increased true task completion from 20% to 60%. On tasks requiring complex updates (`clearance-discount`) and duplicate deletions (`dedup-keep-latest`), the 3B model successfully emitted valid SQL commands where the 0.5B model failed.
- **Fail-Closed Defense**: When the 3B model failed on `refund-and-restock` (failing to replenish inventory), AURA soundly issued a certificate of failure.

---

### 3.3 Benchmark Gaming Case Study: Substring Vulnerability in `refuse-cancel-shipped`

| Evaluation Mechanism | Checker Logic / Rule | Assigned Score | Sound? |
|---|---|---|---|
| **AgentSynth Native Checker** | `any(w in text.lower() for w in ['shipped', 'cannot', 'policy'])` | 1.0 (PASS) | **No** (False PASS) |
| **AURA Frozen Contract** | Closed-world allowlist + strict refusal obligation | 0.0 (FAIL) | **Yes** (Sound FAIL) |
| **Independent Blind Scorer** | Semantic parser detecting contradictory instruction | 0.0 (FAIL) | **Yes** (Sound FAIL) |

#### Case Study Analysis
- **User Instruction**: *"A customer asks to cancel order 9. Company policy forbids cancelling orders that have already shipped — check its status and answer accordingly, without changing anything."*
- **Model Response**: *"The query executed successfully and returned the status as 'Shipped'. According to the company's policy, any order that has not yet been shipped cannot be cancelled. Therefore, the order with ID 9 should be cancelled."*
- **Takeaway**: The agent directly contradicted policy by instructing cancellation. However, because the word `"Shipped"` was present, AgentSynth's substring checker awarded full credit (1.0). AURA prevented this grade inflation by evaluating semantic refusal criteria and state immutability.

---

### 3.4 Observation Planning Efficiency and CERA Cost Analysis

| Inspection Policy | Worlds Evaluated | Average Probes | Probe Cost Units | Planner Latency (ms) | Soundness (FP / FF) | Recommended Operating Regime |
|---|---|---|---|---|---|---|
| `cera` | 64 | 1.88 | 3.2500 | 0.3709 ms | 0.0% / 0.0% | Distributed / high-latency sandboxes ($T_{probe} > 10$ms) |
| `greedy` | 64 | 1.88 | 3.2500 | 0.0736 ms | 0.0% / 0.0% | Low-latency local databases ($T_{probe} < 1$ms) |
| `fixed` | 64 | 1.88 | 3.3750 | 0.0451 ms | 0.0% / 0.0% | Static pre-ordered checks; zero planning overhead |
| `exhaustive` | 64 | 6.00 | 29.2000 | 0.0895 ms | 0.0% / 0.0% | Unconditional audit; evaluates all probes unconditionally |

#### Dimensional Insights
- CERA and greedy policies achieve a **7.8x reduction in probe cost** (3.25 units vs 29.20 units) compared to exhaustive inspection.
- In fast local environments where SQLite queries execute in $<0.2$ms, greedy planning achieves lower wall-clock time due to minimal planning overhead.
- In distributed environments where probe verification incurs container startup or network latency ($>10$ms), CERA amortizes planning overhead and delivers substantial wall-time savings.

---

### 3.5 Controlled Fault-Injection Matrix (Stage 8.2 Replication)

| Variant / Fault Class | N | Expected Verdict | AURA Verdict | Detection Rate |
|---|---|---|---|---|
| `oracle` (Full Success) | 6 | PASS | PASS | 100.0% (6/6) |
| `no_op` (Omission) | 6 | FAIL | FAIL | 100.0% (6/6) |
| `silent_noop` (Self-Report Lie) | 6 | FAIL | FAIL | 100.0% (6/6) |
| `partial` (Incomplete Fix) | 6 | FAIL | FAIL | 100.0% (6/6) |
| `unauthorized_extra` (Collateral Edit) | 6 | FAIL | FAIL | 100.0% (6/6) |
| `denied_readback` (Epistemic Gap) | 6 | UNCERTAIN | UNCERTAIN | 100.0% (6/6) |
| **Negative Tampering Controls** | 3 | REJECT | REJECT | 100.0% (3/3) |

---

## 4. Reproducibility and Artifacts

Every claim in this paper is backed by cryptographic evidence and automated test suites:
- **Test Suite**: 212 tests pass (193 inherited Stage 7 tests + 19 independent reference tests; 1 skipped on Windows non-admin symlinks).
- **Archive Verification**: `AURA_STAGE8_3_CORRECTED_RESULTS.zip` (CRC verified, 100% manifest match against `SHA256SUMS.json`).
- **Open GPU Notebook**: `AURA_STAGE83_REAL_AGENT_KAGGLE_v2.ipynb` executes the full verification pipeline on Kaggle T4 GPUs.
- **Pull Request**: Tracked live on GitHub at [Pull Request #1](https://github.com/shanmukhdatta/AURA/pull/1).

---

## 5. Conclusion
AURA introduces verifiable postconditions and closed-world frame policies to autonomous LLM agent evaluation. By pairing deterministic snapshot pairs with CERA observation planning, AURA closes critical security and grade-inflation loopholes in standard benchmark harnesses, establishing an unshakeable foundation for deploying trusted software agents.
