# AURA Stage 8.2 — Executable SQL Pilot

A CPU-only local experiment using six externally authored AgentSynth `core_v2` SQL task definitions and original reference SQL action plans, with independent AURA Stage 7 certificate verification.

## Quick start

On Python 3.10+:

```bash
python -m pip install jsonschema pytest
python stage82_agentsynth_pilot.py --out ./stage82_results --zip
cd AURA_Stage7
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q
```

On Windows PowerShell, omit the inline environment assignment and use `$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"` before `python -m pytest -q`.

Run these from the directory containing both Python scripts and the `AURA_Stage7` directory. The main driver automatically runs the ablation/integrity audit before packaging the ZIP. The output folder must not already contain files. The scripts use only the Python standard library and AURA's installed `jsonschema` dependency. No network, GPU or API key is needed.

**Inputs:** `stage82_agentsynth_pilot.py` hardcodes only a reviewable six-task source subset from upstream public task files, and declares authorized write scopes separately. **Not official full AgentSynth scoring** and **not a real LLM experiment**. See the detailed report for exact scope and source blob identifiers.

**Outputs:** per-task and per-variant before/after evidence, genuine AURA certificate and observation JSON, benchmark-SQL comparator data, full mutation diffs, `episode_results.csv`, `experiment_summary.json`, `certificate_replay_check.json`, `inspection_ablation_results.csv`, and `ablation_and_negative_audit.json`.

**Research rules:** Do not call injected controlled faults "observed real agent failures". Do not interpret 36 control outcomes as 36 independent external task runs or 144 ablation certificates as 144 separate agents. Preserve the source files and output manifest unchanged. No CERA advantage or external LLM certificate accuracy claim follows from these experiments.
