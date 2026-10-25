import argparse
from aura_evaluation.local_faults import run_local_matrix
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
 rows=run_local_matrix(a.out)
 print(f'{len(rows)} local scripted evaluations; matching expected contract decisions: {sum(x["matched_expected"] for x in rows)}/{len(rows)}')
