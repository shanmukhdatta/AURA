# AURA Stage 8.3 — Independent audit and mandatory corrections

**Audit date:** 2026-10-25  
**Uploaded artifact:** `AURA_STAGE8_3_RESULTS.zip`  
**Reported SHA256:** `46e7901f05e87da1d615ed257c5ea90144439b76df2dfc43df5458e6dba98cf1`  
**Research disposition:** G0/G1 supported by saved receipts; G2/G3 provide meaningful prototype evidence; **G4 is NOT ACCEPTED; G5 archive packaged but final claims require repair**. Do not merge the branch or run the current Kaggle expansion notebook yet.

## 1. Reproducible findings from the provided ZIP

- ZIP contains **155 entries**; ZIP CRC check passed.
- **139/139** SHA256-manifested files match the saved `stage83/results/SHA256SUMS.json`.
- All **five** saved AURA certificates were independently replayed through the **actual AURA Stage 7 `aura_verifier.engine.verify`** from the historical recovery package, with real saved snapshot pairs, contract, probes and observations. In all five cases, verdict, obligation results, evidence references, inspection IDs, reasons, and verified-frame surfaces matched the archived certificate. This verifies deterministic replay of recorded evidence; it does **not** cryptographically prove the LLM originally produced the actions.
- Each of the five archived SQLite database binaries was opened independently. Every saved `after_snapshot.json` table/row state matches the database contents. Observed genuine-cohort trace counts: `raise-ticket-priority` 1 SQL call, `refuse-cancel-shipped` 1, `clearance-discount` 1, `dedup-keep-latest` 4 (all errored), `refund-and-restock` 3.
- Saved model ID is `Qwen/Qwen2.5-0.5B-Instruct` running on CPU with seed 42. No independently reproduced model inference occurred in this audit; model action logs and tool traces were internally consistent.
- The official *published-oracle/no-op G1 CLI benchmark* receipts are present for 14 tasks: 14/14 and 0/14, respectively. The five actual model trials **do not have equivalent CLI-runner grade receipts**.

## 2. Corrected empirical result table (five saved model episodes)

| Task | Saved AURA | Local reproduced SQL outcome (NOT full official score) | Interpretation |
|---|---|---|---|
| `raise-ticket-priority` | PASS | 1.0 | State and AURA certificate consistent; one actual update |
| `refuse-cancel-shipped` | FAIL | 1.0 | **Scoring/reference mismatch**; SQL state-only score omits required answer/tool checks; contract's exact-answer rule is not a faithful rendition of the task |
| `clearance-discount` | FAIL | 0.6667 | Agent calculated a discount via SELECT but did not persist the price change |
| `dedup-keep-latest` | FAIL | 0.0 | Four erroneous SQL attempts; no valid deduplication |
| `refund-and-restock` | FAIL | 0.25 | Agent deleted order 5 instead of refunding; inventory not restored |

Thus: recorded AURA verdicts are **1 PASS, 4 FAIL**, and the **local SQL-only** full-pass count is **2/5**. Antigravity reported "1/5 official task successes," which contradicts its saved `official_native_passed` flags and is not established by official five-task runner records. Do NOT publish an 'official 1/5' or 'official 2/5' rate until the original scorer is executed against the five actual model actions and final answers. If the official runner cannot import already executed actions, label the outcomes **reproduced SQL-only**, not **official**.

The `refuse-cancel-shipped` saved model final response includes an incorrect policy interpretation (suggests cancelling if shipped) while containing the word `shipped`. This demonstrates that a substring-based benchmark condition can be gameable. AURA's contract, however, uses `answer.text_2 eq 'shipped'`, which is an unjustified exact-match requirement for a natural-language refusal. Correct both the reference and the contract; do not call the resulting mismatch proof of general AURA superiority.

## 3. Mandatory analysis fixes

### A. G4 has at least one internally acknowledged disagreement

`stage83/results/g4_metrics.csv` contains one row marked `false_FAIL=True` for `refuse-cancel-shipped`. The separate `g4_mismatch_analysis.md` says "False FAIL Count: 1 (0.0%)"; G4 status and master report say zero. This is a factual inconsistency. The existing `independent_contract_reference.json` for that task says PASS because it checks SQL and frame only, and omits the answer/process obligations that AURA evaluated. This is *not* an equally scoped reference. Until the independent reference implements the **identical frozen contract semantics** and the answer rule is corrected, report the five-task strict-contract false-FAIL rate **not established**, not 0/5 and not 1/5.

### B. Reference labels and cohort separation are wrong in G4 CSV

The 36 historical scripted control rows in `g4_metrics.csv` have placeholder task IDs (`__`), missing `strict_reference`, and fixed synthetic values for byte counts, execution time and planning time. These are **not measurements** of these runs. The CSV marks all 36 as no false positives/negatives despite blank references. Restore actual rows from the original Stage 8.2 evidence, or exclude this cohort from scored Stage 8.3 error rates. Never use **41** as the denominator for a new real-LLM accuracy claim. The real-LLM population is **N=5 tasks, one seed**.

### C. Five-task 'official' outcomes are only SQL-only reconstructed checks

The Stage 8.3 adapter's `evaluate_native_checkers()` evaluates only `kind == 'sql'`. It skips published `called_tool` and `answer` checkers. Its score is then stored as `native_score`, and the run report presents it as official. Official AgentSynth CLI **was** used for G1 oracle/no-op; that does not prove G3 real-model evaluation used the CLI. Keep separately labeled artifacts: `original_agent_synth_official_result`, `reproduced_sql_only_score`, and `aura_contract_verdict`.

### D. Overlapping verifier and reference code are not independent

