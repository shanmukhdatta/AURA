# AURA Stage 8.3 — Independent audit of the corrected submission

**Audit date:** 25 October 2026  
**Evidence:** user-uploaded `AURA_STAGE8_3_CORRECTED_RESULTS.zip` and GitHub branch `feature/stage-8-3-external-verification` / PR #1.  
**Overall disposition: G4 PARTIALLY ACCEPTED; G5 NOT ACCEPTED; Stage 9 may be planned but Stage 8.3 must not be declared fully complete or merged.**

## 1. Independent verification receipts

| Item | Audit action | Finding |
|---|---|---|
| Corrected ZIP | Opened every member and checked ZIP CRC | **PASS:** 165 members, 0 CRC errors |
| Corrected ZIP SHA256 | Hashed uploaded bytes | `e6836569b6276781bd70906b375578ba523c95a177e3f471afb1b058e332534f`, 190,130 bytes |
| SHA256SUMS | Hashed the 142 listed files under `stage83/results/` | **PASS:** 142/142 correct, none missing |
| Frozen task contracts | Hashed all 14 contract files against `frozen_contracts_manifest.json` | **PASS:** 14/14 hashes correct |
| Episode contracts | Parsed each saved episode contract and compared to its frozen source | **PASS** semantically, 5/5; byte hashes differ solely because JSON whitespace/serialization differs |
| Independent reference unit tests | Ran `python -m pytest -q stage83/tests/test_independent_reference.py` on unpacked archive | **PASS:** 14 passed |
| Core AURA tests | Ran original archived Stage 7 test suite independently on Linux | **PASS:** 186 passed (19.11 s). This is the original code, not a rerun of the entire updated PR tree. |
| Corrected references | Recomputed all five using `evaluate_episode_independently` | **PASS** on all verdicts and score values: 1 PASS, 4 FAIL; all five reference labels match saved records. A list/tuple serialization difference occurs in one intermediate dedup observation, not in its verdict. |
| AURA certificate replay | Ran `aura_verifier.engine.verify` for each saved episode with archived probes, observations, contracts and snapshot pair | **PASS:** 5/5 verdicts, obligation results, reasons and evidence refs reproduced |
| Actual SQLite final states | Queried all five saved `.sqlite3` databases and compared row contents with archived `after.json` | **PASS:** 5/5 |
| Historical cohort | Compared corrected 36 scripted rows against original Stage 8.2 CSV | **PASS:** 36/36 names, variants, verdicts, changed-cell counts, probe and verifier latencies. Unknown wall times are explicitly unmeasured. |
| Cost-policy rerun | Called corrected G4 cost evaluator with original AURA Stage 7 planner in a separate temp output path | **PASS** on 64 worlds per policy and on probes/abstract cost values. Planner timings varied by hardware. |
| GitHub | Queried GitHub through the connected GitHub service | **PASS:** feature branch and *open* PR #1 exist; draft status unverified; **claimed SHA `976b4c90fbe257ab7b3ddb2fe6f3f00a402d2508` could not be resolved as a commit/ref.** |
| 207-test claim | Compared report's 193 passed + one skipped inherited run, plus 14 new tests | **PARTIAL:** arithmetically 207 passed + 1 skipped; the archived 14 tests were run here. The complete updated Windows/PR suite was not independently executed in this environment. |

## 2. Review of the seven mandatory corrections

### 1. Independent reference: PARTIAL
- `stage83/independent_reference.py` exists, is executable, does not import AURA's verifier engine and recomputes five case labels (1 PASS, 4 FAIL). Its test module contains 14 tests; all 14 pass independently here.
- **Not fully blinded/independent:** it reads `contract.json` from the AURA episode, loads the task-specific `strict_frame_diff.json` allowlist, and in the answer pathway reads the already-generated AURA `observations.json` rather than extracting the raw user-visible answer directly from a separate, independent log. It is independent in implementation, **not independent of shared specification and observation-construction assumptions**.
- **Generalization limitations:** `evaluate_refusal_semantics('carol spent the most: 410', 'top-customer-spend')` returns `semantically_sound=False`, although that is a potentially correct answer for the spending task. The independent answer checker is specialized to refusal language and cannot validate all 14 tasks as currently written. `compute_independent_frame_diff` did not flag a changed table schema in a targeted schema-change control; full closed-world completeness therefore is not established.
- For G4, distinguish "separately implemented reference over shared contracts" from a truly blinded independently specified human- or benchmark-grounded oracle. Document these limitations and add adversarial/positive tests before expanding.

