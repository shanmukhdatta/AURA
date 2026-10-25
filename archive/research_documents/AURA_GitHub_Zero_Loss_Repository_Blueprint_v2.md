# AURA — Zero-Loss GitHub Repository Blueprint (v2)

**Decision state: REVIEW PLAN ONLY. No GitHub write, commit, push, PR edit, force-push, merge, deletion, or code migration is authorized.**

Repository: https://github.com/shanmukhdatta/AURA  
Known remote branches from read-only audit: `main`, `experiment/stage-8-3-external-llm-verification`, `feature/stage-8-3-external-verification`; PR #1 exists. The **latest** Antigravity local `feature/external-validation-pipeline` was **not** present on the remote at the last check. Its source code and final complete test receipts remain an acquisition item.

## 1. Non-negotiable rule: everything is accounted for, not everything is mixed together

AURA must have **four distinct evidence layers**:

1. **Original historical record — byte-preserved:** original prototype code, Stages 1–7 release snapshots, all early and corrected notebooks, original run exports, raw tool logs, original result archives, original test receipts, and original analysis reports. Never silently replace an old version with a newer one.
2. **Canonical runnable implementation — one maintained code path:** working Stage 7 engine, contract schemas, evidence capture, verifier, CERA planner, baselines, external adapters, and the newest Antigravity CPU validation modules. Use **references and a migration map** to connect canonical code back to its source archives.
3. **Per-experiment proof trail — raw evidence:** frozen task/config, prompt/trajectory, actual tool results (including errors), before/after snapshots and original SQLite files, probes, observations, AURA certificates, strict reference scores, integrity and noninterference receipts, replays, full stdout/stderr and environment details. This layer is immutable.
4. **Derived publication layer:** consolidated CSV/JSON results, separately labeled verifier accuracy/concordance, experimental tables, cost studies, figures and manuscript references. Regenerate from layer 3 rather than hand-editing counts.

A path appearing in a README is NOT evidence that the corresponding file exists. Every referenced file must pass automated existence/hash checks. A failing experiment or abandoned notebook is **preserved and labeled development history**, not silently discarded or mixed with final metrics.

## 2. What is already recoverable and what is missing

The local read-only audit generated `AURA_Local_Source_And_Archive_Member_Manifest_v2.json`. It records **125 locally mounted loose/nested source files**, including **35 accessible ZIPs**, and **3,584 individual archived file members**, each archive/member carrying a SHA256 and archive CRC status. **35/35 ZIP archives passed CRC**. The scan is of available local session files, **not** of Antigravity's private machine, all historic chat sessions, the full GitHub history, or every possible source ever created. Some members are duplicates or development artifacts; counts are inventory entries, not independent experiments.

For the complete roster of original release and experimental archives with file hashes, also use `AURA_GitHub_Reproducibility_Source_Inventory.csv` from the prior audit. The new member-level manifest is complementary and must travel with the eventual handoff.

Not yet remotely verified: the latest `aura_validation/` Python source package, its new tests, the seven Antigravity `validation_reports/` files, the full claimed `224 passed / 1 skipped` test output, and the actual local branch commit history. **Do not record these as pushed or independently reproduced yet.**

## 3. Proposed GitHub tree — exact functions, directories proposed, do not fabricate files

