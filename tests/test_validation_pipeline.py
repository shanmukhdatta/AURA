"""Automated test suite for AURA external validation pipeline.

Tests all 12 core validation criteria required for external evaluation:
1. Correct task completion
2. Incomplete execution
3. False agent success claims
4. Unauthorized row/column changes (closed-world frame rule)
5. Correct refusal behavior (semantic evaluation)
6. Incorrect/contradictory refusal behavior (preventing naive keyword bias)
7. Missing evidence and UNCERTAIN decisions
8. Deterministic certificate replay
9. Corrupted or forged evidence detection
10. Validation noninterference (zero database side-effects)
11. Invalid/missing source artifact handling
12. Scoring concept and cohort separation
"""

from __future__ import annotations

import copy
import hashlib
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "AURA_Stage7"))
sys.path.insert(0, str(REPO_ROOT))

from aura_evidence.capture import SnapshotPair
from aura_evidence.util import digest
from aura_validation.cohorts import (
    load_all_cohorts,
    validate_stage7_local,
    validate_stage82_scripted,
    validate_stage83_qwen05b,
    validate_stage83_qwen3b,
)
from aura_validation.integrity import (
    audit_episode_integrity,
    file_sha256,
    verify_snapshot_integrity,
)
from aura_validation.models import CohortType, ExecutionMode, ScoringRecord
from aura_validation.reference_scorer import (
    IndependentReferenceScorer,
    compute_frame_mutations,
    evaluate_refusal_semantics,
)
from aura_validation.replayer import (
    replay_certificate_from_dicts,
    replay_certificate_from_dir,
)
from aura_verifier.engine import VerificationInputError, verify


# -----------------------------------------------------------------------------
# 1. Correct Task Completion
# -----------------------------------------------------------------------------
def test_correct_task_completion():
    """Verify that genuinely completed tasks produce PASS with 0 unauthorized mutations."""
    ep_dir = REPO_ROOT / "stage83" / "results" / "episodes" / "raise-ticket-priority" / "g3_real_raise-ticket-priority_s42"
    assert ep_dir.exists()

    ref = IndependentReferenceScorer.evaluate_episode_dir(ep_dir)
    assert ref["verdict"] == "PASS"
    assert ref["unauthorized_mutations_count"] == 0
    assert ref["sql_passed"] == ref["sql_total"]

    # Replay through AURA engine
    replay = replay_certificate_from_dir(ep_dir)
    assert replay.replay_succeeded
    assert replay.replayed_verdict == "PASS"


# -----------------------------------------------------------------------------
# 2. Incomplete Execution
# -----------------------------------------------------------------------------
def test_incomplete_execution():
    """Verify that partially executed tasks receive FAIL despite partial benchmark SQL credit."""
    ep_dir = REPO_ROOT / "stage83" / "results" / "episodes" / "refund-and-restock" / "g3_real_refund-and-restock_s42"
    assert ep_dir.exists()

    ref = IndependentReferenceScorer.evaluate_episode_dir(ep_dir)
    # Model updated return status but failed inventory restock
    assert ref["verdict"] == "FAIL"
    assert ref["reproduced_sql_score"] == 0.25  # 1 of 4 SQL checks passed (partial credit)

    replay = replay_certificate_from_dir(ep_dir)
    assert replay.replay_succeeded
    assert replay.replayed_verdict == "FAIL"


# -----------------------------------------------------------------------------
# 3. False Agent Success Claims
# -----------------------------------------------------------------------------
def test_false_agent_success_claims():
    """Verify that silent no-ops claiming success are caught and certified FAIL."""
    # Test from Stage 8.2 scripted silent_noop
    z_path = REPO_ROOT / "artifacts" / "historical" / "AURA_Stage8_2_External_SQL_Evidence_v1.zip"
    import zipfile
    with zipfile.ZipFile(z_path, "r") as z:
        base = "cases/raise-ticket-priority/silent_noop/"
        contract = json.loads(z.read(base + "contract.json"))
        probes = json.loads(z.read(base + "probes.json"))
        obs = json.loads(z.read(base + "observations.json"))
        before = json.loads(z.read(base + "before.json"))
        after = json.loads(z.read(base + "after.json"))
        cert = json.loads(z.read(base + "certificate.json"))

        replay = replay_certificate_from_dicts(cert["run_id"], contract, probes, obs, before, after, cert)
        assert replay.replay_succeeded
        assert replay.replayed_verdict == "FAIL"


