"""Evidence ledger stored outside the agent workspace.

Filesystem hashes and hash chains detect accidental corruption, not malicious
rewriting by an attacker with access to the protected ledger directory.
"""
from pathlib import Path
import hashlib
import json
import os
from .util import canonical_json, read_json, save_json_atomic, digest
from .validation import validate_observation


class EvidenceLedger:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.observations = self.root/'observations'
        self.observations.mkdir(parents=True, exist_ok=True)

    def add(self, ob, probe, *, pair=None):
        validate_observation(ob,probe,pair=pair)
        oid = ob['observation_id']
        if not oid or not all(c.isalnum() or c in '._-' for c in oid):
            raise ValueError('invalid observation id for filename')
        path = self.observations/(oid+'.json')
        save_json_atomic(path,ob)
        return 'observations/'+oid+'.json'

    def load(self, ref):
        path = (self.root/ref).resolve()
        if not path.is_relative_to(self.observations):
            raise ValueError('observation reference outside ledger')
        return read_json(path)

    def verify(self, references, probes, pair=None):
        accepted = []
        for ref in references:
            ob = self.load(ref)
            if ob['probe_id'] not in probes:
                raise ValueError('unknown observation probe')
            validate_observation(ob,probes[ob['probe_id']],pair=pair)
            accepted.append(ob)
        return accepted
