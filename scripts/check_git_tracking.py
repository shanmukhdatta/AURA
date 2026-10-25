#!/usr/bin/env python3
"""Read-only audit that original source assets are tracked in the local Git clone."""
from __future__ import annotations
import csv, pathlib, subprocess, sys
root=pathlib.Path(__file__).resolve().parents[1]
if not (root/'.git').exists():
    print('This audit requires the bundle to be merged into an existing git clone.');sys.exit(2)
expected=[]
for name in ('master_source_registry.csv','master_archive_member_registry.csv','master_workspace_file_registry.csv'):
    with (root/'evidence'/name).open(newline='',encoding='utf-8') as f:
        expected.extend(row['repo_path'] for row in csv.DictReader(f))
seen=set(expected)
proc=subprocess.run(['git','ls-files','-z'],cwd=root,stdout=subprocess.PIPE,check=True)
tracked={x.decode('utf-8') for x in proc.stdout.split(b'\0') if x}
missing=sorted(seen-tracked)
print(f'Required original/extracted files: {len(seen)}; tracked: {len(seen)-len(missing)}; not tracked: {len(missing)}')
for p in missing[:30]:print('NOT TRACKED:',p)
sys.exit(bool(missing))
