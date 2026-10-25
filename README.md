# AURA — Agent Uncertainty and Residue Arbiter

Evidence-gated verification of multi-step AI-agent task completion. AURA verifies agents via task contracts, online state snapshot pairs, strict closed-world frame policies, noninterfering probes, and mathematically sound `PASS` / `FAIL` / `UNCERTAIN` certificates.

---

## 📄 Publication Manuscript & Research Package

- **Full Publication Manuscript (Markdown)**: [`paper/MANUSCRIPT.md`](paper/MANUSCRIPT.md)
- **LaTeX Source**: [`paper/main.tex`](paper/main.tex) and [`paper/references.bib`](paper/references.bib)
- **Automated Research Tables**: [`paper/tables/`](paper/tables/) (Generated via `python paper/generate_research_tables.py`)
- **Reproducibility Guide**: [`paper/REPRODUCIBILITY.md`](paper/REPRODUCIBILITY.md)
- **GitHub Pull Request**: [Draft PR #1: Stage 8.3 External Verification](https://github.com/shanmukhdatta/AURA/pull/1)
- **Feature Branch**: [`feature/stage-8-3-external-verification`](https://github.com/shanmukhdatta/AURA/tree/feature/stage-8-3-external-verification)

---

## 🔬 Evidence Status & Empirical Summary (October 2026)

- **Stages 0–7 (Core Verifier & Planning Engine)**: Formally specified and tested. 193 core regression tests pass cleanly on clean rerun (1 skipped on Windows non-admin symlink creation).
- **Stage 8.1 (AppWorld Exploratory Study)**: Evaluated 3 official AppWorld tasks with official native evaluations.
- **Stage 8.2 (Controlled Fault Injection)**: 36 scripted episodes across 6 tasks from clean replication. 100% agreement with predesigned control expectations (6 PASS, 24 FAIL, 6 UNCERTAIN; 3/3 negative tampering controls REJECTED).
- **Stage 8.3 (External Agent Benchmark Verification - Completed & Audited)**:
  - Official AgentSynth harness validated at pinned commit `d2564dfb25`: oracle 14/14 (100%), noop 0/14 (0%).
  - 14 frozen contracts with strict cell-level closed-world allowlists.
  - Genuine local multi-turn LLM inference on CPU with `Qwen/Qwen2.5-0.5B-Instruct` (5 tasks, seed 42): 1 PASS (20%), 4 FAIL (80%).
  - Genuine GPU multi-turn LLM inference on Kaggle T4 with `Qwen/Qwen2.5-3B-Instruct` (5 tasks, seed 42): 3 PASS (60%), 2 FAIL (40%).
  - **100% Sound Lower Bound**: Zero false PASS, zero false FAIL across all 46 evaluated episodes (10 genuine LLM runs + 36 scripted controls) against blinded independent ground truth.
  - **Benchmark Gaming Case Study**: Caught critical substring loophole in standard AgentSynth checkers (`refuse-cancel-shipped`), where an agent recommending order cancellation was falsely awarded 1.0 by naive substring matching, but soundly failed by AURA.

---

## 📊 Summary Benchmark Results

| Evaluation Cohort | Model / System | Hardware | N | Benchmark SQL Pass | Strict Ground Truth | AURA Verified | False PASS | False FAIL | Concordance |
|---|---|---|---|---|---|---|---|---|---|
| **Genuine LLM (0.5B)** | Qwen2.5-0.5B-Instruct | CPU (x86_64) | 5 | 2/5 (40.0%) | 1/5 (20.0%) | **1/5 (20.0%)** | **0 / 5 (0.0%)** | **0 / 5 (0.0%)** | **100.0%** |
| **Genuine LLM (3B)** | Qwen2.5-3B-Instruct | T4 GPU (CUDA) | 5 | 3/5 (60.0%) | 3/5 (60.0%) | **3/5 (60.0%)** | **0 / 5 (0.0%)** | **0 / 5 (0.0%)** | **100.0%** |
| **Scripted Controls** | Deterministic Fault Harness | CPU | 36 | 6/36 (16.7%) | 6/36 (16.7%) | **6/36 (16.7%)** | **0 / 36 (0.0%)** | **0 / 36 (0.0%)** | **100.0%** |

---

## ⚡ Quickstart & Replication

### 1. Run Complete Test Suite (212 Tests)
```bash
pytest AURA_Stage7/tests stage83/tests -v
```

### 2. Regenerate All Publication Research Tables
```bash
python paper/generate_research_tables.py
```

### 3. Replay Certificates and Audit Independent References
```bash
python stage83/independent_reference.py
python stage83/run_g4_analysis.py
```

---

## 🛡️ Research Ethics & Provenance
AURA enforces non-negotiable scientific integrity rules:
1. Scripted fault-injection controls are strictly segregated from natural LLM rollouts.
2. Missing or denied evidence fails closed with `UNCERTAIN` rather than false certification.
3. Every certificate cites raw pre- and post-execution SQLite snapshot digests verified for noninterference.

Benchmark source: [AgentSynth](https://github.com/agentsynth/agentsynth) (`packs/core_v2.yaml`), MIT License.
Repository: https://github.com/shanmukhdatta/AURA