### 2. Scoring clarification: PASS WITH SCOPE LIMIT
- G1 **original AgentSynth CLI**: archived native oracle JSON `14/14` and no-op `0/14` are present and internally consistent.
- Five LLM episodes: `original_agent_synth_official_result` correctly reads `not_executed_by_cli`. Therefore **there is no official model-run success percentage** for these five episodes.
- Reproduced SQL-only full-pass count **2/5 = 40%**; independent strict reference **1/5 = 20%**; AURA PASS **1/5 = 20%**. Each of these figures was independently confirmed from the saved data.
- Never label 2/5 as an original official score; avoid treating 1/5 as verified broad real-agent reliability.

### 3. Statistical cohort separation: PASS
- The corrected CSV contains **5 genuine-model** rows and **36 scripted-control** rows with correct original task IDs and variants.
- The 36 recorded probe and verifier timings agree with the historic Stage 8.2 CSV; unknown historical wall times are `unmeasured_historical`.
- Real-model results: PASS 1, FAIL 4, UNCERTAIN 0. Scripted controls: PASS 6, FAIL 24, UNCERTAIN 6. Use separate denominators; the very small real-model N=5 remains exploratory.

### 4. Refusal semantics: PARTIAL
- The saved model said that the shipped order **should be cancelled**, which contradicts the policy. The independent refusal heuristic correctly marks this particular response FAIL, while the naive `any_of` benchmark answer substring would match `shipped`.
- AURA's actual frozen contract still specifies `answer.text_2 eq 'shipped'`. This is **not a semantic refusal check**. A valid answer such as `Order 9 has shipped, so I cannot cancel it under company policy.` passes the new semantic heuristic but **would FAIL the existing AURA exact-equality obligation**. The fact that both reject this one bad response does not demonstrate robust policy checking.
- The proper fix is to adopt a validated task-specific refusal predicate or semantically justified deterministic requirements in a **versioned contract**, validate it with positive/negative cases, then assess new or separately labeled sensitivity experiments. Keep historical contracts unchanged.

### 5. CERA comparison: PARTIAL
- The corrected CSV separates abstract probe-cost **units** from planner CPU **milliseconds**; this correction is real. The rerun confirms 4 domains × 16 worlds = **64 worlds per policy** (256 policy-world evaluations).
- CERA: 1.88 probes, 3.25 abstract units; Greedy: **the same** 1.88 probes and 3.25 units; CERA planning overhead is higher. Thus **no measured CERA-over-greedy benefit** exists in the tested average, even at higher common probe latency if the probe counts remain identical.
- The report's claim that CERA has a demonstrated advantage for probes above ~10ms, or "guarantees optimal" probe use, is **unsupported by these results**. It is a hypothesis requiring genuinely timed high-latency experiments with a differing probe-selection advantage, not a conclusion from this table.

### 6. Kaggle notebook v2: FAIL — MUST FIX BEFORE GPU RUN
- **Good:** the `.ipynb` format and all Python cells compile; real `aura_verifier`/`AgentSynthAuraAdapter` imports are present; two tasks are configured for preflight; expansion to 14 × 3 is `RUN_EXPANSION = False` by default.
- **Fatal API mismatch:** cell 3 calls `adapter.run_aura_verification(agent_answer=final_answer)`, but GitHub's `AgentSynthAuraAdapter.run_aura_verification` signature is `(self, deny_readback=False, force_unauthorized_extra=False)`; it has **no** `agent_answer` argument. The preflight will raise `TypeError` at the first task.
- **Correct interface:** `adapter.set_agent_answer(final_answer)` (if an answer exists), followed by `adapter.run_aura_verification()`.
- The notebook does **not** persist `actions_log`, raw model generations or prompt history into the archive, even though they are generated in memory. Add `model_actions.jsonl`, full prompt/version/seed records and execution-error receipts before claiming full trajectory reproducibility.
- Clone of AURA uses a movable branch, not a pinned verified commit; both upstream and AURA commits should be pinned/recorded and checked. A missing GPU should not silently fall back to a small CPU model while labeling it a Qwen3B experiment.
- The preflight currently verifies noninterference and existence of the directory, but does not assert independent certificate replay or check that meaningful model actions were saved.
- **Do not launch GPU expansion using v2 as-is.**

