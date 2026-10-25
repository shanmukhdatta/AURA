# AURA: Evidence-Gated Verification of Multi-Step AI-Agent Task Completion — Design and Preliminary Experimental Evaluation

**Working manuscript — research/technical-note draft; NOT yet submission formatted or peer reviewed**  
**Authors:** [To be supplied and approved by contributors]  
**Affiliation:** [To be supplied]  
**Corresponding author:** [To be supplied]

## Abstract

Language-model agents can report successful task completion despite incomplete database updates, rejected tool commands, missing workflow steps, or unintended side effects. We present AURA (Agent Uncertainty and Residue Arbiter), a contract-driven verification prototype that inspects independent execution evidence and issues PASS, FAIL, or UNCERTAIN certificates. Its task model checks required final-state conditions, declared process obligations, and persistent state changes outside an authorized frame. We evaluate AURA using finite-world policy simulations, 65 scripted local SQLite/filesystem policy executions, 36 fault-injection controls over six externally authored SQL tasks, and 14 real-model episodes with AURA certificates across local and external SQL scenarios. An additional three official AppWorld tasks evaluate an agent but have no AURA certificates and are not included in AURA success estimates. All 36 external SQL control outcomes matched the designed reference labels. On a five-task Qwen2.5-3B Kaggle pilot, AURA issued three PASS and two FAIL judgments, agreeing with reproduced SQL outcome checks. Evidence-selection performance was mixed: CERA reduced modeled marginal probe cost against greedy under a uniform prior, but lost under a high-success prior and incurred more local planning overhead. We report observation-boundary limits and the small-sample nature of this preliminary study.

**Keywords:** AI agents; postcondition verification; uncertainty; persistent side effects; agent benchmarking; evidence selection; SQLite.

## I. Introduction

Tool-using AI agents can edit databases, manipulate files, or interact with application APIs. A final natural-language assertion such as “completed successfully” is not independent evidence that the requested task was performed. Tool execution may fail silently, preserve an outdated value, or create unintended persistent changes. State-based agent benchmarks already exist, so the contribution here is **not** the invention of state checking. We instead study a lightweight, explicit verification workflow in which task contracts, evidence coverage, and uncertainty are first-class outputs.

AURA is intended to answer a restricted question: whether independently observed behavior satisfies **declared** obligations. It does not infer every unstated human intention, prove all transient events from terminal snapshots, or guarantee validity when a source of supposedly independent evidence is untrustworthy. This paper reports a working implementation and a scoped set of pilot experiments, including cases where its planning method is weaker than simpler alternatives.

## II. Related Work and Positioning

AppWorld provides application environments and a native evaluator supporting checks for expected and unexpected changes [1]. ToolSandbox addresses stateful, conversational tool use with trajectory milestones [2]. AgentProcessBench studies step-level annotations of tool-using agents [3]. AgentSynth provides externally authored, outcome-checked SQL scenarios [4]. These works demonstrate that correctness checks, stateful tool environments, and process error analysis are established research directions. AURA focuses on a reproducible composition of **explicit contractual obligations**, conservative three-way verdicts, state/trace evidence, and a counterexample-guided readback selection policy. Broader claims of novelty or superiority would require stronger controlled comparisons than this pilot provides.

## III. Verification Design

### A. Task contracts and evidence

Each AURA task contract declares (i) required postconditions, (ii) permissible persistent writes and forbidden collateral changes, (iii) mandatory process events where warranted, and (iv) available observation surfaces. The local prototype uses SQLite and filesystem snapshots plus controlled tool traces. Observations record provenance, freshness/epoch and content digests; certificate replay requires the same contract and observation data.

### B. Verdict semantics

AURA reports **PASS** when all declared obligations are supported by the available complete evidence, **FAIL** when trusted observations establish a violation, and **UNCERTAIN** when the evidence is insufficient or inconsistent for a decisive judgment. These are relative to the defined contract and inspector trust assumptions; they are not unconditional statements about the world. A before/after diff alone cannot establish that no temporary unauthorized write was later reversed.

