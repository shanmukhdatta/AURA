# Stage 8.3 Gate G3 Status — Genuine LLM Execution

## Execution Summary
- **Gate**: G3 (Genuine LLM-Executed External Tasks)
- **Status**: PASS
- **Model ID**: `Qwen/Qwen2.5-0.5B-Instruct`
- **Provider / Backend**: HuggingFace Transformers (PyTorch CPU)
- **Seed**: `42`
- **Tasks Evaluated**: 5 tasks (preregistered smoke sample across 3 difficulty tiers: easy, medium, hard)
- **Model Load Time**: 6.23 s

## Episode Outcomes
| Task ID | Tier | Model Actions | SQL Queries Executed | Final Answer Extracted | Official Native Passed | Matched Contract Ref | AURA Verdict | Replay Verified |
|---|---|---|---|---|---|---|---|---|
| `raise-ticket-priority` | easy | 2 | 1 | `Ticket 3 has been raised to high priority.` | True | True | **PASS** | True |
| `refuse-cancel-shipped` | medium | 2 | 1 | `To determine whether the order with ID 9 has ` | True | True | **FAIL** | True |
| `clearance-discount` | easy | 2 | 1 | `To accomplish the task of cutting 20% off eve` | False | False | **FAIL** | True |
| `dedup-keep-latest` | medium | 4 | 4 | `To accomplish this task, we can use the `UPDA` | False | False | **FAIL** | True |
| `refund-and-restock` | hard | 4 | 3 | `To accomplish the task of refunding order 5 a` | False | False | **FAIL** | True |

## Aggregate Counts
- Total Genuine LLM Episodes: 5
- Official Native Benchmark Successes: 2/5 (40.0%)
- Matched-Contract Reference Passes: 2/5 (40.0%)
- AURA PASS: 1
- AURA FAIL: 4
- AURA UNCERTAIN: 0

## Integrity & Noninterference
- All SQLite databases were verified for inspection noninterference (pre/post hash equality verified in `audit_receipt.json`).
- Agent trajectories and AURA certificates were hashed before grading against native checkers.
- All certificates replayed with 100% digest match.
- Separate Kaggle GPU notebook (`AURA_STAGE83_REAL_AGENT_KAGGLE.ipynb`) is preserved for expanding to Qwen-2.5-3B-Instruct on T4 GPU per Section 7.