```text
AURA/
├── README.md                         # Start here: objective, architecture, quickstart, evidence index
├── pyproject.toml / requirements/    # CPU dependencies + Kaggle environment pins
├── LICENSE / CITATION.cff            # Only after checking ownership/authorship
├── CHANGELOG.md
├── .gitignore / .gitattributes
├── .github/workflows/              # CI: CPU tests, archive manifests, short certificate replay
│
├── prototype/                       # EXPLICITLY separate original prototype history
│   ├── README.md                    # How original implementation evolved, version crosswalk
│   ├── design/                      # Early research freeze, formal specifications, design notes
│   ├── milestones/                  # Stage 1–7 prototype release/readme index
│   └── source_map.csv               # Version → original archive SHA → canonical module
│
├── AURA_Stage7/                     # INITIAL canonical runnable code, kept in its working layout
│   ├── schemas/                     # TaskContract, ProbeSpec, Observation, Certificate, etc.
│   ├── aura_verifier/               # engine.py; three-way decision
│   ├── aura_evidence/               # capture, diff, probes, trace, validation, ledger, hashes
│   ├── aura_planning/               # CERA, planner, examples, live runner
│   ├── aura_baselines/              # fixed / greedy / exhaustive and supported baselines
│   ├── aura_reasoning/              # reasoning/reference model support
│   ├── aura_external/               # AgentSynth, AgentDiff, AppWorld integration code
│   ├── aura_evaluation/             # local fault study and evaluation
│   ├── tests/                       # ALL Stage 7 unit/integration/regression tests
│   └── README.md
│   # Optional LATER: refactor into src/aura/, ONLY after tests and migration proof pass.
│
├── external_validation/             # LATEST separately identified verifier/replay pipeline
│   ├── README.md
│   ├── aura_validation/            # Copy real exported Antigravity modules unchanged first
│   ├── independent_reference/      # Independent scorer, rules, tests, scorer provenance
│   └── tests/                      # Full new tests, no rewritten expected outcomes
│
├── experiments/
│   ├── README.md                    # The entire taxonomy, all cohorts, correct denominators
│   ├── stage01_formal_prototype/
│   ├── stages02_to06_development/
│   ├── stage07_local_13_cases/
│   ├── stage07_cera_14400_evaluations/
│   ├── stage81_local_qwen_4/
│   ├── stage81_appworld_3_native/
│   ├── stage82_agentsynth_36_controls/
│   ├── stage82_inspection_ablations/
│   ├── stage83_g1_official_calibration/
│   ├── stage83_qwen05b_5/
│   ├── stage83_qwen3b_5/
│   ├── stage83_cera_64_worlds_per_policy/
│   └── external_validation_59_replay/
│   # For EACH executed cohort (use real run IDs, no dummy episode):
│   # README.md, code/, notebooks/, config/, raw/, runs/<run-id>/,
│   # logs/, results/, integrity/, manifest.json, reproduce.md
│   # Stage 8.4 deliberately NOT claimed without original run evidence.
│
├── evidence/                         # CROSS-REFERENCE INDEX, not uncontrolled duplication
│   ├── README.md
│   ├── master_source_registry.json
│   ├── experiment_registry.csv
│   ├── proof_chain_index.json       # Each run → links to raw trace, snapshots, cert, replay
│   ├── certificate_index.json
│   ├── raw_archive_index.json
│   ├── missing_or_unverified.json
│   └── provenances/                # version hashes, authorship/executor, timestamps
│
├── integrity/                        # Standalone research integrity / proof checks
│   ├── README.md
│   ├── sha256/                    # Original manifest and generated cross-check receipts
│   ├── crc/                       # ZIP CRC summaries
│   ├── snapshot_hashes/           # pre/post inspection hash receipts
│   ├── certificate_replay/        # replay results and equality criteria
│   ├── adversarial_controls/      # tampered digest, forged evidence, denied-readback results
│   └── verify_integrity.py        # Recompute hashes; reject missing/mismatched artifacts
│
├── results/
│   ├── README.md
│   ├── execution_results/          # Actual task outcomes, native graders, SQL-only scores
│   ├── verification_results/       # PASS/FAIL/UNCERTAIN, references, false counts, replay
│   ├── planning_and_cera/         # probe cost units, planner latency ms, prior sensitivity
│   ├── ablations/                 # inspection variants, negative controls
│   ├── tests_and_ci/              # command, environment, exact pytest stdout/stderr
│   ├── published_tables/          # generated CSV/Markdown/TeX
│   └── figures/                  # data-driven charts + exact source scripts
│
├── reproducibility/
│   ├── README.md
│   ├── cpu_evidence_replay.md      # No GPU: reproduce certificates from saved evidence
│   ├── cpu_controls.md            # Stage 7, Stage 8.2, CERA costs
│   ├── kaggle_runs.md             # Qwen/AppWorld instructions with version pins
│   ├── dependencies.lock          # Or real format chosen and verified
│   ├── commands/                  # Original shell commands and outputs
│   └── logs/                      # Runtime versions and immutable test/runner transcripts
│
├── docs/
│   ├── ARCHITECTURE.md            # Prototype vs current code, diagrams, module roles
│   ├── PROTOTYPE_EVOLUTION.md     # Stage-by-stage algorithms/changes/results
│   ├── VERIFIER_AND_CONTRACTS.md  # Formal contracts, frames, three-way semantics
│   ├── CERA_AND_BASELINES.md      # Cost model and empirical restrictions
│   ├── CERTIFICATE_AND_INTEGRITY.md
│   ├── EXPERIMENT_INDEX.md
│   ├── RESULT_PROVENANCE.md
│   ├── THREAT_MODEL.md
│   ├── RESEARCH_DECISIONS.md
│   ├── THIRD_PARTY_SOURCES.md
│   └── LIMITATIONS.md
│
├── paper/                          # Draft; not the source of experimental truth
│   ├── main.tex, references.bib, MANUSCRIPT.md
│   ├── tables/ and figures/
│   └── TABLE_TO_EVIDENCE_MAP.md
│
├── scripts/                       # Read-only auditors, verify, reproduce, regenerate tables
│
└── archive/                       # Byte-preserved historical original files
    ├── README.md
    ├── prototype_releases/          # Stage 1–7 original implementation ZIPs
    ├── original_result_exports/     # Original Stage 2–7 results ZIPs
    ├── external_experiment_exports/ # Original Stage 8.1/8.2/8.3 ZIPs
    ├── notebook_history/           # All v2/v3/v4/v5/v6/v7 attempts and their status
    ├── research_reports/           # Original authored research freeze and reports
    ├── earlier_audits/             # Versioned audits/corrections, not substituted
    ├── submission_drafts/          # Previous research handoffs/paper versions
    └── file_migration_manifest.csv # old path, canonical path, SHA256, disposition
```

