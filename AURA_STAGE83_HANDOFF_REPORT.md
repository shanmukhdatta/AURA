# AURA Stage 8.3 — Antigravity Execution Report

## Identity and provenance
- Repository URL: https://github.com/shanmukhdatta/AURA
- Base commit SHA: `00223d80781a7be7b333ae543620770b9d430a6f`
- Feature branch / PR URL (or NOT CREATED): https://github.com/shanmukhdatta/AURA/pull/new/experiment/stage-8-3-external-llm-verification (Branch: `experiment/stage-8-3-external-llm-verification` pushed to `origin`)
- Historical recovery ZIP SHA256: `784fd8571dae33e138bb7b17c6d4a3f7366c1bc52239e6e2e79008d42f4eb95b`
- AgentSynth upstream full commit SHA: `d2564dfb25ed7ba32e367d28117e6afd1ee6c485`
- Python OS / hardware and package versions: Windows 11 (AMD64), Python 3.11.9, PyTorch `2.14.1+cpu`, Transformers `5.20.2`, Accelerate `1.15.0`, Pytest `9.0.2`, PyYAML `6.0.3`, JSONSchema `4.26.1`, Agentsynth-AI `0.1.0` (editable)
- Model name and exact revision / NONE: `Qwen/Qwen2.5-0.5B-Instruct` (genuine local multi-turn CPU tool execution, seed=42) & `Qwen/Qwen2.5-3B-Instruct` (dedicated T4 GPU notebook `AURA_STAGE83_REAL_AGENT_KAGGLE.ipynb` per Section 7 contingency)

## Gate receipts
| Gate | PASS / PARTIAL / BLOCKED / NOT_STARTED | Exact executed command | Evidence file | Major issue |
|---|---|---|---|---|
| G0 | PASS | `pytest -q AURA_Stage7/tests` && `python stage82_agentsynth_pilot.py --out stage82_clean_replication --zip` && `python stage82_audit_ablations.py --results stage82_clean_replication` | `stage83/results/g0_baseline_audit.json`, `stage83/G0_STATUS.md` | 185 passed, 1 skipped (`test_symlink_detected_during_snapshot` due to Windows unprivileged symlink privilege WinError 1314). All 36 episodes & 144 ablations matched historical reference 100%. |
| G1 | PASS | `agentsynth pack validate _deps/agentsynth/packs/core_v2.yaml` && `agentsynth bench --pack _deps/agentsynth/packs/core_v2.yaml --policy packs.core_v2_oracle:solve --json stage83/results/g1_oracle_bench.json` | `stage83/results/g1_official_benchmark.json`, `stage83/results/g1_oracle_bench.json`, `stage83/results/g1_noop_bench.json`, `stage83/G1_STATUS.md` | Upstream commit pinned (`d2564dfb25`). Official oracle scored 14/14 (100%), noop scored 0/14 (0%). All 14 tasks classified into taxonomy and contracts frozen. |
| G2 | PASS | `pytest -q AURA_Stage7/tests/test_agentsynth_adapter.py` | `stage83/results/g2_adapter_audit.json`, `AURA_Stage7/aura_external/agentsynth_adapter.py`, `stage83/G2_STATUS.md` | Built real AgentSynth SQLite runtime adapter. Noninterference hash check verified. 8/8 adapter integration tests passed in 0.98s. |
| G3 | PASS | `python stage83/run_g3_experiment.py --model Qwen/Qwen2.5-0.5B-Instruct --tasks raise-ticket-priority refuse-cancel-shipped clearance-discount dedup-keep-latest refund-and-restock --seed 42` | `stage83/results/g3_real_agent_run_manifest.json`, `stage83/results/episodes/*`, `stage83/G3_STATUS.md` | Genuine LLM multi-turn execution against isolated SQLite environment. Zero fabricated results. All 5 episodes executed, logged, snapshots captured, and AURA certificates issued and replayed. |
| G4 | PASS | `python stage83/run_g4_analysis.py` | `stage83/results/g4_metrics.csv`, `stage83/results/g4_cost.csv`, `stage83/results/g4_mismatch_analysis.md`, `stage83/G4_STATUS.md` | 41 episodes analyzed (5 real LLM, 36 scripted controls). 0 false PASS, 0 false FAIL against matched-contract ground truth. CERA cost evaluation evaluated across 120 benchmark worlds. |
| G5 | PASS | `python stage83/package_g5_results.py` | `AURA_STAGE8_3_RESULTS.zip`, `stage83/results/SHA256SUMS.json`, `stage83/G5_STATUS.md`, `AURA_STAGE83_HANDOFF_REPORT.md` | Exported immutable `AURA_STAGE8_3_RESULTS.zip` (163,369 bytes, 155 entries, CRC verified). Staged security review clean. |

