# AURA - Stage 5: CERA Adaptive Inspection Planner

**Technical implementation and controlled pilot report | October 24, 2026 | v1.0**

## Executive result

Stage 5 integrates an adaptive, counterexample-guided read-only inspection policy (CERA) with AURA Stages 1-4. It compares five methods on **240 authored finite-world episodes** (1,200 policy evaluations) and on **six real local SQLite/filesystem captures** (30 additional policy evaluations). The complete regression suite passes **153 automated tests**. All 30 local evaluations match independently authored scenario expectations.

The central result is **modest**: under the uniform finite-world benchmark, CERA averages **3.630 normalized marginal inspection cost units**, compared with **3.710 for fixed order**, **3.792 for greedy fact coverage**, and **3.597 for the exact small-instance optimizer**. An exhaustive checker uses **30.273** units. The improvement over fixed order is only **2.15%** and must not be characterized as significant without stronger evidence. These cost units are modeling assumptions, not milliseconds.

## 1. System architecture and correctness boundary

Previous components are reused rather than reimplemented: Stage 1 formal contracts and JSON schemas, Stage 2 independently captured state and read-only probes, Stage 3 contract verification and mutation frame checks, and Stage 4 bounded possible-world reasoning. Stage 5 adds `aura_planning/planner.py`, `examples.py`, and `live_runner.py`.

**Input:** A reviewed task contract, predeclared bounded model, observation permissions and estimated probe costs, and only the evidence already independently collected.

**Output:** Selected read-only probes, a Stage 4 verified PASS/FAIL/UNCERTAIN certificate, the trace of inspections, model-relative reasoning records, and actual/estimated cost accounting.

**Key separation:** In the synthetic simulator, only the observation oracle receives the hidden actual-world index; the selection API `plan_next(...)` does not. For real local captures, the initial-state S0 mark (70) is admitted into the finite model before any final-state inspection; the final state S_T and expected scenario label are not passed to the planner.

**PASS safety:** Even when all currently possible worlds look successful, AURA requires independent complete-frame coverage of every declared mutable surface. A known violation can be FAIL without inspecting unrelated surfaces. Inconsistent evidence, model undercoverage and unreachable outcomes return UNCERTAIN, never vacuous PASS.

## 2. Implemented policy baselines

- **Fixed early-stop:** Registered inspection order; stop on a decided verdict.
- **Cost-greedy early-stop:** Greedy marginal unresolved fact and coverage benefit per estimated unit cost.
- **CERA:** Adaptive scoring of pairs of still-compatible successful/failing worlds separated by each probe, normalized by cost; mandatory frame coverage remains explicit.
- **Exact bounded:** Dynamic programming maximizes chance of a decisive verdict, then minimizes expected marginal cost. This is only for small finite models (maximum 9 probes and 500 worlds).
- **Exhaustive:** Executes every available probe, even after an earlier conclusive result; a costly reference, not a strong competitor.

All methods receive the same catalogue, model assumptions, costs, evidence privileges, and contract. No policy is allowed to issue PASS solely from an agent status message.

## 3. Finite-world pilot results

**Authored test set:** Four domains (records, orders, access, files), four variants/domain and 12-16 enumerated worlds/variant = **240** world episodes, each run with all five policies. Four required boolean obligations include one mutation-frame obligation; six permitted probes include both redundant combined probes and a full-frame inspection. These are structurally similar artificial tasks, not 240 independent real-world agent workflows.

| Policy | Mean marginal cost | Mean probes | Decisive coverage | False PASS | False FAIL |
|---|---:|---:|---:|---:|---:|
| fixed | 3.710 | 1.93 | 100% | 0 | 0 |
| greedy | 3.792 | 1.80 | 100% | 0 | 0 |
| cera | 3.630 | 1.93 | 100% | 0 | 0 |
| optimal | 3.597 | 1.80 | 100% | 0 | 0 |
| exhaustive | 30.273 | 6.00 | 100% | 0 | 0 |

**Interpretation:** The small model gives all algorithms exact deterministic probe outcomes and a model that contains the actual test world. This makes zero false decisions an engineering soundness check, not proof of general AI-agent reliability. The high fraction of failed synthetic worlds makes early stopping unusually attractive. Estimated marginal cost omits the shared initial snapshot cost; the local integration reports that separately.

## 4. Stress testing and negative results

