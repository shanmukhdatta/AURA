"""Canonical persistent-state diff for a declared snapshot pair."""
from collections import Counter
from .util import canonical_json


def _ident(row, pk):
    return canonical_json([row[k] for k in pk]).decode('utf-8')


def canonical_diff(pair):
    pair.require_same_epoch()
    b, a = pair.before, pair.after
    changes = []
    for name in sorted(set(b['sqlite']) | set(a['sqlite'])):
        left = b['sqlite'].get(name)
        right = a['sqlite'].get(name)
        if left is None or right is None or left['schema'] != right['schema']:
            changes.append({'surface_id':'sqlite.'+name, 'kind':'schema', 'operation':'schema_change',
                            'table':name, 'before_schema':None if left is None else left['schema'],
                            'after_schema':None if right is None else right['schema']})
            continue
        pk = left['primary_key']
        if pk:
            old = {_ident(r,pk):r for r in left['rows']}
            new = {_ident(r,pk):r for r in right['rows']}
            for key in sorted(set(old) | set(new)):
                if key not in old:
                    changes.append({'surface_id':'sqlite.'+name,'kind':'row','operation':'insert',
                                    'table':name,'pk':{k:new[key][k] for k in pk},'new':new[key]})
                elif key not in new:
                    changes.append({'surface_id':'sqlite.'+name,'kind':'row','operation':'delete',
                                    'table':name,'pk':{k:old[key][k] for k in pk},'old':old[key]})
                elif old[key] != new[key]:
                    fields = {field:{'old':old[key].get(field),'new':new[key].get(field)}
                              for field in sorted(set(old[key]) | set(new[key])) if old[key].get(field) != new[key].get(field)}
                    changes.append({'surface_id':'sqlite.'+name,'kind':'row','operation':'update',
                                    'table':name,'pk':{k:new[key][k] for k in pk}, 'changed_fields':fields})
        else:
            # Tables without primary keys: classify only row-multiset changes, not updates.
            oc = Counter(canonical_json(r).decode('utf-8') for r in left['rows'])
            nc = Counter(canonical_json(r).decode('utf-8') for r in right['rows'])
            for row in sorted(set(oc) | set(nc)):
                if oc[row] != nc[row]:
                    changes.append({'surface_id':'sqlite.'+name,'kind':'row_multiset','operation':'multiset_delta',
                                    'table':name,'row':row,'count_delta':nc[row]-oc[row]})
    for rel in sorted(set(b['files']) | set(a['files'])):
        before = b['files'].get(rel)
        after = a['files'].get(rel)
        if before == after:
            continue
        op = 'create_file' if before is None else 'delete_file' if after is None else 'modify_file'
        changes.append({'surface_id':'filesystem.'+rel.split('/')[0], 'kind':'filesystem',
                        'operation':op, 'path':rel,'old':before,'new':after})
    return changes