`AURA_Stage7/` and `external_validation/` are the two immediate operational roots, so runnable imports can continue to work. `prototype/` explicitly explains and indexes prototypes; `archive/` contains original immutable bytes. `results/verification_results/`, `integrity/`, and `experiments/<cohort>/runs/` distinguish conclusions, proof validation, and actual run records. Unneeded duplication is avoided by **referencing immutable run files** from central index files.

## 4. Concrete original files that must be preserved

### Prototype and design history

- `AURA_Stage1_Formal_Specification_v1.md` and `.pdf`
- `AURA_Stage1_Schema_and_Test_Pack_v1.zip`
- `AURA_Stage2_Implementation_v1.zip` through `AURA_Stage7_Implementation_v1.zip` (all six individual numbered releases)
- `AURA_Stage2_Evidence_v1.zip`, `AURA_Stage3_Results_v1.zip`, `AURA_Stage4_Results_v1.zip`, `AURA_Stage5_Results_v1.zip`, `AURA_Stage6_Results_v1.zip`, `AURA_Stage7_Results_v1.zip`
- Stage-specific source `.md` reports and `.pdf` counterparts (where available), `AURA_Research_Freeze_v1.md` and `.pdf`, `AURA_Research_Decision_Log_v1.md`, project summary, and early prior-art matrix.

### Actual Stage 7 canonical modules and proof

