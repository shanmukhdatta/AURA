# Independent external validation — 59 saved episodes

## Scientific scope
Replays 13 Stage7 scripted + 36 Stage8.2 scripted + five 0.5B genuine + five 3B genuine episodes. Saved report records 59/59 deterministic certificate replay; 224 passed, one skipped, zero failed in the provided test log.

## Original evidence source
`AURA_EXTERNAL_VALIDATION_FINAL_HANDOFF.zip`. The file exists byte-preserved beneath `archive/`; its extracted members appear under experiment-specific `raw/` or `prototype/` paths when applicable. Find exact paths and SHA256 digests in `evidence/master_source_registry.csv` and `evidence/master_archive_member_registry.csv`.

## How to inspect or reproduce
Canonical code in aura_validation/ and tests/test_validation_pipeline.py; raw handoff and seven original reports are preserved. Re-run tests and verify manifest independently before publishing claims.

## Data labels and limitations
- An execution record is not the same as a test, benchmark calibration, planner world, or certificate replay.
- Keep FAIL, UNCERTAIN, skipped or interrupted cases rather than excluding them.
- Do not claim that all experiments were executed in one environment.
- Cite the archived original outputs, not handwritten summaries, in publication figures.
