"""Certificate replay module for AURA external validation.

Re-evaluates saved execution artifacts through AURA's verifier engine to ensure
deterministic reproducibility and certificate integrity without trusting
stored certificates.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "AURA_Stage7"))
sys.path.insert(0, str(REPO_ROOT))

from aura_evidence.capture import SnapshotPair
from aura_verifier.engine import verify
from aura_validation.models import ReplayResult


def replay_certificate_from_dicts(
    run_id: str,
    contract: Dict[str, Any],
    probes: list,
    observations: list,
    before_snapshot: Dict[str, Any],
    after_snapshot: Dict[str, Any],
    original_certificate: Dict[str, Any],
    epoch_id: Optional[str] = None,
    trust_assumptions: Optional[list] = None,
) -> ReplayResult:
    """Replay verification from in-memory evidence dicts."""
    actual_run_id = original_certificate.get("run_id") or (observations[0].get("run_id") if observations else run_id) or run_id
    target_epoch = epoch_id or original_certificate.get("epoch_id") or before_snapshot.get("epoch_id", "epoch_replay")
    assumptions = trust_assumptions or original_certificate.get("trust_assumptions", ["independent_verifier_probes"])

    try:
        # Build live snapshot pair
        pair = SnapshotPair(
            target_epoch,
            before_snapshot,
            after_snapshot,
            f"snapshots/{actual_run_id}.before.json",
            f"snapshots/{actual_run_id}.after.json",
            capture_cost_ms=0.0,
            capture_bytes_read=0,
        )

        replayed_cert = verify(
            contract,
            probes,
            observations,
            run_id=actual_run_id,
            epoch_id=target_epoch,
            pair=pair,
            trust_assumptions=assumptions,
        )

        orig_verdict = original_certificate.get("verdict", "")
        replayed_verdict = replayed_cert.get("verdict", "")

        orig_obs = original_certificate.get("obligation_results", {})
        replayed_obs = replayed_cert.get("obligation_results", {})

        orig_reasons = sorted(original_certificate.get("reason_codes", []))
        replayed_reasons = sorted(replayed_cert.get("reason_codes", []))

        orig_surfaces = sorted(original_certificate.get("frame_coverage", {}).get("declared_surfaces", []))
        replayed_surfaces = sorted(replayed_cert.get("frame_coverage", {}).get("declared_surfaces", []))

        return ReplayResult(
            run_id=run_id,
            original_verdict=orig_verdict,
            replayed_verdict=replayed_verdict,
            verdict_matches=(orig_verdict == replayed_verdict),
            obligations_match=(orig_obs == replayed_obs),
            reasons_match=(orig_reasons == replayed_reasons),
            surfaces_match=(orig_surfaces == replayed_surfaces),
            error=None,
        )
    except Exception as exc:
        return ReplayResult(
            run_id=run_id,
            original_verdict=original_certificate.get("verdict", "UNKNOWN"),
            replayed_verdict="ERROR",
            verdict_matches=False,
            obligations_match=False,
            reasons_match=False,
            surfaces_match=False,
            error=f"{type(exc).__name__}: {str(exc)}",
        )


def replay_certificate_from_dir(episode_dir: Path) -> ReplayResult:
    """Load episode files from directory and replay through AURA verifier."""
    import json

    episode_dir = Path(episode_dir)
    cert_path = episode_dir / "certificate.json"
    if not cert_path.exists():
        cert_path = episode_dir / "aura_certificate.json"
    if not cert_path.exists():
        return ReplayResult(
            run_id=episode_dir.name,
            original_verdict="MISSING",
            replayed_verdict="ERROR",
            verdict_matches=False,
            obligations_match=False,
            reasons_match=False,
            surfaces_match=False,
            error="certificate.json not found",
        )

    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    contract = json.loads((episode_dir / "contract.json").read_text(encoding="utf-8"))
    probes = json.loads((episode_dir / "probes.json").read_text(encoding="utf-8"))
    observations = json.loads((episode_dir / "observations.json").read_text(encoding="utf-8"))

    before_path = episode_dir / "before.json"
    if not before_path.exists():
        before_path = episode_dir / "before_snapshot.json"
    before_snap = json.loads(before_path.read_text(encoding="utf-8"))

    after_path = episode_dir / "after.json"
    if not after_path.exists():
        after_path = episode_dir / "after_snapshot.json"
    after_snap = json.loads(after_path.read_text(encoding="utf-8"))

    run_id = cert.get("run_id", episode_dir.name)
    return replay_certificate_from_dicts(
        run_id=run_id,
        contract=contract,
        probes=probes,
        observations=observations,
        before_snapshot=before_snap,
        after_snapshot=after_snap,
        original_certificate=cert,
    )
