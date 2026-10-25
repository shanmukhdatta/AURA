# AURA prototype implementation and historical evolution

This directory preserves the original releases and schemas from Stages 1–7 separately from the maintained runnable engine `../AURA_Stage7/`.

- **Stage 1:** formal task model, contract/probe/observation/certificate schemas, initial fixtures and acceptance checks.
- **Stage 2:** independent state observations and evidence capture.
- **Stage 3:** verifier logic for PASS/FAIL/UNCERTAIN decisions and frame checking.
- **Stage 4:** reasoning ledger and model-based checks.
- **Stage 5:** live inspection planning and evaluation.
- **Stage 6:** baselines, bounded worlds and external integration.
- **Stage 7:** controlled experimental study, 13 local cases, planning-world evaluations and CERA comparisons.

The original ZIP for every release is preserved in `../archive/prototype_releases/`. Extracted files are browseable in `historical_sources/`. The current locally assembled `AURA_Stage7/` code was prepared from the Stage 7 implementation ZIP plus the later Stage 8.3 Antigravity handoff. In a real GitHub consolidation, retain the existing branch's working Stage7 tree unless a file-by-file code diff and regression tests justify changing it.

**No old prototype sources are deleted.** If two versions disagree, trace them using `../evidence/master_source_registry.csv`.
