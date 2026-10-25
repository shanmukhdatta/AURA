# Table 2: Inspection Policy Efficiency and Planning Latency (64 Worlds per Policy)

| Inspection Policy | Worlds Evaluated | Average Probes | Probe Cost Units | Planner Latency (ms) | Soundness (FP / FF) | Recommended Operating Regime |
|---|---|---|---|---|---|---|
| `cera` | 64 | 1.88 | 3.25 | 0.3709 ms | 0.0% / 0.0% | Advantageous when probe execution cost > 10ms (distributed I/O, heavy sandboxes) |
| `greedy` | 64 | 1.88 | 3.25 | 0.0736 ms | 0.0% / 0.0% | Recommended for fast local databases where planner overhead matters |
| `fixed` | 64 | 1.88 | 3.375 | 0.0451 ms | 0.0% / 0.0% | Suboptimal probe efficiency; fixed order regardless of observations |
| `exhaustive` | 64 | 6.0 | 29.2 | 0.0895 ms | 0.0% / 0.0% | Worst efficiency; evaluates all probes even after decisive failure |
