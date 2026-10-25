# AURA - Stage 3 Verification Engine

**Implementation and acceptance report | 24 October 2026 | Version 1.0**  
**Project:** AURA - Agent Uncertainty and Residue Arbiter  
**Research direction:** Counterexample-Guided Evidence Certification for Multi-Step AI-Agent Task Completion  
**Status:** Completed core-verifier engineering milestone, within a controlled local sandbox. Not a research-paper performance result.

## Executive result

Stage 3 implements the first working **task-completion decision engine**. It takes the Stage 1 `TaskContract`, registered `ProbeSpec` definitions, and trusted Stage 2 `Observation` records, then evaluates the contract and emits a structured `Certificate` with **PASS**, **FAIL**, or **UNCERTAIN**.

An agent's success message is **not** sufficient evidence. In particular, the engine checks exact outcome predicates, authorized changes throughout the declared local frame, cross-artifact facts, mandatory recorded process predicates, and whether required evidence is independently available.

**Engineering acceptance:** 76 automated tests passed (35 inherited Stage 2 tests, 41 new Stage 3 tests); 12/12 authored Stage 1 reference cases matched their expected verdict + decision status; 6/6 fresh local controlled workflow runs matched their expected decisions. These are authored software acceptance cases rather than independent research experiments.

## 1. Architecture: what was added

```text
Contract + Registered Probes             Quiescent controlled workflow
             |                                      |
             |                          Stage 2 independent evidence
             |                           - SQLite + file snapshots
             |                           - Read-only fact probes
             |                           - Trace readout, frame diff
             +------------------------+-------------+
                                      |
                           Stage 3 evidence validation
                    hash, scope, epoch, trust, probe registry
                                      |
                         Contract predicate evaluator
                          - outcomes and counts
                          - cross-artifact facts
                          - complete-frame accounting
                          - recorded process clauses
                                      |
                        Three-valued verdict arbiter
                           PASS / FAIL / UNCERTAIN
                                      |
                       JSON verification certificate
              per-obligation reasons + evidence refs + costs
```

The engine is implemented in `aura_verifier/engine.py`, driven by `verify_task.py`. It reuses the Stage 2 `aura_evidence` infrastructure; Stage 1 JSON schemas remain unchanged. This is **conservative** atomic-predicate evaluation, not the future bounded-exact possible-world solver or the adaptive CERA planner.

### Evidence admission

A live verification requires a valid Stage 2 initial/final snapshot pair; observation records must agree with registered probes and run/epoch identity and pass canonical SHA-256 checks. Snapshot coverage receipts must refer to the actual captured pair. Untrusted agent self-reports are not admitted as authoritative facts.

A separate reference-fixture pathway tests the same decision rules using *preauthored synthetic facts*. This pathway is explicitly labeled non-operational and must not be confused with live verification.

### Atomic task contract checks

Operators: `eq`, `neq`, `true`, `false`, `count_eq`, and `same_as`. `count_eq` requires a genuine nonnegative integer (a boolean is not an integer count). Cross-artifact `same_as` does not accept two null values as proof of consistency.

In `closed_world` frame mode, the contract must include declared zero-unaccounted-mutation predicates covering every declared mutable surface. Their PASS also requires independently validated **complete** receipts. Snapshot-pair evidence covers persistent before/after differences; a transient side-effect claim requires a separate complete journal, which Stage 2 does not yet provide.

### Verdict and diagnostics

- **PASS:** Every declared obligation is supported, with required complete-frame evidence.
- **FAIL:** At least one verified predicate is false, even when other obligations are unobservable.
- **UNCERTAIN:** No known contract failure but one or more required facts/coverage witnesses are missing, or independently trusted same-epoch facts contradict.

A same-epoch evidence conflict is reported as `UNCERTAIN / evidence_conflict` rather than a vacuous proof from incompatible observations. The certificate records contract hash, evidence IDs, each obligation's status, unresolved IDs, verified surfaces, reasons and measured inspection/capture cost.

## 2. Stage 1 specification acceptance cases

