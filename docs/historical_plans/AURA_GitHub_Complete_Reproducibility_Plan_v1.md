# AURA — Complete GitHub Consolidation and Reproducibility Plan (Review Draft v1)

**Status:** PLAN ONLY. No GitHub file was created, edited, pushed, merged, or deleted for this plan.

**Target repository:** https://github.com/shanmukhdatta/AURA

**Audit basis:** Live GitHub read-only inspection on 26 October 2026; locally available AURA release archives, Kaggle exports, report files, and 59-row Antigravity experiment inventory. The accompanying `AURA_GitHub_Reproducibility_Source_Inventory.csv` records file sizes, SHA256, and ZIP CRC for 24 source artifacts. A 'source available' label only establishes that the archive is present and readable, **not** that every contained claim has been reproduced or independently verified.

## 1. Current GitHub status: what is already pushed?

| Remote GitHub location | Observed state | Consequence |
|---|---|---|
| `main` | Exists; the top-level README still describes an early evidence status; no validation pipeline was found in it | Keep protected until reviewed PR |
| `experiment/stage-8-3-external-llm-verification` | Exists; contains Stage 7 core plus historical Stage 8.2 and original Stage 8.3 development | Preserve, do not overwrite blindly |
| `feature/stage-8-3-external-verification` | Exists, five commits ahead of main on read-only comparison; contains Stage 7 core, Stage 8.2 scripts and tables, 0.5B Stage 8.3 evidence, paper drafts and archives | Starting point for careful migration |
| Pull request #1 | URL exists and is open: https://github.com/shanmukhdatta/AURA/pull/1 | Review/update claims and contents, do not merge yet |
| `feature/external-validation-pipeline` | **NOT present** among remote branches; attempts to read `aura_validation/runner.py` at this ref failed | Antigravity's latest validator is currently **not verified as pushed** |
| `aura_validation/`, `validation_reports/` at older feature ref | Both path checks failed | Need Antigravity's local branch export or authorized future push |

The existing remote paper and PR describe *212 passing tests/46 validation episodes* in some places; Antigravity's later **local** report claims *224 passing tests/59 episodes*. These are versions of the record, not numbers to silently combine. PR #1 also contains strong model-scaling/soundness language that needs scientific editorial review later.

## 2. Complete evidence scope and what counts as an 'episode'

| Research phase | Source mode | Primary code and evidence | Count used for paper / registry | Status |
|---|---|---|---|---|
| Stage 1: schemas and contracts | Authored specification and test pack | `AURA_Stage1_Schema_and_Test_Pack_v1.zip`, formal specification | Tests / examples, **not** agent episodes | Local files available |
| Stages 2–6: evolving verifier | Research implementation versions | `AURA_Stage{2..6}_Implementation_v1.zip`, corresponding results/reports | Implementation and controls; do not artificially pool | Local archives available |
| Stage 7 local controlled scenarios | Scripted CPU executions | `AURA_Stage7_Implementation_v1.zip`, `AURA_Stage7_Results_v1.zip` | **13** certified scripted episodes | Local source/evidence available; active Stage 7 engine in GitHub feature branch |
| Stage 7 planning and cost study | Finite-world scripted/simulated evaluations | Stage 7 study outputs, CERA/fixed/greedy/exhaustive/optimal | **14,400 world-policy evaluations**; separate from 13 episodes | Local source/evidence available |
| Stage 8.1 AURA local Qwen | Real LLM action selection on self-authored tasks | `AURA_STAGE8_1_OUTPUTS.zip`; matching notebook and notes | **4** LLM rollouts (not part of 59 validation registry) | Local original output available; select matching notebook after provenance comparison |
| Stage 8.1 AppWorld | Official native AppWorld dev-task evaluations | `AURA_APPWORLD_STAGE8_1_v7_RESULTS.zip`, `AURA_AppWorld_RootFix_v7_Kaggle.ipynb` | **3** native AppWorld tasks, **0** AURA certificates | Local official dev evidence available; not included in AURA accuracy denominator |
| Stage 8.2 AgentSynth SQL | Scripted externally authored controls | `AURA_Stage8_2_External_SQL_Source_v1.zip`, `AURA_Stage8_2_External_SQL_Evidence_v1.zip` | **36** cases; 144 inspection-ablation measurements | Local evidence, some GitHub feature-branch records |
| Stage 8.3 official AgentSynth harness | Oracle and no-op calibrations | Existing Stage 8.3 G1 receipts and frozen upstream commit | **14 official tasks for oracle and no-op policies**; not real LLM AURA episodes | Present in Stage 8.3 evidence; keep scoring provenance distinct |
| Stage 8.3 Qwen2.5-0.5B | Genuine 5-task local CPU LLM | `AURA_STAGE8_3_CORRECTED_RESULTS.zip`, GitHub Stage 8.3 code | **5** genuine LLM episodes | Local archive and feature branch available |
| Stage 8.3 Qwen2.5-3B | Genuine 5-task Kaggle GPU LLM | `AURA_STAGE83_QWEN3B_PILOT_RESULTS.zip`, pilot notebook | **5** genuine LLM episodes | Local archive available; not confirmed as a standalone canonical GitHub cohort |
| Stage 8.3 CERA cost calibration | Deterministic evaluation worlds | `stage83/results/g4_cost_corrected.csv`, replayable cost scripts | **64 worlds per policy**; do not call these agent episodes | Stage 8.3 feature branch; outcome limitations must be retained |
| Stage 8.4 | Name mentioned in discussion | No verified Stage 8.4 source archive/run identifier found in available files or known remote refs | **Not counted** | Reserve namespace only pending proof |
| Latest cross-cohort independent validation | CPU replay of existing evidence | `EXPERIMENT_INVENTORY_FINAL.csv`, `VALIDATION_EXECUTION_REPORT.md`, Antigravity local `aura_validation/` | **59 = 13 + 36 + 5 + 5**, all replay claimed, **224 test passes claimed** | CSV/report present; actual new source, seven reports and complete test log still needed from Antigravity |

