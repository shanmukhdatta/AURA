# Public Agent-Diff contract excerpts — LIMITATIONS

These five small assertion subsets were transcribed from specific records of the public upstream `test.jsonl`, as read through GitHub, on 2026-10-24. Task IDs: `box_145`, `box_125`, `box_146`, `box_119`, `box_126`. The `answer.assertions` fields retain the relevant public assertion semantics; most auxiliary metadata was intentionally omitted, and ignore-field lists were abbreviated or omitted. They are **not verbatim complete test records**. In particular, these excerpts are not the protected initial environment, complete runs, or official benchmark results.

Source: https://github.com/agent-diff-bench/agent-diff/blob/main/datasets/agent-diff-bench/test.jsonl
Original authors: Agent-Diff benchmark maintainers. See upstream repository for license and attribution requirements before redistributing complete data.

This local package only checks that the AURA adapter parses this shape and evaluates **authored diff fixtures** under clearly declared local semantics. Do not calculate or publish Agent-Diff model scores from these examples.

To import the complete source externally, download the published `train.jsonl` or `test.jsonl` yourself into a local folder (or mount it in a supported environment), then run the Stage 6 CLI with `--agentdiff-jsonl /path/to/test.jsonl`. No API key is required to parse local files. Running the benchmark itself requires separate upstream sandbox setup and actual trajectories.
