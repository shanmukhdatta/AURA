# AURA Stage 8.1 Kaggle — Error analysis and corrected v2 execution guide

## Confirmed original error

The uploaded Kaggle log shows the following order:

1. **Cell 2** globally installed model/testing dependencies and then `appworld` into Kaggle's main Python 3.13 kernel. Pip printed several *environment compatibility warnings*, including Pydantic v1 conflicting with libraries requiring v2. A pip compatibility warning is not by itself evidence that AURA failed.
2. **Cell 3** executed `python -m pytest -q` and pytest auto-discovered unrelated third-party plugins from the shared environment.
3. During plugin import, `langsmith` tried to create a Pydantic model and raised `RuntimeError: no validator found for <class 'langsmith.schemas.BinaryIOLike'>`.
4. The notebook's later `AssertionError: AURA Stage 7 regression tests did not pass` was a **secondary consequence** of pytest crashing during startup, not evidence that any of AURA's 186 tests failed their assertions.

No genuine LLM or official AppWorld benchmark outcome was established by this failed run, which ended before those stages.

## Changes in the v2 notebook

- AURA tests run with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, so unrelated LangSmith/other Kaggle plugins cannot crash pytest collection.
- Official AppWorld is installed **only inside `/kaggle/working/aura_stage8_1_appworld_venv`**. No AppWorld dependencies are installed into the main notebook kernel. This prevents it from downgrading shared Pydantic, HTTPX, cryptography, and other packages.
- Track A still runs **the same unmodified Stage 7 AURA code**, verified by the same embedded SHA256; it independently probes SQLite/file state and computes contract-based certificates after real model-selected tool calls.
- Track B is run by a separate AppWorld subprocess. The already loaded Qwen model in the notebook supplies generated code through a JSON-line channel; official evaluator outputs remain isolated from the agent.
- A real AppWorld installation, data download, and official evaluator run are needed for native benchmark results. If these fail, Track B is marked **not executed** and the underlying error is logged.
- Final output archive retains model turns, traces, task certificates, native benchmark outcomes (when produced), fault metadata, manifest and failure reports.

## How to run (important: clean Kaggle kernel)

1. Import **`AURA_Stage8_1_Debug_Fixed_v2.ipynb` as a NEW Kaggle notebook**. Do not continue in the already modified Python kernel from the failed run.
2. Enable **Internet** and a supported **GPU**.
3. Execute all notebook cells in order. The AURA inherited tests should print `186 passed`; this is a code-regression check and **not an agent task-completion score**.
4. Review `EXPERIMENT_SUMMARY.json`: `track_a` contains real local agent run counts and verdicts; `track_b` shows how many *real official* AppWorld evaluator runs completed. Some AppWorld tasks may fail, and that is a legitimate result.
5. Download the file **`/kaggle/working/AURA_STAGE8_1_OUTPUTS.zip`** and share it here **privately**, along with any Kaggle cell exceptions if the run fails before the final export.

## Diagnostic files to keep

- `installation.txt` (main dependencies, isolated AppWorld pip/install/download commands, exit codes)
- `stage7_regression_test_output.txt` (actual AURA regression output)
- `appworld_preflight_error.txt` (if benchmark is unavailable)
- `appworld_worker_stderr.txt` and `appworld_worker_status.json` (isolated native benchmark worker)
- `track_A_llm_AURA/**` (LLM turns, trusted tool trace, before/after evidence, actual AURA certificates)
- `track_B_native_AppWorld/**` (native official results, when benchmark truly ran; NOT AURA certificates)
- `EXPERIMENT_SUMMARY.json` and `FILE_MANIFEST_SHA256.json`

## Validation performed before release of v2

- All notebook code cells parsed with Python AST.
- The exact Stage 7 implementation, **SHA256 `210d7c963aba647c436cba495da5e924062951082e1352fadd9ea8469cc94ff8`**, passed **186/186** tests locally with pytest plugin auto-loading disabled.
- The AppWorld process protocol was exercised with a **mock environment**, including two model-code requests, two task records, and no-action-control export. **This is only wiring validation, not an official AppWorld run**.
- Model weights, Kaggle GPU setup, native AppWorld installation/download, and genuine benchmark execution could **not** be validated from this offline runtime. Do not infer success from notebook syntax tests.

## Important scientific boundary

Track A uses AURA's actual contract verifier on genuine model-selected actions but *locally authored* sandbox tasks. Track B executes genuine AppWorld tasks and native evaluations but still does **not** produce independent AURA AppWorld task-completion certificates: the necessary app-specific AURA contract/probe translation remains unimplemented. Do not substitute an AppWorld official score for an AURA certificate or claim Stage 8.1 external validation completed until that gap has been addressed.
