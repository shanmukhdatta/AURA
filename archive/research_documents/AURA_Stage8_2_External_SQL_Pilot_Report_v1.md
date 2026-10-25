# AURA Stage 8.2 — CPU-first external SQL task verification pilot

**Date:** 25 October 2026  
**Status:** Executed in local sandbox; evidence and reusable source available  
**Study class:** **Scripted, harness-controlled executions of externally authored AgentSynth tasks. NOT real LLM-agent executions, not an official AgentSynth benchmark leaderboard submission.**

## Research question

Does the existing AURA evidence-gated certificate engine distinguish task completion from (a) incomplete task execution, (b) tools that report success without changing state, (c) unauthorized extra persistent state changes, and (d) inadequate verifier access, on tasks not authored by the AURA project?

## External research provenance

We independently inspected the publicly available, MIT-licensed [AgentSynth project](https://github.com/agentsynth/agentsynth) and selected exactly six tasks from its `core_v2` SQL pack. The verified source files at the time of retrieval are:

- [`packs/core_v2.yaml`](https://github.com/agentsynth/agentsynth/blob/main/packs/core_v2.yaml), Git blob `d2bee0100fc46c58bbbe73b94d921b3e6c9f7a7a`.
- [`packs/core_v2_oracle.py`](https://github.com/agentsynth/agentsynth/blob/main/packs/core_v2_oracle.py), Git blob `942c296fadd47c7ec335355af39de05db9f7024a`.

**Task selection:** `raise-ticket-priority` (easy), `clearance-discount` (medium), `refund-and-restock`, `cancel-and-void-payment`, `store-credit-return`, and `reconcile-stock` (four hard). Only SQL-output-checker tasks were selected; answer-quality/refusal scenarios were deliberately excluded from the first protocol because the AURA adapter is limited to persistent SQL-state verification. Selection is *purposive*, not random or representative. Scenarios, schemas, records, checks, and reference SQL plans were manually transcribed from the cited public repository into a self-contained, reviewable script. This source subset is not the full 14-task pack.

### Reused AURA implementation

The unmodified **AURA Stage 7 `aura_verifier.engine.verify`** generated all certificates under Stage 1 schemas, with independent captured SQLite before/after snapshots using Stage 2 `capture_sqlite`. A new **Stage 8.2 adapter**, not the Stage 7 student/report `ProbeRunner`, maps task-specific read-only SQL facts and full table-diff facts into registered observations. The adapter is deliberately narrow; no arbitrary code or unaudited SQL from the model was executed.

## Protocol (predeclared, controlled)

Every task starts with a separately initialized SQLite database using the benchmark-author-provided schema and initial rows. Six execution variants were run for each task:

| Variant | Execution policy | AURA expected verdict |
|---|---|---|
| `oracle` | Execute published reference SELECT/UPDATE steps | PASS |
| `no_op` | Claim completion without executing any SQL | FAIL |
| `silent_noop` | Skip the first mutating statement but return a fake tool success; execute remaining steps | FAIL |
| `partial` | Skip last mutation | FAIL |
| `unauthorized_extra` | Execute reference workflow **and** an additional, locally injected out-of-authorization persistent update | FAIL |
| `denied_readback` | Execute reference workflow; simulate verifier refusal for *both* read-only probe channels | UNCERTAIN |

The task contract is assembled **before** scoring the execution, from the published expected SQL query results plus a task-specific row/field write allowlist. The allowlist preserves non-target data and explicitly limits authorized writes. AURA sees actual one-cell SQL result values and an independently computed count of out-of-allowlist database edits; the adapter does not feed Boolean benchmark pass/fail labels as outcome facts. Oracle reference SQL and fault-injection label are not passed as verifier evidence. Agent tool-return strings always claim success to expose self-report weakness.

**Evidence method:** Before and after the scripted execution, the sandbox captures *every* SQLite table, primary key, row and column. The verifier later reconstructs a read-only SQLite database from the terminal capture and executes the published SQL outcome queries. It independently compares all before/after row fields against the allowed write set, recording complete coverage for each declared table. AURA verifies supplied observation hashes, snapshot epoch references, complete-coverage receipts and contract predicates. The replay audit regenerates certificates from saved contract, probes, snapshots and observations.

**Native baseline definition:** The comparison called `upstream_sql_state_pass` reproduces the selected published SQL query/equality checkers against the independently captured terminal DB. It is **not the full official AgentSynth CLI**, which can also evaluate answer and tool-calling behavior on other tasks.

## Executed results

### AURA verdicts vs designed fault-class expectation

| Variant | Cases | AURA PASS | AURA FAIL | AURA UNCERTAIN | Matched control expectation |
|---|---:|---:|---:|---:|---:|
| Correct oracle | 6 | 6 | 0 | 0 | 6/6 |
| No action | 6 | 0 | 6 | 0 | 6/6 |
| Fake tool success | 6 | 0 | 6 | 0 | 6/6 |
| Incomplete execution | 6 | 0 | 6 | 0 | 6/6 |
| Unauthorized extra update | 6 | 0 | 6 | 0 | 6/6 |
| Verifier denied readback | 6 | 0 | 0 | 6 | 6/6 |
| **Total** | **36** | **6** | **24** | **6** | **36/36** |

The 36/36 agreement is **against known, designed injection conditions**, not an independent test-set accuracy metric, and the 36 cases are correlated within six tasks. Do **not** present it as 100% general accuracy on real-world AI agents.

### Comparison with reproduced published SQL outcome checks

| Variant | SQL outcome-checker PASS | AURA outcome with full authorized side-effect rules |
|---|---:|---|
| Correct oracle | 6/6 | 6 PASS |
| No action | 0/6 | 6 FAIL |
| Fake tool success | 0/6 | 6 FAIL |
| Incomplete execution | 0/6 | 6 FAIL |
| Unauthorized extra update | **6/6** | **6 FAIL** |
| Verifier denied readback | 6/6 (independent comparator still has state) | **6 UNCERTAIN** |

**Main observation:** In the deliberately chosen extra-update controls, published SQL outcome predicates were satisfied while additional, unauthorized table-cell changes persisted. Because its contract includes a complete task-scoped frame condition, AURA detected one unauthorized cell modification in each of the six cases. The result concerns a **different and stronger declared verification contract**; it is not a claim that AgentSynth's implementation is incorrect or that AURA is superior on the full benchmark. In the access-denied control, reference ground truth remained correct but a verifier without independent access abstained.

### Inspection ablations (144 certificates)

| Available evidence | PASS | FAIL | UNCERTAIN |
|---|---:|---:|---:|
| Both outcome + frame probes | 6 | 24 | 6 |
| Outcome probe only; frame unavailable | 0 | 18 | 18 |
| Frame probe only; outcome unavailable | 0 | 6 | 30 |
| No probes | 0 | 0 | **36** |

A known observed violation may justify FAIL even with another requirement unknown. Without enough evidence to establish *all* success conditions, no PASS is issued. These ablations evaluate epistemic behavior of the same 36 cases, not 144 distinct external workflows.

### Integrity and repeatability

- All **36 certificates** replayed against saved snapshot pairs and registered evidence with matching verdicts and per-obligation results.
- All **36 independent SQL checker records** reproduced from saved terminal captures without mismatches.
- Three adversarial input tests were rejected: forged observation facts with invalid digest, forged complete-coverage receipt even after recomputing the observation hash, and a tampered terminal snapshot.
- The **unmodified inherited Stage 7 regression suite passed 186/186 tests** in this sandbox.
- All test case evidence saved: contracts, probes, observations, before/after snapshots, tool traces, per-condition native-style SQL checks, strict frame diffs, and certificates. CSV summaries, ablation summary, and manifest are included.

## Interpretation and limitations

1. **This is already a valid, reproducible engineering experiment on externally authored tasks**. It exercises the exact existing AURA certificate engine against real SQLite state changes and before/after captures, not a copied/fake success judge.
2. **It is not yet external LLM-agent verification.** The agent action plans are publicly supplied scripted oracles with harness fault injection. The next step is to preserve the same task setup and blinded verifier while replacing scripted actions with saved real LLM trajectories, ideally across multiple task types and domains.
3. **No statistically supported benchmark superiority claim.** Six purposively selected tasks, highly correlated perturbations and intentionally constructed extra updates limit generality. The native comparison checks only original SQL outcome predicates while AURA checks a strictly stronger contract.
4. **No claim of physical/process-history completeness.** Trusted, quiescent local SQLite snapshots establish persistent mutations on enumerated tables only. Temporary unauthorized edits that are reverted before terminal capture and external side effects are outside this instrumented boundary.
5. **Adapter trust boundary:** The new adapter independently derives SQL readouts and unauthorized-diff counts from saved captured states, but `aura_verifier.verify` ultimately trusts correctly signed/hash-consistent registered observation contents from that adapter. A compromised adapter or incorrect allowed-effect policy can undermine guarantees; this is not a cryptographic attestation system.
6. **Cost limits:** The short measured adapter-execution times are local descriptive timings, not a benchmarked cross-system latency result. **CERA/planner was not evaluated in this experiment**; no new cost-efficiency advantage is claimed.
7. **Reproduction:** Original published task YAML/oracle files were manually transcribed for a six-task subset; code references source git-blob IDs. A broader study should parse the original upstream files automatically, pin a specific source commit, and run the official AgentSynth scorer independently alongside AURA.

## Recommended next scientific iteration

Move to a preregistered, **held-out** sample of 10–14 independently defined SQL tasks and a balanced set of actually observed agent executions (correct, incorrect, unsafe and evidence-limited), rather than choosing test cases with known outcomes. Run the original benchmark scorer and AURA in parallel, preserve full provenance, compare clear *contract-relative* accuracy, false PASS risk, UNCERTAIN coverage, and readback cost. Then repeat with a separate domain (e.g., tool-use process labels from AgentProcessBench, which are **not equivalent** to final-state completion labels). Test CERA only after verifying both methods receive identical probe access, and include planning overhead.

**No GitHub changes were made.**
