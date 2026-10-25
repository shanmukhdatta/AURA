# Stage 8.2 external SQL pilot — executed results

**Execution date:** 2026-10-25. **Class:** scripted oracle/fault injection on *externally authored* AgentSynth `core_v2` SQL tasks, with actual isolated SQLite state changes and independent AURA Stage 7 certificate verification. **Not** genuine model-generated external trajectories; **not** the official AgentSynth CLI benchmark.

## Executed design

Six selected tasks: `raise-ticket-priority`, `clearance-discount`, `refund-and-restock`, `cancel-and-void-payment`, `store-credit-return`, and `reconcile-stock`.

For each, six preregistered controlled variants were executed: original oracle, no-op, silent no-op falsely reporting tool success, incomplete last write, unauthorized extra write, and denied verifier readback.

| Controlled variant | Trials | PASS | FAIL | UNCERTAIN |
|---|---:|---:|---:|---:|
| Published oracle | 6 | 6 | 0 | 0 |
| No work performed | 6 | 0 | 6 | 0 |
| Falsely successful tool response | 6 | 0 | 6 | 0 |
| Missing final mutation | 6 | 0 | 6 | 0 |
| Extra unauthorized persistent modification | 6 | 0 | 6 | 0 |
| Readback intentionally withheld | 6 | 0 | 0 | 6 |
| **Total** | **36** | **6** | **24** | **6** |

All 36 matched the **designed control expectations**. This is not 100% accuracy on independent model failures.

The reproduced original SQL outcome-only predicates passed all six unauthorized-extra cases, while AURA's separately authored stricter frame contract rejected all six. This is a different-policy comparison; neither party is inherently defective. When both probes were removed, AURA issued 36 UNCERTAIN certificates. A total of 144 ablation certificates reused the same 36 states.

## Integrity and fresh reproduction

- Original Stage 7 inherited suite independently rerun: **186 passed** in ~17–18 s.
- Stage 8.2 source re-executed from clean output directory: **36 cases**, 6 PASS / 24 FAIL / 6 UNCERTAIN, zero mismatches, ~4 s.
- Original evidence archive verified: 331 ZIP members, CRC success, **330/330 SHA256 manifest entries match**, no missing members.
- Reported certificate replay matched 36/36. Three deliberate forged/tampered-evidence inputs were rejected.
- **No GPU was needed** for Stage 8.2; no model inference was run and no CERA cost superiority is claimed.

## Historical artifact hashes

`AURA_Stage8_2_External_SQL_Source_v1.zip` SHA256: `a8d5c9219f5ec6ffb77b9e3028facf4717c1e8d759fab7ad5d0106e5e8c81f2b`

`AURA_Stage8_2_External_SQL_Evidence_v1.zip` SHA256: `d3d50978c72fde8422416fbecd1ee18c28523629ac9e4248049952131f40507b`

`AURA_Stage8_3_Antigravity_Full_Handoff.zip` SHA256: `784fd8571dae33e138bb7b17c6d4a3f7366c1bc52239e6e2e79008d42f4eb95b`

**Upload status:** This GitHub document records the findings, but the above original ZIPs are provided as downloadable ChatGPT artifacts and **have not yet been committed to GitHub**. The Antigravity Stage 8.3 prompt instructs the agent to add the reviewed source and publish appropriately sanitized evidence through a feature branch.

## Upstream sources

[AgentSynth](https://github.com/agentsynth/agentsynth), `packs/core_v2.yaml` blob `d2bee0100fc46c58bbbe73b94d921b3e6c9f7a7a` and `packs/core_v2_oracle.py` blob `942c296fadd47c7ec335355af39de05db9f7024a`. Manual transcription was used; Stage 8.3 must freeze full upstream commit and load the original source automatically.

See `PROJECT_STATUS_AND_GATES.md` and `STAGE_8_3_ANTIGRAVITY_PROMPT.md` for next gates.
