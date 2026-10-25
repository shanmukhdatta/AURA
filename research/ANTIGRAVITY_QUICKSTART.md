# Use Antigravity for AURA Stage 8.3

1. Open Google Antigravity IDE or Agent Manager; clone/open https://github.com/shanmukhdatta/AURA.
2. Download and extract the `AURA_Stage8_3_Antigravity_Full_Handoff.zip` provided alongside the research handoff in ChatGPT to the workspace. It contains the original runnable Stage 7 source/tests, Stage 8.2 scripts, saved evidence and full detailed master prompt. Do not replace earlier experiment evidence.
3. In the Antigravity agent prompt paste the instructions in `research/STAGE_8_3_ANTIGRAVITY_PROMPT.md`. Google Antigravity documents `/goal` for autonomous execution. Review commands, costs and source diffs.
4. Ask it to produce `STATUS.md` and command receipts after each G0–G5 gate. Do not accept claims without linked raw evidence.
5. The next test is CPU-first. Use Kaggle GPU only if a verified, real-model external inference phase actually needs it. A mock policy or oracle run cannot substitute for model data.
6. On completion upload `AURA_STAGE8_3_RESULTS.zip` here for independent review. Do not automatically merge PRs.

Official IDE guide: https://www.antigravity.google/docs/getting-started/