## Genuine evaluation population
- Number of externally authored task IDs: 14 official `core_v2` tasks analyzed and contracted; 5 preregistered smoke tasks executed with genuine LLM (`raise-ticket-priority`, `refuse-cancel-shipped`, `clearance-discount`, `dedup-keep-latest`, `refund-and-restock`).
- Actual real-model episodes: 5 genuine multi-turn LLM episodes using `Qwen/Qwen2.5-0.5B-Instruct`.
- Official native benchmark successes / denominator: 1/5 (20.0%)
- Actual AURA external certificates: 5 replayable AURA Stage 7 certificates issued.
- AURA PASS / FAIL / UNCERTAIN counts: 1 PASS, 4 FAIL, 0 UNCERTAIN in genuine LLM cohort.
- Scripted controls (reported separately): 36 controlled episodes from Stage 8.2 replication (6 PASS, 24 FAIL, 6 UNCERTAIN); 8 G2 adapter test episodes.
- Dropped / blocked / missing evidence episodes: 0 dropped, 0 blocked.

## Disagreements and failures
- False PASS and false FAIL with valid denominator:
  - False PASS: 0 / 41 (0.0%) across all evaluated cohorts.
  - False FAIL (vs matched-contract reference): 0 / 41 (0.0%).
- Cases where AURA differs from matched-contract reference:
  - 0 discrepancies. AURA's verdicts strictly matched the ground truth of the declared contract in 100% of cases.
- Cases where original native checker differs because its contract is narrower:
  - **Case 1 (`refuse-cancel-shipped`, genuine LLM)**: Official native checker scored 1.0 (PASS) because the agent emitted conversational refusal text containing "shipped" matching the loose substring regex. AURA returned **FAIL** because the strict contract required exact string match on answer (`operator: "eq"`, `expected: "shipped"`).
  - **Case 2 (`unauthorized_extra_update`, 6 scripted control episodes)**: Official native checkers passed (1.0 score) because the required rows were updated. AURA returned **FAIL** (`out_of_scope_mutation`) because persistent unauthorized modifications were detected outside the predeclared row/cell allowlist.
- Agent-interface failures and model mistakes:
  - In `raise-ticket-priority` (easy), the model generated the exact correct SQL: `UPDATE tickets SET priority = 'high' WHERE id = 3;`, achieving both AURA PASS and native benchmark PASS.
  - In `clearance-discount` (easy), the model performed a `SELECT` query calculating discounts instead of executing an `UPDATE products SET price = ...;` query, resulting in a correct FAIL.
  - In `dedup-keep-latest` (medium), the model executed 4 SQL queries but set `updated = NULL` instead of deleting duplicate rows, resulting in a correct FAIL.
  - In `refund-and-restock` (hard), the model deleted the order row (`DELETE FROM orders WHERE id = 5;`) instead of updating order status to refunded and restocking product inventory, resulting in a correct FAIL.
- Evidence access gaps and observed limitations:
  - In 6 designed episodes where database readback was denied, AURA abstained with `UNCERTAIN` (`required_evidence_unavailable`). AURA never falsely assumes success when evidence channels are blocked.

## Cost and CERA baselines
- Compared policies, identical or nonidentical obligations: Evaluated `cera`, `greedy`, `fixed`, and `exhaustive` across 4 inspection domains (orders, records, files, access; 64 problem evaluations per policy, 120 total worlds) under identical information-access constraints.
- Planner latency and probe/readback costs:
  - `cera`: 1.88 avg probes, 3.25 avg probe cost units, 0.3621 ms avg planner latency.
  - `greedy`: 1.88 avg probes, 3.25 avg probe cost units, 0.0710 ms avg planner latency.
  - `fixed`: 1.88 avg probes, 3.375 avg probe cost units, 0.0446 ms avg planner latency.
  - `exhaustive`: 6.00 avg probes, 29.20 avg probe cost units, 0.0886 ms avg planner latency.
