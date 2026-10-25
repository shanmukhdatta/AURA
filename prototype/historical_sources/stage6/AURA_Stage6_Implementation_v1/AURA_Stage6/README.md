# AURA — Stage 6: Strong Baselines and External Contract Interoperability

Reproducible **research prototype** continuing Stages 1–5. AURA tests whether the *whole declared task* was completed using independently collected state/trace evidence—not only whether each tool responded successfully.

## Quick start

Python >=3.10. Run from the extracted `AURA_Stage6/` directory:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python reproduce_stage6.py --out ./new_stage6_results
```

This is an offline evaluation; the standard run requires neither a cloud account nor an LLM API. The CLI refuses to overwrite a nonempty results directory.

## What Stage 6 adds

- `aura_baselines/surface.py`: Conservative state-only, trace-only, and combined verification on **the same six** Stage 2 snapshot/trace captures. **These are intentionally NOT information-matched comparisons.**
- `aura_external/agentdiff.py`: Import parser for the upstream Agent-Diff public JSONL contract shape (`answer` stores a JSON-encoded string in the source). It supports a safe subset of assertion operators and refuses to certify unsupported semantics.
- `aura_external/fixtures.py`: Generates **hypothetical, not actual** diff records only for parser/evaluator tests.
- `aura_external/appworld.py`: Honest integration-readiness probe (not AppWorld agent benchmarking).
- `examples/external/agentdiff_public_contract_excerpt.jsonl`: Five **abbreviated** assertion excerpts transcribed from public Agent-Diff tasks. The full upstream dataset has not been bundled.
- `reproduce_stage6.py`: Regenerates Stage 5 matched-planner results and Stage 6 surface/excerpt checks, preserving common snapshot cost accounting.

## Import full public Agent-Diff contracts (format compatibility only)

The researcher may separately download the public source dataset and supply it locally:

```bash
python reproduce_stage6.py --out ./new_results --agentdiff-jsonl ./test.jsonl
```

This reports import counts and unsupported clause counts; it **does not** launch Agent-Diff, run agents, reconstruct native application state, or calculate official benchmark scores. An actual external task-completion comparison additionally requires permitted environment snapshots or genuine agent trajectories and an independent evaluation protocol.

## Existing planner policies

Stage 5 includes `fixed`, `greedy`, `cera`, `optimal` (bounded exact reference), and `exhaustive`, all with identical evidence catalogues for the selection-policy comparison. Stage 6 explicitly separates those **information-matched** tests from the **information-restricted** state-only/trace-only ablation.

## Scientific status

- Stages 2–6 have runnable local code and tests.
- The finite-world benchmark is co-authored and has only a small number of shared structural templates; repeated worlds are not independent real tasks.
- Public Agent-Diff *contracts* were consulted, but no original Agent-Diff trajectories or official outcomes have been evaluated.
- No production-hardening, universal soundness, or SOTA performance is established.
- The original CERA pilot's advantage over fixed/greedy remains modest and may disappear after capture and selection overhead.

## Sources

- Agent-Diff source: https://github.com/agent-diff-bench/agent-diff
- Public Agent-Diff dataset: https://github.com/agent-diff-bench/agent-diff/tree/main/datasets/agent-diff-bench
- AppWorld source: https://github.com/StonyBrookNLP/appworld

No GitHub commits or pushes were performed.
