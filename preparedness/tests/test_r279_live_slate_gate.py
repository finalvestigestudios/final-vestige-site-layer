"""R279's isolated synthetic custody mutations; no real consumer or medical approval."""
import copy
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / 'tools' / 'r279_live_slate_gate.py'
spec = importlib.util.spec_from_file_location('r279_live_slate_gate', SRC)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def manifest_and_tree(root):
    entries = []
    def add(path, role, data):
        f = root / path
        f.parent.mkdir(parents=True, exist_ok=True)
        raw = data.encode()
        f.write_bytes(raw)
        entries.append({'path': path, 'role': role, 'sha': g.blob(raw), 'size': len(raw)})
    for i in range(1, 36):
        slug = f'article-{i:02d}'
        add(f'content/articles/{slug}.body.html', 'article_body', f'<h2>Original article {i}</h2>')
        add(f'content/articles/{slug}.meta.json', 'article_meta', json.dumps({'slug': slug, 'status': {'publish': 'draft'}}))
    for i in range(1, 7):
        slug = f'tool-{i:02d}'
        add(f'content/tools/{slug}.body.html', 'tool_body', f'<h2>Unapproved tool {i}</h2>')
        add(f'content/tools/{slug}.meta.json', 'tool_meta', json.dumps({'slug': slug, 'status': {'publish': 'draft'}}))
    add('content/hubs/start-here.body.html', 'hub_body', '<p>Unapproved hub</p>')
    for i in range(8):
        add(f'sources/fragments/source-{i}.json', 'source_origin', '{}')
    add('sources/crosswalk.json', 'crosswalk', '{}')
    add('audits/r273_shared_source_review_docket_UNAPPROVED.json', 'docket', '{}')
    add('tools/r220_full_slate_draft_custody.py', 'export_gate', 'print("draft")')
    add('tools/r272_crosswalk_snapshot_hold.py', 'source_gate', 'print("hold")')
    add('tools/r273_source_review_docket_hold.py', 'docket_gate', 'print("hold")')
    assert len(entries) == 96
    return {'schema': 'fv-r276-all-slate-identity-v1', 'state': g.HOLD, 'snapshot_ref': g.SNAPSHOT,
            'source_review': {'shared_url_groups': 32, 'duplicate_id_groups': 15, 'held_occurrences': 3},
            'may_merge': False, 'publication_authorized': False, 'independent_qd_pass': False,
            'medical_safety_verified': False, 'privacy_approved': False,
            'merchant_offer_approved': False, 'entries': entries}


class R279(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.m = manifest_and_tree(self.root)

    def invalid_manifest(self, mutation):
        x = copy.deepcopy(self.m)
        mutation(x)
        with self.assertRaises((ValueError, TypeError, KeyError, AttributeError)):
            g.check_manifest(x)

    def invalid_tree(self, mutation):
        mutation(self.root, self.m)
        with self.assertRaises((ValueError, OSError, TypeError, KeyError, AttributeError)):
            g.check_tree(self.root, self.m)

    def test_synthetic_baseline_is_held(self):
        result = g.check_tree(self.root, self.m)
        self.assertEqual(result['state'], g.HOLD)
        self.assertFalse(result['publication_authorized'])
        self.assertFalse(result['independent_qd_pass'])
        self.assertEqual((result['article_count'], result['tool_count'], result['protected_files']), (35, 6, 96))

    def test_unpinned_synthetic_manifest_cannot_pass_production_audit(self):
        p = self.root / g.MANIFEST
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.m))
        self.assertEqual(g.audit(self.root)['state'], g.INVALID)

    def test_missing_manifest_fails_closed(self):
        self.assertEqual(g.audit(self.root)['state'], g.INVALID)

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            g.load_json(b'{"x":1,"x":2}')

    def test_nonfinite_json_rejected(self):
        with self.assertRaises(ValueError):
            g.load_json(b'{"x":NaN}')

    def test_github_blob_computation(self):
        self.assertEqual(g.blob(b'hello\n'), 'ce013625030ba8dba906f756967f9e9ca394464a')


