# AURA research status and honest audit — 2026-10-25

## Where the project stands

AURA is a functional *research prototype* that verifies a declared multi-step task contract using independently collected evidence. It returns `PASS`, `FAIL`, or `UNCERTAIN` and can reject persistent unauthorized modifications when the inspected state surfaces are completely covered.

### Milestones supported by artifacts

| Stage | Verified work | What it does NOT prove |
|---|---|---|
| 0–7 | Contract schemas, snapshot/evidence capture, certificate engine, planning/baselines, 186 regression tests (fresh rerun: 186/186 in ~18 s) | Production-grade reliability or superior verification cost |
| 8.1 local | Four Qwen2.5-3B real-model *local* SQL/file workflows; certificate judgments matched local independent references | Statistically meaningful model/agent generalization |
| 8.1 AppWorld | Three official AppWorld dev tasks executed and evaluated; native task successes 0/3; 12 model execution attempts | AURA did not issue external AppWorld verification certificates |
| 8.2 AgentSynth SQL | Six externally authored SQL scenarios; 36 scripted oracle/injection cases; 6 PASS, 24 FAIL, 6 UNCERTAIN; all matched designed controls | Naturally occurring LLM errors, official AgentSynth CLI scoring, or external success rate |
| 8.2 inspection ablations | 144 dependent certificates: with both probes 6/24/6; outcome only 0/18/18; frame only 0/6/30; neither 0/0/36 | 144 independent tasks or independently sampled experiments |

The six SQL tasks were a *purposively selected* subset of AgentSynth's 14-task `core_v2` pack. Task schemas and original oracle SQL were manually transcribed with source Git blob IDs, and task-scoped write allowlists were authored locally.

### Key scoped result
In six deliberately constructed extra-write controls, the reproduced upstream SQL **outcome predicates** passed 6/6, but AURA's stronger contract rejected the unauthorized persistent modifications 6/6. This is a mismatch between contract coverage, NOT evidence that AgentSynth is defective or that AURA outperforms an equal-strength benchmark.

In six denied-readback controls, independently saved state was correct but the verifier received neither evidence channel and returned UNCERTAIN. This is a simulated permission refusal, not a real filesystem outage.

### Technical issues and computational bottlenecks

- **No Stage 8.2 GPU issue.** The 36-case CPU experiment reproduced in ~4 s in this sandbox; all 186 inherited tests passed again in ~18 s. Nothing was silently running after those calls ended.
- **AppWorld setup** previously failed first on Kaggle Python/package environment and then on an AppWorld root/path mismatch, now resolved in v7. v7 model tasks failed by hallucinating APIs/insufficient guided tool context; that was an *agent* failure, not a failed AURA certificate.
- **Stage 8.2 comparison fairness:** The reproduced upstream SQL predicates do not check all AURA-authorized side effects; use a matched-contract baseline in Stage 8.3.
- **Adapter scope:** Stage 8.2 checks selected scalar SQL outcome queries and enumerated SQLite table diffs; answer/refusal requirements, external services, transient writes, multiple rows, non-primary-key tables, hidden/non-enumerated state were not covered.
- **Trust:** Evidence digests show internal consistency but are not cryptographic remote attestations. A malicious/buggy observation adapter can compromise judgments.
- **Measurement:** No CERA verification-cost advantage has been demonstrated by the latest Stage 8.2 experiment. Previous Stage 7 modeled cost benefit was prior-dependent, and a Stage 8.1 tiny pilot showed worse CERA total times than greedy in some cases.
- **Risk of overclaiming:** All 36 cases were controlled faults sharing six base tasks; 36/36 is *designed-control agreement*, not independent real-agent classification accuracy.

### Necessary corrections before claiming a research benchmark result

1. Pin original AgentSynth full git commit, parse its 14-task YAML automatically, and run its **official scorer**. Keep labels hidden from AURA until predictions are persisted.
2. Predeclare row/column allowlists from task statements or independently written rules BEFORE looking at executions; review both task-contract bugs and grader gaps.
3. Acquire real model-generated SQL actions (not mock/default policy). Log actual SQL, tool arguments, results, wall-time, execution modes, and immutable before/after state.
4. Evaluate >=5-task smoke first, then all 14 if compatible; use multiple runs/seeds only if compute allows. Include oracle, do-nothing, and injected faults as separate controls.
5. Compare to official upstream score AND a fair baseline that checks the *same* obligations and side-effect restrictions as AURA. Report disagreements and false PASS rate. Do not conflate completion labels and process-label benchmarks.
6. Test evidence removals, replay failures, claims based on insufficient coverage, noninterference, and blind label comparison.
7. Only after valid verifier-side measurements, evaluate CERA versus fixed, greedy, and exhaustive policies with identical probe access, actual measured costs including planning overhead, across different priors.
8. Clearly distinguish executed, blocked, mocked and planned experiments in every report.

## Reproduction

The accompanying handoff archive has AURA Stage 7 source/tests and Stage 8.2 scripts. With Python >=3.10:

```bash
python -m pip install jsonschema pytest
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q AURA_Stage7/tests
python stage82_agentsynth_pilot.py --out stage82_repro --zip
```

If `stage82_repro` exists, delete it or supply a different empty directory. No model weights, network access, paid APIs or GPU are needed to repeat Stage 8.2.

**No further experiments run automatically in the background.** The next execution is Stage 8.3 and requires an agent/environment with network or locally staged upstream benchmark files.