**Important:** 59 is **not the complete count of every research activity**. It is the four-cohort certified-validation subset. Preserve the 4 extra Stage 8.1 Qwen rollouts, 3 AppWorld native runs, Stage 7 modeled experiments, G1 official calibration, ablations, and integrity negative controls in their appropriate non-pooled tables. Do not label model-generated actions as scripted controls or reverse.

## 3. Proposed canonical GitHub layout

```text
AURA/
├── README.md                         # Project overview + truthful evidence-status dashboard
├── CITATION.cff                       # Project citation; real authors only
├── LICENSE                            # Add only after confirming ownership/licensing
├── CHANGELOG.md                       # Chronological code/evidence milestones
├── CONTRIBUTING.md                    # How to contribute without altering raw evidence
├── SECURITY.md                        # Trust model / responsible handling
├── .gitignore                         # Exclude secrets, cache, venv, model weights
├── pyproject.toml                     # CPU-first package + exact test groups
├── requirements/                      # cpu.txt, kaggle.txt, dev.txt, locked versions
├── .github/
│   └── workflows/
│       ├── tests.yml                  # Fast CPU unit + replay smoke; no GPU
│       └── verify_artifacts.yml       # Manifest and schema integrity checks
├── src/aura/                           # Canonical actively maintained code (after controlled migration)
│   ├── contracts/                     # Schema/contract loading and validation
│   ├── evidence/                      # snapshots, state diff, receipt and provenance
│   ├── verifier/                      # PASS / FAIL / UNCERTAIN engine
│   ├── planning/                      # CERA and comparison policies
│   ├── baselines/                     # fixed, greedy, exhaustive, optimal
│   └── external/                      # AgentSynth/AppWorld adapters, with true support status
├── aura_validation/                    # Antigravity local new CPU-only validation pipeline
│   ├── __init__.py
│   ├── runner.py
│   ├── inventory.py
│   ├── reference.py
│   ├── replay.py
│   ├── integrity.py
│   └── reports.py
│   # Exact module filenames above illustrative until source is received
├── tests/
│   ├── unit/                           # Existing Stage 1–7 tests (migrated without regressions)
│   ├── integration/                    # SQLite+adapter tests
│   ├── adversarial/                    # signature/hash/receipt/frame negative controls
│   ├── external_validation/            # Latest Antigravity tests
│   └── fixtures/                       # Safe small fixtures only
├── experiments/
│   ├── README.md                       # Experiment taxonomy and counts
│   ├── stage07_internal/
│   │   ├── README.md
│   │   ├── code/ notebooks/ configs/ raw/ results/ logs/ manifests/
│   ├── stage81_local_qwen/
│   │   ├── README.md
│   │   ├── code/ notebooks/ configs/ raw/ results/ logs/ manifests/
│   ├── stage81_appworld/
│   │   ├── README.md
│   │   ├── code/ notebooks/ configs/ raw/ results/ logs/ manifests/
│   ├── stage82_agentsynth_controls/
│   │   ├── README.md
│   │   ├── code/ notebooks/ configs/ raw/ results/ logs/ manifests/
│   ├── stage83_agentsynth_g1_calibration/
│   │   ├── README.md
│   │   ├── code/ configs/ raw/ results/ logs/ manifests/
│   ├── stage83_qwen05b/
│   │   ├── README.md
│   │   ├── code/ configs/ raw/ results/ logs/ manifests/
│   ├── stage83_qwen3b/
│   │   ├── README.md
│   │   ├── code/ notebooks/ configs/ raw/ results/ logs/ manifests/
│   └── cera_planning/
│       ├── README.md
│       ├── code/ configs/ raw/ results/ logs/ manifests/
├── evidence/
│   ├── README.md                       # What evidence proves; observation boundaries
│   ├── master_experiment_registry.csv # One row PER unique execution, not per test/world
│   ├── master_source_registry.csv     # SHA256, source location, authorship, environment
│   ├── attestations/                  # Human review / test receipts (not fabricated)
│   └── certificates/                  # Central index or links, not duplicate binary blobs
├── validation/
│   ├── README.md                       # How reference agreement differs from formal proof
│   ├── reports/                        # Actual 7 Antigravity generated outputs
│   ├── reference_checks/              # Independent reference code/specs
│   └── reconciliation/                # Scoring and study version corrections
├── results/
│   ├── README.md                       # Explicit denominators; official vs reproduced
│   ├── tables/                         # Generated, paper-ready CSV/MD/LaTeX
│   ├── figures/                        # Code-generated figures and provenance
│   └── scripts/                        # Deterministic generators
├── docs/
│   ├── ARCHITECTURE.md
│   ├── THREAT_MODEL.md
│   ├── CONTRACT_AND_CERTIFICATE_SPEC.md
│   ├── EXPERIMENT_DESIGN.md
│   ├── REPRODUCIBILITY.md
│   ├── EVIDENCE_PROVENANCE.md
│   ├── DATA_AND_MODEL_SOURCES.md
│   ├── RESULTS_INTERPRETATION.md
│   ├── RESEARCH_DECISIONS.md
│   └── GLOSSARY.md
├── paper/
│   ├── README.md                       # Not finalized until scientific approval
│   ├── main.tex
│   ├── references.bib
│   ├── MANUSCRIPT.md
│   └── tables/                         # generated, never manually fabricated
├── scripts/
│   ├── verify_sources.py
│   ├── validate_saved_runs.py
│   ├── generate_tables.py
│   └── smoke_reproduce.sh
└── archive/
    ├── README.md                       # Historical, immutable; not primary runtime
    ├── releases/stage01 ... stage07/  # Original authored version ZIPs and reports
    ├── development_runs/              # Prior notebook revisions and failed setup attempts
    ├── submission_drafts/             # Previous bundle/manuscript snapshots
    └── mapping.csv                     # Old path -> new path, SHA256; de-dup policy
```