def wrong_field(m, field, value):
    m[field] = value


def damaged_entry(m, n, field, val):
    m['entries'][n][field] = val


# Each case is its own unittest, rather than hidden inside a loop/subTest.
MANIFEST_CASES = {
    'schema': lambda m: wrong_field(m, 'schema', 'unknown'),
    'snapshot': lambda m: wrong_field(m, 'snapshot_ref', '0'*40),
    'state': lambda m: wrong_field(m, 'state', 'APPROVED'),
    'missing_state': lambda m: m.pop('state'),
    'shared_groups': lambda m: m['source_review'].__setitem__('shared_url_groups', 31),
    'duplicate_groups': lambda m: m['source_review'].__setitem__('duplicate_id_groups', 14),
    'held_occurrences': lambda m: m['source_review'].__setitem__('held_occurrences', 2),
    'missing_source_review': lambda m: m.pop('source_review'),
    'may_merge': lambda m: wrong_field(m, 'may_merge', True),
    'publish': lambda m: wrong_field(m, 'publication_authorized', True),
    'qd': lambda m: wrong_field(m, 'independent_qd_pass', True),
    'medical': lambda m: wrong_field(m, 'medical_safety_verified', True),
    'privacy': lambda m: wrong_field(m, 'privacy_approved', True),
    'merchant': lambda m: wrong_field(m, 'merchant_offer_approved', True),
    'missing_flag': lambda m: m.pop('merchant_offer_approved'),
    'none_flag': lambda m: wrong_field(m, 'publication_authorized', None),
    'numeric_false': lambda m: wrong_field(m, 'publication_authorized', 0),
    'lost_file': lambda m: m['entries'].pop(),
    'added_file': lambda m: m['entries'].append(copy.deepcopy(m['entries'][0])),
    'duplicate_path': lambda m: m['entries'][1].__setitem__('path', m['entries'][0]['path']),
    'path_traversal': lambda m: damaged_entry(m, 0, 'path', '../evil'),
    'absolute_path': lambda m: damaged_entry(m, 0, 'path', '/etc/hosts'),
    'backslash': lambda m: damaged_entry(m, 0, 'path', 'content\\articles\\x'),
    'dot_path': lambda m: damaged_entry(m, 0, 'path', 'content/./articles/x.body.html'),
    'empty_path': lambda m: damaged_entry(m, 0, 'path', ''),
    'null_path': lambda m: damaged_entry(m, 0, 'path', None),
    'missing_sha': lambda m: m['entries'][0].pop('sha'),
    'fake_sha': lambda m: damaged_entry(m, 0, 'sha', 'not-a-sha'),
    'sha_uppercase': lambda m: damaged_entry(m, 0, 'sha', 'A'*40),
    'short_sha': lambda m: damaged_entry(m, 0, 'sha', 'ab'),
    'zero_size': lambda m: damaged_entry(m, 0, 'size', 0),
    'negative_size': lambda m: damaged_entry(m, 0, 'size', -1),
    'float_size': lambda m: damaged_entry(m, 0, 'size', 12.0),
    'bool_size': lambda m: damaged_entry(m, 0, 'size', True),
    'unknown_role': lambda m: damaged_entry(m, 0, 'role', 'approved'),
    'role_swap': lambda m: damaged_entry(m, 0, 'role', 'article_meta'),
    'source_role_swap': lambda m: damaged_entry(m, 0, 'role', 'source_origin'),
    'hub_path': lambda m: next(e for e in m['entries'] if e['role']=='hub_body').__setitem__('path', 'content/hubs/changed.body.html'),
    'crosswalk_path': lambda m: next(e for e in m['entries'] if e['role']=='crosswalk').__setitem__('path', 'sources/replacement.json'),
    'docket_path': lambda m: next(e for e in m['entries'] if e['role']=='docket').__setitem__('path', 'audits/unapproved.json'),
    'export_gate_path': lambda m: next(e for e in m['entries'] if e['role']=='export_gate').__setitem__('path', 'tools/override.py'),
    'source_gate_path': lambda m: next(e for e in m['entries'] if e['role']=='source_gate').__setitem__('path', 'tools/override.py'),
    'docket_gate_path': lambda m: next(e for e in m['entries'] if e['role']=='docket_gate').__setitem__('path', 'tools/override.py'),
    'entry_extra_key': lambda m: m['entries'][0].__setitem__('approved', True),
}

