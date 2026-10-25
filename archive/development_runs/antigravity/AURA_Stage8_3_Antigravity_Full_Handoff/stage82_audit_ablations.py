#!/usr/bin/env python3
"""Stage 8.2 independent verifier replays, evidence-absence ablations, negative controls."""
import argparse,copy,csv,json,sys
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parent))
from stage82_agentsynth_pilot import TASKS, readonly_reference
CORE=Path(__file__).resolve().parent/'AURA_Stage7'
sys.path.insert(0,str(CORE))
from aura_evidence.capture import SnapshotPair
from aura_evidence.validation import ValidationError
from aura_verifier.engine import verify,VerificationInputError
from aura_evidence.util import save_json_atomic

def load(path):return json.loads(Path(path).read_text())
def write_csv(path,rows):
 with open(path,'w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 p=argparse.ArgumentParser();p.add_argument('--results',required=True);a=p.parse_args();root=Path(a.results)
 ab=[];checks=[]
 for tid,t in TASKS.items():
  for variant in ('oracle','no_op','silent_noop','partial','unauthorized_extra','denied_readback'):
   d=root/'cases'/tid/variant
   before,after=load(d/'before.json'),load(d/'after.json')
   cert=load(d/'certificate.json');rid=cert['run_id'];epoch=cert['epoch_id']
   pair=SnapshotPair(epoch,before,after,'snapshots/'+rid+'.before.json','snapshots/'+rid+'.after.json',0,
      before['bytes_read']+after['bytes_read']);pair.require_same_epoch()
   c,pbs,obs=load(d/'contract.json'),load(d/'probes.json'),load(d/'observations.json')
   reference=readonly_reference(after,t)
   assert reference==load(d/'independent_checkers.json'),('native_checkers_mismatch',tid,variant)
   checks.append({'task':tid,'variant':variant,'ref_match':True})
   for ablation,selection in [('all',obs),('no_frame_probe',obs[:1]),('no_outcome_probe',obs[1:]),('no_probes',[])]:
    result=verify(c,pbs,selection,run_id=rid,epoch_id=epoch,pair=pair)
    ab.append({'task':tid,'variant':variant,'ablation':ablation,'verdict':result['verdict'],
       'unresolved':len(result['unresolved_obligation_ids']),
       'observed_failed':sum(v['truth']=='fail' for v in result['obligation_results']),
       'actual_expected':cert['verdict']})
    if ablation=='all':assert result['verdict']==cert['verdict'] and result['obligation_results']==cert['obligation_results']
 # Negative controls: (a) forge an observation value without recomputing digest
 d=root/'cases'/'raise-ticket-priority'/'oracle'
 c,pbs,obs=load(d/'contract.json'),load(d/'probes.json'),load(d/'observations.json')
 before,after=load(d/'before.json'),load(d/'after.json')
 cert=load(d/'certificate.json');rid,epoch=cert['run_id'],cert['epoch_id']
 pair=SnapshotPair(epoch,before,after,'snapshots/'+rid+'.before.json','snapshots/'+rid+'.after.json',0,
      before['bytes_read']+after['bytes_read'])
 control={}
 fake=copy.deepcopy(obs);fake[0]['facts'][0]['value']='bogus'
 try:verify(c,pbs,fake,run_id=rid,epoch_id=epoch,pair=pair);control['forged_observation_digest']='MISSED'
 except (ValidationError,VerificationInputError):control['forged_observation_digest']='REJECTED'
 fake=copy.deepcopy(obs);fake[1]['coverage_receipts'][0]['snapshot_before_ref']='snapshots/mismatched_before.json'
 # Recompute digest to model an adversary who can manipulate an observation but not backing snapshot.
 from aura_evidence.validation import observation_digest
 fake[1]['payload_sha256']=observation_digest(fake[1])
 try:verify(c,pbs,fake,run_id=rid,epoch_id=epoch,pair=pair);control['forged_coverage_receipt']='MISSED'
 except (ValidationError,VerificationInputError):control['forged_coverage_receipt']='REJECTED'
 fake=copy.deepcopy(after);fake['sqlite']['tickets']['rows'][0]['priority']='bogus'
 fake_pair=SnapshotPair(epoch,before,fake,pair.before_ref,pair.after_ref,0,0)
 try:fake_pair.require_same_epoch();control['tampered_snapshot']='MISSED'
 except Exception:control['tampered_snapshot']='REJECTED'
 no_probes=[r for r in ab if r['ablation']=='no_probes']
 assert all(r['verdict']=='UNCERTAIN' for r in no_probes)
 assert all(v=='REJECTED' for v in control.values())
 write_csv(root/'inspection_ablation_results.csv',ab)
 summary={'cases_tested':len(checks),'ablation_certificates':len(ab),
   'ablation_verdict_counts':{k:dict(Counter(row['verdict'] for row in ab if row['ablation']==k))
       for k in ('all','no_frame_probe','no_outcome_probe','no_probes')},
   'negative_controls':control,
   'independent_sql_checkers_replayed_without_mismatches':len(checks),
   'remark':'No probes -> all UNCERTAIN; known observed failures may remain FAIL with only one probe. Neither ablation is an external LLM experiment.'}
 save_json_atomic(root/'ablation_and_negative_audit.json',summary)
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
