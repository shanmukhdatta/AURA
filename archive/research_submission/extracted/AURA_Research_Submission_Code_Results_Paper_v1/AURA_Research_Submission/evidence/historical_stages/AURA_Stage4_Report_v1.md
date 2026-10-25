# AURA - Stage 4: Evidence Model & Logical Reasoning

**Technical implementation and acceptance report** | 24 October 2026 | Version 1.0  
**Project:** AURA - Agent Uncertainty and Residue Arbiter  
**Research direction:** Counterexample-Guided Evidence Certification for Multi-Step AI-Agent Task Completion

## Executive outcome

Stage 4 adds **bounded compatible-world reasoning** to the already implemented Stage 3 conservative verification engine. It accepts the Stage 1 task contract and registered probes; admits independently collected and validated Stage 2 facts through the existing Stage 3 validation path; checks a **separately authored finite logical model**; and returns a Stage 1-compatible `Certificate` accompanied by a new `ReasoningLedger`.

**Acceptance result:** 115 automated tests passed (76 inherited, 39 new); all 12 authored Stage 1 reference scenarios matched the expected verdict and decision status, and all 6 newly captured local SQLite/filesystem workflows matched their expected decisions. A separately labeled synthetic model assumption demonstrates a conditional inferred PASS, **not proof that any real external notification was delivered**.

**Scientific status:** Controlled engineering acceptance only, not an independent external benchmark or demonstrated research novelty. CERA active probe selection remains Stage 5.

## 1. System architecture

```text
Stage 1 contract and probe registry             Stage 2 captured evidence
                 |                                          |
                 +---------------- Stage 3 validation ------+
                                             |
                      Authenticated-scope observations / coverage receipts
                                             |
Stage 4 independently authored model ------> Bounded world enumerator
  finite domains + declared constraints                 |
                                                Evidence-compatible worlds
                                                         |
                                    Obligation-by-world truth evaluation
                                                         |
                                  PASS / FAIL / UNCERTAIN, with safeguards
                                                         |
                                 Certificate + evidence dependency ledger
```

The Stage 3 verifier remains available unchanged to callers; Stage 4 uses an optional internal return of **already validated facts**. The Stage 1 certificate schema is unchanged and already permits the mode `bounded_exact`.

**Added module:** `aura_reasoning/model.py` (finite-model checks and enumeration), `reference_models.py` (testing-only model generator), `verify_bounded.py` (CLI), `reproduce_stage4.py` (end-to-end reproducibility), `BoundedWorldModel.schema.json`, `ReasoningLedger.schema.json`, and Stage 4 tests.

## 2. Logical semantics

For observed, independently admitted evidence `E` and a declared model `M`, let `K(E,M)` be **every assignment within the finite model domains** that satisfies both `E` and the constraints of `M`.

- **PASS:** `K(E,M)` is nonempty and every compatible world satisfies the entire declared contract, with required authentic mutation-coverage receipts.
- **FAIL:** `K(E,M)` is nonempty and every compatible world violates at least one contract obligation.
- **UNCERTAIN:** Both successful and failing worlds remain compatible with the observations; or required coverage is missing; or the model cannot be soundly evaluated.

Safety-specific cases:

| Condition | Outcome | Reason |
|---|---|---|
| Two trusted observations contradict | UNCERTAIN / `evidence_conflict` | Do not select a convenient observation |
| No world fits evidence and constraints | UNCERTAIN / `model_inconsistent` | Empty set must not imply vacuous PASS |
| Domain product exceeds declared cap | UNCERTAIN / `solver_indeterminate` | No partial enumeration presented as complete |
| Missing complete frame receipt | UNCERTAIN unless proven FAIL | Finite model cannot manufacture inspection coverage |
| Mixed success/failure worlds | UNCERTAIN | Observations are not sufficient to certify either |
| Every world violates task, each atomic obligation varies | FAIL | Joint contract failure can be established logically |

The model is **not** a source of independently measured truth. A model assumption such as `report_exists => notification_delivered` would usually be unjustified and must never be used as evidence of delivered communication without a trustworthy guarantee of that implication.

## 3. Recorded acceptance results