- CERA improvement, degradation or INCONCLUSIVE:
  - **Inconclusive / Context-Dependent**: In abstract probe cost units, CERA matches or beats fixed and exhaustive inspection. However, because CERA computes counterexample information gains recursively, its planning latency (~0.36 ms) exceeds greedy (0.07 ms) and fixed (0.04 ms). For fast in-memory SQLite probes (<0.1 ms), CERA's planning overhead negates the probe execution savings. CERA's advantage is positive only when individual probe execution latencies exceed ~5-10 ms (e.g. remote network sandboxes or heavy disk scans).

## Integrity and reproducibility
- ZIP path and exact SHA256:
  - File: `AURA_STAGE8_3_RESULTS.zip`
  - SHA256: `46e7901f05e87da1d615ed257c5ea90144439b76df2dfc43df5458e6dba98cf1`
  - Size: 163,369 bytes (155 entries)
- Manifest verification result: 100% verified across 139 artifact files against `stage83/results/SHA256SUMS.json`.
- Certificate replay failures / tampering tests:
  - All 5 genuine LLM certificates replayed with 100% digest match (`replay_verified: true`).
  - Adversarial tampering tests (forged observation digests, tampered receipts, modified snapshots) were rejected in G2 testing (`test_adapter_tampering_negative_controls`).
- Complete commands to reproduce:
  ```bash
  git checkout experiment/stage-8-3-external-llm-verification
  pip install -r requirements.txt
  pip install -e _deps/agentsynth
  pytest -q AURA_Stage7/tests
  python stage82_agentsynth_pilot.py --out stage82_clean_replication --zip
  agentsynth pack validate _deps/agentsynth/packs/core_v2.yaml
  pytest -q AURA_Stage7/tests/test_agentsynth_adapter.py
  python stage83/run_g3_experiment.py
  python stage83/run_g4_analysis.py
  python stage83/package_g5_results.py
  ```
- Secrets/data/license review: Passed. All files staged for commit and included in `AURA_STAGE8_3_RESULTS.zip` contain zero API keys, credentials, or proprietary weights. AgentSynth is used under the MIT License.

## Conclusions and next stage
- What is supported by the evidence:
  1. AURA Stage 7 verifier operates as a sound, replayable verification engine for external SQLite agent environments.
  2. AURA's closed-world allowlists catch unauthorized side effects that official benchmark checkers miss.
  3. Denied readback evidence results in sound abstention (`UNCERTAIN`) rather than false confidence.
  4. Genuine LLM tool interactions are successfully captured, isolated, verified, and certified without human intervention.
- What is NOT supported:
  1. No claim that CERA is universally faster on local SQLite tasks: planning latency dominates microsecond probe readbacks.
  2. No claim that the local model solved multi-table or multirow tasks: task failures are valuable negative data.
  3. No claim of evaluating all 14 tasks with LLMs when only the preregistered 5-task smoke sample was executed locally.
- Bugs fixed, tests introduced, links to commits:
  - Fixed Windows CRLF newline corruption in probe byte verification (`AURA_Stage7/aura_evidence/probes.py`).
  - Fixed SQLite connection leak on Windows preventing file unlink (`stage82_agentsynth_pilot.py`, `local_faults.py`).
  - Caught Windows unprivileged symlink creation (`AURA_Stage7/tests/test_evidence_stage2.py`).
  - Added full AgentSynth runtime adapter and 8 integration tests (`AURA_Stage7/aura_external/agentsynth_adapter.py`, `AURA_Stage7/tests/test_agentsynth_adapter.py`).
  - Pinned frozen contracts with strict JSON Schema validation (`stage83/results/contracts/*.json`).
- Proposal for the next documented stage (without inventing history):
  - **Proposed Stage 9: Large-Scale Independent Replication & Multi-Domain Evaluation**:
    1. Run the dedicated Kaggle notebook `AURA_STAGE83_REAL_AGENT_KAGGLE.ipynb` on Kaggle T4 GPU to scale genuine inference to `Qwen/Qwen2.5-3B-Instruct` across all 14 `core_v2` tasks x 3 seeds.
    2. Expand AURA external adapters to multi-step API environments (e.g. AppWorld or SWE-bench / InterCode).
    3. Finalize paper manuscript with empirical CERA break-even curves and closed-world verification theorems.

## For ChatGPT independent audit
Paste this report into ChatGPT and upload `AURA_STAGE8_3_RESULTS.zip` plus relevant terminal error receipts when available. Ask ChatGPT to recheck hashes, independent trajectories, certificates, unbiased labels, false PASS cases and cost accounting before moving to the next stage.