- `AURA_Stage7/schemas/{TaskContract,ProbeSpec,Observation,Certificate,BoundedWorldModel,ReasoningLedger}.schema.json`
- `AURA_Stage7/aura_verifier/engine.py`; `aura_evidence/{capture,diff,trace,probes,validation,ledger,util}.py`
- `AURA_Stage7/aura_planning/{planner,examples,live_runner}.py`, `aura_baselines/surface.py`
- `AURA_Stage7/aura_reasoning/`, `aura_external/`, `aura_evaluation/`, `verify_task.py`, `verify_capture.py`, `verify_bounded.py`, `reproduce_stage3.py` ... `reproduce_stage7.py`, `run_stage7_local.py`, `tests/`, `pyproject.toml`
- **Raw Stage 7 evidence includes 13 actual `.sqlite3` files**, individual captures and traces, snapshot/run manifests, cost CSVs, policy tables, bootstrap differences, 4 image figures, ablation and scaling measurements. Retain the entire original results ZIP and readable relevant extracted files.

### Stage 8.1 local Qwen and AppWorld

- `AURA_STAGE8_1_OUTPUTS.zip`, actual matching notebook(s), run configs, `track_A/` prompt and model turns, four saved certificates, SHA256 manifest, independent reference and experiment summary.
- `AURA_APPWORLD_STAGE8_1_v7_RESULTS.zip`, `AURA_AppWorld_RootFix_v7_Kaggle.ipynb`, native task trajectories, API calls `.jsonl`, official AppWorld evaluation receipts, setup/environment and no-op records.
- Keep older AppWorld v5/v6 and notebook edits under `archive/notebook_history/` **with their errors**; mark AppWorld's 3 official agent tasks as having **no AURA certificates**.

### Stage 8.2 externally authored SQL control experiment

- `AURA_Stage8_2_External_SQL_Source_v1.zip`; `AURA_Stage8_2_External_SQL_Evidence_v1.zip`; original pilot `.md` and instructions; original episode and ablation `.csv` files.
- The evidence ZIP holds **331 file members**, including 36 case directories with per-variant `before.json`, `after.json`, `certificate.json`, `contract.json`, `independent_checkers.json`, `observations.json`, `probes.json`, `strict_frame_diff.json`, `trace.json`. Keep extra audits and summaries rather than manually recreating them.
- Preserve the actual source pack `core_v2.yaml` and upstream **commit citation** for AgentSynth; where redistribution rights are uncertain, pin source download instead of copying third-party assets.

### Stage 8.3 actual model cases and scoring

- Both `AURA_STAGE8_3_RESULTS.zip` (historical) and `AURA_STAGE8_3_CORRECTED_RESULTS.zip` (corrected), with visible superseded/corrected labels.
- Five Qwen0.5B saved multi-turn tool logs, model actions `.jsonl`, original `.sqlite3` states, prompts, frozen contracts, probes, observations, certificates, independent references, official G1 calibrations, replay receipts, `g4_metrics_corrected.csv`, `g4_cost_corrected.csv`, original audit/report and evidence SHA256 manifests.
- `AURA_STAGE83_QWEN3B_PILOT_RESULTS.zip` and **actual executed** `AURA_Stage83_Qwen3B_Real_Agent_Kaggle_Pilot.ipynb`, prompts/configs, SQL tool outputs, database snapshots, five AURA certificates, 103 manifest file hashes (verified earlier), original pilot report.
- Keep old Kaggle notebook v1/v2 under `archive/notebook_history/` if it was not the one actually executed; **do not claim** an unexecuted notebook produced results.

### Independent validations, integrity and publication generators

- Actual Antigravity local `aura_validation/` package, its new tests, **all seven** `validation_reports/` outputs, full `pytest` log and CPU environment receipt — **must first be exported**.
- `EXPERIMENT_INVENTORY_FINAL.csv`, `cohort_summary(1).csv`, `VALIDATION_EXECUTION_REPORT.md`; reconcile against the exact runner outputs and file hashes.
- Preserve independent reference code `stage83/independent_reference.py`, original scorer tests, negative tampering tests, and versioned reference definitions. Do not call shared-task-contract agreement independently proven semantic correctness.
- Include the reproducible table generator and existing draft files `paper/generate_research_tables.py`, `paper/main.tex`, `paper/MANUSCRIPT.md`, and `.bib`, while keeping prior drafts in the archive.

