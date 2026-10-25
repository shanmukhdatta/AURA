# AURA Stage 8.3 — Independent External-Agent Verification

This directory contains the complete implementation, experiment harness, execution receipts, and evaluation deliverables for **AURA Stage 8.3**.

## Quickstart & Replication

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install -e _deps/agentsynth

# 2. Run G0 Baseline Audit
python -m pytest -q AURA_Stage7/tests
python stage82_agentsynth_pilot.py --out stage82_replication --zip

# 3. Validate Official AgentSynth Pack
agentsynth pack validate _deps/agentsynth/packs/core_v2.yaml

# 4. Run G2 Adapter Integration Tests
pytest -q AURA_Stage7/tests/test_agentsynth_adapter.py

# 5. Run G3 Genuine LLM Experiments
python stage83/run_g3_experiment.py --model Qwen/Qwen2.5-0.5B-Instruct --tasks raise-ticket-priority refuse-cancel-shipped clearance-discount dedup-keep-latest refund-and-restock

# 6. Run G4 Analysis and CERA Comparison
python stage83/run_g4_analysis.py
```

## Directory Structure
- `G0_STATUS.md` through `G5_STATUS.md`: Step-by-step gate execution receipts.
- `results/contracts/`: 14 precommitted task contracts with closed-world allowlists.
- `results/episodes/<task_id>/<run_id>/`: Full raw evidence per episode (prompts, tool traces, snapshots, certificates, audits).
- `results/g4_metrics.csv`: 20-column episode-level comparison table across all cohorts.
- `results/g4_cost.csv`: CERA empirical cost comparison against full, greedy, fixed, and exhaustive policies.
- `results/g4_mismatch_analysis.md`: Detailed policy-scope divergence analysis.
- `AURA_STAGE83_REAL_AGENT_KAGGLE.ipynb`: Dedicated GPU notebook for Kaggle T4 inference.
