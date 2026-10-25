#!/usr/bin/env python3
"""Check original archive/source file bytes against original packaging-time manifest."""
import csv,pathlib,hashlib,sys,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
def hash_file(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
missing=[];mismatch=[];zip_crc=[];ok=0
with (ROOT/'evidence/master_source_registry.csv').open(newline='',encoding='utf8') as f:
 for rec in csv.DictReader(f):
  p=ROOT/rec['repo_path']
  if not p.is_file():missing.append(rec['repo_path']);continue
  if hash_file(p)!=rec['sha256']:mismatch.append(rec['repo_path']);continue
  if p.suffix.lower()=='.zip':
   try:
    with zipfile.ZipFile(p) as z:
     bad=z.testzip()
     if bad:zip_crc.append(p.as_posix()+'::'+bad)
   except Exception as e:zip_crc.append(str(e))
  ok+=1
print(f'Original artifacts: {ok} verified, {len(missing)} missing, {len(mismatch)} mismatches, {len(zip_crc)} archive CRC failures')
if missing:print('Missing:',missing[:20])
if mismatch:print('Mismatches:',mismatch[:20])
if zip_crc:print('ZIP CRC:',zip_crc[:20])
sys.exit(bool(missing or mismatch or zip_crc))
