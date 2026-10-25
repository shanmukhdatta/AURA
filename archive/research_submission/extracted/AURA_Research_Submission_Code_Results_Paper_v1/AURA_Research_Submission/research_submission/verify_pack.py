"""Check file digests for the distribution's outer manifest."""
from pathlib import Path
import hashlib, json, sys

def verify(root:Path) -> dict:
    manifest=root/'SUBMISSION_MANIFEST_SHA256.json'
    if not manifest.exists():raise FileNotFoundError(manifest)
    data=json.loads(manifest.read_text(encoding='utf-8'))
    bad=[]
    for rel,entry in data['files'].items():
        p=root/rel
        if not p.is_file() or p.stat().st_size!=entry['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=entry['sha256']:
            bad.append(rel)
    return {'files_checked':len(data['files']),'bad_files':bad,'verified':not bad}

if __name__=='__main__':
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
    result=verify(root);print(json.dumps(result,indent=2));raise SystemExit(0 if result['verified'] else 1)