In `AgentSynthAuraAdapter.run_aura_verification()`, the reproduced upstream SQL checker results are computed before the AURA certificate, and the same observed SQL queries are projected into AURA facts. Even if the `matched` booleans are not supplied directly, the resulting reference is not fully code-independent. Implement a **separate, blinded, matched-contract ground-truth checker** that evaluates saved world state, trace, answer and allowed edits *after the AURA certificate has been frozen*, ideally with a different code path and test suite.

### E. CERA-cost claims need dimensional and population fixes

The saved G4 comparison uses four modeled planning domains and `64` cases per policy. Its report also calls this `120 total worlds`, which needs source-supported clarification. The G4 CSV calculates `total_effective_cost` by adding **abstract probe-cost units** to **milliseconds of planner latency** without a declared conversion. That sum is dimensionally invalid as a wall-time estimate. It also shows CERA and greedy both at **1.88 average probes / 3.25 units**, while CERA has higher average planner overhead (**0.3621 ms vs 0.0710 ms**). Hence **no CERA advantage over greedy is demonstrated** by these data. Report probe units and planner milliseconds separately unless both are calibrated to a common measurement unit; disclose modeled vs actual I/O. The suggested high-latency break-even threshold is not directly measured here.

### F. Existing Kaggle expansion notebook should not be run unchanged

`AURA_STAGE83_REAL_AGENT_KAGGLE.ipynb` is syntactically valid (six cells, five code cells). However it:
- Defaults to **14 tasks × one fixed seed**, not the advertised **14 × three seeds**.
- Re-implements a simplified SQLite execution environment, not the full upstream AgentSynth evaluator.
- Does **not import or call AURA**; issues **zero AURA certificates**.
- Saves before/after **raw SHA256 digests**, not full independent before/after snapshots and task contracts; omits official/native grading, independent contract references, certificate replay and noninterference audits.
- Installs packages in the Kaggle global Python environment (risk of Python/dependency interference).

Running it would yield agent trajectory data, **not the required Stage 8.3 verification evidence**. Correct the notebook, dry-run on two tasks, validate ZIP evidence and only then expand.

## 4. GitHub and PR

- Feature branch **exists**: `experiment/stage-8-3-external-llm-verification` in `https://github.com/shanmukhdatta/AURA`.
- Supplied URL `https://github.com/shanmukhdatta/AURA/pull/new/experiment/stage-8-3-external-llm-verification` is a **create-PR page**, not an existing pull request number. GitHub issue/PR search returned **no pull requests** at audit time. No merge or changes have been made by this independent audit.
- Open a **draft PR** only after the status/results documentation is corrected; keep main untouched until reviewed.

## 5. What to ask Antigravity to return next

Use this as the operative instruction:

> **AURA Stage 8.3 corrective audit — no fresh GPU run yet.** Read this entire file and inspect `AURA_STAGE8_3_RESULTS.zip` and the pushed branch. Fix the G4 reference/scoring inconsistencies, do not rewrite existing evidence, and implement a genuine independent strict-contract scorer for the five already saved model executions. Separate original AgentSynth runner results from reconstructed SQL-only checks and AURA certificates. Correct natural-language refusal semantics, with tests showing both justified acceptance and rejection. Recover true Stage 8.2 control task IDs/references/costs from historical evidence rather than inserting placeholders; report missing measurements as missing. Fix the CERA cost units, world-count denominator and misleading superiority claims. Run all inherited tests and add adversarial tests for incorrect task acceptance, false PASS, false FAIL, missing evidence and data tampering. Prepare a **separate** corrected Kaggle notebook that produces genuine model tool traces, actual independent SQL snapshots, verified AURA certificates, reference scores, repeat seeds and complete export, without rerunning old stages. Test its two-task smoke and ZIP manifest before recommending the 14-task GPU expansion. Keep previous results immutable, record a correction changelog, push changes to a feature branch, and create a **draft PR** (no merge). Do not claim Stage 8.3 complete until the saved five episodes have honest comparable scores and the research report is internally consistent.

**Required deliverables:**
1. `AURA_STAGE83_CORRECTED_AUDIT.md`: per-episode trace evidence, clarified full native vs SQL-only vs strict-reference definitions, corrected cohort denominators and all metric discrepancies.
2. `stage83/results/g4_metrics_corrected.csv` and `stage83/results/g4_cost_corrected.csv`: computed from original data; no hardcoded fabricated measurements.
3. `stage83/results/strict_contract_independent_reference.json`: fresh independent review of outcome + trace + answer + side effects for five tasks, with written reason per verdict and contract-hash provenance.
4. `stage83/tests/test_independent_reference.py` plus original 186 regression-suite receipt and new negative tests.
5. `AURA_STAGE83_CORRECTED_RESULTS.zip` with SHA256 manifest, source revisions, actual trace/snapshot/certificate data and audit receipts, excluding secrets and big model weights.
6. Updated `AURA_STAGE83_REAL_AGENT_KAGGLE_v2.ipynb` with 2-task preflight, 14 × 3 as an opt-in after preflight, fully valid AURA adapter and CPU/GPU environments, fail-closed diagnostics and final ZIP even on partial failure.
7. **Actual draft PR URL** with a numbered `/pull/<number>` link and commit SHA (or `NOT_CREATED` with specific error), no merge.
8. An explicit `STATUS.md` table with executed vs blocked vs untested tasks; list the exact commands, exit codes, known limitations, and smallest next step.

**Research next-stage gate:** accept Stage 8.3 only after an independent checker of equal contractual strength evaluates the saved real-LLM episodes *without using AURA output as an input*, and metrics are recomputed from that fresh reference. If the model's output semantically contradicts the user request but published/native substring tests pass, report an evaluator weakness and document the justified stricter policy, rather than relying on an arbitrary exact-answer rule.
