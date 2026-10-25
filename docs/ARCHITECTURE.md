# AURA architecture and module responsibilities

**Signal path:** natural-language task → declared `TaskContract` → agent actions/tool trace → captured final state → independent read-only probes → per-obligation postconditions + process evidence + closed-world frame diff → PASS/FAIL/UNCERTAIN certificate → evidence replay + integrity audit.

The canonical *working layout* remains `AURA_Stage7/` pending a separate backwards-compatible source migration:

| Module | Primary responsibility |
|---|---|
| `schemas/` | TaskContract, ProbeSpec, Observation, Certificate, ReasoningLedger schemas |
| `aura_evidence/` | Capturing snapshots, computing before/after diffs, probes, trace, evidence ledger, validation and SHA/digest helpers |
| `aura_verifier/` | Contract checking, frame allowlist enforcement, 3-way decision |
| `aura_planning/` | CERA cost-aware inspection choices, policy candidates, live runner |
| `aura_baselines/` | Reference inspection baseline strategies |
| `aura_external/` | Adapters/helpers for AgentSynth, AgentDiff and AppWorld workflow integration |
| `aura_evaluation/` | Controlled local failure experiments and study results |
| `aura_reasoning/` | Model and reasoning-related reference machinery |
| `aura_validation/` | Independent reference scoring, certificate replay, cross-cohort metrics and manifest audits from Antigravity |

## Three-way semantics

- **PASS:** observed evidence covers specified obligations and none is violated.
- **FAIL:** a definite contract violation is established.
- **UNCERTAIN:** available evidence is insufficient to establish or refute complete satisfaction.

The frame boundary is **only** as complete as declared/observed surfaces. Transient/out-of-scope effects cannot be claimed verified. Original schemas and historical algorithms are browseable beneath `prototype/`, and the exact latest-known recorded code is retained unchanged in the source archives.
