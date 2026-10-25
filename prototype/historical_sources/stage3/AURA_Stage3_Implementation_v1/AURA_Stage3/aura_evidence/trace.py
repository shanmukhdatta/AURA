"""Harness-controlled tool proxy trace; not a complete mediation guarantee."""
from pathlib import Path
import json
from .util import canonical_json, digest, save_json_atomic, utc_now


class TraceRecorder:
    def __init__(self, evidence, epoch_id):
        self.evidence = Path(evidence)
        self.epoch_id = epoch_id
        self.events = []

    def tool_call(self, tool, operation, *args, **kwargs):
        try:
            result = operation(*args,**kwargs)
        except Exception as exc:
            self.record(tool,dict(args=list(args),kwargs=kwargs), {'error_type':type(exc).__name__},status='error')
            raise
        self.record(tool,dict(args=list(args),kwargs=kwargs), {'result':result},status='ok')
        return result

    def record(self, tool, arguments, response, status='ok'):
        event = dict(index=len(self.events),epoch_id=self.epoch_id,tool=tool,
                     args=arguments, response=response,status=status,observed_at=utc_now())
        self.events.append(event)
        return event

    def persist(self):
        ref = 'traces/' + self.epoch_id + '.json'
        save_json_atomic(self.evidence/ref,{'epoch_id':self.epoch_id,'events':self.events,'sha256':digest(self.events)})
        return ref
