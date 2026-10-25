"""Four read-only Stage 2 probe adapters (sql, file, state-diff, trace).

The specializations for student/report facts are intentionally explicit;
this is evidence plumbing, not a general-purpose TaskContract interpreter.
"""
from pathlib import Path
import re
import time
from .capture import SnapshotError
from .diff import canonical_diff
from .util import canonical_json, digest, file_digest, read_json, utc_now
from .validation import observation_digest, validate_contract, validate_probes


class ProbeError(RuntimeError):
    pass


_DB_EFFECT = re.compile(r'^([a-z][a-z0-9_]*)=(\d+), ([a-z][a-z0-9_]*) only$')
_FK = re.compile(r'^(student|report)\.(\d+)\.(marks|matching_count|exists|matches_db)$')


def _allowed_mutation(change, effect):
    if change['surface_id'] != effect['surface_id'] or change['operation'] != effect['operation']:
        return False
    if change['kind']=='row' and change['operation']=='update':
        m = _DB_EFFECT.fullmatch(effect['target_pattern'])
        if not m:
            raise ProbeError('unsupported structured SQLite effect target; cannot assert clean frame')
        pk_name, pk_text, field = m.groups()
        return (set(change['pk'])=={pk_name} and str(change['pk'][pk_name])==pk_text and
                set(change['changed_fields'])=={field})
    if change['kind']=='filesystem':
        pattern = effect['target_pattern']
        if pattern.startswith('/') or '\\' in pattern or '..' in Path(pattern).parts or any(ch in pattern for ch in '*?[]'):
            raise ProbeError('unsupported or unsafe filesystem target pattern')
        return change['path']==pattern
    # Insert/delete and complex patterns require an explicit future parser;
    # refuse rather than silently treat them as safe.
    return False


