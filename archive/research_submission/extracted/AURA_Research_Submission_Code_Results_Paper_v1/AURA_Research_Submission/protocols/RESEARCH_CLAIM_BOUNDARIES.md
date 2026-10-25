# AURA — claim/evidence rules for an honest short paper

| Claim | Evidence source | Permitted wording | Forbidden inference |
|---|---|---|---|
| Core prototype works in controlled setting | Original Stage 7 suite and Stage 7 report | 186 regression tests passed on the original environment; 13 scripted worlds x 5 policies | Zero errors for arbitrary real agents |
| Planner CERA is cost-effective under some priors | Stage 7 results ZIP, original policy_summary.csv | Uniform prior: 3.193 vs greedy 4.316 abstract cost units; 90%-clean prior: 9.120 vs greedy 8.407 | Always faster; measured network speedup |
| Local real-LLM checks | Stage 8.1 `track_A` | 4 real-Qwen locally designed workflows, 1 PASS / 3 FAIL certificates | External generalization |
| AppWorld agent baseline | Stage 8.1 v7 `track_B` | 3 native AppWorld failures; 0 AURA AppWorld certificates | AURA false-pass/accuracy on AppWorld |
| Fault/denial controls | Stage 8.2 external SQL | Six upstream task definitions, 36 scripted controls (6 PASS, 24 FAIL, 6 UNCERTAIN), all matched injected expectations | 36 genuine LLM runs or broad model accuracy |
| GPU proof of concept | Stage 8.3 Qwen2.5-3B Kaggle | 5 real LLM episodes; 3 PASS / 2 FAIL; 5/5 certificate replay | Native AgentSynth CLI score, independent test-set accuracy |
| CPU proof of concept | Stage 8.3 Qwen2.5-0.5B | 5 real LLM episodes; 1 PASS / 4 FAIL; matched strict contract in saved analysis | Better/worse than 3B (different tasks/interfaces) |
| Refusal semantics | Stage 8.3 independent scorer shared task contract | Contradictory cancellation recommendation rejected; benchmark answer substring is inadequate in this case | Fully independent reference generation or universal semantic verifier |
| CERA Stage8.3 cost | Corrected g4_cost_corrected.csv | In 64 modeled worlds per policy: CERA and greedy both ~1.88 probes / 3.25 abstract cost; CERA higher planning latency | Guaranteed high-latency advantage |

**Data lineage:** all numerical tables from `python -m research_submission.run_all` over archived immutable sources. If reported values differ, stop and investigate before revising the manuscript. Do not quietly edit raw observations, reference labels or experiments after viewing desired results.

**Reproducibility:** archived checksums verify local file integrity, not remote execution attestation. Cross-model cohorts share neither full task list nor inference protocol; do not pool into a model-comparison significance test.
