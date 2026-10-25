# Stage 8.3 G1 — Official AgentSynth calibration

## Scientific scope
Upstream official AgentSynth CLI calibration with oracle and no-op controls. Four scoring notions must remain separate: official CLI results, reproduced SQL-only checks, strict contract reference, and AURA certificate. The calibration cases are not part of the 59 certified episodes.

## Original evidence source
`AURA_STAGE8_3_CORRECTED_RESULTS.zip`. The file exists byte-preserved beneath `archive/`; its extracted members appear under experiment-specific `raw/` or `prototype/` paths when applicable. Find exact paths and SHA256 digests in `evidence/master_source_registry.csv` and `evidence/master_archive_member_registry.csv`.

## How to inspect or reproduce
See stage83/results/g1_* and stage83/G1_STATUS.md. Verify precise G1 counts against official receipts, not the AURA episode registry.

## Data labels and limitations
- An execution record is not the same as a test, benchmark calibration, planner world, or certificate replay.
- Keep FAIL, UNCERTAIN, skipped or interrupted cases rather than excluding them.
- Do not claim that all experiments were executed in one environment.
- Cite the archived original outputs, not handwritten summaries, in publication figures.
