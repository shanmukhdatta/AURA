# AURA Stage 8.1 — AppWorld v7 independent results audit

**Evidence:** User-provided `AURA_APPWORLD_STAGE8_1_v7_RESULTS.zip` (25 October 2026). This is the uploaded v7 benchmark result, not a synthetic dry run.

## Study status

- Setup: `PASS` (Python 3.11, official AppWorld `0.1.3.post1`, 57 published dev task IDs, verified task-data tree, evaluator preflight).
- Model: `Qwen/Qwen2.5-3B-Instruct`, inference only; 7-step maximum; 300 new tokens per generation; three consecutive dev examples `50e1ac9_1`, `50e1ac9_2`, `50e1ac9_3`.
- All three task worlds genuinely ran and returned official evaluator summaries. **0/3 official task successes.** These are all from the same task family, not representative of the full 57-task split.
- Official subtests: one of two passed per task, **3/6 in total**. However, the corresponding no-action baseline also passes exactly one of two per task (**3/6**), so this is **zero improvement over no-op** and not evidence of partially successful agent problem solving.
- No external AURA certificates are present. The official scores validate AppWorld outcomes only, not AURA's independent verification on AppWorld.

## Per-task outcomes

| Task | Inference turns | Runtime errors | Native API log calls | Official evaluator | No-op baseline | Analysis |
|---|---:|---:|---:|---|---|---|
| `50e1ac9_1` | 2 | 1 | 1 | 1/2; success=False | 1/2 | Invented `spotify__get_top_rnb_songs`; then called `supervisor.complete_task` with an inability statement. Completing the supervisor API is not a successful user task. |
| `50e1ac9_2` | 3 | 2 | 2 | 1/2; success=False | 1/2 | Invented `spotify.show_top_tracks`; submitted a hardcoded list, initially with an invalid API argument type, then converted it to a string. No supported Spotify information retrieval was recorded. |
| `50e1ac9_3` | 7 | 7 | 0 | 1/2; success=False | 1/2 | Repeated invalid `spotify.show_top_tracks` calls seven times, never called complete_task, and logged zero successful native API calls. |

## Integrity checks

- Archive CRC test passed; manifest is a list of SHA256 and byte-length claims for research artifacts.
- Manifest entry count: **29**; archive member count: **31**; unmanifested supporting members: `FILE_MANIFEST.json`, `README.txt`.
- Every manifest SHA256 and file length verified against the uploaded archive. Native log bytes and record counts matched each task's evidence-status record.
- The third task's empty official API-call log is an authentic *zero-call observation*, not missing file evidence.
- No independent replay of AppWorld's evaluator was possible from the curated archive because benchmark DB state and hidden test ground truth are intentionally excluded. Therefore we can validate the *consistency and provenance claims of the saved official results*, not independently recompute official scores.

## Methodological interpretation

1. The original v6 setup failure is resolved; this is the first completed genuine external AppWorld run in AURA Stage 8.1.
2. The **agent baseline failed 3/3 tasks** and offered no measured improvement over the no-action control. The agent often hallucinated nonexistent APIs or answers; the supervisor completion method is not equivalent to task achievement.
3. The worker's `get_context` implementation ranks at most 3 apps and caps generated API documentation at 14,000 characters; actual prompt content is not saved, only a SHA256 hash and byte count. The model states that Spotify documentation is missing, but **the archive does not prove whether the relevant documented Spotify endpoints were omitted or merely ignored**. A documentation-coverage audit is required before judging model quality.
4. First three dev IDs share generator prefix `50e1ac9`, and hence represent a narrow task family rather than broad AppWorld coverage.
5. No AppWorld-to-AURA contract/probe adapter was run; external independent verification accuracy, calibration and efficiency remain **not measured**.

## Next experiment — no blind retraining

- Keep the v7 ZIP immutable as a negative external agent-baseline result.
- Run a *CPU-only documentation preflight* which exports (a) the exact context shown to the model or a redacted equivalent, (b) names and argument schemas for Spotify and supervisor APIs that AppWorld exposes, (c) an explicit list of API names retained after truncation, and (d) whether tasks require authorization and which API calls support it. Never include test answers or evaluator ground truth.
- If documentation is incomplete, repair app-specific API selection and prompt construction and test one dev task before scaling up. Require agents to **never invent tool names or answers**, inspect documentation or call available documented lookup methods, and stop looping on a proven-invalid API.
- Diversify task selection across generator prefixes and functional app families with a predeclared seed and task IDs; avoid choosing three nearly identical tasks for headline conclusions.
- Build the external **AURA verification adapter** with per-task contracts, admissible read-only final-state probes, trace obligations and verified uncertainty cases, evaluated *separately* from AppWorld's official scores. Use official evaluators only as reference labels after AURA decisions are recorded.

## Research claim allowed now

> A lightweight custom agent baseline (Qwen2.5-3B-Instruct, seven-step limit, v7 prompt/API routing) was evaluated on three official AppWorld development tasks. The native evaluator reported zero complete successes; in each case the one of two tests passed under both the agent and no-action control. The pilot yielded genuine external agent traces but no external AURA verdicts. Therefore the pilot supports diagnosis and adapter development, not yet an external AURA verification success claim.
