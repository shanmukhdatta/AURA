"""AppWorld integration boundary and preparation checks.

Stage 6 does not falsely report benchmark outcomes without a runnable public
AppWorld environment and its official evaluator. Returns a readiness report.
"""
from __future__ import annotations
import importlib.util

def integration_status():
    installed=importlib.util.find_spec('appworld') is not None
    return {'source':'https://github.com/StonyBrookNLP/appworld',
            'installed':installed,'official_task_data_loaded':False,
            'executed_agent_trajectories':0,'official_evaluation_runs':0,
            'status':'ready_for_environment_setup' if installed else 'not_installed',
            'instructions':'Use AppWorld official installation, task data, permitted run records and evaluator; do not treat authored fixtures as native benchmark scores.'}
