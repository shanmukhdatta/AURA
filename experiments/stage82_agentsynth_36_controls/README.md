# Stage 8.2 — AgentSynth scripted control matrix

## Scientific scope
Six externally specified SQL tasks, each run with six scripted controlled conditions (36 total): oracle, no-op, silent no-op, partial, unauthorized mutation, and denied readback. This is NOT genuine LLM agent execution. Recorded AURA decisions: 6 PASS, 24 FAIL, 6 UNCERTAIN.

## Original evidence source
`AURA_Stage8_2_External_SQL_Evidence_v1.zip`. The file exists byte-preserved beneath `archive/`; its extracted members appear under experiment-specific `raw/` or `prototype/` paths when applicable. Find exact paths and SHA256 digests in `evidence/master_source_registry.csv` and `evidence/master_archive_member_registry.csv`.

## How to inspect or reproduce
Browse 36 case directories, certificates, observations, frame diffs and native checkers; reproduce with stage82_agentsynth_pilot.py where compatible, and preserve upstream source/license restrictions.

## Data labels and limitations
- An execution record is not the same as a test, benchmark calibration, planner world, or certificate replay.
- Keep FAIL, UNCERTAIN, skipped or interrupted cases rather than excluding them.
- Do not claim that all experiments were executed in one environment.
- Cite the archived original outputs, not handwritten summaries, in publication figures.
