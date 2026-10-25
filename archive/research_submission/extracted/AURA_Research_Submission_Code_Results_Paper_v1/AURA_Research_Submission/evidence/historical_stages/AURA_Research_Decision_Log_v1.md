# AURA Research Decision Log — v1.0 (24 October 2026)

| ID | Decision | Rationale | Status |
|---|---|---|---|
| D01 | AURA verifies completion of every **declared task obligation**, not merely tool-call execution. | Directly preserves the project's user-centered purpose. | Locked |
| D02 | Use contract-defined postconditions, allowed-change frame, process obligations, and observation scope. | Defines precisely what can and cannot be certified. | Locked |
| D03 | Do not claim novelty for state diffs, closed-world side effects, PASS/FAIL/UNCERTAIN, completion graphs, or adaptive checking alone. | Overlaps verified prior work. | Locked |
| D04 | Study counterexample-guided **evidence sufficiency** and budgeted read-only inspection with full cost accounting. | Falsifiable candidate differentiator. | Research hypothesis |
| D05 | Exact bounded-world semantics is the research reference, with a sound conservative fallback for scale. | Avoids silently equating approximate computation with proof. | Locked |
| D06 | PASS for no-side-effects needs complete observation of the declared mutation frame. | Prevents false assurance from targeted-only reads. | Locked |
| D07 | Missing/contradictory evidence never generates PASS. | Fail-closed handling of inconsistent models. | Locked |
| D08 | Ground-truth oracle/fault identifiers are invisible to AURA. | Prevents evaluation leakage and circular detection. | Locked |
| D09 | Compare at matched evidence menu, contracts, budget, and decisive coverage; baseline target includes targeted-evidence work. | Isolates planner benefits from information privilege. | Locked |
| D10 | Core must be deterministic and inspect-only; no LLM judge or automatic recovery in v1. | Stronger reproducibility and tractable scope. | Locked |
| D11 | Stage 0 creates specifications; no execution code or Git commits yet. | Preserves plan-first user instruction. | Locked |
| D12 | Novelty and paper acceptability remain unsettled until stronger prior-art audit and measured results. | Honesty about publication risk. | Open |

## Next gate

Specify the finite-world reference model and canonical `TaskContract`, `ProbeSpec`, `Observation`, and `Certificate` schemas. Only then implement the verification foundation. Do not silently expand scope without an explicit design revision.
