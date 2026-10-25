# Gate G2 Status: PASS

## 1. Executive Summary
Gate G2 has executed completely and successfully achieved **PASS**.
The real AURA Stage 7 verification and certificate engine (`AURA_Stage7/aura_verifier/engine.py`) has been connected to AgentSynth environments via the new runtime adapter `AURA_Stage7/aura_external/agentsynth_adapter.py`.
The entire G2 test battery (8 comprehensive integration tests in `AURA_Stage7/tests/test_agentsynth_adapter.py`) passed in 1.11s.

## 2. Adapter Architecture & Design Guarantees
- **Independent Observation**: Captures consistent, read-only before/after SQLite snapshots via `capture_sqlite()`.
- **Inspection Noninterference**: Computes SHA256 of the on-disk world database before and after AURA evaluation; verified that AURA inspection never modifies or contaminates the database.
- **Ordered Tool Tracing**: Logs every tool call (`sql_query`), write-flag, raw SQL text, response, and error into an immutable trace.
- **Strict Closed-World Frame**: Automatically extracts table schemas and compares primary-key row/column edits against the pre-frozen task allowlist (`TASK_ALLOWLISTS` / `frozen_contracts_manifest.json`).
- **Cryptographic Certificate Engine**: Replays certificates through `verify()`, reproducing exact verdicts, reason codes, and obligation evaluations.

## 3. Test Battery Results
1. **Known PASS (`test_adapter_known_pass`)**:
   - Scenario: `raise-ticket-priority`
   - Oracle execution: Native score = 1.0, AURA verdict = `PASS`, issues = 0, authorized changes = 1.
2. **Known FAIL (No-Op, `test_adapter_known_fail_noop`)**:
   - Scenario: `raise-ticket-priority`
   - No actions taken: Native score = 0.0, AURA verdict = `FAIL`, reason = `outcome_predicate_violated`.
3. **Known FAIL (Silent No-Op, `test_adapter_known_fail_silent_noop`)**:
   - Scenario: `raise-ticket-priority`
   - Agent reports 'all done' but only executes read queries: Native score = 0.0, AURA verdict = `FAIL`. Agent self-reports are not trusted.
4. **Unauthorized Collateral Edit Divergence (`test_adapter_unauthorized_extra_divergence`)**:
   - Scenario: `raise-ticket-priority`
   - Agent correctly updates ticket 3 (`priority='high'`) BUT also performs unauthorized edit on ticket 2 (`priority='normal'`).
   - Native checker score = 1.0 (PASS, because it only checks ticket 3 and 1).
   - AURA verdict = `FAIL` (caught collateral mutation on ticket 2 with reason `out_of_scope_mutation`).
5. **Denied Readback (`test_adapter_denied_readback_yields_uncertain`)**:
   - When evidence readback is marked unavailable, AURA abstains with `UNCERTAIN` (`required_evidence_unavailable`).
6. **Noninterference Audit (`test_adapter_noninterference_check`)**:
   - Scenario: `clearance-discount`
   - Pre-evaluation DB hash strictly matches post-inspection DB hash.
7. **Certificate Replayability (`test_adapter_replayable_certificate`)**:
   - Replaying certificate with saved artifacts produces 100% identical verdict, reason codes, and obligation results.
8. **Security / Negative Controls (`test_adapter_tampering_negative_controls`)**:
   - Forged observation digest -> REJECTED (`ValidationError`)
   - Forged coverage receipt -> REJECTED (`ValidationError`)
   - Tampered snapshot -> REJECTED (`SnapshotError`)
