# AURA Stage 8.3 — Qwen2.5-3B Kaggle Pilot: Independent Evidence Audit

**Audit date:** 25 October 2026  
**Submitted archive:** `AURA_STAGE83_QWEN3B_PILOT_RESULTS.zip`  
**Archive SHA256:** `416b28a87621022668d8f04c63a3db6d8fd3be5c8d6a260346cae4da505d3a4d`  
**Archive entries:** 104; ZIP CRC: passed; manifest SHA256: 103/103 passed; no unmanifested members.

## Decision

**ACCEPT as a small, independently replayed real-model task-completion and verification pilot. Do not interpret it as official AgentSynth model benchmark accuracy or proof of general AURA accuracy.**

Five executions are recorded for Qwen/Qwen2.5-3B-Instruct, seed 42, with model-generated SQL actions and SQLite state. All five tasks were evaluated by the actual AURA Stage 7 contract verifier. A fresh audit reran the Stage 7 verifier against archived contracts, probes, observations, and SnapshotPair instances and reproduced all five verdicts, obligation outcomes and reason codes. An independent, read-only SQLite query of each archived database exactly matched the exported after-snapshot rows and SQL checker observations.

### Observed task outcomes

| Upstream AgentSynth core_v2 task | Tool calls / SQL errors | Reproduced published SQL checkers | AURA | Independent observed explanation |
|---|---:|---:|---|---|
| `raise-ticket-priority` | 2 / 0 | 2/2 | **PASS** | Agent read ticket 3 and updated priority to `high`; no extra persistent modification detected |
| `clearance-discount` | 1 / 0 | 3/3 | **PASS** | Agent applied `UPDATE products ... price * 0.8` to the eligible clearance row; other rows unchanged |
| `dedup-keep-latest` | 2 / 0 | 3/3 | **PASS** | Agent selected latest contact and deleted older duplicate ID 1, retaining ID 3 and unrelated contact |
| `cancel-and-void-payment` | 4 / 4 | 2/4 | **FAIL** | All SQL calls returned errors; agent still asserted that both updates succeeded. Order/payment stayed unmodified |
| `refund-and-restock` | 6 / 4 | 1/4 | **FAIL** | Agent retrieved the correct order line items but submitted multi-statement SQL that SQLite rejected. No refund or restock occurred |

**Totals:** 5 genuine model episodes; 3 PASS, 2 FAIL, 0 UNCERTAIN; 15 SQL calls; 8 calls ended in SQL errors; 5/5 verdict replay matches and 5/5 archived database/state checks match. Five runs are insufficient for a statistically strong accuracy claim.

## Reproduction and trust checks performed

1. Read and CRC-verified the submitted ZIP, then verified every `results/FILE_MANIFEST_SHA256.json` file hash and byte size against archive content.
2. Loaded the archived `contract.json`, `probes.json`, `observations.json`, `before.json`, and `after.json` for each model episode; invoked the unmodified local AURA Stage 7 `aura_verifier.engine.verify(...)` with a real `SnapshotPair` (**not** the saved boolean `certificate_replay.json`). Checked verdict, obligation results, and reason codes against archived certificates. 5/5 matched.
3. Loaded each archived `.sqlite3` file in independent read-only SQLite mode and compared all table rows to the after-snapshot, and reran published SQL predicates recorded in `native_checkers.json`. All 5 databases and SQL observations matched.
4. Verified raw archived database SHA256 against `audit_receipt.json` post-execution and post-inspection hashes for all five episodes.
5. Checked raw tool action/response logs against final outcome: two real examples of agent self-reporting success with ineffective SQL, caught by AURA's end-state checks.
6. Reviewed the scripted verifier preflight control and separated it from five model episodes; it is **not** an additional model task.

## Provenance and reproducibility limitations

- The actual captured AURA source revision is `607ffc9fc554db23a972f478475148514e9cc94e`, from branch `experiment/stage-8-3-external-llm-verification` (confirmed reachable as a GitHub commit), rather than the later corrected `feature/stage-8-3-external-verification` PR branch. These five SQL-state contracts should be reconciled with the corrected PR before combining datasets.
- Upstream AgentSynth source commit reported as `d2564dfb25ed7ba32e367d28117e6afd1ee6c485`.
- Model ID is recorded as `Qwen/Qwen2.5-3B-Instruct`. The README claims Hugging Face revision `aa8e72537993ba99e69dfaafa59ed015b17504d1`, but `environment.json` records `hf_revision: null`; the exact checkpoint revision is **not consistently pinned** in the machine-readable run configuration. Record `model.config._commit_hash` or resolved snapshot revision in the next run.
- The upstream *official AgentSynth benchmark runner* was **not** run on these five model episodes. Reproduced checker pass=3/5 is a locally reconstructed state-based comparison, not an official leaderboard score. These five tasks are SQL-only so this reconstruction is useful, but must be labeled accurately.
- One seed only, five purposively selected tasks, and no independent human-scored natural failures; verdict-to-reference agreement on these five does not establish population accuracy. No real-model UNCERTAIN case was observed.
- The two failed complex tasks share a prompt/tool-formatting weakness: the agent emits multiple SQL statements in one `sql_query` call, which is rejected by SQLite `execute`. The `cancel` task also mimicked the literal example text `ONE SQL STATEMENT;`, and claimed success after errors. Preserve this original run. If improving the tool prompting/parser, run new episodes with a new preregistered prompt version and never overwrite prior evidence.
- Frame checking covers persistent terminal SQLite state in enumerated tables. It does not demonstrate detection of transient, external, or non-SQL side effects. The verification readback is independent of the agent's claims, not an independently operated third-party attestation.
- Although certificate cost metadata exists, this experiment did not compare real adaptive CERA/fixed/greedy probe schedules. Do not cite this pilot as evidence of CERA cost savings.
- The saved model trajectory and tool errors support real generation, but they cannot independently attest to the Kaggle remote GPU run beyond recorded environment and model-output metadata.

## Recommendation

**Record this as the Stage 8.3 Qwen3B external SQL pilot: verification integration PASS; 3 genuine task successes, 2 genuine task failures.** It is stronger feasibility evidence than a mock-only control, but not sufficient alone for publication-quality broad reliability claims.

Before Stage 9 research claims, perform a lightweight CPU-only consolidation: import the five episodes as a separate `qwen2_5_3b_seed42` cohort on the corrected PR branch, preserve all hashes, check contract equivalence, and rerun the corrected independent strict reference *without access to AURA's verdicts*. Include both negative examples in the failure taxonomy. Avoid another immediate expensive GPU run unless needed to test the repaired one-statement agent interface.

The next carefully controlled model comparison should keep identical tasks, prompts, contracts, and seeds across models; the earlier Qwen0.5B five-task cohort differs by one task and prompting/runtime setup, so the raw 1/5 versus 3/5 contrast is not a fair model benchmark comparison.

**No GitHub commits/merges or Kaggle executions were performed by this audit.**
