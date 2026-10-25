"""Evidence-surface ablations for Stage 6, not information-parity comparisons.

All records come from the same frozen Stage 2 sandbox. State-only and trace-
only are intentionally information-restricted; dual uses all surfaces.
This tests evidence complementarity, NOT whether CERA beats other algorithms.
"""
from pathlib import Path
from aura_evidence.capture import EvidenceSandbox
from aura_evidence.probes import ProbeRunner
from aura_evidence.util import read_json
from aura_evidence.validation import validate_probes,validate_observation
from aura_verifier.engine import verify

MODES={
 'state_only':frozenset(('sql_read','file_read','state_diff')),
 'trace_only':frozenset(('trace_read',)),
 'dual_surface':frozenset(('sql_read','file_read','state_diff','trace_read')),
}

def run_surface_ablation(sandbox_dir,contract,registered,mode,*,force_denied=()):
    if mode not in MODES:raise ValueError('unknown surface mode')
    sand=EvidenceSandbox(Path(sandbox_dir))
    manifest=read_json(sand.evidence/'run_manifest.json')
    pair=sand.load_pair(manifest['epoch_id']);pair.require_same_epoch()
    validate_probes(contract,registered)
    runner=ProbeRunner(sand,pair,contract,registered)
    selected=[p for p in registered if p['adapter'] in MODES[mode]]
    results=[]
    for p in selected:
        obs=runner.run(p['probe_id'],manifest['run_id']+'.stage6.'+mode,
                       force_unavailable='permission_denied' if p['probe_id'] in force_denied else None)
        validate_observation(obs,p,pair=pair);results.append(obs)
    cert=verify(contract,registered,results,
                run_id=manifest['run_id']+'.stage6.'+mode,epoch_id=manifest['epoch_id'],pair=pair,
                capture_latency_ms=manifest['snapshot_capture_latency_ms'],
                capture_bytes_read=manifest['snapshot_capture_bytes_read'],
                trust_assumptions=['Controlled local harness state; same before/after snapshots for all methods.',
                    'Surface ablation deliberately restricts evidence, NOT information-matched algorithm comparison.'])
    return {'mode':mode,'scenario':manifest['scenario'],
       'verdict':cert['verdict'],'decision_status':cert['decision_status'],
       'num_probes':len(results),'selected_probes':[p['probe_id'] for p in selected],
       'actual_probe_ms':sum(o['actual_cost']['latency_ms'] for o in results),
       'capture_ms':manifest['snapshot_capture_latency_ms'],
       'certificate':cert}
