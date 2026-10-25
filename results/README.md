# Results: source-linked and cohort-separated

- `execution_results/`: initial benchmark outcomes and SQL-only postconditions where available.
- `verification_results/`: PASS / FAIL / UNCERTAIN, reference agreement and certificate replay.
- `planning_and_cera/`: planner comparison outputs and source study CSVs; distinguish modeled probe costs from CPU wall time.
- `ablations/`: controlled missing-evidence and fault-injection inspection conditions.
- `tests_and_ci/`: saved Antigravity 224-pass/one-skip test transcript and metadata.
- `published_tables/`: manuscript-ready derived tables only after exact source-to-table tracking.

The uploaded 59-episode independent-validation result reports 13 PASS, 39 FAIL, 7 UNCERTAIN; four verified cohorts (13+36+5+5). The mean reproduced SQL scores are 23.1%, 75.0%, 58.3% and 75.0% respectively, *not accuracy estimates*. AgentSynth official CLI calibration must be labeled separately.

Inspect `../validation_reports/` and `../evidence/experiment_registry.csv` for the original numeric data.