| Case | Scenario | Expected | Stage 3 | Check |
|---|---|---|---|---|
| 01 | Complete success | PASS | PASS | Matched |
| 02 | Missing report | FAIL | FAIL | Matched |
| 03 | Unrelated mutation | FAIL | FAIL | Matched |
| 04 | Duplicate target record | FAIL | FAIL | Matched |
| 05 | Unobservable notification | UNCERTAIN | UNCERTAIN | Matched |
| 06 | Known wrong marks plus unknown notification | FAIL | FAIL | Matched |
| 07 | Insufficient full-frame coverage | UNCERTAIN | UNCERTAIN | Matched |
| 08 | Contradictory independent values | UNCERTAIN / evidence_conflict | UNCERTAIN / evidence_conflict | Matched |
| 09 | Missing required validation | FAIL | FAIL | Matched |
| 10 | Unobservable transient effect | UNCERTAIN | UNCERTAIN | Matched |
| 11 | Permitted alternate path | PASS | PASS | Matched |
| 12 | Unobserved external frame | UNCERTAIN | UNCERTAIN | Matched |

These **12 synthetic fixtures** deliberately contain authored facts, not verified database execution. The verifier **does not import** fixture `reference_possible_worlds` or harness-only actual-world labels. Its PASS statements for these examples establish compatibility with the authored evidence/contract semantics only.

**Fixture-hash compatibility correction:** 52 original Stage 1 synthetic observation hashes did not match the canonical Stage 2 digest algorithm. Stage 3 generates test-only fixture copies with corrected hashes; all facts, expected outcomes and contracts are unchanged. The original Stage 1 file package remains intact. A full old/new hash audit is included as `docs/STAGE1_FIXTURE_HASH_COMPATIBILITY.json`.

## 3. Six independently captured *local* demonstration runs

| Scenario | Stage 3 decision | Main reason |
|---|---|---|
| Clean workflow | PASS | All declared predicates and frame coverage supported |
| Missing report | FAIL | Required report is absent and comparison false |
| Collateral state change | FAIL | Extra out-of-frame persistent difference |
| Silent no-op | FAIL | Tool reported success but the stored marks remained wrong |
| Denied readback | UNCERTAIN | Required marks/count fact unavailable |
| Missing validation | FAIL | Required validation event not recorded before the update |

Each run has its own captured SQLite database, workspace, before/after snapshots, structured observations, tool trace, capture manifest and final Stage 3 certificate. The result archive contains these files and a compact CSV. A single regeneration command is included in the implementation.

## 4. Tests and reproducibility

**Final suite: 76 passed**, including retained Stage 2 evidence-integrity tests and 41 Stage 3 verification tests. Negative cases test missing frame coverage, illegitimate frame rules, conflicting authoritative facts, forged snapshot refs, changed digest, cross-epoch records, self-reported success, transient-journal unavailability, impossible integer counts, and unsupported predicate operators.

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python run_demo.py --scenario clean --out ./test_clean
python verify_task.py --run ./test_clean --out ./test_clean/certificate.json
python verify_task.py --fixture tests/fixtures/stage1_inputs/08_conflicting_evidence
python reproduce_stage3.py --out ./stage3_regenerated
```

Use new output directories; create-once evidence records and certificate files are intentionally not silently overwritten.

## 5. Scientific claims and limitations

**What is demonstrated:** contract predicate evaluation over verified local evidence; independent persistent-state outcomes are used instead of tool-success claims; the engine correctly handles the staged acceptance examples; explicit uncertainty prevents guessing unobserved effects.

**What is not demonstrated:** arbitrary multi-step agent verification, global natural-language user-intent satisfaction, external provider outcome guarantees, adversarial isolation from a malicious privileged agent, complete detection of transient reverted changes, causal derivation proof, the bounded exact possible-world semantics, adaptive CERA inspection selection, benchmark superiority, or any publication-level novelty claim.

The harness is **cooperatively quiescent**, not a hardened distributed transaction system. SQLite backup is internally consistent, but the database and filesystem captures are not globally atomic. Snapshot/digest validation assumes evidence-store isolation; a hash alone is not source authentication. Unknown contracts or unsupported probes are rejected rather than silently certified.

## 6. Next milestone

**Stage 4 - Evidence Model & Logical Reasoning:** construct an obligation-to-evidence dependency model; add bounded compatible-world reasoning on small research instances; compare conservative versus bounded-exact outcomes; and test evidence indistinguishability and solver-indeterminate cases. The CERA adaptive inspector is **Stage 5**, not Stage 3.

**No GitHub commits or pushes have been made.**
