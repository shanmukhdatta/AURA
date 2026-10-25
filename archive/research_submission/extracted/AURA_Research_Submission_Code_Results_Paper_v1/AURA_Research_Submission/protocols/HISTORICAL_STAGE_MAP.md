# Stage-by-stage implementation and paper evidence map

| Stage | Research/engineering contribution | How used in paper | Raw/source material |
|---|---|---|---|
| Stage 1 | Formal task contract and conservative verdict definitions | Verification semantics and design assumptions | Formal specification, original report and early schema pack |
| Stage 2 | Capture SQLite/file state and basic independent observations | Evidence capture | Historical Stage 2 report and results ZIP |
| Stage 3 | Persistent-state and declared side-effect checks | Closed-world frame checks | Historical Stage 3 report and results ZIP |
| Stage 4 | Evidence arbitration and consistency | Three-way verdict | Historical Stage 4 report and results ZIP |
| Stage 5 | Planner policy comparisons | Background to CERA | Historical Stage 5 report and results ZIP |
| Stage 6 | Broader experiment/test routines | Engineering integration | Historical Stage 6 report and results ZIP |
| Stage 7 | Controlled evaluation, prior ablation, local execution and latency | **Primary modeled/local methodology results**; 48 authored templates × 3 priors, 14,400 policy/world evaluations; 13 × 5 local scripted runs | `evidence/source_archives/AURA_Stage7_Results_v1.zip` and `evidence/AURA_Stage7_Report_v1.md` |
| Stage 8.1 local | Four real-model local workflows | Small real-model feasibility sample | `AURA_STAGE8_1_OUTPUTS.zip` |
| Stage 8.1 AppWorld | 3 native agent tasks, 0 native successes | External agent feasibility / negative baseline; **no AURA AppWorld verdicts** | `AURA_APPWORLD_STAGE8_1_v7_RESULTS.zip` |
| Stage 8.2 | Externally-authored six SQL tasks, 36 scripted control outcomes; 144 dependent inspection ablations | Verification cases and uncertainty results | `AURA_Stage8_2_External_SQL_Evidence_v1.zip` |
| Stage 8.3 CPU | Five genuine Qwen0.5 external SQL tasks, corrected metrics and independent shared-contract reference | Real model evidence with 1 PASS / 4 FAIL | `AURA_STAGE8_3_CORRECTED_RESULTS.zip` |
| Stage 8.3 GPU | Five genuine Qwen3B external SQL tasks with snapshots/certificates | Real model evidence with 3 PASS / 2 FAIL | `AURA_STAGE83_QWEN3B_PILOT_RESULTS.zip` |
| Stage 9 | Publication packaging, independent paper tables, source provenance and manuscript drafting | **This submission overlay** — not a new agent experiment | `research_submission/`, `paper/`, `outputs/` |

**No double counting:** Stages 1–6 are development history feeding Stage 7, not independent novel samples to be added to Stage 7 counts. Stage 8.2's 144 ablation certificates are derived from the same 36 states, not 144 new worlds. Stage 8.1 local and Stage 8.3 real-LLM cohorts are separate runs. AppWorld's official agent scores do not measure AURA verifier quality.
