# AURA Stage 8.1 — Final pre-Kaggle go/no-go audit (v4)

## Research question and exact scope

The notebook tests whether the **original AURA Stage 7 verifier** can produce evidence-backed PASS/FAIL/UNCERTAIN certificates after a real small LLM performs tool actions in a local SQLite/filesystem workflow. A separate AppWorld track runs an LLM coding agent on authentic AppWorld **development** tasks and records the benchmark's **native** state-based evaluation. **AppWorld task outcomes are not independent AURA certificates yet.** Implementing a task-specific AppWorld → AURA contract-and-evidence adapter remains further research work.

This notebook **does not train, fine-tune, or update model weights**. It runs **model inference and evaluation**. It contains four local LLM episodes (two clean, one `silent_noop` tool fault, one denied evidence readback), four scripted preflight cases (not model results), three AppWorld dev tasks, and three AppWorld no-action control runs.

## Corrections in v4

1. Corrected the `.ipynb` schema: removed erroneous `execution_count` and `outputs` properties from Markdown cells. Validated the notebook with the official `nbformat.validate` and compiled all code cells.
2. Tightened the separately computed local reference so **every** update must be preceded by a successful validation, not merely the first update.
3. Added an independent **replay** of each AURA certificate from the original captured observations and snapshot pair. Comparison covers verdict, decision status, reason codes, per-obligation results, evidence references and frame coverage; it does not rely on the saved certificate's self-report alone.
4. Made the existence and consistency of each local **non-interference receipt** and the four local policy summaries a condition of a fully audited episode.
5. Validated native AppWorld API-call logs as parseable JSONL; preserved their record counts and SHA256 checksums, and required their presence for a fully validated native episode.
6. Recorded the isolated AppWorld package version. Kept installation logs, package wheels, model weights, raw AppWorld databases, worker scripts, and hidden native evaluator details **out of the result ZIP**.
7. Added explicit research/method references and clarified that native AppWorld scores cannot be presented as AURA-on-AppWorld accuracy.

## Validation in the assistant's sandbox

- **Notebook schema:** passes `nbformat.validate`; all executable code cells compile; notebook has no prefilled output cells.
- **Source integrity:** embedded Stage 7 archive SHA256 verified; **186/186** inherited AURA regression tests pass in a clean extraction with unrelated pytest plugin autoload disabled.
- **Four scripted operational preflight cases:** expected PASS / FAIL / FAIL / UNCERTAIN, all matched.
- **Four scripted local workflow integration cases:** expected PASS / PASS / FAIL / UNCERTAIN, all matched. They exercise the original verifier and real local SQLite/files; they **are not real model-generated experiments**.
- **AppWorld subprocess mock:** 3/3 fake tasks complete to validate IPC, native evaluation summary serialization, JSONL API log handling and no-action control protocol. **This is not an AppWorld benchmark run.**
- **Full archive integration:** model-mocked, AppWorld-mocked export succeeds; curated ZIP contains **80** allowlisted members, roughly 40 KB, with SHA256 and size verification. This is a structural test; actual Kaggle ZIP size and results will differ.
- **Fail-closed negatives:** an intentionally corrupted AURA PASS fails independent certificate replay/reference validation; deleting an expected native API-call log results in `NOT_READY_MISSING_REQUIRED_FILES` with explicit audit errors.

### Environment and research limitations

We could **not** run the genuine Qwen checkpoint nor download/execute official AppWorld tasks in this sandbox. Accordingly, real Kaggle GPU availability, network access, model loading, AppWorld installation, API compatibility, runtime limits, LLM capability, and resulting task performance are **not guaranteed**. Run-time tool failures must be reported as installation/inference issues, **never agent FAIL or AURA FAIL**. AppWorld code executes only in its own isolated virtual environment, and its native evaluator is called after agent steps. Official evaluator results are withheld from the agent.

The current pilot has only four local episodes and three external dev tasks. It is sufficient for initial evidence inspection **if it executes**, but it is not adequate for paper-level generalization or independent external AURA accuracy claims.

## Running the notebook on Kaggle

1. Import **`AURA_Stage8_1_Kaggle_FINAL_Rechecked_v4.ipynb`** into a **new** Kaggle Python notebook. Avoid continuing a session that ran an older notebook and altered installed dependencies.
2. Turn on **Internet** and a **GPU**. Run All, without changing tasks/prompts after seeing their outcomes. No paid model API is required; the notebook downloads open model weights.
3. At the end, look for `STAGE 8.1 FINAL READINESS:` followed by one of:
   - `READY_FOR_PILOT_ANALYSIS` — four local episodes passed integrity audit and three genuine AppWorld dev tasks and no-op controls were scored with required native logs; **still no AppWorld-specific AURA certificates**.
   - `PARTIAL_LOCAL_ONLY_ANALYSIS` — local AURA evidence can be examined, but AppWorld validation is unfinished.
   - `NOT_READY_INCOMPLETE`, `NOT_READY_REVIEW_AUDIT_ERRORS`, or `NOT_READY_MISSING_REQUIRED_FILES` — full evidence not available or audit mismatch; do not claim full success.
4. Download **only** `/kaggle/working/AURA_STAGE8_1_OUTPUTS.zip`. It is the **only intended saved output**. Upload that ZIP for analysis. If Run All fails before the export cell, copy the exact first error/traceback instead.

### Result ZIP: strict allowlist

The archive contains only reproducibility metadata, local task contracts/prompts, test receipts, local model trajectories and AURA certificates, validated probe observations, snapshot/trace evidence, post-verifier non-interference receipt, local reference labels and policy summaries, native AppWorld agent trajectories, the benchmark's limited official PASS/FAIL-count summaries, available native API-call logs and native no-action control summaries, readiness/audit reports, and a per-file SHA256 manifest. It **does not** include original Stage 7 source code, libraries, virtual environments, model checkpoint weights, installation dumps, raw AppWorld database states, hidden test bodies, or full debug stack traces. Keep the archive private while its contents are reviewed.

## References / scientific provenance

- AURA working project repository: https://github.com/shanmukhdatta/AURA (the exact embedded code is identified **by SHA256**, not by an unverified GitHub commit).
- AppWorld official repository, installation and evaluation: https://github.com/StonyBrookNLP/appworld
- AppWorld paper: Harsh Trivedi et al., *AppWorld: A Controllable World of Apps and People for Benchmarking Interactive Coding Agents*, ACL 2024: https://aclanthology.org/2024.acl-long.850/
- Qwen2.5-3B-Instruct official model card and usage: https://huggingface.co/Qwen/Qwen2.5-3B-Instruct

These citations support the choice and methods of the external environment and model; they do **not** certify results that have not yet been generated.
