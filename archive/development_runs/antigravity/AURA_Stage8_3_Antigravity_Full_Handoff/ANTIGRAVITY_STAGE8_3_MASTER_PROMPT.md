# MASTER PROMPT — AURA Stage 8.3, for Google Antigravity

You are the engineer and independent replication auditor for AURA (Agent Uncertainty and Residue Arbiter). Work in this repository: https://github.com/shanmukhdatta/AURA. Your goal is **genuine, publishable-quality experimental evidence**, not apparent success. Build, run, verify, package and report the next stage, within tools and budget you actually have. Read `README.md`, `research/PROJECT_STATUS_AND_GATES.md`, existing source and artifacts before any implementation.

## Safety and integrity rules — non-negotiable
- NEVER invent scores, traces, test receipts, benchmark labels, timestamps, model calls, evaluator responses or proofs.
- NEVER present manually scripted oracle/fault trajectories as real LLM trajectories.
- NEVER present official AgentSynth outcomes or AppWorld scores as independent AURA certificates.
- NEVER score by feeding benchmark labels, oracle solutions or expected verdicts into the AURA verifier.
- DO NOT make arbitrary changes to original Stage 7 engine or overwrite historical evidence merely to make a benchmark pass. Any change needs a test, reason and diff.
- DO NOT commit API keys, tokens, cookies, personal data, third-party model weights, hidden evaluator files, large raw logs, or third-party proprietary materials.
- Record the exact source commit SHA, model identifier/revision, environment versions, task selection, temperatures, seeds, failure modes, and command outputs.
- If internet, GPU, a provider, or external data are unavailable, stop that experiment, create a diagnostic receipt, and continue feasible CPU tests. Mark `NOT_RUN` rather than fabricate success.
- Avoid public leaderboard submission and paid API calls without explicit authorization. Free/local model inference is preferred. Use GitHub feature branch + pull request; do not silently rewrite main.

## Phase 0 — audit baseline before implementing
1. Inspect repository structure, tests, last Stage 8.2 source/evidence and research report.
2. Run `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q AURA_Stage7/tests` and re-run Stage 8.2 experiment from a clean output path.
3. Verify evidence ZIP CRC, SHA256 manifests, certificate replay and 36/36 scoped control records; note which claims are not supported.
4. Save `stage83/results/00_baseline_audit.json` with exact commands, exit codes, test counts, Python versions, elapsed time, hashes and limitations.

## Phase 1 — official external benchmark and provenance
1. Clone `https://github.com/agentsynth/agentsynth` at a specific Git commit; record the commit SHA and its license. Pin installation dependencies in an isolated venv. Use the official `core_v2` pack (14 tasks) and its official CLI/native scorer; verify accepted command options against installed `agentsynth --help` instead of assuming.
2. Before model inference, run the **published oracle** using the OFFICIAL scorer and an official no-action control, capturing per-task outcome and stdout/stderr, raw result JSON and errors. Do not substitute the handwritten Stage 8.2 native-style SQL comparison.
3. Ingest upstream task specs by parsing YAML, avoiding hand transcription. Prepare list of verified supported and unsupported checker types; support scalar and multi-row SQL outcomes, tool-call and answer checks where warranted. Be explicit if a task cannot be evaluated under an AURA contract.
4. Define authorized-write scopes and task obligations independently and *before seeing agent outputs*, recording who/what authored each contract. Review authorizations manually for ambiguity. Freeze hashes of contracts and task selection.
5. Give independent AURA probe code access only to task/contract, trusted before/after state, and approved tool trace—not oracle labels or grader outcomes.

## Phase 2 — correct evidence-capture adapter
Implement `aura_external/agentsynth_runtime.py` (or similarly named narrowly scoped adapter):
- Connect the official AgentSynth SQL runtime to an *independent* SQLite snapshot reader, not to agent self-reports.
- Persist complete table schemas, primary keys, row/field changes, the task-scoped frame allowlist, epoch identity, traces (including parameters, tool return/failure and execution success).
- Ensure observation capture is read-only, consistent, and noninterfering. Include a test that runs AURA and proves DB hash is unchanged.
- Do NOT claim process compliance from terminal state alone; temporal event obligations require trusted ordered traces.
- Implement clear UNAVAILABLE -> UNCERTAIN behavior when evidence required for PASS is missing; known observed violation can establish FAIL even if another obligation is unknown.
- For valid tasks, replay AURA's certificates from immutable saved inputs; test deliberately tampered observation, forged coverage receipt, and mutated snapshot.
- If upstream runtime doesn't expose a reliable state path/snapshot, record a blocker and use documented instrumentation, not fake `independent` observations.
- Keep independently computed official/native labels sealed in separate `reference/` until after the AURA certificate is stored.

