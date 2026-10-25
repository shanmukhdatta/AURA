# Antigravity master prompt — AURA Stage 8.3

You are implementing and independently auditing Stage 8.3 of AURA (Agent Uncertainty and Residue Arbiter) in this repo. Start by reading `README.md` and `research/PROJECT_STATUS_AND_GATES.md`. The aim is honest external AI-agent outcome verification, not a successful-looking notebook.

## Never violate these rules

1. Never fabricate results, tests, model outputs, metrics, GitHub commits, evidence or external scorer judgments.
2. Never call scripted oracle/fault injections real LLM failures. Never call AppWorld native evaluations AURA certificates.
3. Never give AURA the published expected verdict, hidden labels, scorer success flags or oracle solution when constructing independent verification observations. Freeze contract rules before evaluation.
4. If evidence is missing, return UNCERTAIN rather than manufacturing an observation or complete-coverage claim.
5. Do not silently alter Stage 7 verifier code or past results to get a passing score. Any fix requires a separate regression test and documented change.
6. Use only a free/local approved model for inference; do not spend on an API, submit to a public leaderboard, push to main or merge without user authorization.
7. Never commit secrets, private data, access tokens, raw hidden benchmark evaluators, model weights or private service responses. Publish sanitized evidence only.
8. If a gate is blocked, record the exact error and deliver the available receipts. Do not claim later gates completed.

## Stage 8.3 execution plan

**G0 — baseline reproduction.** Inspect the repository and accompanying AURA Stage 8.3 handoff ZIP if provided; extract source into an isolated workspace as needed. Install `jsonschema pytest`. Run `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q AURA_Stage7/tests`, then `python stage82_agentsynth_pilot.py --out stage82_fresh --zip` in a fresh output path. Verify hashes, 36 certificate records and results. Record exact commands, exit status, wall times, relevant package versions.

**G1 — benchmark.** Clone `https://github.com/agentsynth/agentsynth`, pin and record its current actual Git commit, read its MIT license and README, install in isolated venv. Run `agentsynth --help` first to discover exact supported CLI syntax. Parse the full 14-task `core_v2` YAML rather than manually retyping fixtures. Run official scorer with original oracle and a no-op control, save native JSON/raw logs. Do not substitute the Stage 8.2 internal SQL predicate comparator for official scoring. Verify which tasks need answer/tool-event checks and classify unsupported ones.

**G2 — independent state/trace adapter.** Predeclare each task's outcomes and row/field write allowances BEFORE model episodes; freeze hashes. Implement an adapter using AURA's real certificate engine, independent read-only snapshot of the exact official AgentSynth SQL world, trusted ordered trace, and complete table/row/field diff. AURA may inspect task/contract and observed before/after states, not official score/ground truth. Never infer process requirements from final-state diff alone. Save full probe observations/certificates for each episode, replay and test noninterference. Include negative tests for forged observation digests, forged coverage receipts and corrupted snapshots.

**G3 — genuine LLM run.** First run five official external tasks using real model inference (suggest Qwen2.5-3B-Instruct if accessible), correct tools and documentation, fixed configuration/seeds. NOT mock; save all prompts, actual agent output, arguments, SQL calls, tool responses, errors, final state, model/revision. If it works, expand toward all 14 tasks and 2–3 preregistered seeds/trials subject to actual resources. Save original native benchmark score separately. Keep scripted oracle, no-op, fault controls in a separate cohort from genuine model failures.

**G4 — fair analysis and cost.** Save AURA predictions before looking at official labels. Compare native success against the native evaluator; compare strict task+frame outcomes against an equal-policy full-snapshot baseline with the *same* allowed effects. Report PASS/FAIL/UNCERTAIN, false PASS/FAIL, abstention, decisive coverage, per-task tier, denominators, missing evidence, raw timings and bytes read. Evaluate CERA/fixed/greedy/exhaustive only with identical available probes and include planning overhead. Report negative or inconclusive results clearly.

**G5 — delivery.** Produce `stage83/results/` with config, pin hashes, environment receipt, official scorer raw results, task contracts, per-episode before/after snapshots, traces, observations, AURA certificates, official score, mismatch table, CERA cost if measured, tests, report, SHA256 manifest, and final ZIP. Write `STATUS.md` after each gate describing exactly what is done. Create feature branch `experiment/stage-8-3-external-llm-verification` and PR (no merge). Show final PR link, ZIP path, commands, all failures and scientific limitations.

**Resource rule:** CPU and official benchmark first. Use Kaggle GPU only if genuine LLM inference cannot run locally. Produce a separate small Kaggle notebook for just the real LLM phase if needed; never repeat obsolete AppWorld setup or relabel mock performance as LLM evidence.

## Minimum completion condition

Stage 8.3 is **NOT COMPLETE** until (1) official external benchmark scores exist, (2) a real model generated agent actions on the external task, (3) independently captured persistent state/trace feeds AURA's actual verifier, (4) certificates replay and agree/disagree against an independent strict-contract reference, (5) limitations/abstentions and baselines are reported.

Begin with G0 and G1. If required source code is not in the remote GitHub repo, use the provided `AURA_Stage8_3_Antigravity_Full_Handoff.zip` and commit the verified runnable source/test files into the feature branch before proceeding.