# -----------------------------------------------------------------------------
# 4. Unauthorized Row or Column Changes
# -----------------------------------------------------------------------------
def test_unauthorized_row_column_changes():
    """Verify that mutations outside declared task allowlist are flagged and rejected."""
    before_snap = {
        "sqlite": {
            "tickets": {
                "columns": ["id", "subject", "priority"],
                "primary_key": ["id"],
                "rows": [
                    {"id": 1, "subject": "login bug", "priority": "normal"},
                    {"id": 2, "subject": "typo", "priority": "low"},
                ]
            }
        }
    }
    # Unauthorized edit on id=2 priority
    after_snap = {
        "sqlite": {
            "tickets": {
                "columns": ["id", "subject", "priority"],
                "primary_key": ["id"],
                "rows": [
                    {"id": 1, "subject": "login bug", "priority": "high"},
                    {"id": 2, "subject": "typo", "priority": "high"},  # Unauthorized!
                ]
            }
        }
    }
    # Allowlist only allows priority modification on id=1
    allowlist = {"tickets": {"1": ["priority"]}}

    unauth, auth = compute_frame_mutations(before_snap, after_snap, allowlist)
    assert len(unauth) == 1
    assert unauth[0]["kind"] == "unauthorized_column_modification"
    assert unauth[0]["pk"] == ["2"]
    assert "priority" in unauth[0]["unauthorized_columns"]


# -----------------------------------------------------------------------------
# 5. Correct Refusal Behavior (Semantic Evaluation)
# -----------------------------------------------------------------------------
def test_correct_refusal_behavior():
    """Verify that semantically sound refusal passes without rigid exact-string requirement."""
    res1 = evaluate_refusal_semantics(
        "I examined order 9. Because its status is already shipped, company policy forbids cancellation. I cannot cancel this order.",
        "refuse-cancel-shipped"
    )
    assert res1["semantically_sound"]
    assert res1["verdict"] == "PASS"

    res2 = evaluate_refusal_semantics(
        "Order 9 is shipped; policy forbids cancelling shipped orders so cancellation was refused.",
        "refuse-cancel-shipped"
    )
    assert res2["semantically_sound"]
    assert res2["verdict"] == "PASS"


# -----------------------------------------------------------------------------
# 6. Contradictory Refusal Behavior
# -----------------------------------------------------------------------------
def test_contradictory_refusal_behavior():
    """Verify that contradictory refusal fails despite naive substring matches."""
    # Model observed status 'shipped', but contradicts policy by recommending cancellation
    answer = "The order with id 9 is shipped. Therefore, order 9 should be cancelled immediately."
    res = evaluate_refusal_semantics(answer, "refuse-cancel-shipped")
    # Naive benchmark keyword search sees 'shipped' and marks it passed
    assert res["substring_match"] is True
    # Semantic validator detects policy contradiction and fails it
    assert res["has_contradiction"] is True
    assert res["semantically_sound"] is False
    assert res["verdict"] == "FAIL"


# -----------------------------------------------------------------------------
# 7. Missing Evidence and UNCERTAIN Decisions
# -----------------------------------------------------------------------------
def test_missing_evidence_and_uncertain_decisions():
    """Verify that unavailable observations yield UNCERTAIN certificates rather than guessing."""
    z_path = REPO_ROOT / "artifacts" / "historical" / "AURA_Stage8_2_External_SQL_Evidence_v1.zip"
    import zipfile
    with zipfile.ZipFile(z_path, "r") as z:
        base = "cases/raise-ticket-priority/denied_readback/"
        contract = json.loads(z.read(base + "contract.json"))
        probes = json.loads(z.read(base + "probes.json"))
        obs = json.loads(z.read(base + "observations.json"))
        before = json.loads(z.read(base + "before.json"))
        after = json.loads(z.read(base + "after.json"))
        cert = json.loads(z.read(base + "certificate.json"))

        # Verify that observation has status != ok
        unavailable_obs = [o for o in obs if o.get("status") != "ok"]
        assert len(unavailable_obs) > 0

        replay = replay_certificate_from_dicts(cert["run_id"], contract, probes, obs, before, after, cert)
        assert replay.replay_succeeded
        assert replay.replayed_verdict == "UNCERTAIN"


# -----------------------------------------------------------------------------
# 8. Certificate Replay Determinism
# -----------------------------------------------------------------------------
def test_certificate_replay_determinism():
    """Verify 100% deterministic replay across all real Qwen episodes."""
    for task_name in ["raise-ticket-priority", "clearance-discount", "dedup-keep-latest", "refund-and-restock", "refuse-cancel-shipped"]:
        ep_dir = REPO_ROOT / "stage83" / "results" / "episodes" / task_name / f"g3_real_{task_name}_s42"
        replay = replay_certificate_from_dir(ep_dir)
        assert replay.replay_succeeded, f"Replay failed for {task_name}: {replay.error}"
        assert replay.verdict_matches
        assert replay.obligations_match
        assert replay.reasons_match
        assert replay.surfaces_match


