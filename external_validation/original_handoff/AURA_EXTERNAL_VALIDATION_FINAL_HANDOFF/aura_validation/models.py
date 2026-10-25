"""Data models and type definitions for AURA external validation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class CohortType(str, Enum):
    STAGE7_LOCAL = "stage7_local"
    STAGE82_SCRIPTED_CONTROLS = "stage82_scripted_controls"
    STAGE83_QWEN05B_GENUINE = "stage83_qwen05b_genuine"
    STAGE83_QWEN3B_GENUINE = "stage83_qwen3b_genuine"


class ExecutionMode(str, Enum):
    GENUINE_LLM = "genuine_llm"
    SCRIPTED_CONTROL = "scripted_control"
    LOCAL_BASELINE = "local_baseline"


@dataclass
class ScoringRecord:
    """Four distinct, non-conflated evaluation concepts."""
    # 1. Official AgentSynth CLI runner result (only available if official CLI executed)
    official_cli_result: Optional[str] = None  # "PASS", "FAIL", or None
    official_cli_score: Optional[float] = None  # e.g. 1.0, 0.0, or None

    # 2. Reconstructed upstream SQL-only checker score
    reproduced_sql_score: float = 0.0  # 0.0 to 1.0

    # 3. Independent strict task-contract reference judgment
    strict_contract_reference: str = "UNKNOWN"  # "PASS", "FAIL", "UNCERTAIN"
    strict_reference_reason: str = ""

    # 4. AURA verification certificate verdict
    aura_certificate_verdict: str = "UNKNOWN"  # "PASS", "FAIL", "UNCERTAIN"

    # Concordance and error flags
    concordant: bool = False
    false_pass: bool = False
    false_fail: bool = False

    def evaluate_concordance(self) -> None:
        self.concordant = (self.aura_certificate_verdict == self.strict_contract_reference)
        self.false_pass = (self.aura_certificate_verdict == "PASS" and self.strict_contract_reference == "FAIL")
        self.false_fail = (self.aura_certificate_verdict == "FAIL" and self.strict_contract_reference == "PASS")


@dataclass
class ReplayResult:
    """Outcome of replaying saved evidence through AURA verify engine."""
    run_id: str
    original_verdict: str
    replayed_verdict: str
    verdict_matches: bool
    obligations_match: bool
    reasons_match: bool
    surfaces_match: bool
    error: Optional[str] = None

    @property
    def replay_succeeded(self) -> bool:
        return (
            self.verdict_matches
            and self.obligations_match
            and self.reasons_match
            and self.surfaces_match
            and self.error is None
        )


@dataclass
class IntegrityRecord:
    """Integrity and noninterference audit results."""
    task_id: str
    run_id: str
    before_snapshot_sha256: str
    after_snapshot_sha256: str
    database_on_disk_sha256: str
    noninterference_verified: bool  # after_snapshot == database_on_disk
    manifest_match: bool
    missing_files: List[str] = field(default_factory=list)


@dataclass
class ValidationEpisode:
    """Complete record of an externally validated episode."""
    task_id: str
    run_id: str
    cohort: CohortType
    execution_mode: ExecutionMode
    model_id: str
    seed: Optional[int]
    scoring: ScoringRecord
    replay: Optional[ReplayResult] = None
    integrity: Optional[IntegrityRecord] = None
    unauthorized_mutations_count: int = 0
    authorized_changes_count: int = 0
    wall_time_s: Optional[float] = None
    provenance_path: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
