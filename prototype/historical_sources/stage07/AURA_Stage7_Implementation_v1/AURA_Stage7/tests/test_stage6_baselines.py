import pytest
from pathlib import Path
from run_demo import run
from aura_evidence.util import read_json
from aura_baselines.surface import run_surface_ablation
ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('scenario',('clean','missing_report','collateral','silent_noop','denied_readback','missing_validation'))
def test_evidence_surface_ablation_is_conservative(tmp_path,scenario):
    path=tmp_path/scenario;run(scenario,path)
    contract=read_json(ROOT/'examples/reference/task_contract.json')
    catalogue=read_json(ROOT/'examples/reference/probe_catalogue.json')
    force=('student_state',) if scenario=='denied_readback' else ()
    values={mode:run_surface_ablation(path,contract,catalogue,mode,force_denied=force) for mode in ('state_only','trace_only','dual_surface')}
    assert values['dual_surface']['verdict']=={'clean':'PASS','missing_report':'FAIL','collateral':'FAIL','silent_noop':'FAIL','denied_readback':'UNCERTAIN','missing_validation':'FAIL'}[scenario]
    assert values['state_only']['verdict']!='PASS'
    assert values['trace_only']['verdict']!='PASS'
    assert values['trace_only']['num_probes']==1
    assert values['state_only']['num_probes']==3
