# AURA Stage 8.1 — v5 Kaggle AppWorld Retry Guide

## Why this notebook supersedes v4

Your real v4 Kaggle output is valid as a **local-agent pilot**: four model runs, eight tool calls, four audited AURA certificates, and 186 passing regressions. It is **not** a completed external benchmark experiment. AppWorld did not initialize because Kaggle's Python failed at `ensurepip` during virtual environment setup. The notebook properly reported `PARTIAL_LOCAL_ONLY_ANALYSIS` and exported no invented AppWorld scores.

v5 **changes only the AppWorld environment setup and its minimal error-status receipt**. The original Stage 7 source ZIP remains unchanged. The model, test tasks, task contract, verification policies and strict local-agent JSON decoding remain unchanged. The experiment name and notebook revision are updated so this rerun is distinguishable from v4.

## What was tested before giving you v5

- The v5 `.ipynb` passes Notebook v4 schema validation; every Python code cell compiles. All notebook cell outputs are empty (no simulated results embedded).
- The unchanged Stage 7 code passes 186/186 pytest cases in a clean extract.
- `uv venv` created an isolated Python 3.13 environment **without pip**. A tiny locally created wheel was then successfully installed using `uv pip install --python <isolated_python>` despite `pip` and `ensurepip` not being present inside the environment.
- The local mock agent + mock AppWorld end-to-end export produced a valid allowlisted ZIP and reached the pilot-readiness gate. Mock results are only engineering tests and are **not** empirical agent performance.
- A deliberately corrupted AURA certificate was rejected (`NOT_READY_REVIEW_AUDIT_ERRORS`). A simulated isolated package-install failure preserved local results and recorded the exact setup stage as incomplete.
- A genuine AppWorld package install/download **was not verified locally**: this sandbox cannot resolve `pypi.org`. The Kaggle environment must provide the public downloads and native AppWorld execution.

## Kaggle steps

1. Import `AURA_Stage8_1_Kaggle_AppWorld_UV_Fix_v5.ipynb` into a **new Kaggle notebook** (fresh Python process) rather than resuming the previous notebook after its failed environment setup.
2. Enable **GPU** and **Internet**. This notebook performs **inference/evaluation**, not training.
3. Run the full notebook from the beginning. Allow AppWorld's package and task-data installation to finish if Kaggle permits them.
4. Check the last printed `STAGE 8.1 FINAL READINESS` status. The notebook generates only the curated `/kaggle/working/AURA_STAGE8_1_OUTPUTS.zip` file, which you can share here.
5. If native setup fails again, share the ZIP **and the text printed at Cell 6**. `EXPERIMENT_SUMMARY.json` now includes `appworld_setup_phase`; the ZIP includes one concise `appworld_setup_status.json`, not raw installation logs or environments.

## What indicates valid external execution?

A true AppWorld pilot should contain three `track_B/<task_id>/` records with official evaluation summaries, model code trajectories, native API-call JSONL evidence and completeness receipts, plus three no-agent-control summaries. The status `READY_FOR_PILOT_ANALYSIS` requires these evidence checks as well as the four local model episodes.

Even a fully completed AppWorld pilot does **not** mean AURA scored native AppWorld tasks. That requires a new AppWorld-to-AURA contract/evidence adapter. Do not cite native AppWorld task scores as AURA verification accuracy.

## Retain original evidence

Keep the original v4 `AURA_STAGE8_1_OUTPUTS.zip` unchanged for audit and comparison. The v5 run is a new experiment, potentially with different model outputs despite fixed inference settings. Avoid pooling its four local episodes with v4 as if they were independent held-out benchmarks.
