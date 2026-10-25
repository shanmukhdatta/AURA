# Reproducibility: CPU checks and original Kaggle runs

AURA is designed so original LLM trajectories can be evaluated and certificates replayed on CPU using saved evidence. **Rerunning the original language model generation is a separate procedure and may require model weights, Kaggle T4 capacity and pinned environments.**

## Archive and provenance checks

```sh
python integrity/verify_archives.py
python integrity/verify_archive_members.py
python integrity/verify_evidence_links.py
```

## AURA code and tests (where dependencies available)

```sh
python -m pip install pytest
python -m aura_validation.runner
python -m pytest AURA_Stage7/tests tests/test_validation_pipeline.py -q
```

The original Antigravity run log records 224 tests passed and one skipped. Test counts may change if a different dependency setup or test-discovery path is used. Preserve original output under `results/tests_and_ci/`.

## Kaggle evidence

See `experiments/stage81_local_qwen_4/`, `experiments/stage81_appworld_3_native/`, and `experiments/stage83_qwen3b_5/` for executed notebooks, config, environment receipts and trajectory evidence. Development or failed setup notebooks belong under `archive/notebook_history/`. No new GPU runs are necessary to check the existing evidence archive.

## Provenance discrepancies

The Stage 8.3 results manifest passed 246/246 in the corrected handoff. A separate historical handoff manifest recorded four source-file hash mismatches out of 135 entries. Both reports are preserved, not silently rewritten.