| Evaluation | Expected | Observed |
|---|---:|---:|
| Automated tests | All passing | **115 passed** |
| Authored Stage 1 reference cases | 12/12 | **12/12** |
| Fresh local controlled SQLite/filesystem runs | 6/6 | **6/6** |
| Observationally indistinguishable success/failure | UNCERTAIN | **UNCERTAIN** |
| Same-epoch evidence conflict | UNCERTAIN | **UNCERTAIN** |
| Inconsistent model/evidence | UNCERTAIN | **UNCERTAIN** |
| Model exceeding computation cap | UNCERTAIN | **UNCERTAIN** |
| Unobserved frame scope | Not PASS | **UNCERTAIN** |

**Detailed six-run comparison** (each run is a *new* sandbox with captured evidence):

| Case | Stage 3 | Stage 4 |
|---|---|---|
| Complete task | PASS | PASS |
| Missing report | FAIL | FAIL |
| Unrelated persistent mutation | FAIL | FAIL |
| Misleading success response / silent no-op | FAIL | FAIL |
| Denied authoritative readback | UNCERTAIN | UNCERTAIN |
| Mandatory validation skipped | FAIL | FAIL |

For the **12 standard authored fixtures and 6 new local runs**, Stage 4 agrees with Stage 3. This is the *correct* result: without additional independently justified relationships, bounded reasoning should not invent information or claim superiority.

An additional **synthetic logic-only demonstration** explicitly introduces the authored assumption `report exists => external notice delivered`. Stage 3 returns UNCERTAIN, whereas bounded logical evaluation returns a *conditional* PASS. The assumption is not valid in general; the example demonstrates entailment mechanics, **not a successful independently verified task**.

## 4. What the graph and reasoning ledger contain

The obligation graph tracks each contractual requirement, the fact keys necessary to evaluate it, potential registered probes, and required complete-coverage surfaces. This is a **static evidence dependency representation**, not Stage 5's active selection mechanism.

The `ReasoningLedger` records model and contract SHA-256 hashes, observed fact-key names, graph edges, counts of compatible/successful/failing candidate worlds, example success/failure witness assignments where available, decision status, assumption count and elapsed reasoning time. These witness assignments are illustrative *possible worlds*, never the hidden actual-world truth.

The Stage 4 reasoning latency is included in `certificate.costs.planner_latency_ms`, with a separately reported `stage4_reasoning_latency_ms` in the ledger. Existing capture and readback costs remain included.

## 5. Limitations and validity boundaries

1. **Finite-world conditionality.** Exactness holds only inside the declared small discrete model; the enumerator cannot establish that the model includes the actual world.
2. **Unvalidated assumptions.** An incorrect implication can produce an unjustified model-relative PASS. Assumptions must be independently documented, audited and frozen before held-out evaluation.
3. **No external ground truth.** The 12 reference inputs and 6 local scenarios are authored engineering acceptance cases. No third-party agent benchmark or blind mutation study has been run.
4. **Static observations.** Stage 4 never requests the next probe; active counterexample-guided inspection belongs to Stage 5.
5. **State scope.** Complete-frame guarantees depend on the Stage 2 declared surfaces and valid coverage receipts; reversed transient effects and unobserved external services remain outside guaranteed detection.
6. **Computational bound.** Brute-force finite enumeration is not scalable arbitrary SMT verification. Exhausting `max_worlds` returns UNCERTAIN.
7. **Model generation for examples.** The included reference model generator uses observable facts to create simple test domains. This is valid for software tests but must not be used to argue unbiased empirical gains.
8. **Security.** Hashes detect changes assuming an isolated evidence store; they are not protection against a fully compromised verifier host.

## 6. Reproduce and inspect

Unpack the implementation ZIP, then in its root run:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python reproduce_stage4.py --out ./fresh_stage4_results
python verify_bounded.py \
  --fixture tests/fixtures/stage1_inputs/05_unobservable_notification \
  --model examples/models/external_uncertainty_reference.json \
  --out ./my_stage4_certificate
```

Use fresh paths; output files are intentionally not silently overwritten. The results ZIP includes complete local sandbox captures, Stage 3/Stage 4 certificates, finite models, reasoning ledgers and `stage4_verification_summary.csv`. The code archive contains the tests and both new JSON schemas.

## 7. Next milestone

**Stage 5 - CERA Adaptive Inspection Planner.** Use the obligation/evidence model to choose the next *read-only* probe. Compare fixed, greedy, exact small-instance and adaptive strategies under matched contracts, available evidence permissions and **full capture + probe cost**. Establish whether targeted observations improve the cost-risk-coverage frontier. Stage 4 does **not** establish that result.

**GitHub status:** No commits or pushes performed.
