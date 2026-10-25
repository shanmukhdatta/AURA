#!/usr/bin/env python3
"""Safely import AURA offline bundle into an existing clone without overwriting files."""
import sys,pathlib,hashlib,shutil,json
if len(sys.argv)!=3:
 print('usage: python merge_into_existing_repo.py <bundle_dir> <existing_repo_dir>');sys.exit(2)
src=pathlib.Path(sys.argv[1]).resolve();dst=pathlib.Path(sys.argv[2]).resolve()
if not (dst/'.git').exists():
 print('ERROR: target must be an existing Git clone with a .git directory');sys.exit(2)
if src==dst or dst.is_relative_to(src):
 print('ERROR: source and destination must be separate');sys.exit(2)
conflicts=[];copied=0;identical=0
for f in src.rglob('*'):
 if not f.is_file() or '.git' in f.relative_to(src).parts:continue
 r=f.relative_to(src);to=dst/r
 if to.exists():
  if hashlib.sha256(f.read_bytes()).digest()==hashlib.sha256(to.read_bytes()).digest(): identical+=1
  else:conflicts.append({'path':r.as_posix(),'existing_sha256':hashlib.sha256(to.read_bytes()).hexdigest(),'bundle_sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
  continue
 to.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,to);copied+=1
report={'copied_files':copied,'identical_unchanged':identical,'conflicting_unchanged':len(conflicts),'conflicts':conflicts}
(dst/'CONSOLIDATION_CONFLICTS.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='conflicts'},indent=2))
print('Conflicts are NOT overwritten. Review CONSOLIDATION_CONFLICTS.json before committing.')
