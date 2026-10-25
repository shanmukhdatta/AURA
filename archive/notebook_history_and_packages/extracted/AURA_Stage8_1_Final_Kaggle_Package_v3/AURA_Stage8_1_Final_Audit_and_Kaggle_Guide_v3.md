# AURA Stage 8.1 — Final audited Kaggle notebook (v3)

**Notebook:** `AURA_Stage8_1_Kaggle_FINAL_Audited_v3.ipynb`  
**Notebook SHA256:** `fb6dbf6e0c0adfde21139c5110eadad746bb0de9364b5639f3c333e1a58396a5`  
**AURA Stage 7 source SHA256 embedded and checked:** `210d7c963aba647c436cba495da5e924062951082e1352fadd9ea8469cc94ff8`

## Three audit conditions

### 1. Execution, errors, and non-interference

- The embedded AURA Stage 7 code is SHA256-checked before execution. Its 186 inherited regression tests are run with external pytest plugin autoload disabled.
- A separate four-case, **scripted** operational preflight checks the actual AURA engine's PASS / FAIL / UNCERTAIN decisions. These are not counted as LLM research results.
- The real Qwen model is run on Kaggle when GPU and network are available. The main notebook does not install AppWorld in the main Python environment. AppWorld runs in a fresh, isolated Python virtual environment and a JSON-lines worker subprocess.
- The notebook records main-environment package versions before/after the AppWorld phase and checks whether AppWorld was imported into the main notebook process.
- For each completed local episode, a new SQLite and filesystem readback after verification/policy inspections must match the frozen terminal snapshot. This tests for verifier interference within **declared local surfaces**, not arbitrary host or external side effects.
- If the model, official environment, or evaluator cannot run, the phase is marked incomplete. No missing phase is converted to a fabricated success score.

### 2. Correctness of results and ZIP contents

- Local agent decisions are inspected using the **unchanged** AURA verifier. A separately written controlled-sandbox reference checks the actual SQLite rows, saved report, permitted files, and trusted validation-before-update condition.
- Every completed local run exports the raw model-selected tool trajectory, certificate, validated probe observations, before/after JSON snapshots, trusted tool trace, run manifest, and independent reference. Report text is exported only when the report exists. A small policy summary is retained.
- A SHA256-verified `FILE_MANIFEST_SHA256.json` describes every file in the exported ZIP. The ZIP is opened again and every member hash and size are checked against the manifest.
- The AppWorld track exports each task's model-generated code trajectory, **sanitized** official native evaluation summary (counts and success, not hidden test bodies), native API calls (when present and <=8 MB), evidence availability receipt, task status, and no-agent baseline summary. **These are AppWorld scores, not AURA task certificates.**
- ZIP contents are **strictly allowlisted**. Model weights, virtualenvs, embedded source archive, AppWorld raw databases, official ground-truth evaluator internals, temporary worker scripts, setup logs, and full traceback dumps are excluded. Temporary working directories are outside `/kaggle/working`.
- Only **one deliverable ZIP** is intentionally created in Kaggle's saved working directory: `/kaggle/working/AURA_STAGE8_1_OUTPUTS.zip`.

### 3. Is this sufficient to proceed?

**Sufficient for Stage 8.1 pilot analysis if the ZIP's `EXPERIMENT_SUMMARY.json` reports `READY_FOR_PILOT_ANALYSIS` and the audits show no issues.** This indicates the planned four local runs and three native external developer tasks were independently captured and could be examined. Model success rates may legitimately be zero.

**Not sufficient for final publication-level external AURA verification.** The current external AppWorld adapter executes true benchmark workloads and obtains its official scores, but it does not yet translate AppWorld-specific task requirements and state evidence into independent AURA certificates. Stage 8.1's larger external-verification objective therefore remains open. Four local episodes and three dev tasks also cannot establish broad comparative accuracy or statistical generalization.

## What was run *here*, before Kaggle

- Extracted the original Stage 7 source in a clean directory and ran its 186 regression tests: **186 passed**.
- Executed four scripted local sandbox tool sequences through AURA: expected **PASS, PASS, FAIL, UNCERTAIN**, with exact matching actual results.
- Executed four separate scripted smoke cases (clean, missing report, unauthorized change, denied readback): **4/4 expected verdicts**.
- Ran an AppWorld **mock worker**, not the official AppWorld environment, to test JSON-line communication, code trajectory recording, API-log extraction, and sanitized evaluation serialization. The mocked worker completed three tasks.
- Exercised the full result ZIP builder using mock outputs: **79 file entries**, approximately **39 KB**, and the complete SHA256 manifest checked out.
- Deliberately changed a failed certificate into a PASS: audit correctly flagged `FALSE_PASS_VS_INDEPENDENT_REFERENCE` and set readiness to `NOT_READY_REVIEW_AUDIT_ERRORS`.
- All notebook Python cells compile; all notebook outputs and execution counts are empty. **Neither the actual model checkpoint nor the true AppWorld task environment was run in this sandbox.** Real Kaggle compatibility, model capabilities and official benchmark results remain unknown until your run.

## Running in Kaggle

1. Create a **fresh** Kaggle notebook, import `AURA_Stage8_1_Kaggle_FINAL_Audited_v3.ipynb` and choose Python 3.
2. Enable **Internet** and a **GPU**. The model is `Qwen/Qwen2.5-3B-Instruct`. No paid API is needed; it downloads model weights on first run.
3. Run All. Read `MODEL_READY`, the four operational preflight decisions, and the printed final `STAGE 8.1 FINAL READINESS` label.
4. Locate `/kaggle/working/AURA_STAGE8_1_OUTPUTS.zip` under Kaggle output files. **Download that ZIP only**, then upload it here for analysis. Do not share extracted AppWorld task data publicly; review any personal-like seeded text in trajectories before posting elsewhere.
5. If the notebook fails before export, send the traceback at the point of failure. If it completes with a partial or NOT_READY status, send the ZIP anyway; it explains exactly which evidence is missing.

### How to interpret final status

- `READY_FOR_PILOT_ANALYSIS`: local AURA evidence audit passed and all planned native AppWorld evaluations plus no-op controls are available; **still no independent AppWorld AURA certificates**.
- `PARTIAL_LOCAL_ONLY_ANALYSIS`: local AURA runs passed audit, but native AppWorld completion was unavailable or incomplete.
- `NOT_READY_INCOMPLETE`: model actions or local runs did not meet minimum execution requirements.
- `NOT_READY_REVIEW_AUDIT_ERRORS`: a decisive disagreement, malformed evidence, or main-kernel isolation problem occurred.
- `NOT_READY_MISSING_REQUIRED_FILES`: the exporter could not find one or more required files.

**Research caution:** Check which local trials had deliberate `silent_noop` or `deny_readback` faults before calculating any unmodified-agent success rate. Do not treat the four scripted preflight cases or simulated AppWorld worker tests performed during notebook development as agent research outcomes.