TREE_CASES = {
    'article_byte_edit': lambda root,m: (root/'content/articles/article-01.body.html').write_text('<h2>tampered</h2>'),
    'tool_byte_edit': lambda root,m: (root/'content/tools/tool-01.body.html').write_text('<h2>tampered</h2>'),
    'article_meta_edit': lambda root,m: (root/'content/articles/article-01.meta.json').write_text('{"status":{"publish":"publish"}}'),
    'tool_meta_edit': lambda root,m: (root/'content/tools/tool-01.meta.json').write_text('{"status":{"publish":"publish"}}'),
    'crosswalk_edit': lambda root,m: (root/'sources/crosswalk.json').write_text('{"approved":true}'),
    'docket_edit': lambda root,m: (root/'audits/r273_shared_source_review_docket_UNAPPROVED.json').write_text('{"approved":true}'),
    'origin_edit': lambda root,m: (root/'sources/fragments/source-2.json').write_text('{"modified":true}'),
    'hub_edit': lambda root,m: (root/'content/hubs/start-here.body.html').write_text('<p>changed</p>'),
    'exporter_edit': lambda root,m: (root/'tools/r220_full_slate_draft_custody.py').write_text('print("release")'),
    'source_gate_edit': lambda root,m: (root/'tools/r272_crosswalk_snapshot_hold.py').write_text('print("release")'),
    'docket_gate_edit': lambda root,m: (root/'tools/r273_source_review_docket_hold.py').write_text('print("release")'),
    'missing_article': lambda root,m: (root/'content/articles/article-01.body.html').unlink(),
    'missing_source': lambda root,m: (root/'sources/fragments/source-0.json').unlink(),
    'unexpected_article': lambda root,m: (root/'content/articles/extra.body.html').write_text('<h2>extra</h2>'),
    'unexpected_tool': lambda root,m: (root/'content/tools/extra.meta.json').write_text('{}'),
    'article_symlink': lambda root,m: ((root/'content/articles/article-01.body.html').unlink(), (root/'content/articles/article-01.body.html').symlink_to(root/'content/articles/article-02.body.html')),
    'tool_symlink': lambda root,m: ((root/'content/tools/tool-01.body.html').unlink(), (root/'content/tools/tool-01.body.html').symlink_to(root/'content/tools/tool-02.body.html')),
    'source_symlink': lambda root,m: ((root/'sources/fragments/source-0.json').unlink(), (root/'sources/fragments/source-0.json').symlink_to(root/'sources/fragments/source-1.json')),
}


def make_manifest(name, mutate):
    def test(self):
        self.invalid_manifest(mutate)
    test.__name__ = 'test_manifest_rejects_' + name
    return test


def make_tree(name, mutate):
    def test(self):
        self.invalid_tree(mutate)
    test.__name__ = 'test_tree_rejects_' + name
    return test


for name, mutation in MANIFEST_CASES.items():
    setattr(R279, 'test_manifest_rejects_' + name, make_manifest(name, mutation))
for name, mutation in TREE_CASES.items():
    setattr(R279, 'test_tree_rejects_' + name, make_tree(name, mutation))

if __name__ == '__main__':
    unittest.main(verbosity=2)
