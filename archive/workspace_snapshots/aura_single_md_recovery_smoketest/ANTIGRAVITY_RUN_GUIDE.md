# How to run the AURA Stage 8.3 work in Antigravity (Windows)

1. Open the Antigravity IDE/Agent Manager and choose **Open workspace / Clone repository**.
2. Use `https://github.com/shanmukhdatta/AURA`. If the repo only has docs initially, extract the provided `AURA_Stage8_3_Handoff_Source.zip` under this workspace, preserving `AURA_Stage7/` next to `stage82_agentsynth_pilot.py`.
3. Open the agent input box and paste **the entire** `ANTIGRAVITY_STAGE8_3_MASTER_PROMPT.md`. In current official Antigravity documentation, `/goal` requests an autonomous run; use only if you want that mode.
4. Permit only the necessary non-destructive actions, and review diffs/commands. The agent should start by running regression tests and the external-SQL reproduction, NOT by generating a new training notebook.
5. Follow the G0→G4 stop/go checkpoints. Ask the agent for `STATUS.md` and command receipts after each gate. Do not accept 'complete' without referenced files, source commit IDs, independent certificate files and native scorer outputs.
6. If a REAL LLM is needed and the local environment has no approved inference budget or GPU, request a new *isolated* Kaggle `.ipynb` to run only the real-LLM phase. Make sure results are downloaded and uploaded for independent review.
7. Before any GitHub push, review the new files, ensure no credentials or private benchmark data are present, and open a feature-branch PR rather than merge main automatically.

Antigravity official docs: https://www.antigravity.google/docs/getting-started/
Benchmark: https://github.com/agentsynth/agentsynth

For the current Stage 8.2 experiment itself, **no GPU or Kaggle is required**. Run `python stage82_agentsynth_pilot.py --out stage82_local_recheck --zip` from the extracted source folder.
