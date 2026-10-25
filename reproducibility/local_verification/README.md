# Locally regenerated verification receipts (distinct from upstream originals)

- `cpu_59_episode_replay_stdout.txt`: local CPU replay of saved evidence, 59/59 exact certificate match.
- `local_integrity_check.json`: Stage 8.3 246/246, with 0 missing or mismatched; separate historical manifest shows 124/135 because 11 remote-only source files were unavailable in this local assembled tree, NOT because the upstream final PR reports that outcome.
- `cpu_regression_fast_subset_stdout.txt`: 184 passed, 14 excluded long-running Stage7 study tests.
- `full_suite_attempt_timed_out_stdout.txt`: partial local suite progress. Full-suite completion could not be confirmed before this environment's execution timeout.
- Original Antigravity full-suite evidence remains `test_execution_log.txt` and `results/tests_and_ci/antigravity_test_execution_log.txt` (224 passed, one skipped on original environment).

These are **new local packaging-time checks**, not additional LLM experiments or evidence that earlier real model trajectories were re-executed.
