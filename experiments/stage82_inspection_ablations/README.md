# Stage 8.2 — Targeted inspection and negative controls

## Scientific scope
Saved inspection ablations and evidence-tampering/negative-control artifacts from Stage 8.2. These are inspections of scripted cases, not additional genuine model episodes.

## Original evidence source
`AURA_Stage8_2_External_SQL_Evidence_v1.zip`. The file exists byte-preserved beneath `archive/`; its extracted members appear under experiment-specific `raw/` or `prototype/` paths when applicable. Find exact paths and SHA256 digests in `evidence/master_source_registry.csv` and `evidence/master_archive_member_registry.csv`.

## How to inspect or reproduce
Read the ablation files inside the Stage 8.2 original evidence archive and accompanying scripts. Any count should be obtained from the original CSV.

## Data labels and limitations
- An execution record is not the same as a test, benchmark calibration, planner world, or certificate replay.
- Keep FAIL, UNCERTAIN, skipped or interrupted cases rather than excluding them.
- Do not claim that all experiments were executed in one environment.
- Cite the archived original outputs, not handwritten summaries, in publication figures.
