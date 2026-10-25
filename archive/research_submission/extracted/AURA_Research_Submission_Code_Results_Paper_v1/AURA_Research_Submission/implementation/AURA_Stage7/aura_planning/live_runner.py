"""Stage 5 live read-only inspection runner using Stage 2 captures + Stage 4.

This collects one selected Stage 2 Observation at a time and delegates every
actual verdict to the existing Stage 4 verified-evidence engine. The planning
worlds are pre-authored models, not the actual hidden test execution state.
"""
from pathlib import Path
import time

from aura_evidence.capture import EvidenceSandbox
from aura_evidence.probes import ProbeRunner
from aura_evidence.util import read_json, save_json_atomic
from aura_evidence.validation import validate_probes, validate_observation
from aura_reasoning.model import enumerate_worlds
from aura_reasoning.reference_models import make_reference_model
from aura_reasoning.model import verify_bounded
from .planner import FiniteInspectionProblem, Inspection, plan_next, frozen_value


def frozen_preinspection_model(contract, registered, pair):
    """Public prior built from expected values and initial S0 only (NOT final S_T)."""
    model=make_reference_model(contract,registered,[],model_id='frozen_S0_reference')
    initial_rows=pair.before['sqlite'].get('students',{}).get('rows',[])
    for fact_key,domain in model['fact_domains'].items():
        import re
        m=re.fullmatch(r'student\.(\d+)\.marks',fact_key)
        if m:
            match=[r for r in initial_rows if r.get('student_id')==int(m.group(1))]
            if len(match)==1:
                value=match[0]['marks']
                if not any(type(v) is type(value) and v==value for v in domain):
                    domain.append(value)
    return model


def live_plan_problem(contract, registered, model=None):
    if model is None:
        raise ValueError('live planner requires explicit preinspection frozen model')
    inspections=[]
    for p in registered:
        # Stage 2 independent readback adapters only; actual unsupported
        # services excluded from a valid operational inspection catalogue.
        available=(p['independence']=='independent_verifier' and p['adapter'] in
                   ('sql_read','file_read','state_diff','trace_read'))
        inspections.append(Inspection(p['probe_id'],tuple(p['provides_fact_keys']),
                            tuple(p['covered_mutation_surfaces']) if p['mutation_coverage']=='complete' else (),
                            float(p['estimated_cost']['latency_ms']),available))
    return FiniteInspectionProblem(contract,model,inspections)


def run_live_policy(sandbox_dir,contract,registered,policy,*,force_denied=(),out_dir=None,model=None):
    sand=EvidenceSandbox(Path(sandbox_dir))
    manifest=read_json(sand.evidence/'run_manifest.json')
    pair=sand.load_pair(manifest['epoch_id']);pair.require_same_epoch()
    validate_probes(contract,registered)
    if model is None:
        model=frozen_preinspection_model(contract,registered,pair)
    problem=live_plan_problem(contract,registered,model=model)
    runner=ProbeRunner(sand,pair,contract,registered)
    run_id=manifest['run_id']+'.stage5.'+policy
    history=[]; observations=[];indices=problem.initial_indices;used=frozenset();selection_ms=0.0
    # All methods receive identical opportunity to inspect the frozen captures.
    while True:
        start=time.perf_counter_ns()
        next_probe=plan_next(problem,indices,used,policy)
        selection_ms+=(time.perf_counter_ns()-start)/1e6
        if next_probe is None:break
        obs=runner.run(next_probe,run_id,
                       force_unavailable='permission_denied' if next_probe in force_denied else None)
        validate_observation(obs, runner.probes[next_probe], pair=pair)
        observations.append(obs);used=used|frozenset({next_probe})
        if obs['status']=='ok':
            actual={f['fact_key']:f['value'] for f in obs['facts']}
            surviving=[]
            for i in indices:
                if all(k in problem.worlds[i] and frozen_value(problem.worlds[i][k])==frozen_value(v)
                       for k,v in actual.items()):
                    surviving.append(i)
            indices=tuple(surviving)
        history.append({'probe_id':next_probe,'status':obs['status'],
                        'reason_code':obs['reason_code'],
                        'actual_cost':obs['actual_cost'],
                        'surviving_model_worlds':len(indices)})
        if not indices:
            # Evidence outside our predeclared finite model -> no model-relative PASS.
            break
    cert,reasoning=verify_bounded(contract,registered,observations,model,
                                 run_id=run_id,epoch_id=manifest['epoch_id'],pair=pair,
                                 capture_latency_ms=manifest['snapshot_capture_latency_ms'],
                                 capture_bytes_read=manifest['snapshot_capture_bytes_read'],
                                 trust_assumptions=[
                                     'Frozen preinspection finite reference model; conditional inference only.',
                                     'Consistent Stage 2 captured local DB/filesystem, no live external claim.',
                                     'Identical probe catalogue and snapshot for all Stage 5 policies.'
                                 ])
    # Evidence model and full Stage 4 validation are authoritative. Planner cannot
    # override an UNCERTAIN or inconsistent verdict based on cheap heuristics.
    if not indices and cert['verdict']!='FAIL':
        cert['verdict']='UNCERTAIN';cert['decision_status']='model_inconsistent'
        cert['reason_codes']=['observation_outside_frozen_model']
        cert['unresolved_obligation_ids']=[o['id'] for o in contract['obligations']]
        for r in cert['obligation_results']:
            r['truth']='unknown';r['reason_code']='model_inconsistent'
    cert['costs']['planner_latency_ms']=round(cert['costs']['planner_latency_ms']+selection_ms,6)
    from aura_evidence.validation import validate_shape
    validate_shape(cert,'Certificate')
    result={
      'policy':policy,'scenario':manifest['scenario'],'run_id':run_id,
      'verdict':cert['verdict'],'decision_status':cert['decision_status'],
      'selected_probes':[h['probe_id'] for h in history],
      'num_probes':len(history),'estimated_probe_ms':sum(problem.inspections[h['probe_id']].cost for h in history),
      'actual_probe_ms':sum(h['actual_cost']['latency_ms'] for h in history),
      'capture_ms':manifest['snapshot_capture_latency_ms'],
      'capture_bytes_read':manifest['snapshot_capture_bytes_read'],
      'planner_selection_ms':round(selection_ms,6),
      'certificate':cert,'reasoning':reasoning,'trace':history,
      'observations':observations,
      'notice':'Controlled local sandbox; no independent external agent benchmark.'
    }
    if out_dir is not None:
        path=Path(out_dir);path.mkdir(parents=True,exist_ok=True)
        save_json_atomic(path/(manifest['scenario']+'_'+policy+'.json'),result)
    return result