We reweighted the same worlds with an explicit public prior giving successful worlds 50% or 90% total probability. There was no change in the actual model or probe catalogue.

| Policy | Expected cost, clean prior 0.5 | Expected cost, clean prior 0.9 |
|---|---:|---:|
| fixed | 7.794 | 11.559 |
| greedy | 7.715 | 11.543 |
| cera | 7.715 | 11.543 |
| optimal | 7.442 | 10.986 |
| exhaustive | 29.200 | 29.200 |

**Negative finding:** Under these cleaner-environment priors CERA **ties cost-greedy** and does not match the exact small-instance optimum. We also tested a 1/2/3-probe budget; mean decision coverage was respectively 50%, 75%, and 87.5% for every policy on these four test templates. AURA's UNCERTAIN verdict remains explicit under the budgets. There is no claim of superiority on these stress controls.

## 5. Local integrated verification

The six Stage 2 controlled tasks are: correct completion, missing report, unrelated persistent modification, silent tool no-op, denied authoritative readback, and missing mandatory validation. Each is captured from a new local SQLite/filesystem run. The five methods then inspect the same frozen task evidence and use Stage 4 as the authoritative verifier.

**All 30 of 30 results matched expected verdicts:** clean PASS, four invalid-state/process examples FAIL, and denied-readback UNCERTAIN. No independent LLM-agent benchmark has yet been used.

| Policy | Total probes across six tasks | Mean estimated marginal probe cost (ms) | Mean selection overhead (ms) |
|---|---:|---:|---:|
| fixed | 18 | 17.700 | 0.029 |
| greedy | 18 | 14.783 | 0.054 |
| cera | 18 | 14.783 | 0.861 |
| optimal | 18 | 14.783 | 2.109 |
| exhaustive | 24 | 26.000 | 0.017 |

**Cost caveat:** The estimates in the table are predefined adapter cost parameters, not measured latency. Measured probe and planner latencies and the common snapshot cost are recorded in `local_live_policy_results.csv` and individual certificates. On this tiny environment, CERA's additional selection overhead can outweigh probe-time savings. No credible system-level speedup is established.

## 6. Quality assurance and reproducibility

- **153 automated tests passing**, including 115 inherited regression tests and 38 Stage 5 tests (finite-model planning, coverage, failure-dominance, no hidden-world leakage, exact comparison, budgets, invalid models, real Stage 2 replay, and all 30 integration decisions).
- Stage 4's validated Observation admission and Stage 1 Certificate shape preserved. No direct arbitrary fact injection from the planner.
- Every result includes the selected probes, stepwise state of uncertainty, policy, and costs; live results contain the verification certificate and bounded reasoning ledger.
- `reproduce_stage5.py` refuses to overwrite nonempty output directories; it regenerates simulations, prior-shift tests, budget controls, and six local execution captures.

**Reproduction:**

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python reproduce_stage5.py --out ./fresh_stage5_results
```

The synthetic summaries should reproduce numerically on subsequent runs. Fine-grained wall-clock milliseconds may vary due to machine load.

## 7. Limitations, threats and required next stage

1. The benchmark has 240 enumerated **world assignments**, not 240 independent workflows. All four domains share closely related Boolean structures. The fault model and successful contract are co-authored; external validity is untested.
2. Four small Boolean obligations do not capture realistic semantics, long-horizon causal provenance or unobserved external effects.
3. The exact optimizer assumes deterministic probe results and a correctly specified prior. It is computationally limited to tiny cases.
4. Original CERA's separation heuristic may be tied or beaten by greedy under other conditions; it is not SOTA or proven optimal.
5. Whole-frame completeness and trustworthy snapshots remain assumptions. No claim covers transient reverted effects or external services outside the declared boundary.
6. Stage 5 does not show statistically significant or practically meaningful advantage over strong heuristics on external tasks. Our earlier aspirational 25% cost improvement target was **not met** against fixed or greedy in this pilot.

**Stage 6 priority:** adapt to externally sourced tasks and trajectories (AppWorld / Agent-Diff as compatible), add information-matched state-only/trace-only and targeted-evidence baselines, construct held-out fault mixtures with blind ground truth, and evaluate overall capture + planning + inspection costs. Only after that can we judge whether CERA is a research contribution or an illustrative engineering implementation.

**Repository:** No GitHub commits or pushes were made; the link supplied by the user is not required for this standalone Stage 5 implementation.