## Phase 3 — real external LLM episodes, progressive gates
A. Smoke (5 tasks): use a REAL LLM inference provider available under a free or approved local budget. Qwen2.5-3B-Instruct is a reasonable baseline, but test the official SQL tool schema and prompt carefully. NO mock-model fallback under the `real_llm` label. Run >=5 tasks, 1 seed each. Save every actual model-generated tool action and error.
B. Expanded: only if phase A passes; ideally all 14 `core_v2` tasks x 2-3 independent seeds/trials, depending on actual GPU/runtime constraints. Include appropriate different task tiers. Do not choose the best runs retrospectively. Report model success/failure and coverage per task/tier.
C. Alternative CPU-only option: obtain genuinely external **already-recorded** agent trajectories with independent outcome state from a documented source; do not infer completion from transcript-only records without state readback.
D. Use natural model failures as the main verifier evaluation set. Keep oracle, no-op, silent-noop, partial, unauthorized-extra and denied-readback controls in separate results and analysis. Distinguish all agent-generated vs injected examples.

## Phase 4 — evaluation, baselines and statistics
Produce per-episode:
`task_id, task_source_commit, model_id, seed, native_benchmark_result, contractual_ground_truth, aura_verdict, reference_coverage, reason, evidence_coverage, trace_provenance, false_pass, false_fail, uncertain, probes, bytes_read, planner_latency_ms, verifier_latency_ms, wall_seconds, execution_mode`.
Compute:
- native success, strict task+frame success, PASS/FAIL/UNCERTAIN confusion tables, false PASS count/rate with denominator, false FAIL, decisive coverage, abstention, condition-wise errors, and grouped-by-task bootstrap intervals if sample supports it;
- fair baseline matching the same contract/readback: simple full snapshot comparison / fixed probes / greedy or exhaustive as applicable;
- compare CERA only after actual objective and costs align across policies, include planner overhead. Do not use modeled cost numbers as empirical performance.
- report cases the native scorer passes but strict AURA contract fails as **policy-scope differences**, not bare verifier superiority.

## Phase 5 — deliver audit-ready artifact, README and pull request
Produce:
`stage83/results/config.json`, `environment.json`, `provenance.json`, `baseline_receipt.json`, `official_scorer_raw.json`, `task_contracts/`, `episodes/<task>/<run>/` (prompt, model actions, full trace, read-only before/after snapshots, observations, AURA certificate, official reference, independent contract check), `metrics.csv`, `failure_analysis.md`, `study_report.md`, `SHA256SUMS.json`, and `AURA_STAGE8_3_RESULTS.zip`.
Run tests and ZIP CRC/hash audit. Do not add models, secrets, or hidden official evaluator ground truth to a public repo. Public repo should contain minimal/redacted representative evidence and a reproducible script/manifest; keep bulky raw results as an explicitly linked user-controlled artifact.
Use a new branch `experiment/stage-8-3-external-llm-verification` and open a PR; **do not force push or merge without approval**.
At the end, return an evidence table with: exact executed commands, outcomes, task counts, model and source revisions, working links, warnings, what remains unverified, reproducibility instructions, PR/commit URL, and the results ZIP location.

## Stop/go checks
- G0: inherited 186 tests and prior experiment replay PASS.
- G1: official AgentSynth scorer callable, core_v2 tasks accessible, native controls saved with raw evidence.
- G2: adapter emits correct replayable AURA certificate for at least one actual external SQL task; noninterference PASS, denial -> UNCERTAIN, corruption rejected.
- G3: real LLM generates actual tool calls, not mock or oracle transcripts, on at least five tasks; provenance preserved.
- G4: predefined experiment runs and independently assessed metrics, with no label leakage and matched-contract baselines.
- If blocked, stop at the failing gate and deliver a precise error, completed receipts, and a minimal next-step fix. Do not rewrite history or invent G4 success.

## Resource strategy
Do CPU-first tests and the official scorer in your local environment. Use Kaggle GPU only if actual model inference can't run locally. If building Kaggle notebook, ensure only `stage83` experiments run, not old AppWorld loops; verify dependencies are isolated; capture first failure traceback; always export partial evidence and runnable commands. No paid API use without consent.

## Communication
Produce a concise `STATUS.md` at the end of each completed gate: what's run, evidenced results, blockers, and the exact next command. Do not describe work not actually done as completed. Start Phase 0 immediately; ask questions only when genuinely blocked by missing private access or authorization.
