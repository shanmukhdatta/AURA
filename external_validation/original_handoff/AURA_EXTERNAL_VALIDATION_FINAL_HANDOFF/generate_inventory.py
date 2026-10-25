"""Generate EXPERIMENT_INVENTORY_FINAL.csv documenting all 59 validated episodes."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

from aura_validation.cohorts import load_all_cohorts
from aura_validation.models import CohortType


def generate_inventory_csv(output_path: Path):
    cohorts = load_all_cohorts()
    rows = []

    for cohort_type, episodes in cohorts.items():
        for ep in episodes:
            rows.append({
                "experiment_id": ep.run_id,
                "stage": cohort_type.value.split("_")[0],
                "cohort": cohort_type.value,
                "task_id": ep.task_id,
                "execution_environment": (
                    "Local CPU, isolated Python sandbox" if ep.cohort == CohortType.STAGE7_LOCAL else
                    "AgentSynth SQLite benchmark harness (scripted fault injection)" if ep.cohort == CohortType.STAGE82_SCRIPTED_CONTROLS else
                    "Local CPU, PyTorch/Transformers (max 4 turns)" if ep.cohort == CohortType.STAGE83_QWEN05B_GENUINE else
                    "Kaggle T4 GPU, PyTorch/Transformers (max 6 turns)"
                ),
                "model_name": ep.model_id if ep.execution_mode.value == "genuine_llm" else "N/A (Scripted)",
                "execution_type": ep.execution_mode.value,
                "original_source_artifact": ep.provenance_path,
                "aura_verdict": ep.scoring.aura_certificate_verdict,
                "independent_reference_verdict": ep.scoring.strict_contract_reference,
                "reproduced_sql_score": ep.scoring.reproduced_sql_score,
                "official_cli_benchmark_result": ep.scoring.official_cli_result or "N/A",
                "certificate_replay_status": "MATCH" if (ep.replay and ep.replay.replay_succeeded) else "FAIL",
                "evidence_integrity_status": "VERIFIED" if (ep.integrity and ep.integrity.noninterference_verified) else "UNVERIFIED",
                "notes": ep.notes,
            })

    fieldnames = [
        "experiment_id",
        "stage",
        "cohort",
        "task_id",
        "execution_environment",
        "model_name",
        "execution_type",
        "original_source_artifact",
        "aura_verdict",
        "independent_reference_verdict",
        "reproduced_sql_score",
        "official_cli_benchmark_result",
        "certificate_replay_status",
        "evidence_integrity_status",
        "notes",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Generated {output_path} with {len(rows)} experiment rows.")


if __name__ == "__main__":
    generate_inventory_csv(REPO_ROOT / "EXPERIMENT_INVENTORY_FINAL.csv")
