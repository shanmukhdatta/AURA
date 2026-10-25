# AURA External Validation — Exact Reproduction Commands

This document contains the exact commands to reproduce all validation reports, test suite executions, and inventory audits on a clean CPU environment.

## Environment Requirements
- Python 3.10+ (tested on Python 3.11.9)
- Dependencies: `pytest`, `sqlite3` (built-in), `pyyaml`, `transformers`, `torch` (CPU only)
- No GPU or cloud credentials required.

---

## 1. Execute Modular External Validation Workflow
Generates all seven deliverable reports in `validation_reports/`:
```bash
python -m aura_validation.runner
```
Outputs:
- `validation_reports/validation_summary.json`
- `validation_reports/external_episode_metrics.csv`
- `validation_reports/cohort_summary.csv`
- `validation_reports/certificate_replay_results.json`
- `validation_reports/integrity_check.json`
- `validation_reports/validation_failures.md`
- `validation_reports/VALIDATION_EXECUTION_REPORT.md`

---

## 2. Generate Experiment Inventory CSV
Generates the 59-episode inventory mapping:
```bash
python generate_inventory.py
```
Output:
- `EXPERIMENT_INVENTORY_FINAL.csv`

---

## 3. Run Automated Validation Test Suite
Executes the 12 validation pipeline test cases covering task completion, omissions, false claims, unauthorized edits, semantic refusal checks, epistemic gaps, replay, tampering, noninterference, and cohort separation:
```bash
pytest tests/test_validation_pipeline.py -v
```

---

## 4. Run Complete Available Test Suite
Executes all unit, integration, verifier, adapter, and validation tests across the entire codebase:
```bash
pytest AURA_Stage7/tests stage83/tests tests/test_validation_pipeline.py -v
```
Expected Output:
`224 passed, 1 skipped` (Windows symlink privilege test cleanly skipped).

---

## 5. Verify Immutable Evidence Archive Integrity
Audit frozen historical evidence hashes:
```bash
python -c "from aura_validation.integrity import audit_repository_manifest; import json; print(json.dumps(audit_repository_manifest('stage83/results/SHA256SUMS.json'), indent=2))"
```