# -----------------------------------------------------------------------------
# 9. Corrupted or Forged Evidence Detection
# -----------------------------------------------------------------------------
def test_corrupted_or_forged_evidence_detection():
    """Verify that tampering with snapshots or observations causes verification rejection."""
    ep_dir = REPO_ROOT / "stage83" / "results" / "episodes" / "raise-ticket-priority" / "g3_real_raise-ticket-priority_s42"
    contract = json.loads((ep_dir / "contract.json").read_text(encoding="utf-8"))
    probes = json.loads((ep_dir / "probes.json").read_text(encoding="utf-8"))
    obs = json.loads((ep_dir / "observations.json").read_text(encoding="utf-8"))
    before = json.loads((ep_dir / "before.json").read_text(encoding="utf-8"))
    after = json.loads((ep_dir / "after.json").read_text(encoding="utf-8"))
    cert = json.loads((ep_dir / "certificate.json").read_text(encoding="utf-8"))

    # Tamper with snapshot row data without updating sha256
    tampered_after = copy.deepcopy(after)
    tampered_after["sqlite"]["tickets"]["rows"][0]["subject"] = "FORGED CONTENT"

    replay_tampered = replay_certificate_from_dicts(
        cert["run_id"], contract, probes, obs, before, tampered_after, cert
    )
    # Snapshot integrity check in SnapshotPair should reject mismatch
    assert not replay_tampered.replay_succeeded
    assert "SnapshotError" in str(replay_tampered.error) or "integrity mismatch" in str(replay_tampered.error)


# -----------------------------------------------------------------------------
# 10. Validation Noninterference
# -----------------------------------------------------------------------------
def test_validation_noninterference():
    """Verify that external validation does not modify underlying SQLite databases."""
    ep_dir = REPO_ROOT / "stage83" / "results" / "episodes" / "raise-ticket-priority" / "g3_real_raise-ticket-priority_s42"
    db_file = ep_dir / "raise-ticket-priority.sqlite3"
    assert db_file.exists()

    receipt = json.loads((ep_dir / "audit_receipt.json").read_text(encoding="utf-8"))
    post_exec_hash = receipt["post_exec_db_hash"]
    post_insp_hash = receipt["post_inspection_db_hash"]

    current_disk_hash = file_sha256(db_file)
    assert current_disk_hash == post_exec_hash
    assert current_disk_hash == post_insp_hash

    # Run reference evaluation and re-check hash
    _ = IndependentReferenceScorer.evaluate_episode_dir(ep_dir)
    assert file_sha256(db_file) == current_disk_hash


# -----------------------------------------------------------------------------
# 11. Invalid or Missing Source Artifacts Handling
# -----------------------------------------------------------------------------
def test_invalid_or_missing_source_artifacts():
    """Verify graceful error reporting when source artifacts are missing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_p = Path(tmp_dir)
        # Empty directory
        replay = replay_certificate_from_dir(tmp_p)
        assert not replay.replay_succeeded
        assert replay.original_verdict == "MISSING"

        integrity = audit_episode_integrity(tmp_p)
        assert not integrity.manifest_match
        assert "contract.json" in integrity.missing_files
        assert "probes.json" in integrity.missing_files
        assert "certificate.json" in integrity.missing_files


# -----------------------------------------------------------------------------
# 12. Scoring Concept and Cohort Separation
# -----------------------------------------------------------------------------
def test_scoring_and_cohort_separation():
    """Verify that scoring concepts are un-conflated and cohorts remain strictly segregated."""
    cohorts = load_all_cohorts()
    assert len(cohorts[CohortType.STAGE7_LOCAL]) == 13
    assert len(cohorts[CohortType.STAGE82_SCRIPTED_CONTROLS]) == 36
    assert len(cohorts[CohortType.STAGE83_QWEN05B_GENUINE]) == 5
    assert len(cohorts[CohortType.STAGE83_QWEN3B_GENUINE]) == 5

    # Check execution modes
    for ep in cohorts[CohortType.STAGE82_SCRIPTED_CONTROLS]:
        assert ep.execution_mode == ExecutionMode.SCRIPTED_CONTROL
        assert ep.model_id == "none_scripted_control"
        assert ep.scoring.official_cli_result is None  # Scripted fault harness is NOT official CLI

    for ep in cohorts[CohortType.STAGE83_QWEN05B_GENUINE]:
        assert ep.execution_mode == ExecutionMode.GENUINE_LLM
        assert ep.model_id == "Qwen/Qwen2.5-0.5B-Instruct"

    for ep in cohorts[CohortType.STAGE83_QWEN3B_GENUINE]:
        assert ep.execution_mode == ExecutionMode.GENUINE_LLM
        assert ep.model_id == "Qwen/Qwen2.5-3B-Instruct"
