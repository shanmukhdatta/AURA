# AURA — Agent Uncertainty and Residue Arbiter

**Evidence-gated verification for multi-step AI agents operating over persistent state.**

AURA checks required task postconditions, closed-world allowlisted mutations, required process/tool evidence, and sufficiency of independent observations. It emits a structured **PASS / FAIL / UNCERTAIN** certificate linked to preserved evidence. The prototype is implemented primarily in Python/SQLite.

> **Research evidence release:** This tree is a **consolidation bundle constructed from preserved ChatGPT workspace, Antigravity handoff, and Kaggle export files**. It is intended to be overlaid onto the existing GitHub `feature/external-validation-pipeline` branch. It is not itself evidence that GitHub has already received these added files. The previous GitHub branch's unmodified files must be retained when merging this bundle. No new LLM training or episode executions were performed during packaging.

## Quick navigation

| Location | What is here |
|---|---|
| [`AURA_Stage7/`](AURA_Stage7/) | Latest locally recoverable core verifier, schemas, evidence capture, CERA planner, baselines, tests |
| [`aura_validation/`](aura_validation/) | External reference scoring, certificate replay, integrity and cohort validation |
| [`prototype/`](prototype/) | Stage 1–7 implementation histories, original formal/design reports |
| [`experiments/`](experiments/) | Per-cohort source links, saved evidence, logs, notebooks, snapshots and results |
| [`evidence/`](evidence/) | Every original file and extracted ZIP member indexed with SHA256 and source paths |
| [`integrity/`](integrity/) | Independent archive hash and link checking scripts, original integrity receipts |
| [`results/`](results/) | Readable research tables, experiment summaries and non-interference evidence |
| [`reproducibility/`](reproducibility/) | CPU replay, Kaggle guidance, environment and exact test execution logs |
| [`archive/`](archive/) | Byte-preserved original ZIPs, historical notebooks, research reports, superseded runs |
| [`paper/`](paper/) | Preliminary manuscript draft and table-to-evidence conventions |

## Recorded evaluation status (not a new measurement)

The uploaded Antigravity validation receipts report 59 certified episodes: 13 local scripted cases, 36 controlled AgentSynth SQL cases, five genuine Qwen2.5-0.5B agent runs, and five genuine Qwen2.5-3B agent runs. The recorded validator reproduced 59/59 certificates; its test log reports 224 passed, one skipped. Separately, four Stage 8.1 local Qwen cases and three official AppWorld development evaluations are preserved, but the three AppWorld cases have **no AURA certificates**. Stage 7 planning-world evaluations are not agent episodes.

**Limitations:** Reference agreement is measured against contract-based references sharing specifications with AURA, not a proof of universal soundness. Hash/certificate replay establishes deterministic consistency under the available evidence, not external authenticated signing. The CPU and Kaggle Qwen studies have different task sets and turn budgets, so must not be compared as a controlled model-size study.

## CPU reproducibility

```sh
python integrity/verify_archives.py
python integrity/verify_archive_members.py
python integrity/verify_workspace_files.py
python integrity/verify_evidence_links.py
python -m aura_validation.runner
python -m pytest AURA_Stage7/tests tests/test_validation_pipeline.py -q
```

The last two commands use the most recent Antigravity code and may depend on compatibility with the existing upstream repository. See [`reproducibility/README.md`](reproducibility/README.md) and the original pinned environment logs before comparing output counts. **Replaying evidence does not re-run GPU language-model generation**.

## Research navigation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — module responsibilities and complete verification path.
- [`docs/EXPERIMENT_INDEX.md`](docs/EXPERIMENT_INDEX.md) — separation of all cohorts, sample sizes and scoring concepts.
- [`docs/PROVENANCE_AND_LIMITATIONS.md`](docs/PROVENANCE_AND_LIMITATIONS.md) — original versus consolidated sources, disclosures, and missing data policy.
- [`prototype/README.md`](prototype/README.md) — historical development and runnable source layout.
- [`archive/README.md`](archive/README.md) — rules for byte-preserving the original work.
- [`paper/README.md`](paper/README.md) — manuscript and result evidence pointers.

## Provenance and GitHub branches

Original GitHub repository: https://github.com/shanmukhdatta/AURA  
Original validation PR: https://github.com/shanmukhdatta/AURA/pull/2  
Original validation fix commit: `b1e814ff1a05aac5846cc3637b98308d2053d475`.  
Do not overwrite or force-push the original commit history. See `CONSOLIDATION_AND_PUSH.md` for a safe workflow.

Historical notebooks, scripts and database files remain **original evidence**, with experimental status and exact checksums described in machine-readable manifests. No missing historical experiment is silently assigned a reconstructed output.