## 5. One-row-per-artifact master inventory and per-run proof chain

All *top-level files and every member inside every preserved ZIP* must appear in the `master_source_registry.json` with at least:

`asset_id`, `kind`, `original_location`, `original_filename`, `archive_member_path` if applicable, `size_bytes`, `sha256`, `archive_crc_status`, `origin_executor` (`ChatGPT sandbox`/`Antigravity`/`Kaggle`/`user`/`third_party`/`unknown`), `stage`, `experiment_id`, `canonical_git_path`, `status` (`ORIGINAL`/`EXTRACTED_COPY`/`GENERATED`/`SUPERSEDED`/`MISSING`/`UNVERIFIED`), `shareability` (`PUBLIC`/`REDACT`/`PRIVATE`/`REVIEW`), `notes`, and `source_commit` when known.

The per-run `proof_chain_index.json` must link the following **without inventing missing items**:

1. Task request, task ID, frozen contract and contract hash.
2. Exact source code/notebook ID, upstream dataset commit, dependency/environment config, seed, decoding settings, max turns and machine/GPU if available.
3. Raw model dialogue/tool call records and **actual tool outputs** (including SQL syntax errors), whether task was scripted or genuine LLM.
4. Before/after snapshots and original `.sqlite3`/filesystem capture; frame diff and allowed mutation surfaces.
5. Independent probes, observations, reference/scorer provenance, AURA original certificate, integrity digest, and replay certificate/result.
6. Command stdout/stderr, wall/probe/planner timing **where measured**, hash noninterference receipt, negative control results when relevant.
7. Exact CSV table row(s), figure data and paper table/claim that derived from this run.

For records that had no certificate (notably AppWorld), use `certificate_available=false`; do not populate one. A `MISS`/`NOT_APPLICABLE` field is appropriate when real evidence is absent or a stage did not run.

## 6. Automated **zero-omission** and integrity gates before the first push

**Gate Z0 — Source freeze:** export Antigravity's unpushed branch and reports. Store/read SHA256 for all uploaded ZIPs, first-party source notebooks, and original test logs. Capture Git remote branch heads and PR #1 current state.

**Gate Z1 — Coverage inventory:** enumerate every visible local source file **and every ZIP archive member**, plus every existing GitHub tracked file, and Antigravity's exported files. Compare all three inventories; record every discrepancy by hash. No silent omission. Report duplicates by hash; deduplicate in canonical working tree only.

**Gate Z2 — Source-to-repository mapping:** assign each inventory record an explicit `PRESERVE_ORIGINAL`, `EXTRACT_AS_READABLE`, `CANONICAL_CODE`, `ARCHIVE_ONLY`, `PRIVATE_REDACT`, `EXTERNAL_UPSTREAM_LINK`, or `MISSING` disposition. Mapping for `AURA_Stage7/` must preserve imports until migration passes tests.

**Gate Z3 — Proof validation:** for each eligible actual run, require a complete chain or record exactly which links are missing. Verify `sha256`, CRC, original SQLite snapshot, certificate replay, reference-source version and noninterference where applicable. Do not assert 100% replay for unverified cases.

**Gate Z4 — Execution receipts:** run tests from the exact code tree, save **unabridged stdout/stderr**, `python --version`, OS, dependency lock, commands, start/end time, exit code, and skipped-test reasons. Run additional CPU reproduction and note non-deterministic timing/model-generation limitations. CI must validate artifacts, not just syntax.

**Gate Z5 — Scientific tables:** regenerate all counts from the registry, strictly separate `13 + 36 + 5 + 5 = 59` certified validation episodes from **four extra Stage 8.1 local Qwen trajectories**, **three AppWorld native evaluations without certificates**, **14,400 Stage 7 planning/world-policy evaluations**, Stage 8.2 ablations, and official G1 calibration. Stage 8.4 remains unclaimed.

