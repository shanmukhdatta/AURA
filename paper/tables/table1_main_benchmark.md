# Table 1: Multi-Turn Agent Verification Benchmark across Model Scales

| Evaluation Cohort | Model / System | Hardware | Evaluated Tasks | Tool Calls (Avg) | Reproduced SQL Pass | Strict Ground Truth | AURA Verified | False PASS | False FAIL | Concordance |
|---|---|---|---|---|---|---|---|---|---|---|
| **Genuine LLM (0.5B)** | Qwen2.5-0.5B-Instruct | CPU (x86_64) | 5 | 3.0 | 2/5 (40.0%) | 1/5 (20.0%) | **1/5 (20.0%)** | **0 / 5 (0.0%)** | **0 / 5 (0.0%)** | **100.0%** |
| **Genuine LLM (3B)** | Qwen2.5-3B-Instruct | T4 GPU (CUDA) | 5 | 3.0 | 3/5 (60.0%) | 3/5 (60.0%) | **3/5 (60.0%)** | **0 / 5 (0.0%)** | **0 / 5 (0.0%)** | **100.0%** |
| **Scripted Controls** | Deterministic Fault Harness | CPU | 36 | 2.0 | 6/36 (16.7%) | 6/36 (16.7%) | **6/36 (16.7%)** | **0 / 36 (0.0%)** | **0 / 36 (0.0%)** | **100.0%** |
