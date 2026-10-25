# AURA research summary — generated from saved archived result files

*This summary is a reconstruction of existing evidence, not a new benchmark execution.*

## Experimental cohorts (do not pool)

| Cohort | Unit | N | PASS | FAIL | UNCERTAIN | Not AURA-evaluated |
|---|---|---:|---:|---:|---:|---:|
| stage8_1_local_qwen3b | real LLM local-controlled workflows | 4 | 1 | 3 | 0 | 0 |
| stage8_1_appworld | AppWorld native agent evaluation; no AURA certificates | 3 | 0 | 0 | 0 | 3 |
| stage8_2_scripted | 6 tasks x 6 scripted oracle/fault/denial controls | 36 | 6 | 24 | 6 | 0 |
| stage8_3_qwen05 | Qwen2.5-0.5B; AgentSynth SQL environment; 1 seed | 5 | 1 | 4 | 0 | 0 |
| stage8_3_qwen3b_gpu | Qwen2.5-3B on Kaggle GPU; 5 tasks; 1 seed | 5 | 3 | 2 | 0 | 0 |

14 real-model episodes have AURA certificates across three distinct real-model cohorts; 3 additional AppWorld agent episodes have native evaluations **without** AURA certificates. The 36 scripted controls are not real-model episodes.

## Stage 7 modeled prior sensitivity (cost units, not milliseconds)

| Prior | Fixed | Greedy | CERA | Bounded exact | CERA minus greedy |
|---|---:|---:|---:|---:|---:|
| uniform | 5.4847 | 4.3157 | 3.1933 | 3.1709 | -1.1224 |
| clean_50 | 9.8709 | 6.475 | 6.3237 | 5.894 | -0.1513 |
| clean_90 | 13.7943 | 8.4066 | 9.1205 | 7.761 | 0.7139 |

## Stage 7 controlled local latency (milliseconds, one execution per scenario/policy)

| Policy | Scripted scenarios | Mean end-to-end latency (ms) | Matched scoped verdict |
|---|---:|---:|---:|
| fixed | 13 | 2.9954 | 13 |
| greedy | 13 | 3.0107 | 13 |
| cera | 13 | 3.7506 | 13 |
| optimal | 13 | 4.9536 | 13 |
| exhaustive | 13 | 3.1166 | 13 |

## Stage 8.3 modeled inspection policy comparison

| Policy | Worlds/policy | Avg probes | Abstract probe-cost units | Planner latency (ms) |
|---|---:|---:|---:|---:|
| cera | 64 | 1.88 | 3.25 | 0.3709 |
| greedy | 64 | 1.88 | 3.25 | 0.0736 |
| fixed | 64 | 1.88 | 3.375 | 0.0451 |
| exhaustive | 64 | 6.0 | 29.2 | 0.0895 |

**Dimensional warning:** abstract costs are not added to milliseconds. This dataset does not establish a high-latency CERA advantage.

## Central limitations

- No AppWorld-to-AURA adapter evaluation in these archived results.
- Qwen0.5B and Qwen3B external task mixes are different; do not treat them as a controlled model comparison.
- AgentSynth SQL score checks used in real model pilots are local reproductions, not the official CLI on those episodes.
- Side-effect comparison uses stronger task-defined frame policies than the narrow SQL-only outcome checks.
- A complete-before/final snapshot can miss reverted transient unauthorized edits.
- Small pilot sample: no population claim, no false PASS probability bound.

**Source:** evidence archives listed in `derived_audit.json`; see exact ZIP hashes therein.
