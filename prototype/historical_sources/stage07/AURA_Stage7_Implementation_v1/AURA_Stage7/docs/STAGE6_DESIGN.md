# AURA Stage 6 - Integration architecture and validity boundaries

## Two distinct study designs

**A. Information-matched selection:** Continue Stage 5 fixed/greedy/CERA/exact/exhaustive policies with the identical catalog, finite model, and cost assumptions. This tests inspection selection.

**B. Evidence-surface ablation:** Run state-only, trace-only, and dual-surface on identical controlled local captures but intentionally different probe permissions. This tests what kinds of evidence enable outcomes; it **cannot establish algorithmic superiority**.

## External integration scope

The Agent-Diff task `answer` format is imported from JSONL, which may encode a JSON string with a list of assertions. The conservative parser handles a subset of documented constraints and returns UNCERTAIN when input semantics are unsupported, ambiguous, or incompletely observed. The *actual upstream evaluator* must be used for official task scores.

The five bundled public task excerpts are deliberately **abbreviated**. A local generator constructs hypothetical diffs to test our adapter; these are never passed off as external agent trajectories.

AppWorld readiness is checked, not installed or benchmarked. Production integration requires the real environment, permitted task/agent outputs, and an independent reference evaluator.

## Security/trust assumptions

- All Stage 2 captures have a cooperative quiescence boundary.
- Evidence is stored outside the agent's writable workspace.
- Source code does not assert that all uninstrumented external effects can be verified.
- Contract parsers neither execute source strings nor perform task writes.
- The verifier must not silently infer no collateral damage from partial readback.

## Reproduction

Run `python -m pytest -q` then `python reproduce_stage6.py --out ./new_results`. A complete 224-task official benchmark outcome cannot be produced by these commands alone.
