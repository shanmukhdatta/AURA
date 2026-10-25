"""Integrity and noninterference audit module for AURA external validation."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "AURA_Stage7"))
sys.path.insert(0, str(REPO_ROOT))

from aura_evidence.util import digest
from aura_validation.models import IntegrityRecord


REQUIRED_EPISODE_FILES = [
    "contract.json",
    "probes.json",
    "observations.json",
    "certificate.json",
]


def file_sha256(path: Path) -> str:
    """Compute sha256 hex digest of file on disk."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_snapshot_integrity(snapshot_dict: Dict[str, Any]) -> Tuple[bool, str, str]:
    """Verify that snapshot internal sha256 matches canonical digest of its contents."""
    declared_sha = snapshot_dict.get("sha256", "")
    content_to_hash = {k: v for k, v in snapshot_dict.items() if k != "sha256"}
    computed_sha = digest(content_to_hash)
    return (declared_sha == computed_sha, declared_sha, computed_sha)


def audit_episode_integrity(episode_dir: Path) -> IntegrityRecord:
    """Audit evidence integrity and noninterference for an episode directory."""
    episode_dir = Path(episode_dir)
    missing = []
    
    # Check for certificate (either name)
    cert_path = episode_dir / "certificate.json"
    if not cert_path.exists():
        cert_path = episode_dir / "aura_certificate.json"
    if not cert_path.exists():
        missing.append("certificate.json")

    # Check for before/after snapshots
    before_path = episode_dir / "before.json"
    if not before_path.exists():
        before_path = episode_dir / "before_snapshot.json"
    if not before_path.exists():
        missing.append("before.json")

    after_path = episode_dir / "after.json"
    if not after_path.exists():
        after_path = episode_dir / "after_snapshot.json"
    if not after_path.exists():
        missing.append("after.json")

    for req in ["contract.json", "probes.json", "observations.json"]:
        if not (episode_dir / req).exists():
            missing.append(req)

    task_id = episode_dir.parent.name if episode_dir.parent.name != "episodes" else episode_dir.name
    run_id = episode_dir.name

    before_sha = ""
    after_sha = ""
    db_sha = ""
    noninterference = True
    manifest_match = (len(missing) == 0)

    if before_path.exists():
        try:
            b_dict = json.loads(before_path.read_text(encoding="utf-8"))
            before_sha = b_dict.get("sha256", "")
            valid, _, _ = verify_snapshot_integrity(b_dict)
            if not valid:
                manifest_match = False
        except Exception:
            manifest_match = False

    if after_path.exists():
        try:
            a_dict = json.loads(after_path.read_text(encoding="utf-8"))
            after_sha = a_dict.get("sha256", "")
            valid, _, _ = verify_snapshot_integrity(a_dict)
            if not valid:
                manifest_match = False
        except Exception:
            manifest_match = False

    # Check SQLite database noninterference
    sqlite_files = list(episode_dir.glob("*.sqlite3"))
    audit_receipt_path = episode_dir / "audit_receipt.json"

    if sqlite_files:
        db_path = sqlite_files[0]
        db_sha = file_sha256(db_path)
        if audit_receipt_path.exists():
            try:
                receipt = json.loads(audit_receipt_path.read_text(encoding="utf-8"))
                post_exec = receipt.get("post_exec_db_hash", "")
                post_insp = receipt.get("post_inspection_db_hash", "")
                if post_exec and post_insp:
                    # Noninterference holds if on-disk hash matches post_exec and post_inspection
                    noninterference = (db_sha == post_exec == post_insp)
                elif post_insp:
                    noninterference = (db_sha == post_insp)
            except Exception:
                noninterference = False

    return IntegrityRecord(
        task_id=task_id,
        run_id=run_id,
        before_snapshot_sha256=before_sha,
        after_snapshot_sha256=after_sha,
        database_on_disk_sha256=db_sha,
        noninterference_verified=noninterference,
        manifest_match=manifest_match,
        missing_files=missing,
    )


def audit_repository_manifest(manifest_path: Path, base_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Verify stored SHA256SUMS against actual repository files using intelligent path resolution."""
    manifest_path = Path(manifest_path)
    if not manifest_path.exists():
        return {"error": f"Manifest not found: {manifest_path}", "verified_count": 0, "mismatches": [], "missing": []}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    verified = 0
    mismatches = []
    missing = []

    for rel_path, entry in manifest.items():
        expected_sha = entry["sha256"] if isinstance(entry, dict) else str(entry)
        
        # Check candidate search paths in order of specificity
        candidates = []
        if base_dir:
            candidates.append(Path(base_dir) / rel_path)
        candidates.append(manifest_path.parent / rel_path)
        candidates.append(REPO_ROOT / rel_path)
        candidates.append(REPO_ROOT / "artifacts" / "historical" / rel_path)

        target = next((p for p in candidates if p.is_file()), None)
        if not target:
            missing.append(rel_path)
            continue

        actual_sha = file_sha256(target)
        if actual_sha.lower() == expected_sha.lower():
            verified += 1
        else:
            mismatches.append({"file": rel_path, "resolved_path": str(target.relative_to(REPO_ROOT)), "expected": expected_sha, "actual": actual_sha})

    return {
        "manifest_file": str(manifest_path.relative_to(REPO_ROOT) if manifest_path.is_relative_to(REPO_ROOT) else manifest_path),
        "total_declared": len(manifest),
        "verified_count": verified,
        "missing_count": len(missing),
        "mismatches": mismatches,
        "missing": missing,
    }
