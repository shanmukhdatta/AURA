# MASTER TASK — AURA research-code modularization and short-paper submission

You are the software engineer, methodologist, and reproducibility auditor for **AURA (Agent Uncertainty and Residue Arbiter)**. The project has already been built through Stage 8.3, with real positive and negative evidence. **Your mission is to USE the experiments we have, finish a modular and verifiable research package, and help prepare a credible short IJERT research/technical-note submission. STOP treating every imperfect result as a reason to rerun all agents. Preserve failures as useful observations.**

## A. Source, workspace and provenance

1. Clone `https://github.com/shanmukhdatta/AURA`, inspect `main` and PR #1's `feature/stage-8-3-external-verification` branch; record real SHA using `git rev-parse HEAD`. Do not invent commit IDs, assume tags, or rewrite main.
2. Extract the provided `AURA_Research_Submission.zip` into a separate working directory. Its archival original source files and raw result ZIPs are immutable. Read `README.md`, `protocols/RESEARCH_CLAIM_BOUNDARIES.md`, `paper/AURA_Preliminary_Research_Paper_Draft.md`, and `outputs/build_receipt.json` first.
3. Compare *research overlay* to existing GitHub implementation. Reuse current `AURA_Stage7` verifier, CERA planner, and AgentSynth runtime adapter. Avoid rebuilding working systems or modifying the Stage 8.1/8.2/8.3 output history.
4. The stage83 code and Stage 7 code in the archive are historical snapshots; the integrated `aura_external.agentsynth_adapter` is on the feature GitHub branch. Reconcile versions deliberately, test imports, and log actual provenance.

## B. The research objective / paper positioning

Study whether a contract-driven verifier can distinguish completed, failed and unobservable agent workflows using independently collected terminal state, trusted tool traces and explicit authorized-write frames. AURA provides PASS, FAIL and UNCERTAIN certificates. CERA is an adaptive readback planner; its advantages are conditional, not universal.

Use this **working title**:
`AURA: Evidence-Gated Verification of Multi-Step AI-Agent Task Completion — Design and Preliminary Experimental Evaluation`

Target a **small primary research paper or technical note**, not an invented SOTA journal breakthrough. Follow the current journal's actual official template and page limits; do not assert acceptance.

## C. Modules to create/reconcile (do actual code changes)

```text
AURA/
  AURA_Stage7/                 # Existing runtime: verifier/evidence/planner (preserve APIs)
  stage82_agentsynth_pilot.py  # Existing scripted external SQL controls
  stage83/                     # Existing real model agent runtime + independent reference + tests
  research_submission/        # NEW reproducibility overlay
    audit.py                   # ZIP CRC + SHA manifest validation + provenance
    tables.py                  # Recomputed Stage7/CERA and Stage8.x cohort tables
    run_all.py                 # One-command report reconstruction
    tests/                     # Negative/tamper and integration tests
    paper/                     # Submission-quality manuscript + supporting tables
    protocols/                # Scientific claim rules, experiment limitations, tasks
    outputs/                  # Machine-generated CSV/JSON/receipts
```

Either integrate the provided research package into a new `research/paper-packaging` feature branch or, if that conflicts with the existing PR, open a separate PR targeting its current feature branch. Keep relative imports and commands reproducible. Add minimal docs and a non-destructive dependency lock. Do not commit huge binaries, hidden benchmark test fixtures, model weights or private data without review; link/hash large evidence externally instead.

## D. Evidence inventory — use EVERY experiment appropriately, not one pooled accuracy number

- Stage 7: 48 created planner templates, 3 priors, 14,400 modeled policy-world trials; 13 scripted SQLite/filesystem scenarios × 5 policies = 65 local executions; 186 legacy regressions; timed CERA vs greedy results; a deliberately *undetected reverted transient mutation*.
- Stage 8.1 local: 4 genuine Qwen2.5-3B tool-agent local-controlled tasks; 1 PASS / 3 FAIL AURA certificates.
- Stage 8.1 AppWorld: 3 authentic benchmark tasks, native agent results 0/3 success; **zero AURA-AppWorld certificates**. Keep as agent-only negative baseline, not AURA validation.
- Stage 8.2 AgentSynth: 6 upstream task definitions × 6 scripted variants = 36 real SQLite control outcomes (6 PASS, 24 FAIL, 6 UNCERTAIN), and 144 dependent inspection ablations. Controls are not new agent-generated runs. The extra-write / narrower SQL-checker difference is a contract-scope illustration.
- Stage 8.3 Qwen0.5B CPU: 5 real LLM external SQL episodes, 1 PASS / 4 FAIL, single seed; matched strict-contract judgments are shared-spec references; original CLI not used on the five model episodes.
- Stage 8.3 Qwen3B GPU: 5 real LLM external SQL episodes, 3 PASS / 2 FAIL; SQL-predicate reproduction and replayed AURA certificates; original CLI not used on these five model episodes.
- Stage 8.3 CERA four-domain modeled study: 64 worlds per policy; CERA and greedy matched modeled cost with higher CERA planning latency. Do not present predicted >10ms probe benefits as demonstrated empirical results.