**Directory tree is a proposed design, not an existing directory listing.** Use the real `aura_validation/` module layout once Antigravity exports it. Do not create empty stage folders or pretend Stage 8.4 exists.

## 4. Exact migration rules

1. **No historical loss:** Retain every authored code version (Stages 1–7) as immutable, traceable ZIP snapshots. Use Stage 7 as the starting live engine, not 7 competing package roots. For the initial consolidation commit, preserve `AURA_Stage7/` paths to avoid breaking import semantics; move to `src/aura/` only after a dedicated no-behavior-change migration with tests.
2. **Do not rewrite raw evidence:** Original ZIPs/notebook outputs and model logs remain byte-for-byte unchanged. Extract *readable copies* for review and cite the archive hash + member path. Derived data is regenerated from canonical raw inputs.
3. **Every episode receives provenance:** `run_id`, `cohort`, `execution_kind`, `task_id`, `model_id`, `seed`, `max_turns`, `hardware`, `environment`, `git_code_commit`, `upstream_dataset_commit`, `contract_sha256`, `raw_evidence_path`, `raw_evidence_sha256`, `certificate_path`, `reference_source`, `replay_status`, `verification_scope`, and `official_vs_reproduced` scorer status. Use explicit `UNKNOWN`, `NOT_RUN`, `UNAVAILABLE` rather than guesses.
4. **Exact proof chain per eligible task:** Task specification and frozen contract -> executable code / notebook -> prompts and tool API -> actual tool trace and errors -> before/after database or filesystem snapshots -> independent probe observations -> AURA certificate -> independent reference result -> replay receipt -> integrity manifest -> aggregated row. Missing links must be visible.
5. **AppWorld is different:** Save official dev grader outputs and native API logs with explicit `aura_certificate_available=false`; do not create dummy AURA certificates or count these runs in AURA agreement rates.
6. **CERA is different:** Separate synthetic units, measured planner latency (ms), real probe execution latency (ms), and shared snapshot overhead. Never add unrelated units or claim high-latency superiority without experiment. Keep baseline comparisons and prior sensitivity intact.
7. **Version conflicts:** Preserve old and corrected Stage 8.3 results, but clearly label one as archival and one as the approved corrected analysis. Record any changed task contracts and whether score differences arose from reference definitions. Do not overwrite published numbers without change logs.
8. **Notebook hygiene:** Keep the final successful Kaggle notebook and output for each cohort as canonical. Archive earlier fix attempts and failure logs under `archive/development_runs/`, not beside final paper numbers. Keep raw cell outputs when relevant, but strip API keys, access tokens, cookies, private paths, and inadvertently captured secrets before public push.
9. **Third-party provenance:** Pin AgentSynth upstream commit (`d2564dfb25ed7ba32e367d28117e6afd1ee6c485`) and cite original source; AppWorld should be installed from its official source and run with its licensed assets; do not vendor third-party restricted data or model weights into Git.
10. **Artifact hygiene:** Git should contain code, small raw evidence, logs and manifests; for any file approaching GitHub file-size limits, move to a versioned external release or Git LFS and store a content hash and stable acquisition instructions. Do not commit caches, `.venv`, checkpoints, large downloaded datasets, or generated temporary SQLite write-ahead logs.

