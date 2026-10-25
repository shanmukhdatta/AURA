# Stage 8.3 — Qwen2.5-0.5B genuine agent executions

## Scientific scope
Five genuine SQL tool-using Qwen2.5-0.5B-Instruct episodes executed locally with a four-turn budget. Recorded AURA outcomes are 1 PASS and 4 FAIL. The model, tasks, and budget differ from the Qwen3B pilot.

## Original evidence source
`AURA_STAGE8_3_CORRECTED_RESULTS.zip`. The file exists byte-preserved beneath `archive/`; its extracted members appear under experiment-specific `raw/` or `prototype/` paths when applicable. Find exact paths and SHA256 digests in `evidence/master_source_registry.csv` and `evidence/master_archive_member_registry.csv`.

## How to inspect or reproduce
Saved trajectories, task contracts, before/after SQLite evidence, native checker scores, certificates, reference judgments and G3/G4 outputs are browsable under raw/ and the canonical stage83 directory.

## Data labels and limitations
- An execution record is not the same as a test, benchmark calibration, planner world, or certificate replay.
- Keep FAIL, UNCERTAIN, skipped or interrupted cases rather than excluding them.
- Do not claim that all experiments were executed in one environment.
- Cite the archived original outputs, not handwritten summaries, in publication figures.
