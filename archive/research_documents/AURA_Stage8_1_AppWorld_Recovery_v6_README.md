# AURA Stage 8.1 — AppWorld-only Kaggle Recovery (v6)

## Decision

Use **this new notebook**, not v5. In a fresh Kaggle notebook, enable **Internet** and a GPU (T4 recommended), import the `.ipynb`, and select **Run All**. You do not need to rerun previously completed AURA local experiments.

`ENVIRONMENT_NOT_FOUND` indicates the temporary AppWorld environment from your *previous Kaggle session* no longer exists. It does **not** mean AURA's local verification failed.

## Why v6 exists

The original v5 notebook completed local AURA experiments, but stopped during `check_native_appworld_import_and_dev_index`. The result archive did not contain that Python exception, so we cannot yet know whether the fault was the interpreter, AppWorld import, or dataset index.

Version 6 therefore:

1. Creates a separate **managed Python 3.11 environment** with `uv`, without depending on Kaggle's `ensurepip`.
2. Installs and unpacks the public `appworld` package; downloads AppWorld official data.
3. Checks import and **dev task index separately**, preserving full stderr/stdout excerpts on failure.
4. Initializes an actual AppWorld task and runs the official evaluator in a **no-action preflight** (not an agent score).
5. Only if the benchmark is operational does it load `Qwen/Qwen2.5-3B-Instruct` and request real model-selected Python actions in three AppWorld *dev* tasks.
6. Exports one **minimal ZIP** with official summary scores, trajectory, API evidence and a failure traceback where relevant.

## Download from Kaggle

`/kaggle/working/AURA_APPWORLD_STAGE8_1_v6_RESULTS.zip`

Upload this file, **even if setup fails**. The ZIP contains `EXPERIMENT_SUMMARY.json`, and on installation failure includes `SETUP_DIAGNOSTIC.txt`. That is sufficient to diagnose the precise Python exception without redoing AURA's previous four local episodes.

## Readiness meanings

- `READY_FOR_EXTERNAL_NATIVE_BENCHMARK_ANALYSIS` — three model-driven AppWorld dev episodes with native evaluation and selected evidence records passed the notebook's export checks.
- `NOT_READY_APPWORLD_SETUP_ERROR` — benchmark setup or native evaluator preflight failed; read the diagnostic traceback.
- `NOT_READY_MODEL_ERROR` — AppWorld is operational but Qwen inference could not start.
- `PARTIAL_NATIVE_BENCHMARK` — some AppWorld episodes/evidence remain incomplete.
- `NOT_READY_MISSING_EXPORT_ARTIFACTS` — the required research evidence was missing at packaging.

Even the READY status **does not mean that the agent succeeded on all tasks or that AURA verified AppWorld itself**. AppWorld's evaluator is the official reference for its tasks. AURA's own independent contract/probe adapter to AppWorld remains unfinished. This is a **development-set pilot**, not a held-out leaderboard result.

## Exactly what the ZIP includes

- Configuration, step-by-step setup status, native preflight outcome, model/worker status, experiment summary.
- For executed tasks: agent-generated Python trajectory, native AppWorld official score summary and native API-call evidence.
- If any setup/model/worker stage failed: a bounded **error traceback** so the cause is no longer hidden.
- `FILE_MANIFEST.json` with every member's size and SHA256 digest.

It **does not** include source code or virtual environments, package installation output when setup succeeds, LLM weights, benchmark databases, hidden evaluator code, or full private AppWorld artifacts.

## Validation performed before handoff

- Notebook JSON schema validation with `nbformat` and compilation of all six code cells.
- Failure-path run simulating installation errors: archive generated, error preserved, no false benchmark success.
- Curated-export integration using three **mocked** native task records: archive manifest/hashes pass and unnecessary contents excluded.
- Direct three-task **mock worker roundtrip**: message exchange, fake code execution, and receipt/export paths work.

**Not performed here:** installing full AppWorld datasets or running Qwen inference in an actual Kaggle GPU environment. These operations remain for your Kaggle run and may uncover platform-specific issues. No real benchmark scores were generated in these tests.

## Official source

[AppWorld installation, tasks, and evaluator](https://github.com/StonyBrookNLP/appworld/blob/main/README.md).
