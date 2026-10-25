# AURA Stage 8.1: Second Kaggle run, independent ZIP audit

**Input:** `AURA_STAGE8_1_OUTPUTS (1).zip` (uploaded October 25, 2026)  
**Audit:** independently parsed the ZIP file, verified ZIP CRC, compared all manifest SHA-256 values and declared sizes, independently evaluated saved SQLite before/after snapshots, report content and trusted tool order, compared these with certificate and withheld harness reference, and compared prior uploaded run. No official external benchmark success is inferred.

## Result

**Status: `PARTIAL_LOCAL_ONLY_ANALYSIS`.** The 186-test regression receipt reports a clean pass. Four genuine Qwen-generated local episodes were recorded with **8 executed tool calls**, and their AURA verdicts were **PASS, FAIL, FAIL, FAIL**. In all four saved cases, the independently reconstructed task result agrees with AURA and the harness reference. Sample is far too small to establish accuracy or generalization; all four episodes reuse the same locally authored task contract.

**AppWorld: no native task was executed or scored.** Version 5 resolved the earlier `ensurepip` setup failure, but now stops at the `check_native_appworld_import_and_dev_index` preflight. `appworld_setup_status.json` shows exit code 1, but the ZIP deliberately excludes the underlying Python traceback; therefore the root cause **cannot be determined from this ZIP alone**. Do not assume it is a data-download or Python-version issue without seeing the traceback.

## Integrity and reproducibility

- Archive contains **58 ZIP members**, of which **56** are SHA-256 manifest entries; remaining entries are README and manifest. All hash/size checks and ZIP CRC checks passed.
- Model environment receipt: **Tesla T4**, Python 3.13.15, PyTorch 2.11.0+cu128, Transformers 4.57.6, `Qwen/Qwen2.5-3B-Instruct`, model ready. This is a self-reported runtime provenance receipt rather than cryptographic platform attestation.
- AURA version/source hash: `210d7c963aba647c436cba495da5e924062951082e1352fadd9ea8469cc94ff8`.
- All four saved per-run non-interference receipts say the verifier made no persistent changes, which also agrees with the archived audit status. These receipts are a bounded sandbox check, not proof of universal isolation.
- Both uploaded Kaggle ZIPs have the same 4 verdicts and the same 8 executed tool calls, despite different AppWorld setup failures; these are repeated seeded runs, not independent benchmark tasks.

## Local agent episodes

| Episode | Agent behavior and actual state | AURA | Independent reference |
|---|---|---|---|
| `01_direct` | Executed validation → update → report. Student 101 changed 70→85, other row unchanged, correct report persisted. | **PASS** | **completed** |
| `02_procedural` | Generated malformed concatenated JSON during 10 model turns; strict decoder executed zero tools. Student 101 stayed at 70; report absent. | **FAIL** | **not completed** |
| `03_silent_tool_noop` | Validated and called update tool, which deceptively responded `success` but left database at 70. Wrote report asserting 85; state mismatch detected. | **FAIL** | **not completed** |
| `04_denied_readback` | Updated student 101 to 85 and wrote report, but omitted required validation; database probe intentionally unavailable. Known process violation yields FAIL while two database obligations remain unknown. | **FAIL** | **not completed** |

The denied-readback run does **not** demonstrate successful verification under missing evidence alone: it also contains an independently established procedural failure. A separate deterministic preflight tests UNCERTAIN, but it is not an authentic LLM episode.

## CERA overhead

The recorded variable runtimes include planner-selection time plus marginal probe time but exclude common evidence snapshot acquisition and agent inference. They are short, one-machine pilot timings and should not support general speed claims.

| Episode | CERA probes | Greedy probes | Fixed probes | Exhaustive probes | CERA variable ms | Greedy variable ms |
|---|---:|---:|---:|---:|---:|---:|
| `01_direct` | 4 | 4 | 4 | 4 | 2.1072 | 1.0597 |
| `02_procedural` | 1 | 1 | 1 | 4 | 1.1575 | 0.0987 |
| `03_silent_tool_noop` | 1 | 1 | 1 | 4 | 1.1292 | 0.0772 |
| `04_denied_readback` | 3 | 3 | 4 | 4 | 2.5374 | 0.6699 |

CERA's planner overhead dominates in these four runs; it is not faster than the greedy policy in any recorded episode when selection time is included. This does not negate the earlier larger synthetic finding, which used different normalized modeled costs.

## Research validity and immediate next action

1. **Keep both uploaded ZIPs as valid local-pilot evidence** and mark Stage 8.1 external evaluation as unfinished.
2. **Get AppWorld's actual exception without rerunning the Qwen experiments:** in the original Kaggle v5 notebook session, scroll to *Cell 6 — Install AppWorld*, find the output for `check_native_appworld_import_and_dev_index`, and copy the traceback. If the session remains active, use the standalone diagnostic cell supplied alongside this report.
3. After diagnosing that precise error, adjust only the AppWorld setup/worker and run genuine native tasks with the official scorer. Do not infer AppWorld success from data installation alone.
4. For publication-level external AURA verification, a task-specific **AppWorld-to-AURA contract/evidence adapter** is still required. Official AppWorld scores by themselves are not independent AURA verdicts.
5. Capture original tool arguments in trusted traces in a future protocol revision; current trace `args` fields are empty although the separate `agent_turns.json` holds the parsed arguments. Do not overclaim trace completeness.

**Limits:** The ZIP includes no raw native AppWorld evidence and no AppWorld exception traceback, so no exact fix can be scientifically justified from this export. The local harness reference is independently implemented but shares the controlled simulator's assumptions. Four episodes and one task contract are not enough for statistical publication claims.
