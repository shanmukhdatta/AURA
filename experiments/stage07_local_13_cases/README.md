# Stage 7 — Local controlled verification scenarios

## Scientific scope
Thirteen scripted local SQLite/filesystem cases with postcondition, frame, observation-boundary, and process-obligation conditions. Three PASS, nine FAIL, and one UNCERTAIN are represented in the current 59-episode external-validation registry.

## Original evidence source
`AURA_Stage7_Results_v1.zip`. The file exists byte-preserved beneath `archive/`; its extracted members appear under experiment-specific `raw/` or `prototype/` paths when applicable. Find exact paths and SHA256 digests in `evidence/master_source_registry.csv` and `evidence/master_archive_member_registry.csv`.

## How to inspect or reproduce
Read raw run records under raw/, then AURA_Stage7/reproduce_stage7.py and run_stage7_local.py. Preserve exact results and original databases.

## Data labels and limitations
- An execution record is not the same as a test, benchmark calibration, planner world, or certificate replay.
- Keep FAIL, UNCERTAIN, skipped or interrupted cases rather than excluding them.
- Do not claim that all experiments were executed in one environment.
- Cite the archived original outputs, not handwritten summaries, in publication figures.
