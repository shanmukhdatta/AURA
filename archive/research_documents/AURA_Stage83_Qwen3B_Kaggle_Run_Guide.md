# AURA Stage 8.3 — Qwen2.5-3B Kaggle GPU Pilot

**Prepared:** 25 October 2026. **Execution status:** Notebook authored, validated and smoke-tested locally; genuine Qwen2.5-3B GPU episodes are **not yet executed**.

## What is Antigravity doing? (CPU, no GPU)

Antigravity should complete the Stage 8.3 corrective audit on the GitHub branch `experiment/stage-8-3-external-llm-verification`: reconcile official AgentSynth scoring with locally reproduced SQL predicates, fix the unjustified exact-answer contract, correct false-Fail denominators, remove placeholder historical measurements, verify certificate replay, and repair CERA cost reporting. This work uses Python/SQLite and does **not** require a GPU. Have Antigravity create a numbered draft PR without merging into `main`.

## What are you running in Kaggle? (GPU inference)

**Qwen/Qwen2.5-3B-Instruct**, *not* 0.5B and *not* training. Five SQL state tasks, one deterministic trajectory each:

1. `raise-ticket-priority`
2. `clearance-discount`
3. `dedup-keep-latest`
4. `cancel-and-void-payment`
5. `refund-and-restock`

Excluded: `refuse-cancel-shipped` because its Stage 8.3 answer contract is disputed, and other tasks with answer semantics that need CPU-side correction.

The new pilot clones the existing AURA feature branch and pins original AgentSynth commit `d2564dfb25ed7ba32e367d28117e6afd1ee6c485`. Kaggle must have **Internet ON** and a **T4 GPU**. One T4 is sufficient. All actions execute on isolated benchmark SQLite data, not on personal/user records. The model is downloaded once; no finetuning or training is performed.

## Run instructions

1. Open https://www.kaggle.com/code → **New Notebook** → File > Import Notebook (or Upload) and select `AURA_Stage83_Qwen3B_Real_Agent_Kaggle_Pilot.ipynb`.
2. In **Notebook settings**, set Accelerator = **GPU T4** (one T4 is enough); **Internet = On**.
3. Click **Run All**. Do not upload a Hugging Face token unless prompted by an actual authentication restriction; this public Qwen repository is normally downloadable anonymously, subject to rate limits.
4. The sequence is: clone and verify sources, run AURA CPU preflight, load the actual Qwen3B GPU model, execute five isolated multi-turn SQL workflows, issue and replay AURA certificates, reproduce all published SQL checkers, save raw traces/snapshots, export ZIP.
5. In `/kaggle/working/`, download **`AURA_STAGE83_QWEN3B_PILOT_RESULTS.zip`**, even if setup fails. Upload the ZIP here for an independent audit.

## What the ZIP will contain

- `results/config.json`, `environment.json`, `run_status.json`, command receipts, and source/benchmark commit SHAs;
- per task: the exact model response and SQL actions, SQL tool observations/errors, saved SQLite DB, before/after snapshots, AURA probes, observations, certificate, certificate-replay result, noninterference receipt, and reproduced published-checker results;
- `results/pilot_results.csv`, `README_RESULTS.md`, and a `FILE_MANIFEST_SHA256.json` manifest. The ZIP is internally re-verified before export.

## Scientific notes (must appear in submission)

- A task counts as a **genuine model execution** only if `state=EXECUTED_AND_AURA_EVALUATED` and its evidence exists; blocked/error runs must not count as completed.
- The recorded `published_checker_reproduction` is a local implementation of the public `core_v2` YAML predicates, **not an execution of the official AgentSynth CLI scoring**. The full official scorer needs separate replay/verification by Antigravity before claiming native benchmark accuracy.
- The AURA adapter also uses the published SQL predicates to derive certain readback facts, so this is not fully blinded evaluation. The next audit must address the reference independence.
- The frozen task contracts are from Antigravity's Stage 8.3 branch and may need semantic correction; any edits must be versioned and applied without hiding prior model results.
- Five tasks is enough for a **preliminary experimental report/demo with explicit limitations**, not a definitive performance study, statistically strong accuracy estimate, or general proof of superiority.
- If all five tasks fail, those remain scientifically valid negative model-agent results. Do not erase or cherry-pick them.
- The notebook does **not** measure CERA's policy advantage, use GPU training, push to GitHub, or alter the saved Stage 8.2 controls.

## Instruction to give Antigravity after Kaggle

> Continue the Stage 8.3 CPU audit on the feature branch. I am running `AURA_Stage83_Qwen3B_Real_Agent_Kaggle_Pilot.ipynb` on Kaggle T4. When I give you `AURA_STAGE83_QWEN3B_PILOT_RESULTS.zip`, verify its entire SHA256 manifest, replay AURA certificates, independently grade against the *official* AgentSynth benchmark where faithful trajectory replay is possible, and reconcile the contract/reference score definition. Keep model-generated trajectories separate from scripted controls, and report all negative and uncertain outcomes. Commit only reviewed code and sanitized evidence to a feature branch, open a numbered draft PR, and do not merge to main.
