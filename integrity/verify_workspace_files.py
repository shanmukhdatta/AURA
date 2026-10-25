#!/usr/bin/env python3
"""Compare all supplementary original workspace files to their frozen SHA256 inventory."""
from __future__ import annotations
import csv, hashlib, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
manifest = ROOT/'evidence/master_workspace_file_registry.csv'
if not manifest.exists():
    print('MISSING workspace manifest'); sys.exit(1)
missing=[]; mismatched=[]; checked=0
with manifest.open(newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        p=ROOT/row['repo_path']
        if not p.is_file():missing.append(row['repo_path']);continue
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        if actual!=row['sha256']:mismatched.append(row['repo_path']);continue
        checked+=1
print(f'Workspace originals: {checked} verified; {len(missing)} missing; {len(mismatched)} SHA256 mismatches')
for x in (missing+mismatched)[:20]:print('  '+x)
sys.exit(bool(missing or mismatched))
