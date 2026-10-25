# AURA — Agent Uncertainty and Residue Arbiter

Evidence-gated verification of multi-step AI-agent task completion. The verifier uses task contracts, independent read-only observations, required end-state conditions, frame/side-effect restrictions, and PASS / FAIL / UNCERTAIN certificates.

## Evidence status — 25 October 2026

- **Stages 0–7:** Prototype AURA engine implemented and maintained; 186 local regression tests passed on a fresh rerun.
- **Stage 8.1:** Four real Qwen2.5-3B-Instruct *local* workflows were run and checked with AURA; four matching reference judgments. Three official AppWorld development tasks executed and received official native evaluations (0/3 agent successes), but these have **no independent AURA certificates**.
- **Stage 8.2:** Six externally authored AgentSynth SQL task definitions were exercised in 36 **scripted** correct/fault execution controls using real SQLite states. AURA gave 6 PASS, 24 FAIL, and 6 UNCERTAIN, matching the predesigned control expectations. This is **not** 36 naturally observed external AI-agent runs, and not an official AgentSynth benchmark run. CERA cost superiority was **not tested** in Stage 8.2.
- **Stage 8.3:** Planned independent LLM-driven benchmark execution and verification, with original AgentSynth evaluator, preregistered task contracts, stronger matched-rule baseline, independent snapshots, and evidence-integrity audits. **Not executed yet.**

The six-task benchmark source is [AgentSynth](https://github.com/agentsynth/agentsynth), `packs/core_v2.yaml` and `packs/core_v2_oracle.py`. The dataset and solution plans belong to their authors. Preserve attribution and original MIT license requirements.

## Research ethics and evaluation rules

Never describe scripted failure injections as natural LLM failures; never call official AppWorld native scores AURA certificates; never treat a stronger AURA task contract as a fair performance comparison unless the baseline checks the same contract. Mark missing independent evidence as UNCERTAIN. Do not fabricate runs, timings, evidence, or success rates.

## Hand-off to Antigravity

See `research/STAGE_8_3_ANTIGRAVITY_PROMPT.md` and `research/PROJECT_STATUS_AND_GATES.md` (added separately). Antigravity should inspect this repo before editing, operate in an isolated feature branch, and open a PR for review rather than overwrite `main`.

**Repository:** https://github.com/shanmukhdatta/AURA
