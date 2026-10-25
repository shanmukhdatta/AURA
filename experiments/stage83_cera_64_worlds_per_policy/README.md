# Stage 8.3 — CERA probe-cost comparisons

## Scientific scope
Policy-world cost comparisons from Stage 8.3 G4, separate from the agent-success table. CERA is not proven uniformly cheaper than greedy across all measured conditions.

## Original evidence source
`AURA_STAGE8_3_CORRECTED_RESULTS.zip`. The file exists byte-preserved beneath `archive/`; its extracted members appear under experiment-specific `raw/` or `prototype/` paths when applicable. Find exact paths and SHA256 digests in `evidence/master_source_registry.csv` and `evidence/master_archive_member_registry.csv`.

## How to inspect or reproduce
See stage83/results/g4_cost_corrected.csv and Stage 8.3 analysis code; distinguish modeled probe costs from planner CPU overhead.

## Data labels and limitations
- An execution record is not the same as a test, benchmark calibration, planner world, or certificate replay.
- Keep FAIL, UNCERTAIN, skipped or interrupted cases rather than excluding them.
- Do not claim that all experiments were executed in one environment.
- Cite the archived original outputs, not handwritten summaries, in publication figures.
