# AURA Stage 4 - Evidence Model & Logical Reasoning

**Version:** 0.4.0 | **Status:** implemented in a controlled local research prototype, 24 October 2026.

## 1. Architectural purpose

Stage 3 conservatively evaluates independently admitted atomic observations against a contract. Stage 4 adds **finite compatible-world reasoning** over an externally declared, bounded `BoundedWorldModel` and emits a separate `ReasoningLedger`. It does **not** choose or perform additional inspections; counterexample-guided adaptive probing belongs to Stage 5.

```text
Stage 1 TaskContract + registered ProbeSpecs
                 |                      Stage 2 evidence
                 +---------------> Stage 3 validation
                                         |
                              admitted independently trusted facts
                                         |
Finite researcher-authored model ----> Stage 4 candidate worlds
     domains + constraints               |    and obligation/evidence graph
                                         v
                          W(E) = candidate worlds compatible with E
                                         |
                           contract truth evaluated for each world
                                         |
                           PASS / FAIL / UNCERTAIN (conditional)
                                         |
                          Stage 1 Certificate + ReasoningLedger
```

## 2. Semantics

Let `K(E,M)` denote the set of worlds obtained by enumerating **every value assignment within the finite domains declared in M**, retaining only assignments that satisfy **both independently admitted facts E and the model's declared logical constraints**.

- `PASS` when `K` is nonempty and all worlds satisfy all task obligations, **and** the Stage 3 evidence validator confirms any independently required frame/trace coverage.
- `FAIL` when `K` is nonempty and every compatible world violates at least one task obligation.
- `UNCERTAIN` when `K` includes both successful and failing worlds, when required coverage cannot be established, or if the input is conflicted, model-inconsistent, or the enumeration budget is exceeded.

Critical special cases:

- Trusted conflicting same-epoch observations produce `UNCERTAIN / evidence_conflict` **before** reasoning.
- Empty `K` produces `UNCERTAIN / model_inconsistent`. An empty candidate set must never yield vacuous PASS.
- Raw Cartesian domain size above `max_worlds` produces `UNCERTAIN / solver_indeterminate`. No incomplete enumeration is represented as exact.
- A definite violation can logically follow from the **conjunction** even if no single obligation's truth value is fixed over all worlds.
- Model assumptions are not independently verified; PASS based on an authored implication is a *conditional finite-model result*, not confirmation of an external action.
- Complete mutation-scope accounting requires the authentic Stage 2 coverage receipts. Bounded assumptions do not fabricate missing receipts.

## 3. Data structures and modules

- `aura_reasoning/model.py`: input validation, relation grammar, graph construction, world enumeration, Stage 3 admission integration, verdict refinement, reasoning ledger.
- `aura_reasoning/reference_models.py`: **test-only** finite-domain model generator, never hidden-world truth. Models derived from observations are for compatibility tests only, not a valid independent prior for unbiased research experiments.
- `schemas/BoundedWorldModel.schema.json`: `schema_version`, `model_id`, finite scalar `fact_domains`, `constraints` with `fact_eq`, `fact_same`, `not`, `and`, `or`, `implies`, and integer `max_worlds`.
- `schemas/ReasoningLedger.schema.json`: model/contract hashes, support graph, world counts, example compatible success/failure worlds, diagnostics and measured reasoning time.
- `verify_bounded.py`: explicit model-file CLI for a Stage 1 fixture or a Stage 2 saved run; creates new certificate and ledger files.
- `reproduce_stage4.py`: generates fresh controlled evidence and reference fixture comparisons.

The Stage 1 certificate schema already allows `mode=bounded_exact`; it is unchanged. The original Stage 3 `verify` entrypoint is unchanged for existing callers. An internal optional `return_context=True` exposes **validated** facts to Stage 4, not hidden oracle values.

## 4. Limits of the mathematical guarantee

The verdict is **exact within the finite model that the researcher has explicitly supplied**, and only insofar as that model covers the relevant task properties. It is not a universal proof of task completion. An unsupported or inaccurate model constraint can force a spurious model-relative PASS; the full-world reality may differ. A finite-domain closed-world assumption is therefore a **trust and adequacy assumption**, not something proved by enumeration.

The implementation is deliberately limited to scalar finite variables, a small propositional formula grammar and brute-force enumeration. Large domains, external services, adversarial agents, real-time concurrent writes, hidden side channels, and generalized SMT solving are not supported.

The reference generator may freeze an observed value into a singleton domain; this is acceptable for regression testing but **must not** be used as a blinded benchmark model because it would mix data-dependent domain design with evaluation.

## 5. Implementation validation (not research benchmark)

- **115 automated tests** passed (76 inherited Stage 3 tests and 39 new Stage 4 tests).
- **12 of 12 authored Stage 1 reference fixtures** matched expected verdict and status under a test-only finite model.
- **6 of 6 freshly generated local sandboxes** matched the expected Stage 3 verdicts under a test-only finite model.
- A **synthetic, explicitly questionable implication** changed one unknown notification result to a conditional model-relative PASS. It is included solely to demonstrate logical entailment. The report must not portray it as independent verification of a delivered notification.
- Counterexample-twin case: a model can retain one task-success world and one task-failure world with identical observed evidence. Verdict is correctly UNCERTAIN.
- Joint entailment case: a model can prove global FAIL even when two individual obligations are unresolved. This requires assumed relationships and cannot be interpreted as an observed failure without independent justification of those relationships.

## 6. Cost and artifact accounting

Stage 4 reasoning latency is measured and added to `certificate.costs.planner_latency_ms` (the existing Stage 1 field); a separate exact `stage4_reasoning_latency_ms` appears in the ledger. Earlier Stage 2 capture and inspection costs remain included.

Hashes link the certificate to the authored model. They provide integrity checking under protected evidence-store assumptions; they do **not** authenticate a malicious or compromised host.

## 7. Reproduction

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python reproduce_stage4.py --out ./stage4_fresh_results
python verify_bounded.py \
  --fixture tests/fixtures/stage1_inputs/05_unobservable_notification \
  --model examples/models/external_uncertainty_reference.json \
  --out ./stage4_single_case
```

Use *fresh* output paths. No network, model API, GPU, or production secrets are required.

## 8. Next stage

**Stage 5 - CERA Adaptive Inspection Planner:** The fixed evidence-obligation dependency graph will become the planning input; develop exact small-world selection, strong static/greedy baselines and adaptive selection **with the same probe catalogue, costs and evidence permissions**. Stage 4 has not demonstrated an inspection-cost advantage.

**GitHub:** No commit or push performed.
