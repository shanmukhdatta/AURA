# Stage 5 - CERA Adaptive Inspection Planner

**Status:** Controlled software prototype and authored pilot only. No external agent benchmark has been executed.

## Core integration

Stage 5 extends, and does not replace, the four prior AURA stages:

- Stage 1: `TaskContract`, `ProbeSpec`, `Observation` and `Certificate` schemas.
- Stage 2: independent quiescent SQLite/filesystem capture and read-only probes.
- Stage 3: validated atomic predicate evaluation and independent frame coverage.
- Stage 4: finite-world compatibility, conditional entailment, three-valued verdicts.
- Stage 5: sequential inspection selection using only public model constraints and observations already acquired.

## Pre-inspection information boundary

The planner receives: reviewed contract, public finite model, full catalogue of available read-only probes (costs/coverage/fact keys) and earlier observations. It **does not** receive the hidden tested world, the scenario's expected label, or any unchecked final state.

`aura_planning.planner.FiniteInspectionProblem` is the symbolic reference. The benchmark simulation oracle alone maps a requested probe to values from the held-out actual world. The planner is a different function (`plan_next`) without world identity as an argument. Results and model assumptions are labeled synthetic.

In the actual Stage 2 integration, `live_runner.py` constructs the prior before inspections from Stage 1 contract expected-value neighborhoods plus the known initial (`S0`) SQLite marks value, **not the final (`ST`) marks**. Every selected Stage 2 Observation is independently checked, and the final verdict is delegated to `verify_bounded` (which itself uses full Stage 3 evidence admission). An inconsistent model leads to `UNCERTAIN`, never PASS.

## Five methods

1. `fixed`: predeclared, registered probe order, early stopping on decisive verdict.
2. `greedy`: additional unresolved contract fact keys plus mandatory frame coverage per declared cost, early stopping.
3. `cera`: cross-class (successful versus unsuccessful worlds) distinguishing pairs per cost, with a mandatory frame-coverage term; updates after every observation.
4. `optimal`: bounded dynamic programming maximizing probability of a decisive verdict before minimizing expected marginal probing cost; small models only.
5. `exhaustive`: collect all permitted independent inspections even when verdict was decided earlier. This is a reference, not a strong efficiency baseline.

The operational `CERA` implementation uses an exact finite prior but a heuristic, NOT an optimum. Neither CERA nor exact uses unseen test-case labels in deciding actions.

## Decision safety

- `PASS` only if every still-compatible world satisfies the contract **and** all required frame surfaces have complete coverage under successfully performed probes.
- `FAIL` if every still-compatible world violates the contract.
- `UNCERTAIN` otherwise, including empty compatible-world sets, insufficient frame evidence, missing probes or model inconsistency.
- The live Stage 4 `Certificate` is authoritative over any planning heuristic; a probe-selection guess can never override a certified UNKNOWN.
- In actual operation read-only inspections cannot create a separate external effect; this has not been verified for arbitrary third-party tools.

## Experiment boundaries

- Four **structurally similar** authored synthetic domains: records, orders, access, files.
- Four cost/constraint variants per domain; 240 (not statistically independent) finite model worlds.
- Five methods: 1,200 synthetic policy evaluations. Uniform prior makes failures very prevalent (roughly 15 of 16 worlds are failures in simple templates).
- Varying success prevalence (0.5, 0.9) is explicitly stress tested by reweighting the world prior and comparing cost under that same prior.
- Probe budgets 1/2/3 measure decision coverage; abstention is never reported as a correct binary classification.
- Six *actual sandbox* captures from `run_demo.py` evaluated independently with five policies (30 more evaluations). They use a common, already paid baseline capture per scenario.
- Synthetic cost units are **estimated marginal probe costs**, not real response latency or total verification cost. Live captures, probe latency, planner-selection time and Stage 4 reasoning costs are all separately reported. One-time capture costs must be accounted for in comparisons.

## Known limitations / reasons this does not demonstrate research novelty

1. The benchmark generator, evaluation models and valid outcome rules are authored together. It cannot establish unbiased performance or external generalization.
2. Boolean facts and tiny finite worlds exclude realistic probabilistic, temporal and semantic uncertainties.
3. The planner treats probes as deterministic; varying availability and conflicting observations are tested in the actual integration but are not modeled by the exact simulated policy.
4. All PASS outcomes require whole-frame capture/receipts; cheap targeted readback cannot replace that requirement.
5. Real six-scenario timings are far too small for stable performance or memory-overhead claims.
6. Fixed/greedy are already strong on this small task. The original CERA heuristic cannot be called SOTA, and may lose under other priors/cost structures.
7. Stage 5 does not incorporate a learned model, external API verifier, online LLM or independent agent benchmark.

## Interfaces

- `aura_planning.planner.run_policy(problem, actual_world_index, policy)`: **simulation-only**; never use benchmark oracle as operational verifier.
- `aura_planning.live_runner.run_live_policy(sandbox_dir, contract, probes, policy, ...)`: live protected snapshot/probe evaluation; returns Stage 4 certificate, inspections, measured costs and a conditional reasoning ledger.
- `reproduce_stage5.py`: creates a fresh complete results tree; refuses to overwrite prior evidence.
