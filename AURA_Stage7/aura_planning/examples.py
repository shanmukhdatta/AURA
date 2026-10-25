"""Frozen model-relative synthetic problems, NOT externally sourced agent outcomes.

Domains represent abstract verified task outcomes. No generated world labels are
used as planner inputs; outcomes are disclosed through selected synthetic probes.
"""
from .planner import FiniteInspectionProblem,Inspection

def make_problem(domain='records',case=0):
    if domain not in ('records','orders','access','files'):
        raise ValueError('unknown synthetic template domain')
    # 4 booleans: each required outcome must be true (with a frame check).
    keys = {
      'records':('student_updated','report_saved','eligibility_checked','mutation_clean'),
      'orders':('order_cancelled','inventory_restored','refund_once','mutation_clean'),
      'access':('permission_set','approval_recorded','audit_complete','mutation_clean'),
      'files':('manifest_correct','hashes_match','report_saved','mutation_clean'),
    }[domain]
    obligations=[]
    for idx,k in enumerate(keys):
        obligations.append({'id':'ob_'+k,'category':'frame' if idx==3 else 'outcome',
                            'predicate':{'operator':'true','fact_key':k},
                            'required_complete_coverage':['scope.main'] if idx==3 else []})
    contract={'obligations':obligations,
              'frame_policy':{'policy':'closed_world','declared_mutation_surfaces':['scope.main']}}
    domains={k:[False,True] for k in keys}
    # Some domains have valid physical correlation between steps. It is an authored
    # assumption, not learned from the tested actual world.
    constraints=[]
    if case%4 == 3:
        # status of a saved report implies its metadata source was available
        constraints=[{'op':'implies', 'if':{'op':'fact_eq','fact_key':keys[1],'value':True},
                      'then':{'op':'fact_eq','fact_key':keys[0],'value':True}}]
    model={'schema_version':'1.0','model_id':domain+'_'+str(case),
           'fact_domains':domains,'constraints':constraints,'max_worlds':500}
    # Fixed alternative evidence catalogue. A single inspector can prove two
    # mutually dependent facts; a mandatory coverage probe is required for PASS.
    multiplier=1+0.18*(case%3)
    probes=[
        Inspection('status_main',(keys[0],),(),1.0*multiplier),
        Inspection('status_related',(keys[1],),(),2.0/multiplier),
        Inspection('trace_step',(keys[2],),(),1.5),
        Inspection('frame_diff',(keys[3],),('scope.main',),8.0*multiplier),
        Inspection('joined_read',(keys[0],keys[1]),(),2.7),
        Inspection('bulk_evidence',(keys[0],keys[1],keys[2],keys[3]),('scope.main',),14.0),
    ]
    return FiniteInspectionProblem(contract,model,probes)
