# AURA — Stage 7: Controlled Evaluation and Statistical Validity

Research prototype for evidence-backed **full contract task completion**, not tool-return checks. This package contains all Stage 2-7 implementation modules, Stage 1 schemas and examples, strong inspection-policy baselines, 13 local SQLite/filesystem execution scenarios, and formal negative controls.

## Run locally (no Kaggle, GPU, paid API, or cloud required)

Use Python 3.10+ from this extracted directory:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python reproduce_stage7.py --out ./my_stage7_finite_results
python run_stage7_local.py --out ./my_stage7_local_results
```

The most recent verification of this release passed **186 automated tests**. All results directories must be new/empty. If you want to reproduce the inherited Stage 6 ablations separately:

```bash
python reproduce_stage6.py --out ./my_stage6_results
```

## Major experiment outputs

- 48 distinct **authored** task/probe catalogues, 3 prior sensitivity regimes, 14,400 world-policy evaluations.
- `fixed`, `greedy`, `cera`, `optimal` small-instance and `exhaustive` inspector baselines, matched for allowed evidence.
- 13 script-executed local SQLite/file workflows x 5 policies = 65 end-to-end verification evaluations.
- Boundary-denied controls, budget ablations, scaling checks, and template-resampled *descriptive* cost intervals.
- Static Agent-Diff public contract importer; this is NOT equivalent to executing Agent-Diff agents or to the official score.
- Regression correction: directly observed contract violation remains FAIL even when a bounded reference model lacks the observed value.

## Scientific result

CERA has lower modeled marginal cost than greedy under an authored uniform prior but costs more under a 90% clean-workflow prior. On the local cases, real planner latency removes the apparent marginal-cost advantage. **No SOTA, deployment reliability, general formal soundness, or external benchmark advantage is established.**

The `transient_reverted_unobserved` case returns PASS **relative to the current contract** because temporary unauthorized mutation leaves no terminal-state trace. It is an observed blind spot, not evidence of full-history safety.

## Files

- `aura_evaluation/study.py`: paired finite-model policy design, templates, bootstrapping, budget/boundary/stress controls.
- `aura_evaluation/local_faults.py`: real local SQLite/file/scripted fault executions.
- `audit_agentdiff_contracts.py`: public external contract *static* coverage audit (takes locally downloaded upstream JSONL; no agent execution).
- `reproduce_stage7.py`, `run_stage7_local.py`: one-command reproduction of the two Stage 7 studies.
- `docs/STAGE7_REPORT.md`: complete results, limitations and experimental protocol.
- `docs/AGENTDIFF_FULL_DATASET_AUDIT_REFERENCE.json`: public GitHub inspection provenance.

## External benchmark status

AppWorld and Agent-Diff native agent trajectories and their official native evaluation were **not** executed here. 224 published Agent-Diff *contract descriptions* were inspected remotely, but those are not before/after states or real rollout outcomes. Running a native benchmark requires a compatible backend and a permitted trajectory/evaluation setup; simply running a public contract parser on Kaggle is not a substitute.

Source repositories: https://github.com/StonyBrookNLP/appworld and https://github.com/agent-diff-bench/agent-diff

No GitHub commits or pushes were performed.
