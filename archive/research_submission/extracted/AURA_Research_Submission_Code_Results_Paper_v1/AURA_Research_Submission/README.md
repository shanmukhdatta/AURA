# AURA Preliminary Research Submission — Reproducible Evidence & Manuscript Pack

**Status: assembled and CPU-validated; paper draft ready for author review, NOT submitted/accepted.**

Purpose: reorganize existing AURA work for a small research paper/technical note, without deleting failures or running another GPU model. This folder is a *research-publication overlay* and deliberately does not replace the full GitHub repository.

## Current source repository

https://github.com/shanmukhdatta/AURA — inspect the feature branch `feature/stage-8-3-external-verification` and PR #1 for the current integrated AURA + AgentSynth runtime adapter. This local archive includes the Stage 7 snapshot and Stage 8.2/8.3 experiment scripts as archived. Stage 8.3 scripts that import `aura_external.agentsynth_adapter` require the integrated **GitHub feature-branch** copy of that adapter; the original Stage 7 snapshot predates it. Do not mistake this evidence-focused copy for a self-contained rebuild of the entire Stage 8.3 inference runtime.

## Layout

```text
AURA_Research_Submission/
├── research_submission/        # New stdlib-only source: ZIP checks + metric/CSV reproduction
│   ├── audit.py                # 5 experimental cohorts + manifest verification
│   ├── tables.py               # Stage 7 model/local studies and Stage 8.3 cost tables
│   └── run_all.py              # One-command research report build
├── tests/                      # Research-overlay unit/integration tests
├── evidence/source_archives/   # Immutable saved experiment ZIPs, six total
├── evidence/*.md              # Historical independent reports
├── implementation/            # Original Stage 7, Stage 8.2, Stage 8.3 archival source
├── outputs/                   # Regenerated CSVs, JSON and audit receipts
├── paper/                     # Manuscript and short publication plan
├── protocols/                 # Research rules and Antigravity enhanced prompt
└── SUBMISSION_MANIFEST_SHA256.json # Audit of archive as prepared
```

## Rebuild the paper's quantitative tables (no GPU or web)

```bash
cd AURA_Research_Submission
python -m research_submission.run_all
python -m unittest discover -s tests -v
```

If `pytest` is installed, you may instead use `python -m pytest -q tests`. Both use only the Python standard library for the research overlay. Replaying the *full* Stage 7 engine tests requires the original Python project requirements and can be done separately.

`outputs/episode_registry.csv` deliberately contains **53 labeled rows: 17 genuinely model-driven episodes including 3 AppWorld-only results, plus 36 scripted external SQL controls**. The total is not an accuracy denominator. AURA certificates exist for 14 model episodes; AppWorld's 3 native agent outcomes are not AURA certificates. The Stage 8.3 GPU and CPU models are not directly comparable because different scenarios/interfaces were used.

## Evidence and test claims

The historical source archives are copied without modification. The new scripts verify existing SHA256 manifests for all five Stage 8.x experiment ZIPs, plus a CRC check of the Stage 7 result ZIP. Table results from stage7 source are not hand-edited. **No new agent episodes were executed as part of this packaging work.** Paper-level statements and references should be reviewed independently before submission.

## Using this with Antigravity

Give Antigravity `protocols/ANTIGRAVITY_RESEARCH_SUBMISSION_MASTER_PROMPT.md`, `README.md`, the source pack, and the existing GitHub feature branch. It must retain raw evidence unchanged, add only reproducible analysis/citation/formatted-manuscript changes, and request review before any main-branch merge.

## Publication caution

IJERT currently asks for a template-formatted manuscript and accepts original research, technical notes and fast communications. It describes up to 8 pages excluding references and abstract and an acceptance-stage fee on its own website. Confirm requirements before actual submission: https://www.ijert.org/guidelines-for-authors . A publication outcome cannot be guaranteed.
