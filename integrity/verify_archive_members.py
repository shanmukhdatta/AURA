#!/usr/bin/env python3
"""Verify every extracted member file matches its original archived-byte digest."""
import csv,pathlib,hashlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
missing=[];mismatch=[];ok=0
with (ROOT/'evidence/master_archive_member_registry.csv').open(newline='',encoding='utf8') as f:
 for rec in csv.DictReader(f):
  p=ROOT/rec['repo_path']
  if not p.is_file():missing.append(rec['repo_path']);continue
  if hashlib.sha256(p.read_bytes()).hexdigest()!=rec['sha256']:mismatch.append(rec['repo_path']);continue
  ok+=1
print(f'Extracted ZIP members: {ok} verified, {len(missing)} missing, {len(mismatch)} mismatches')
if missing:print('Missing',missing[:20])
if mismatch:print('Mismatches',mismatch[:20])
sys.exit(bool(missing or mismatch))