### C. Counterexample-guided evidence selection

The CERA planner uses a bounded finite-world model to select discriminative verification probes. Its theoretical search-space reduction competes with a fixed order, cost-greedy policy, a bounded exact reference and exhaustive inspection. Inspection cost in simulation is measured in **authored abstract units**, separate from measured CPU planning time and actual database readback time.

## IV. Experimental Method

The evaluated evidence spans five distinct populations. They are reported separately rather than counted as interchangeable independent samples.

**E1 — modeled selection policies:** 48 researcher-authored task/probe templates, three declared prior regimes, and 14,400 policy/world evaluations. Simulated model correctness and marginal probe-cost outcomes are compared within identical worlds; template-resampled bootstrap intervals describe **only this constructed suite**.

**E2 — controlled local execution:** 13 author-defined SQLite/filesystem cases × five planner policies = 65 executions, including an example of an unauthorized transient write fully reversed before capture.

**E3 — local real LLM:** Four Qwen2.5-3B-Instruct tool workflows with self-authored tasks and independent local reference judgments. Two scenarios contain injected tool or readback faults. These are not external benchmark tasks.

**E4 — external SQL scripted controls:** Six selected published AgentSynth `core_v2` tasks × six scripted execution variants = 36 outcomes. These are not 36 real-model episodes. They use actual persisted SQLite states and AURA evidence capture, with custom task-frame restrictions.

**E5 — real LLM on external SQL:** Five Qwen2.5-0.5B-Instruct CPU episodes and five Qwen2.5-3B-Instruct Kaggle GPU episodes, each at one seed. Task selections, prompts, runtime and source revisions differ; **no controlled head-to-head model comparison is inferred**. Official AgentSynth CLI evaluation was performed for an oracle (14/14) and a do-nothing control (0/14) but **not** for the recorded LLM episodes, which use reproduced SQL-checker and/or shared-contract reference assessments.

A separate three-task AppWorld dev evaluation resulted in 0/3 agent successes. AURA issued no AppWorld certificates, so those native scores evaluate the agent, not AURA.

## V. Results

### A. Modeled probe selection

| Declared world prior | Fixed cost | Greedy cost | CERA cost | Bounded exact reference |
|---|---:|---:|---:|---:|
| Uniform | 5.485 | 4.316 | **3.193** | 3.171 |
| 50% clean | 9.871 | 6.475 | **6.324** | 5.894 |
| 90% clean | 13.794 | **8.407** | 9.120 | 7.761 |

All costs are model-assigned marginal **probe-cost units**, not milliseconds. CERA saved approximately **26.0% relative to greedy under the uniform prior**, but incurred approximately **8.5% more modeled cost** under the 90% clean prior. In the 65 local scripted executions, mean end-to-end verification time was about **3.751 ms for CERA versus 3.011 ms for greedy**. A later four-domain 64-world-per-policy model evaluation measured the same average probe cost (3.25 units) for CERA and greedy, with higher planning overhead for CERA (about 0.371 ms versus 0.074 ms). These results do **not** establish a practical universal speedup.

### B. External SQL control study

| Scripted variant | AURA result | Cases |
|---|---|---:|
| Correct oracle action | PASS | 6 |
| No action | FAIL | 6 |
| Falsely successful tool response | FAIL | 6 |
| Incomplete required work | FAIL | 6 |
| Unauthorized extra persistent write | FAIL | 6 |
| Denied independent readback | UNCERTAIN | 6 |

Agreement was 36/36 relative to **designed injection expectations**, not independent generalization accuracy. Notably, all six unauthorized-extra-write cases still satisfied the narrower reproduced SQL outcome predicates, whereas the local AURA frame contract rejected the additional changes. This is a **difference in assessed obligation scope**, not a fair claim of superiority over a baseline enforcing identical rules.

### C. Real-model agent episodes