The 53-row derived registry has 17 genuine agent episodes total including AppWorld-only 3, plus 36 scripted external SQL control rows. NEVER use 53 as an AURA accuracy denominator. Different LLM model cohorts are not comparable without an identical task, prompt and evaluator setup.

## E. First commands (run before editing results)

```bash
python -m research_submission.run_all
python -m unittest discover -s tests -v
# In integrated GitHub runtime environment, additionally:
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q AURA_Stage7/tests stage83/tests
```

Confirm ZIP CRC and manifest, regenerate `cohort_summary.csv`, `episode_registry.csv`, Stage 7 prior sensitivity, bootstrap data, local timing, and 64-world cost table. Record timestamps, Python/package versions and executed commands. If a test can't run, mark `NOT_RUN` and explain why.

## F. Manuscript writing and submission preparation

1. Use the provided draft's architecture, vocabulary, limitations and all supported cohorts. Avoid reconstructing source science from generic model knowledge.
2. Write a concise, independently understandable IJERT-style manuscript: title, author/affiliation placeholders, abstract, introduction, related work with accurate citations, contract/evidence/decision methods, experiment design, quantitative results, limitations and conclusion. Format using the downloaded **official current journal template**; do not submit or pay without the user's final approval.
3. Keep original/source result tables in appendices, and a small selected set in the paper: planner cost sensitivity, 36 control outcomes, 3 real-LLM AURA cohorts, and the 3 AppWorld-native outcomes clearly labeled without AURA.
4. Cite the upstream task authors and relevant work (AppWorld, ToolSandbox, AgentProcessBench, AgentSynth). Never claim ownership of external datasets, “world-first” verification, SOTA, universal zero false accepts or a general GPU speedup.
5. Add a **reproducibility and research limitations** section including detection of a reverted transient mutation as a known blind spot. State trial counts and seeds.
6. Keep accepted review improvements narrowly focused on factual errors: authorship, template layout, quote/citation correctness, measured counts, fatal reproducibility problems. Do not unnecessarily rerun old experiments or re-engineer completed modules.

## G. What extra experiments to consider only if needed

**Default: no extra GPU work.** We already have a small-paper pilot. At most recommend one of the following, with scientific rationale, not all by default:
- Five-to-ten independently sampled agent tasks under a single shared model/prompt/evaluator to support a stronger statement about real-agent verification; OR
- Repair evaluation of the existing saved LLM episodes using the *complete official AgentSynth scorer*, with clear trajectory provenance; OR
- A fair identical-contract postcondition/frame comparator and measured remote probe-cost experiment before making a CERA speed claim.

Do not force continuation to 14 tasks × 3 seeds to write a modest feasibility report. More task data are optional, not a prerequisite to the engineering contribution.

## H. Deliverables and stop conditions

Produce and link:
1. `research_submission/README.md` and runnable `python -m research_submission.run_all` command.
2. Verified `evidence_registry.json` or CSV + SHA256 manifest, raw source archive references.
3. Generated `paper_tables/*.csv` and a paper-ready Results section that agrees with the archives.
4. `paper/AURA_IJERT_Manuscript.docx` and a viewable PDF if the official template is accessible; otherwise a complete Markdown draft and a template blocker. Do not change results to fit the page count.
5. `AURA_RESEARCH_REPRODUCIBILITY_REPORT.md` with executed commands, tests, graph/table provenance and known limitations.
6. GitHub feature-branch commit and PR (no automatic main merge). If unable to push, return a complete diff/ZIP and exact instructions.
7. A short `NEXT_OPTIONAL_EXPERIMENTS.md` (only actionable studies that improve a clearly stated missing scientific claim).

**Stop and return finished artifacts when these are done.** It is better to submit a clearly scoped, honest and reproducible technical note than to repeatedly claim that inconclusive results require another full pipeline rebuild.