## 5. Required experiment-specific README template

Every `experiments/<cohort>/README.md` must explain: **purpose; authorship/origin; the exact task set; how many unique runs; whether scripted or actual LLM; model/seed/turn limit; hardware; upstream version; path and SHA256 for source archive; commands for setup, run, replay and scoring; expected CSV schema; definitive reported results; known failures; what cannot be claimed; and whether original inference can be reproduced CPU-only, requires GPU, or requires licensed upstream assets.** Provide a one-line example and a real artifact path for each major claim.

Root `README.md` should have a short overview, architecture diagram, quickstart (CPU smoke and certificate replay), experimental cohort table **without pooled scripted+LLM accuracy**, documentation index, provenance badges based on real CI receipts only, citation instructions, and limitations. Detailed explanation belongs in docs and cohort READMEs.

## 6. Runnable reproducibility levels

- **Level A / fastest, CPU only:** install locked CPU dependencies; validate archive hashes; run verifier unit/integration tests; replay saved certificates; regenerate official-versus-reproduced cohort tables. This should work with no LLM or GPU and produce a report comparing actual against checked-in result hashes.
- **Level B / CPU controlled experiments:** regenerate Stage 7 local and finite-world policies, Stage 8.2 36 scripted controls and ablations, Stage 8.3 CERA costs; record measured rather than expected times, validate environmental differences.
- **Level C / original inference:** run the Stage 8.1 local Qwen notebooks and Stage 8.3 Qwen 0.5B / 3B notebooks, with GPU optional or required as originally documented, and native AppWorld tasks subject to upstream assets. Require pinned model revision, dataset commit, prompts, seeds and full tool action traces. Re-running generative models need not reproduce identical tokens across GPU/driver versions; replay of **saved verification evidence** is the deterministic claim.

## 7. Deployment sequence — NO PUSH UNTIL APPROVAL

**Gate P0 — Inventory review (now).** Freeze migration plan, read-only GitHub diff, match source inventory and 59-episode registry; flag gaps. User approves plan.

