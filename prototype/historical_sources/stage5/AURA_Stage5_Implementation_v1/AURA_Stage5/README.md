# AURA - Stage 5 (CERA Inspection Planner)

**Research prototype** implementing AURA Stage 1-5: formal contracts, independent evidence collection, task verification, bounded compatible-world reasoning, and adaptive inspection selection.

The AURA engine checks **whether the task is completed**, not whether tools simply returned success. Stage 5 tests which trustworthy inspection to perform next when completion remains uncertain.

## Run from a clean environment

Requires Python >=3.10:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python reproduce_stage5.py --out ./fresh_stage5_results
```

`--out` must be a new or empty directory. Experiments never silently overwrite saved records.

## Inspection strategies

`fixed`, `greedy`, `cera`, `optimal`, `exhaustive`. The exact reference is intentionally limited to small finite instances. All policies use the same frozen contract and read-only inspection catalogue. `CERA` uses counterexample-separation scoring; it does not receive the test-world identity.

## Contents

- `aura_evidence/`: Stage 2 trusted sandbox and read-only probes
- `aura_verifier/`: Stage 3 conservative certified verdicts
- `aura_reasoning/`: Stage 4 bounded compatible-world reference
- `aura_planning/`: Stage 5 policies, synthetic environments, and Stage 2 live integration
- `tests/`: inherited regression + Stage 5 acceptance tests
- `schemas/`: Stage 1 and Stage 4 contract/certificate/model schemas
- `docs/STAGE5_DESIGN.md`: algorithm, safety assumptions, and experiment limitations
- `reproduce_stage5.py`: finite-model comparisons, success-prior shifts, probe-budget stress, and six local workflow captures

## Scientific validity

This project has **not** yet demonstrated novel research performance. Generated worlds are not independent third-party tasks. A limited success/failure test and code-level passing tests are engineering acceptance, not statistical significance. The main prerequisite for a research paper is Stage 6: stronger baselines, independent tasks, and defensible evidence-cost measurements.

## GitHub

No commits or pushes were performed in this stage.
