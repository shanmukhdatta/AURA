"""Deterministic serialization and safe artifact creation."""
import datetime as dt
import hashlib
import json
import os
import tempfile
from pathlib import Path


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(obj):
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def file_digest(path):
    h = hashlib.sha256()
    count = 0
    with Path(path).open("rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            count += len(data)
            h.update(data)
    return h.hexdigest(), count


def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def save_json_atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"evidence artifact already exists: {path}")
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".writing-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(canonical_json(data))
            f.write(b"\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
