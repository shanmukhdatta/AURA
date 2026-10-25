# AURA: project status, evidence and Stage 8.3 gates

**Verified on 25 Oct 2026.** The project's real objective is independent evidence-gated verification of multi-step AI-agent completion (end states, mandatory process events and unauthorized persistent side effects) with PASS / FAIL / UNCERTAIN.

## Recorded results, with exact scope

| Work | Completed | Limits |
|---|---|---|
| AURA core through Stage 7 | 186 regression tests passed on a fresh rerun (about 18 s) | Research prototype; not production assurance |
| Stage 8.1 local Qwen2.5-3B | Four model-driven local SQL/file tasks, 4/4 verdict/reference agreement | Same four designed test cases, not general agent accuracy |
| Stage 8.1 AppWorld | 3 official dev tasks executed, 0 successes, 12 model execution attempts | **0 independent AURA certificates on AppWorld**; agent hallucinated tool APIs |
| Stage 8.2 external AgentSynth SQL subset | 6 published SQL task definitions, 6 scripted execution variants each, real SQLite before/after snapshots, 36 AURA certificates | **Not** naturally occurring LLM trajectories or the official AgentSynth scoring CLI |
| Stage 8.2 inspection ablation | 144 certificates on same 36 states under four evidence-access conditions | Not 144 independent workflows; CERA cost not tested |

**Stage 8.2 verdicts:** Oracle 6 PASS; no-op 6 FAIL; fake tool success 6 FAIL; partial work 6 FAIL; unauthorized extra edits 6 FAIL; denied readback 6 UNCERTAIN. 36/36 agreement is against predesigned injection expectations.

**Important comparison caveat:** In six deliberately injected extra-write controls, the *reproduced upstream SQL outcome predicates* passed but AURA's *stronger locally authored full-frame policy* failed. This shows value of that explicitly stricter contract, not superiority over a baseline given the same rules.

**Integrity:** Historical report states 36 certificate replays, six-task original SQL comparisons, three forged/tampered-input rejection tests. Archive includes hashes, snapshots, contracts, probes and tool traces. The inherited Stage 7 tests reproduced at 186/186; CPU Stage 8.2 reproduction took about four seconds.

## Bottlenecks and corrections

- Stage 8.2 did **not** require GPU, LLM weights or paid APIs; no current computation failure.
- Earlier AppWorld effort was blocked by Python/dependency, then data-root configuration; fixed by v7. Low agent success on v7 is not AURA verifier failure.
- Must stop conflating official benchmark success, model task success, and AURA certificate accuracy.
- Tasks were manually transcribed and purposively selected (6/14); verify/parse pinned upstream source automatically.
- Need to use original AgentSynth CLI scorer, not only our reproduction of its SQL checks.
- Require independently written task contracts and allowed-write rules *before* looking at test outputs; include fair full-state comparator subject to identical rules.
- The Stage 8.2 adapter supports selected scalar SQL predicates and enumerated persistent SQLite frame state; it cannot prove absence of reverted interim writes or unobserved external side effects.
- Source-linked evidence hashes prove internal consistency, not trusted remote execution provenance. The observation adapter is a trust boundary.
- No CERA empirical cost advantage was established by the Stage 8.2 study. A prior 4-case timing pilot suggested planner overhead can make it slower than greedy.

## Stop/go gates for Stage 8.3

G0: Re-run inherited tests 186/186 and audit/replay the original Stage 8.2 evidence, no edits to history.

G1: Install and pin upstream AgentSynth, enumerate full core_v2 task pack, run its original evaluator on published oracle and do-nothing controls with raw results saved.

G2: Implement read-only external SQLite capture, immutable before/after state and trusted trace logs. Predeclare contract permissions; generate actual AURA certificates from observed facts *without benchmark labels*. Tests must show repeatable certificate replay, readback denial -> UNCERTAIN, noninterference and rejection of forged evidence.

G3: Run 5 real-model external task smoke trials (not mock). If successful, expand to 14 official tasks with preregistered seeds subject to the available GPU budget. Record actual model actions. Model failure is useful evidence, not reason to fabricate success.

G4: Blind-label comparison after AURA predictions are saved: native scorer, independently checked strict contract, equal-policy full-snapshot baseline, per-task metrics, false PASS / false FAIL, abstention and actual measured cost. Compare CERA only when readback and cost measurements are comparable.

G5: Reproducibility pack, SHA256 manifest, raw receipts, limitations, feature-branch PR. Do not force-push or merge without approval.

## Upstream provenance

AgentSynth: https://github.com/agentsynth/agentsynth

Stage 8.2 used `packs/core_v2.yaml` Git blob `d2bee0100fc46c58bbbe73b94d921b3e6c9f7a7a` and `packs/core_v2_oracle.py` blob `942c296fadd47c7ec335355af39de05db9f7024a`. Attribute the upstream dataset and retain license notices when redistributing their source.