**Gate P1 — Receive missing Antigravity branch.** Export `feature/external-validation-pipeline` as a ZIP or `git bundle`, plus seven reports, tests, complete pytest log, `git status`, current `git rev-parse HEAD`, and path-to-SHA256 manifest. No GitHub write yet.

**Gate P2 — Stage and map.** Create dedicated *local* `feature/research-reproducibility-consolidation` from current remote `feature/stage-8-3-external-verification` (or another user-approved base). Build an `old_path,new_path,action,sha256` migration manifest. Keep artifacts immutable. Normalize paths and reconcile duplicates by SHA not filename.

**Gate P3 — Run consistency checks.** Automated ZIP CRC and SHA256; verify 59 unique certified IDs; independently replay eligible certificates; preserve official AppWorld observations with no AURA certificates; regenerate Stage 7/8.1/8.2/8.3 numbers; report missing stage/contract evidence. Run complete 224-test suite from actual local branch and capture timestamps/skips; do not substitute older 212-test receipt.

**Gate P4 — Reproducibility and documentation.** Install fresh CPU environment, execute Level A and Level B commands, document Level C Kaggle reproduction; generate all tables and result readmes. Verify referenced paths actually exist. Explicitly note invalidated early scripts and corrected versions.

**Gate P5 — Pre-push review.** Return diff manifest, file counts/sizes, duplicate list, integrity report, test logs, material omissions, proposed PR body, and paper-impact summary. Review before any remote update.

**Gate P6 — Push only after explicit authorization.** Antigravity pushes the reviewed consolidation branch (not `main`); open new draft PR into `main` or update PR #1 only if the user chooses. No force pushes, no merge. Check GitHub Actions and public README links again after push.

**Gate P7 — Freeze for manuscript.** Tag immutable data/code release only after final user approval; cite versioned experiment registry and hashes; keep the paper's numerics reproducibly generated from this tag.

## 8. Remaining materials required from the user / Antigravity

**Already present locally:** Original Stage 1–7 release ZIPs; Stage 7 results; Stage 8.1 local Qwen outputs; AppWorld v7 outputs and notebook; Stage 8.2 source/evidence; corrected 0.5B Stage 8.3 archive; Qwen3B pilot evidence/notebook; 59-row inventory; independent execution report; prior research submission bundle. No need to upload these again unless they differ from your latest local copies.

**Required missing handoff:** Antigravity's actual unpushed `aura_validation/` Python package, its new tests, **all seven `validation_reports/` files**, full stdout/stderr 224-test pytest receipt, and uncommitted changes; delivered as a ZIP or `git bundle`. This is the only essential new package before a complete push plan can be executed.

**Please also confirm:** (i) whether a separate Stage 8.4 experiment actually ran, including exact source/log; (ii) whether the latest Kaggle notebook/result differs from the Qwen3B pilot ZIP already here; (iii) which branch you eventually want as consolidation PR base; and (iv) paper authors/license/ownership metadata once preparing a public release. None of these should block an inventory-only review.

## 9. Pre-push acceptance checklist

- [ ] Inventory distinguishes all experiment classes and excludes double-counting.
- [ ] Every canonical raw archive linked and SHA256 pinned.
- [ ] All historical authored code versions retained without conflicting live imports.
- [ ] Validated stage 8.1 local and AppWorld native outputs preserved separately.
- [ ] 36 Stage 8.2 scripted and 10 Stage 8.3 genuine episodes included with traces/snapshots/certificates.
- [ ] Stage 7 13 episodes, finite-world evaluations, ablations, and costs preserved.
- [ ] G1 official CLI calibration separated from Stage 8.3 SQL-only checks.
- [ ] Antigravity 59-episode validator source and seven actual reports included.
- [ ] All measured times, costs, and uncertain labels have original provenance.
- [ ] Fresh CPU replay, integrity check, and test suite executed with preserved logs.
- [ ] Kaggle notebooks and environment version receipts archived, no model weights or credentials committed.
- [ ] Root and cohort READMEs, threat model, reproducibility guide, citations, and limitations complete.
- [ ] Existing PR scientific claims corrected (not automatic universal soundness/model-scaling proof).
- [ ] No source files overwritten silently; no pushes or merges without approval.

**Bottom line:** The latest 59-episode validation code has **not been verified as pushed**. GitHub contains much of the earlier Stage 7–8.3 work but not the local latest pipeline. The next engineering action is an Antigravity export, then a reviewable local migration, and only then an authorized push.
