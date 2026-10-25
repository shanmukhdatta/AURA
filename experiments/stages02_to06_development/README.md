# Stages 2–6 — Verifier development and evidence capture

## Scientific scope
Historical versions of evidence capture, task verification, reasoning ledgers, adaptive inspection planning, and baseline comparisons. The original implementation/result archives are preserved independently for each version.

## Original evidence source
`AURA_Stage2_Implementation_v1.zip through AURA_Stage6_Results_v1.zip`. The file exists byte-preserved beneath `archive/`; its extracted members appear under experiment-specific `raw/` or `prototype/` paths when applicable. Find exact paths and SHA256 digests in `evidence/master_source_registry.csv` and `evidence/master_archive_member_registry.csv`.

## How to inspect or reproduce
Preserve original implementation and outcome ZIPs. Stages are progressive historical releases, not independent benchmark cohorts. See prototype/historical_sources and archive/.

## Data labels and limitations
- An execution record is not the same as a test, benchmark calibration, planner world, or certificate replay.
- Keep FAIL, UNCERTAIN, skipped or interrupted cases rather than excluding them.
- Do not claim that all experiments were executed in one environment.
- Cite the archived original outputs, not handwritten summaries, in publication figures.