class ProbeRunner:
    """Run read-only probes against trusted immutable captures.

    All source artifacts live in sandbox.evidence outside agent workspace.
    A successful complete receipt is limited to the named local surfaces.
    """
    def __init__(self, sandbox, pair, contract, probes):
        self.sandbox = sandbox
        self.pair = pair
        self.pair.require_same_epoch()
        self.contract = validate_contract(contract)
        validate_probes(contract,probes)
        self.probes = {p['probe_id']:p for p in probes}
        self.count = 0

    def _sql(self, probe):
        tables = self.pair.after['sqlite']
        if 'students' not in tables:
            raise ProbeError('required table absent in captured state')
        rows = tables['students']['rows']
        facts = []
        for k in probe['provides_fact_keys']:
            m = _FK.fullmatch(k)
            if not m or m.group(1)!='student' or m.group(3) not in ('marks','matching_count'):
                raise ProbeError('unsupported sql fact key; no arbitrary SQL permitted')
            sid = int(m.group(2)); attr=m.group(3)
            matches = [r for r in rows if r.get('student_id')==sid]
            value = len(matches) if attr=='matching_count' else matches[0]['marks'] if len(matches)==1 else None
            facts.append({'fact_key':k,'value':value,'source_ref':'captured:'+self.pair.after_ref+'#sqlite.students'})
        return facts, [], len(canonical_json(rows))

    def _file(self, probe):
        facts = []
        readings = {}
        total_bytes = 0
        for k in probe['provides_fact_keys']:
            m = _FK.fullmatch(k)
            if not m or m.group(1)!='report' or m.group(3) not in ('exists','matches_db'):
                raise ProbeError('unsupported report fact key')
            sid=int(m.group(2)); attr=m.group(3)
            rel=f'reports/student_{sid}.md'
            manifest=self.pair.after['files'].get(rel)
            exists=manifest is not None and manifest.get('kind')=='file'
            if exists and rel not in readings:
                p=self.sandbox.workspace/rel
                if not p.resolve().is_relative_to(self.sandbox.workspace.resolve()) or not p.is_file() or p.is_symlink():
                    raise SnapshotError('report missing since terminal snapshot')
                sha,size=file_digest(p)
                if sha != manifest['sha256'] or size != manifest['size']:
                    raise SnapshotError('report stale since terminal snapshot')
                text=p.read_text('utf-8')
                import hashlib
                if hashlib.sha256(text.encode('utf-8')).hexdigest() != manifest['sha256']:
                    raise SnapshotError('report changed between read and parse')
                readings[rel]=text
                total_bytes+=size
            if attr=='exists':
                value=exists
            else:
                matches=re.search(r'(?m)^Marks:\s*(\d+)\s*$',readings[rel]) if exists else None
                rows=self.pair.after['sqlite'].get('students',{}).get('rows',[])
                record=[r for r in rows if r.get('student_id')==sid]
                value= bool(matches and len(record)==1 and int(matches.group(1))==record[0]['marks'])
            facts.append({'fact_key':k,'value':value,
                          'source_ref':'captured:'+self.pair.after_ref+'#files/'+rel})
        return facts,[],total_bytes

    def _diff(self, probe):
        changes=canonical_diff(self.pair)
        frame=self.contract['frame_policy']
        required=set(frame['declared_mutation_surfaces'])
        covered=set(probe['covered_mutation_surfaces'])
        if not required.issubset(covered):
            raise ProbeError('probe cannot certify required surface set')
        declared_surfaces={s['surface_id']:s for s in self.contract['surfaces']}
        for s in covered:
            if s not in declared_surfaces:
                raise ProbeError('unregistered surface coverage')
            kind=declared_surfaces[s]['kind']
            if kind=='sqlite':
                name=s.split('.',1)[1]
                if name not in self.pair.before['sqlite'] or name not in self.pair.after['sqlite']:
                    raise ProbeError('declared table absent in complete snapshot')
            elif kind=='filesystem':
                prefix=s.split('.',1)[1]
                if prefix=='':
                    raise ProbeError('invalid workspace scope')
                # The whole workspace was enumerated; nonexistent empty directories
                # must be absent at both epochs, not silently inferred otherwise.
            else:
                raise ProbeError('unsupported complete coverage surface')
        # All effects must use the supported policy grammar. Unknown patterns
        # cannot be claimed clean merely because no such effect was observed.
        for effect in frame['allowed_effects']:
            if effect['operation']=='update' and not _DB_EFFECT.fullmatch(effect['target_pattern']):
                raise ProbeError('unsupported allowed-effect grammar')
            if effect['operation'] in ('create_file','modify_file','delete_file'):
                patt=effect['target_pattern']
                if patt.startswith('/') or '..' in Path(patt).parts or any(ch in patt for ch in '*?[]'):
                    raise ProbeError('unsupported file allowed-effect grammar')
            if effect['operation'] not in ('update','create_file','modify_file','delete_file','none'):
                raise ProbeError('insert/delete allowed-effect grammar not yet supported')
        unaccounted=[]
        for change in changes:
            if change['surface_id'] not in covered:
                continue
            allowed=any(_allowed_mutation(change,effect) for effect in frame['allowed_effects'])
            if not allowed:
                unaccounted.append(change)
        facts=[]
        for k in probe['provides_fact_keys']:
            if k != 'mutation.out_of_frame_count':
                raise ProbeError('unsupported state diff fact key')
            facts.append({'fact_key':k,'value':len(unaccounted),
                          'source_ref':'snapshot-pair:'+self.pair.before_ref+'|'+self.pair.after_ref})
        receipts=[]
        for s in sorted(covered):
            receipts.append({'surface_id':s,'completeness':'complete','method':'snapshot_pair',
                             'consistent_epoch':True,'independent_source':True,
                             'snapshot_before_ref':self.pair.before_ref,'snapshot_after_ref':self.pair.after_ref})
        return facts,receipts, len(canonical_json(self.pair.before))+len(canonical_json(self.pair.after))

    def _trace(self, probe):
        ref=self.sandbox.evidence/'traces'/ (self.pair.epoch_id+'.json')
        if not ref.is_file():
            raise ProbeError('independent trace unavailable')
        data=read_json(ref)
        if data['epoch_id'] != self.pair.epoch_id or data['sha256']!=digest(data['events']):
            raise SnapshotError('trace integrity or epoch failure')
        events=data['events']
        names=[e['tool'] for e in events if e['status']=='ok']
        valid_index=next((i for i,e in enumerate(events) if e['tool']=='validate_eligibility'
                         and e['status']=='ok' and e['response'].get('result') is True),None)
        update_index=next((i for i,e in enumerate(events) if e['tool']=='update_marks' and e['status']=='ok'),None)
        valid=valid_index is not None and update_index is not None and valid_index<update_index
        facts=[]
        for k in probe['provides_fact_keys']:
            if k!='trace.validation_before_update':
                raise ProbeError('unsupported trace fact key')
            facts.append({'fact_key':k,'value':valid,'source_ref':'trace:'+str(ref.relative_to(self.sandbox.evidence))})
        return facts,[],len(canonical_json(data))

    def run(self, probe_id, run_id, *, force_unavailable=None):
        if probe_id not in self.probes:
            raise ProbeError('unknown probe')
        p=self.probes[probe_id]
        if p['adapter']=='external_status' or p['coverage_method']=='complete_journal':
            # Independent external/journal integrations are future-stage capabilities.
            force_unavailable=force_unavailable or 'unsupported'
        start_wall=time.perf_counter_ns(); start_cpu=time.process_time_ns()
        facts=[];receipts=[];bytes_read=0
        status='ok';reason='none'
        if force_unavailable:
            if force_unavailable not in ('permission_denied','timeout_no_readback','stale','unsupported'):
                raise ValueError('unsupported simulated unavailable reason')
            status='unavailable';reason=force_unavailable
        else:
            try:
                adapter={'sql_read':self._sql,'file_read':self._file,
                         'state_diff':self._diff,'trace_read':self._trace}.get(p['adapter'])
                if adapter is None:
                    raise ProbeError('unsupported adapter')
                facts,receipts,bytes_read=adapter(p)
            except (SnapshotError, UnicodeError):
                status='error';reason='integrity_failure'
            except ProbeError:
                status='error';reason='unsupported'
            except (OSError, PermissionError):
                status='unavailable';reason='permission_denied'
        self.count+=1
        ob=dict(schema_version='1.0',observation_id=f'obs.{run_id}.{probe_id}.{self.count}',
                run_id=run_id,probe_id=probe_id,epoch_id=self.pair.epoch_id,
                observed_at=utc_now(),status=status,reason_code=reason,channel=p['independence'],
                facts=facts,coverage_receipts=receipts,
                actual_cost={'latency_ms':round((time.perf_counter_ns()-start_wall)/1e6,5),
                             'cpu_ms':round((time.process_time_ns()-start_cpu)/1e6,5),
                             'bytes_read':bytes_read})
        ob['payload_sha256']=observation_digest(ob)
        return ob
