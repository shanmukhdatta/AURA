# Stage 7 experiment design and status

Controlled paired study with 48 distinct authored contract/probe catalogues x 3 public prior regimes (uniform / 50% clean / 90% clean). Every policy sees the same contract, model, allowed read-only inspections and prior. Simulation oracle reveals only selected probe outcome, never world ID, to the decision policy. Exhaustive, fixed, greedy, counterexample-guided and bounded-exact policies produce comparable verdict/cost records.

13 local script-executed SQLite/file cases x 5 policies separately test end-to-end independent snapshots, trace, contract and certificate outputs. The reverted transient mutation is deliberately an unobservable negative control under the current persistent state contract; it proves a limitation rather than a clean-workflow guarantee.

48 authored templates are the task-level units; simulated worlds are repeated assignments, not independent empirical tasks. Bootstrap ranges resample authored templates and cannot justify SOTA statistical inference. Modeled marginal costs exclude common snapshots. Actual local wall-clock figures include the shared capture time and selection/readback costs.

Published public Agent-Diff JSONL contracts are useful for DSL compatibility research only. No authentic external agent execution, native scoring or general performance estimate was produced.

Stage 7 fix: preserve independently proven conservative FAIL on a bounded-model contradiction while ensuring a model contradiction can never produce PASS. All direct-observation conflicts remain UNCERTAIN.
