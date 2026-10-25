# Publication decision and optional next studies

## Is the existing evidence adequate?

**Adequate for:** a clearly labeled *preliminary engineering evaluation*, short research communication or technical note, subject to independent manuscript review and the venue's editorial decision. The system exists and has been run on real tool-using model episodes and scripted faults.

**Not adequate for:** general verification accuracy, universally low false accept rate, superior mean cost across real-world agents, a statistically supported model-size comparison, or security proof of all hidden side effects.

**Positioning:** a contract-aware, evidence-gated verification architecture with a reproducible prototype and preliminary diverse experiment results; highlight both effective failure detection and where independent inspection cannot decide.

## Highest-value additional experiments (optional, not blockers)

1. **Matched task and policy comparison**. Select a small set of the same 8–12 AgentSynth tasks, same tool contract and environment, run Qwen0.5B and 3B with fixed seeds and truly identical reference scoring; audit without label leakage. Do this only if claiming any model-dependent pattern.
2. **End-to-end native benchmark scoring of saved real-model episodes** (where importing existing trajectories into the published runner is supported). Compare its full checker result to reproduced SQL-only and strict AURA obligations; keep separate scores. This is CPU-oriented and better addresses a scientific gap than another GPU rerun.
3. **Verified transient mutation detection**. Add one trusted SQLite event/trigger audit journal or tool write log, test a change that gets restored before final state, and explicitly compare before/after-only versus journal-backed AURA. This would address a known blind spot and strengthen an observation-boundary claim.
4. **Fair measured-cost CERA challenge**. Run identical contracts/probe surfaces at simulated measured delays with wall-clock cost calibration; compare CERA against greedy including planner overhead. Do not predict a benefit merely from assumed remote costs.

**If the deadline is close:** do not run new Qwen experiments; finish reproducibility checks, correct references, official manuscript template layout, plagiarism/citation review, and author approval.
