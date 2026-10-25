# Gate G4: Fair Analysis, Baseline Comparison, and Cost Evaluation (Status: PASS)

## Summary of Completed Audits
- **Gate Status**: PASS (100% sound lower bound verified across genuine and scripted cohorts)
- **Genuine LLM Cohort**: N = 5 tasks, 1 seed (`Qwen/Qwen2.5-0.5B-Instruct` on CPU)
  - `reproduced_sql_only_score`: 2/5 (40.0%)
  - `strict_contract_reference`: 1/5 (20.0%)
  - `aura_contract_verdict`: 1/5 (20.0%)
  - False PASS: 0 / 5 (0.0%)
  - False FAIL: 0 / 5 (0.0%)
- **Scripted Control Cohort**: N = 36 episodes across 6 tasks (Stage 8.2 replication)
  - False PASS: 0 / 36 (0.0%)
  - False FAIL: 0 / 36 (0.0%)
  - Denial of readback handled soundly with `UNCERTAIN` verdicts (6/6).
- **CERA Cost Evaluation**:
  - Evaluated across 4 domains (64 distinct evaluation worlds per policy).
  - Probe cost units and planner latency reported separately with dimensional rigor.
  - Demonstrated that greedy planning is optimal for low-latency in-memory databases, while CERA is indicated for high-latency (>10ms) distributed probe execution.

## Artifact Deliverables
1. `stage83/results/g4_metrics_corrected.csv` (139 files SHA256 hashed)
2. `stage83/results/g4_cost_corrected.csv`
3. `stage83/results/g4_mismatch_analysis.md`
4. `stage83/results/strict_contract_independent_reference.json`
