"""Render a source-linked, paper-readable results sheet from derived CSVs.

Does NOT invent confidence intervals or aggregate incompatible real-model cohorts.
"""
from pathlib import Path
import csv
import json

def _rows(p:Path) -> list[dict]:
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def write_report(out:Path)->Path:
    groups=_rows(out/'cohort_summary.csv')
    priors=_rows(out/'table_planner_prior_sensitivity.csv')
    local=_rows(out/'table_local_policy_latency.csv')
    cost=_rows(out/'table_stage83_modeled_planning.csv')
    d={r['cohort']:r for r in groups}
    assert len(groups)==5
    assert sum(int(r['n']) for r in groups)==53
    c={r['policy']:r for r in cost}
    assert len(c)==4 and all(int(r['worlds_evaluated_per_policy'])==64 for r in cost)
    lines=['# AURA research summary — generated from saved archived result files','',
    '*This summary is a reconstruction of existing evidence, not a new benchmark execution.*','',
    '## Experimental cohorts (do not pool)','',
    '| Cohort | Unit | N | PASS | FAIL | UNCERTAIN | Not AURA-evaluated |',
    '|---|---|---:|---:|---:|---:|---:|']
    for r in groups:
        lines.append('| '+ ' | '.join(str(r[k]) for k in ['cohort','scope','n','pass','fail','uncertain','not_aura_evaluated'])+' |')
    lines+=['','14 real-model episodes have AURA certificates across three distinct real-model cohorts; 3 additional AppWorld agent episodes have native evaluations **without** AURA certificates. The 36 scripted controls are not real-model episodes.','',
        '## Stage 7 modeled prior sensitivity (cost units, not milliseconds)','',
        '| Prior | Fixed | Greedy | CERA | Bounded exact | CERA minus greedy |',
        '|---|---:|---:|---:|---:|---:|']
    for r in priors:
        lines.append('| '+' | '.join(str(r[k]) for k in ['prior','fixed_units','greedy_units','cera_units','optimal_units','cera_minus_greedy_units'])+' |')
    lines+=['','## Stage 7 controlled local latency (milliseconds, one execution per scenario/policy)','',
        '| Policy | Scripted scenarios | Mean end-to-end latency (ms) | Matched scoped verdict |',
        '|---|---:|---:|---:|']
    for r in local:
        lines.append('| '+' | '.join(str(r[k]) for k in ['policy','executions','mean_total_ms','matched_contract_expected'])+' |')
    lines+=['','## Stage 8.3 modeled inspection policy comparison','',
        '| Policy | Worlds/policy | Avg probes | Abstract probe-cost units | Planner latency (ms) |',
        '|---|---:|---:|---:|---:|']
    for r in cost:
        lines.append('| '+' | '.join(str(r[k]) for k in ['policy','worlds_evaluated_per_policy','avg_probes','avg_probe_cost_units','avg_planner_latency_ms'])+' |')
    lines+=['','**Dimensional warning:** abstract costs are not added to milliseconds. This dataset does not establish a high-latency CERA advantage.','',
        '## Central limitations','',
        '- No AppWorld-to-AURA adapter evaluation in these archived results.',
        '- Qwen0.5B and Qwen3B external task mixes are different; do not treat them as a controlled model comparison.',
        '- AgentSynth SQL score checks used in real model pilots are local reproductions, not the official CLI on those episodes.',
        '- Side-effect comparison uses stronger task-defined frame policies than the narrow SQL-only outcome checks.',
        '- A complete-before/final snapshot can miss reverted transient unauthorized edits.',
        '- Small pilot sample: no population claim, no false PASS probability bound.',
        '','**Source:** evidence archives listed in `derived_audit.json`; see exact ZIP hashes therein.','']
    result=out/'PAPER_RESULTS_FROM_RAW_EVIDENCE.md';result.write_text('\n'.join(lines),encoding='utf-8');return result
