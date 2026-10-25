# AURA Research Reproducibility Guide

This guide describes how to replicate every empirical table, test, and verification certificate in the AURA manuscript.

---

## 1. Environment Requirements
- **Python**: 3.10+ (tested on Python 3.11)
- **Dependencies**: `pip install -r requirements.txt` (or `pip install pytest torch transformers accelerate pydantic pyyaml jsonschema numpy`)
- **OS**: Linux, macOS, or Windows (Windows non-admin skips unprivileged symlink test cleanly)

---

## 2. One-Command Full Regression Suite
To run all 212 tests across core verification, planning, independent references, and Qwen2.5-3B pilot:

```bash
pytest AURA_Stage7/tests stage83/tests -v
```

**Expected Output:**
- 212 passed, 1 skipped (`test_symlink_detected_during_snapshot` skipped on Windows without Developer Mode / Admin)
- 0 failures
- Total duration: ~85 seconds

---

## 3. Regenerating Publication Research Tables
To recompute and generate all research tables in both LaTeX (`.tex`) and Markdown (`.md`):

```bash
python paper/generate_research_tables.py
```

Outputs generated in `paper/tables/`:
- `table1_main_benchmark.tex` and `.md`
- `table2_cera_cost.tex` and `.md`
- `table3_ablation_soundness.tex`
- `table4_benchmark_gaming.tex`

---

## 4. Replaying AURA Certificates from Raw Evidence
To independently re-verify the archived AURA certificates against raw pre/post snapshots:

```bash
# Re-audit genuine LLM episodes (Qwen2.5-0.5B)
python stage83/independent_reference.py

# Re-audit CERA cost analysis across 64 worlds
python stage83/run_g4_analysis.py
```

Outputs generated:
- `stage83/results/strict_contract_independent_reference.json`
- `stage83/results/g4_metrics_corrected.csv`
- `stage83/results/g4_cost_corrected.csv`

---

## 5. Reproducing the Qwen2.5-3B GPU Inference Run
To re-run the 3B agent on a free Kaggle T4 GPU:
1. Open [Kaggle](https://www.kaggle.com) and create a new notebook with a **GPU T4 x2** accelerator.
2. Upload [`AURA_STAGE83_REAL_AGENT_KAGGLE_v2.ipynb`](file:///c:/Users/lokes/Datta/Projects/New%20folder/AURA/AURA_STAGE83_REAL_AGENT_KAGGLE_v2.ipynb).
3. Run all cells:
   - Cell 4 executes the 2-task preflight smoke verification.
   - Cell 5 executes the multi-task rollout.
   - Cell 6 generates `AURA_STAGE83_REAL_AGENT_OUTPUTS.zip` containing raw SQLite snapshot pairs, tool traces, and verified certificates.
4. Download the generated ZIP and unpack into `stage83/results/qwen3b_pilot/`.

---

## 6. Cryptographic Manifest Verification
To verify the integrity of all 142 research artifacts against their SHA256 checksums:

```bash
python -c "
import json, hashlib
from pathlib import Path

manifest = json.loads(Path('stage83/results/SHA256SUMS.json').read_text())
mismatches = []
for rel, expected in manifest.items():
    p = Path('stage83/results') / rel
    if not p.is_file():
        mismatches.append(f'Missing: {rel}')
        continue
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    if actual != expected:
        mismatches.append(f'Mismatch: {rel}')
print(f'Verified {len(manifest)} files. Mismatches: {len(mismatches)}')
"
```

**Expected Output:** `Verified 142 files. Mismatches: 0`