**Gate Z6 — README and links:** check root README, prototype README, core engine README, external validation README, EVERY cohort README, results README, integrity README, archive README, and reproducibility docs. Each table claim points to a registry/query/log and valid file; mark proof strength and limitations.

**Gate Z7 — Security and Git hygiene:** scan for tokens, API keys, personal data, third-party dataset redistribution restrictions, notebook outputs with secrets, disallowed artifacts, large models. Preserve unredacted originals **securely outside the public Git repository if needed**, with private digest references; do not compromise privacy in the name of publishing everything. Use Git LFS/GitHub Releases for legitimately large public evidence only with pinned hashes and reproducible download instructions.

**Gate Z8 — Pre-push human review:** produce full dry-run `git status`, `git diff --stat`, `git diff --name-status`, new/missing file mapping, integrity report, test receipt, missing-evidence register, generated table comparison, and proposed PR description. **STOP here until explicit user approval**. Afterwards, push a dedicated consolidation branch without touching `main` and open/update only the user-approved PR.

## 7. What every README must explain

- **Root:** project motivation, contribution and limitations; quickstart; architecture figure; evidence matrix (not a single misleading success percentage); exact stage/file map; `CPU evidence replay` and `CPU controlled re-run` commands; pointer to logs/certificates/hashes; licensing and official-vs-reproduced scores.
- **Prototype:** chronological Stage 1–7 objectives, original source ZIPs/reports, versions of engine and schemas, reasons for design changes, which source is canonical now.
- **Verification/core:** contracts, independent probes, frame restrictions, PASS/FAIL/UNCERTAIN reason codes, trusted assumptions, certificate fields, SHA integrity versus digital signatures, exact test commands.
- **CERA:** prior assumptions, fixed/greedy/exhaustive/optimal baselines, theoretical/prototype limits, 14,400-world study, 64-world corrected comparison; dimensional separation of probe cost units and milliseconds; negative results preserved.
- **Every experiment:** source and exact task set, scripted/LLM, execution environment, model/version/seed/turns, raw artifact SHA, all files in original ZIP, exact command, outputs, known failures, correct denominator, how to verify/reproduce, limitations.
- **Integrity:** archive-member manifest, checksum algorithm, CRC, snapshot hash, certificate replay equality, adversarial negative controls, unverified artifacts and trust assumptions. A SHA256 digest proves integrity relative to trusted anchor, **not** provenance or authenticity by itself.
- **Results:** distinguish original task success, published native scores, reproduced SQL-only checks, independent reference judgments, AURA certificates, scripted control truth labels, CERA worlds, and notebook setup trials. Each table has generating code.
- **Archive:** explain why early/failed attempts are retained, which version superseded which, and that historical files should not be imported as current code.

## 8. Required Antigravity handoff before implementation

Only the **latest missing local code/report export** is essential, because other major original archives are present in the session. Ask Antigravity to provide:

1. A `.zip` or `git bundle` preserving `feature/external-validation-pipeline` source and its history (not only screenshots), with a manifest.
2. Complete `aura_validation/` source, newly added tests, all 7 `validation_reports/` files and all original pytest outputs corresponding to the claimed **224 passed, 1 skipped**.
3. Original `git status`, `git rev-parse HEAD`, branch name, `git log -10 --oneline`, unstaged files list, OS/Python versions, and exact full reproducing commands.
4. Inventory mapping the stage's 59 recorded cases back to original raw artifacts; documented exclusions of 4 Qwen Stage 8.1, 3 AppWorld and planner evaluations.
5. If there was a real Stage 8.4, provide exact source code, raw run files and matching hashes; otherwise leave it as not performed.

**Do not require re-running Qwen or Kaggle. Do not push yet.**

## 9. Approval checkpoint

The planned repository is complete **only when every available historical source artifact has a manifest row and disposition**, every claimed result has a provenance path or explicit gap, the core imports and tests pass, and all README links work. This does not mean every archival experiment can be recreated on every machine, but it does make limitations transparent. Show the dry-run diff and missing-file list, then obtain explicit approval before any GitHub push.
