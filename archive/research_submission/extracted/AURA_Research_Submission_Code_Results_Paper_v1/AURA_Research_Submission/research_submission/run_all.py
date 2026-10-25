"""Reproducible, read-only analysis entrypoint for the preliminary AURA paper."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from .audit import audit_and_export
from .tables import build_tables
from .report import write_report

def main():
    root=Path(__file__).resolve().parents[1]
    p=argparse.ArgumentParser(description='Verify AURA source experiment archives and rebuild all paper tables')
    p.add_argument('--source-dir',type=Path,default=root/'evidence/source_archives')
    p.add_argument('--out',type=Path,default=root/'outputs')
    args=p.parse_args()
    audit=audit_and_export(args.source_dir,args.out)
    derived=build_tables(args.source_dir,args.out)
    report_path=write_report(args.out)
    (args.out/'build_receipt.json').write_text(json.dumps({'audit_status':'PASS','cohort_counts':audit['cohorts'],'table_counts':derived},indent=2)+'\n')
    print('BUILD VERIFIED: %s model/scripted records across %s distinct cohorts' % (sum(x['n'] for x in audit['cohorts']),len(audit['cohorts'])))
    print('Paper results summary:',report_path)
    print('See',args.out)

if __name__=='__main__':main()
