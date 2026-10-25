# AURA — Stage 8.1 Kaggle pilot: Run guide and research protocol

**Status when delivered:** Notebook authored and syntax checked. Embedded AURA Stage 7 SHA-256 checked. All **186 Stage 7 regression tests** passed locally. A **wiring-only dry run using fixed test tool calls** demonstrated the expected local PASS / FAIL / UNCERTAIN paths; this is **not** an LLM test result. **Actual Kaggle model execution and actual native AppWorld task execution are not yet performed**. Your Kaggle run is needed to produce those results.

## What the notebook tests

### Track A: Real LLM-driven tasks + real AURA verification

- Downloads and runs `Qwen/Qwen2.5-3B-Instruct` locally (free public model; GPU recommended).
- The LLM sees a user instruction and registered tools. It chooses **actual tool calls** rather than replaying scripted reference solutions.
- Calls modify real isolated SQLite records and report files through the AURA sandbox.
- AURA's existing Stage 7 capture/probe/verifier implementation independently checks `S₀`, `Sₜ`, persistent diffs, tool trace, required facts, and frame coverage.
- Each episode outputs: model messages, tool invocations, trusted snapshots, observations, conservative AURA certificate, four inspection-policy summaries, and an **after-the-run withheld harness outcome**.
- Four default episodes: two unmodified task prompts, one declared simulated lying tool (silent no-op), and one simulated authoritative-readback denial. This intentionally mixes *natural model outcomes* with *injected tool conditions*, labeled separately in metadata.
- A `PASS` means only the predeclared local `TaskContract` requirements were established; it does not guarantee all unlisted requirements or every transient change.

### Track B: Real published external AppWorld benchmark

- Installs native [`appworld`](https://github.com/StonyBrookNLP/appworld), runs `appworld install` and `appworld download data`.
- Uses the **first three published `dev` task IDs in official dataset order**, no result-based selection.
- Gives only task instructions, app descriptions and available API documentation to the LLM; **never** ground truth, solution code, or evaluator labels.
- The LLM writes its own Python code to use AppWorld sandbox API calls via `world.execute(...)`.
- AppWorld's own evaluator runs **after** the model's final action. The notebook archives the original evaluator dictionary, agent-generated code, official API logs, official persisted state-difference records, and native version metadata if available.
- Runs a separate **no-agent-action baseline** using fresh task environments for the same task IDs; preserves its official evaluations.
- The notebook creates an evidence inventory and explicitly reports `AURA_external_task_verdict = UNCERTAIN` because the current AURA Stage 7 code does **not** implement a task-specific AppWorld contract/probe adapter. AppWorld's evaluator score is **not** counted as AURA's independent score.
- A handful of `dev` tasks is a **pilot** only, not a held-out leaderboard score or a statistically powered comparison.

## How to run

1. Open Kaggle → **New Notebook** → **File / Import Notebook** → upload `AURA_Stage8_1_Real_Agent_Evaluation_Kaggle.ipynb`.
2. In Notebook Settings, select **GPU** (T4/P100 or compatible). Enable **Internet** for Python packages, model weights and official AppWorld data.
3. Click **Run All**. A one-time benchmark download can require a working Kaggle network connection and sufficient disk space. The notebook will record failures rather than invent results.
4. Find `/kaggle/working/AURA_STAGE8_1_OUTPUTS.zip` in Kaggle's **Output** pane. Download the complete ZIP.
5. Upload that **entire ZIP to ChatGPT**, without editing `EXPERIMENT_SUMMARY.json`, `FILE_MANIFEST_SHA256.json`, certificates, or logs. Also report if Kaggle displayed dependency/install errors or memory errors.
6. Do **not** share private AppWorld seed-world dumps or its protected evaluation code in a public GitHub repo; AppWorld requests that extracted bundled data/code not be published. Let us first analyze what is safe to release.

## Which files to examine afterward

- `EXPERIMENT_SUMMARY.json`: whether each phase truly executed and how many runs were evaluated.
- `track_A_llm_AURA/summary.csv`: actual model actions, AURA decisions, independently measured local task outcomes and failure modes.
- `track_A_llm_AURA/<episode>/aura_certificate_conservative.json`: obligation-by-obligation evidence-backed decision.
- `track_A_llm_AURA/<episode>/agent_turns.json`: the model's exact outputs and tool responses.
- `track_A_llm_AURA/<episode>/sandbox/evidence`: before/after captures and trusted execution trace.
- `track_A_llm_AURA/<episode>/policy_summary.json`: inspection selection and measured costs (four baseline/CERA methods).
- `track_B_native_AppWorld/summary.csv`: official native benchmark status and completion signals (not AURA certificates).
- `track_B_native_AppWorld/<task>/official_appworld_evaluation.json`: original native evaluator result.
- `track_B_native_AppWorld/<task>/official_artifacts`: native API logs/state deltas if created by the installed version.
- `track_B_native_AppWorld/<task>/AURA_external_evidence_inventory_NOT_CERTIFICATE.json`: scoped evidence inventory and explicit certification boundary.
- `track_B_native_AppWorld/no_op_controls.json`: official no-agent control results.
- `FILE_MANIFEST_SHA256.json`: integrity checks for all exported files.

## Before making research claims

We must check how many *actual* LLM tool calls occurred, inspect the native AppWorld API logs and evaluator reports, separate fault injections from spontaneous errors, check false PASS and false FAIL against the independent local reference, analyze UNCERTAIN results, account for planning and evidence-capture costs, and report the small sample size. AppWorld score should not be substituted for AURA's own task-contract verification. For full Stage 8.1 external verification, a **separate trustworthy adapter** mapping AppWorld task requirements to AURA obligations and native state/trace probes must be built and validated. This notebook is the first genuine execution and evidence-collection pilot, not a finished end-to-end AURA-on-AppWorld benchmark.

**Primary references:** [AppWorld official repo](https://github.com/StonyBrookNLP/appworld); [Agent-Diff official repo](https://github.com/agent-diff-bench/agent-diff); [AURA Stage 7 project](https://github.com/shanmukhdatta/AURA).