### 7. Evidence integrity and tests: PARTIAL
- 165 members, 142 SHA256 listed research files, all matching. Five archived certificates replay against Stage 7; SQLite binary states match snapshots. Historical data is preserved.
- New 14 tests pass here; original Stage 7's 186 tests also pass here. The corrected report claims that its changed branch's inherited tests are 193 passed, one skipped, plus 14 new = 207 passed, one skipped. This is plausible and consistent but **not independently reproduced on the complete updated PR branch**.
- **G5 provenance defect:** `stage83/G5_STATUS.md` included inside the new corrected archive still gives the *old* `AURA_STAGE8_3_RESULTS.zip` SHA256 `46e790...`, size 163,369 bytes and 155 members. The corrected archive is SHA256 `e68365...`, size 190,130 and 165 members. It also mentions old 139-file manifest coverage in other status text. Correct all stale receipts, regenerate the corrected ZIP and manifest, and check a clean reconstruction.
- GitHub PR #1 is real and open; the supplied exact commit SHA `976b4c...` was not resolvable using the GitHub connector. Request the output of `git rev-parse HEAD` and reconcile branch/PR head with the uploaded archive.

## 3. Gate disposition and required next actions

**Gate G4: PARTIALLY ACCEPTED, NOT SIGNED OFF** — successful reproducible controlled observations, corrections to data separation and SQL-only-vs-official scoring, five replayable certificates, real external agent trajectories as archived. Blockers: shared-contract reference not fully blind, invalid exact-answer contract for a refusal, and unsupported CERA high-latency claim. Restrict results to an exploratory five-task proof-of-concept.

**Gate G5: NOT ACCEPTED** — archive integrity is good but stale G5 receipts, the unresolved claimed commit SHA and an immediate runtime bug in Kaggle v2 prevent a clean reproducible final handoff.

**Stage 9:** Design/planning can begin in parallel, but **formal transition and any claim that Stage 8.3 is fully complete must wait** for the remaining corrections.

### Minimal correction set (CPU-first; no need to rerun the five existing LLM episodes)
1. Fix the Kaggle adapter call and save raw model transcripts/prompts; add a mock/fake-adapter notebook preflight test plus a *real* 1–2-task GPU pilot before any 14×3 expansion.
2. Make the independent reference read the raw final answer, use independently specified/verifiable decision rules, add clear success/failure unit tests including a valid refusal; document shared-contract dependencies and avoid calling it fully blinded.
3. Version the refusal policy contract; do not retroactively modify the evidence or misrepresent the previous verdict.
4. Revise the CERA statement to **no demonstrated average advantage over greedy**; if that advantage is the research contribution, design and run a true calibrated remote/delayed-probe experiment.
5. Fix `G5_STATUS.md`, `G4_STATUS.md` and all archive/manifest/hash/count references. Pin and verify Git branch commit; rerun the updated 207-test suite and save a machine-readable test receipt.
6. Repackage and check the archive in a clean workspace; preserve the original corrected ZIP SHA as historical evidence, do not overwrite it silently.

## Scientific conclusion

The submission genuinely advances AURA: five model-driven external task traces are preserved, five AURA certificates replay and match five separately implemented strict reference outcomes on this **selected set**, and archive checks pass. That is a valid exploratory prototype milestone. It does **not yet** substantiate general false-pass=0%, general blinded-verifier accuracy, broad semantic policy correctness, or cost superiority. Final G4/G5 signoff requires the narrow corrections above, not another large expensive model run.