| Evaluation cohort | Total | AURA PASS | AURA FAIL | AURA UNCERTAIN | Reference scope |
|---|---:|---:|---:|---:|---|
| Local Qwen2.5-3B | 4 | 1 | 3 | 0 | Author-defined local contract |
| External SQL Qwen2.5-0.5B | 5 | 1 | 4 | 0 | Shared strict contract; reproduced SQL checks |
| External SQL Qwen2.5-3B | 5 | 3 | 2 | 0 | Reproduced published SQL outcome predicates |

All five Qwen2.5-3B GPU certificates were independently replayed; three persisted the required database changes and two rejected SQL calls left tasks uncompleted. The 0.5B external run also produced replayable certificates but included a refusal-answer specification disagreement during earlier analysis. A later stand-alone strict reference agreed on the negative outcome for that saved response; it used the task contract definitions shared with AURA, so fully independent task-intent validation remains incomplete. The GPU and CPU external cohorts cannot be compared as a controlled model-size study.

### D. External benchmark failures without AURA scoring

The AppWorld pilot evaluated three genuine agent tasks with an official native scorer; all three tasks failed. No AppWorld-to-AURA contract adapter was run. We retain these as **agent baseline/protocol feasibility evidence**, not as verification accuracy measurements.

## VI. Discussion and Limitations

These pilots demonstrate that the implementation can produce reproducible evidence-gated certificates on actual SQLite states and real LLM-generated tool actions. They also expose important limits. The contract is an explicit approximation of the user's actual intent. Some upstream checkers are narrower than the AURA contract, so agreement/disagreement does not by itself imply methodological superiority. An independent scorer sharing AURA's contract is blind to AURA's predictions but is not an independent task-specification authority. Five external episodes per model cohort and one seed are insufficient for a population-level accuracy claim. The original 186-regression-test suite is engineering validation, not statistical evidence of external soundness. CERA's benefits are prior- and cost-model-dependent; its planner can be slower than greedy locally. Missing authoritative readback requires abstention. Transient reverted mutations can escape final-snapshot comparison. No cryptographic attestation of remote tool honesty is provided by local digests alone.

For reproducibility, the companion research package includes original source/result ZIPs, SHA256/CRC checks, a read-only cohort builder, and derived CSV tables. Historical artifacts and negative results are preserved unchanged.

## VII. Conclusion

AURA is a functional contract-driven prototype for checking AI-agent task completion against independent persistent-state and trace evidence. Across controlled local and externally authored SQL experiments it detected missed updates, extra persistent writes and unavailable evidence. Real Qwen2.5-3B GPU executions produced three verified PASS and two FAIL certificates in five task episodes. CERA was economical under certain simulated priors but was not consistently better than greedy in modeled or local timing comparisons. The results support **technical feasibility and preliminary experimental evaluation**, not universal accuracy, optimality or deployment-level guarantees. Future work should investigate independent natural-language contract validation, fully official benchmark scoring of model episodes, trusted mutation journals, and comparable measured verification cost across larger runs.

## References

[1] H. Trivedi et al., “AppWorld: A Controllable World of Apps and People for Benchmarking Interactive Coding Agents,” *ACL*, 2024. https://aclanthology.org/2024.acl-long.850/

[2] J. Lu et al., “ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities,” *Findings of NAACL*, 2025. https://aclanthology.org/2025.findings-naacl.65/

[3] S. Fan et al., “AgentProcessBench: Diagnosing Step-Level Process Quality in Tool-Using Agents,” *arXiv*, 2026. https://arxiv.org/abs/2603.14465

[4] AgentSynth contributors, “AgentSynth: Offline-first outcome-checked agent benchmark and SQL scenario packs,” software and `core_v2` pack, pinned commit `d2564dfb25ed7ba32e367d28117e6afd1ee6c485`. https://github.com/agentsynth/agentsynth

[5] AURA research artifacts and experiment reports, accompanying reproducibility package, October 2026; GitHub: https://github.com/shanmukhdatta/AURA

---

**Submission checklist:** Confirm authorship contributions; run plagiarism and citation verification; proofread; use IJERT's current template; check actual page count and references; confirm submitted tables match regenerated CSVs. This MD is a source draft, **not** a final IJERT-formatted manuscript.
