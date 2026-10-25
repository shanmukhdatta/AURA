# Stage 8.3 — Qwen2.5-3B Kaggle T4 pilot

## Scientific scope
Five genuine Qwen2.5-3B-Instruct SQL tool executions on Kaggle GPU with a six-turn budget. Recorded AURA outcomes are 3 PASS and 2 FAIL. Do not present as a controlled model-size improvement over the 0.5B cohort.

## Original evidence source
`AURA_STAGE83_QWEN3B_PILOT_RESULTS.zip`. The file exists byte-preserved beneath `archive/`; its extracted members appear under experiment-specific `raw/` or `prototype/` paths when applicable. Find exact paths and SHA256 digests in `evidence/master_source_registry.csv` and `evidence/master_archive_member_registry.csv`.

## How to inspect or reproduce
See raw/.../results/ and original executed Kaggle notebook and run guide under archive/notebook_history. Preserve all SQLite and trace files.

## Data labels and limitations
- An execution record is not the same as a test, benchmark calibration, planner world, or certificate replay.
- Keep FAIL, UNCERTAIN, skipped or interrupted cases rather than excluding them.
- Do not claim that all experiments were executed in one environment.
- Cite the archived original outputs, not handwritten summaries, in publication figures.
