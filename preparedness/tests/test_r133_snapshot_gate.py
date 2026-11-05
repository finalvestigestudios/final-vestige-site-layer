"""Adversarial isolated fixture tests. All edits occur in TemporaryDirectory only."""
import json
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'tools' / 'r133_snapshot_gate.py'
spec = importlib.util.spec_from_file_location('r133_gate', MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.files = {}
        self.manifest = {'schema_version': 1, 'release_status': gate.HOLD,
                         'candidate_parent': '5685b54796d520e8dd50e0cdf4d35e38c9cec7a4',
                         'qd_pass': False, 'may_publish': False,
                         'medical_safety_verified': False,
                         'merchant_offer_verified': False,
                         'expected_citation_occurrences': 35}
        self.slate = [{'n': i+1, 'slug': f'article-{i:02d}', 'section': 'start-here',
                       'track': 'modern', 'gate': i < 4} for i in range(35)]
        self._write('preparedness/taxonomy.json', {'base_path': '/preparedness/', 'slate': self.slate})
        self._write('preparedness/sources/register.json', {'sources': [
            {'id':'s1','url':'https://example.org/s1','title':'Source','supports':'Relevant scope',
             'verified_on':'2026-11-04'}]})
        for name in ('start', 'shelter', 'food', 'health', 'hist-food', 'hist-home', 'hist-field'):
            self._write(f'preparedness/sources/fragments/{name}.json', {'sources': []})
        groups = [{'review_status': gate.PENDING, 'reviewer': None, 'reviewed_on': None,
                   'variants': [{'origin':'base','source':{'id':f's-{i}-a','url':f'https://test/{i}'}},
                                {'origin':'food','source':{'id':f's-{i}-b','url':f'https://test/{i}'}}]}
                  for i in range(32)]
        self._write('preparedness/sources/crosswalk.json',
                    {'status':'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
                     'groups':groups,'article_origins':{}})
        for row in self.slate:
            slug = row['slug']
            self._write(f'preparedness/content/articles/{slug}.body.html',
                        '<p>Follow current guidance.{{cite:s1}}</p>', json_output=False)
            self._write(f'preparedness/content/articles/{slug}.meta.json',
                        {'slug':slug,'section':'start-here','track':'modern',
                         'status':{'publish':'draft'},'safety_review':{'state':'pending'},
                         'source_use':{'s1':'Author read page for specific action'}})
        self.relock()

    def _write(self,path,obj,json_output=True):
        p=self.root/path
        p.parent.mkdir(parents=True,exist_ok=True)
        raw=(json.dumps(obj,sort_keys=True).encode('utf-8') if json_output else obj.encode('utf-8'))
        p.write_bytes(raw)
        self.files[path]=raw
        return p

    def rewrite(self,path,fn,json_output=True):
        if json_output:
            obj=json.loads(self.files[path]);fn(obj)
            self._write(path,obj)
        else:
            raw=self.files[path].decode('utf-8')
            self._write(path,fn(raw),False)
        self.relock()

    def relock(self):
        self.manifest['files']=[{'path':p,'blob_sha':gate.blob(b)}
                                for p,b in sorted(self.files.items())]

    def audit(self):
        return gate.audit(self.root, self.manifest)

    def test_complete_35_article_fixture_is_structural_hold(self):
        out=self.audit()
        self.assertEqual(out['articles'],35)
        self.assertEqual(out['visible_citation_occurrences'],35)
        self.assertEqual(out['shared_source_groups_pending'],32)
        self.assertFalse(out['qd_pass'])
        self.assertFalse(out['may_publish'])

    def test_forged_manifest_approval(self):
        self.manifest['qd_pass']=True
        with self.assertRaisesRegex(gate.IntegrityHold,'FORGED_APPROVAL'):self.audit()

    def test_published_metadata_fails_even_when_relocked(self):
        self.rewrite('preparedness/content/articles/article-00.meta.json',
                     lambda m:m['status'].update(publish='published'))
        with self.assertRaisesRegex(gate.IntegrityHold,'PUBLICATION_UPGRADE'):self.audit()

    def test_safety_gate_downgrade_fails(self):
        self.rewrite('preparedness/content/articles/article-00.meta.json',
                     lambda m:m['safety_review'].update(state='not-required'))
        with self.assertRaisesRegex(gate.IntegrityHold,'HIGH_CONSEQUENCE_GATE_DOWNGRADE'):self.audit()

    def test_historical_approved_not_qd(self):
        self.rewrite('preparedness/content/articles/article-00.meta.json',
                     lambda m:m['safety_review'].update(state='approved',reviewer='historical reviewer',date='2026-10-30'))
        out=self.audit()
        self.assertEqual(out['historical_safety_states_not_independent_approval']['approved'],1)
        self.assertFalse(out['qd_pass'])

    def test_hiding_citation_in_attribute_fails(self):
        self.rewrite('preparedness/content/articles/article-01.body.html',
                     lambda b:'<p title="{{cite:s1}}">Action.</p>',False)
        with self.assertRaisesRegex(gate.IntegrityHold,'HIDDEN_OR_ATTRIBUTE'):self.audit()

    def test_hiding_citation_in_comment_fails(self):
        self.rewrite('preparedness/content/articles/article-01.body.html',
                     lambda b:'<!-- {{cite:s1}} --><p>Action</p>',False)
        with self.assertRaisesRegex(gate.IntegrityHold,'HIDDEN_OR_ATTRIBUTE'):self.audit()

    def test_hiding_citation_in_script_fails(self):
        self.rewrite('preparedness/content/articles/article-01.body.html',
                     lambda b:'<script>{{cite:s1}}</script>',False)
        with self.assertRaisesRegex(gate.IntegrityHold,'HIDDEN_OR_ATTRIBUTE'):self.audit()

    def test_hiding_citation_in_template_fails(self):
        self.rewrite('preparedness/content/articles/article-01.body.html',
                     lambda b:'<template>{{cite:s1}}</template>',False)
        with self.assertRaisesRegex(gate.IntegrityHold,'HIDDEN_OR_ATTRIBUTE'):self.audit()

    def test_hiding_citation_with_aria_fails(self):
        self.rewrite('preparedness/content/articles/article-01.body.html',
                     lambda b:'<div aria-hidden="true"><p>{{cite:s1}}</p></div>',False)
        with self.assertRaisesRegex(gate.IntegrityHold,'HIDDEN_OR_ATTRIBUTE'):self.audit()

    def test_hiding_citation_with_inert_fails(self):
        self.rewrite('preparedness/content/articles/article-01.body.html',
                     lambda b:'<div inert><p>{{cite:s1}}</p></div>',False)
        with self.assertRaisesRegex(gate.IntegrityHold,'HIDDEN_OR_ATTRIBUTE'):self.audit()

    def test_hiding_citation_with_style_fails(self):
        self.rewrite('preparedness/content/articles/article-01.body.html',
                     lambda b:'<div style=" display: none ">{{cite:s1}}</div>',False)
        with self.assertRaisesRegex(gate.IntegrityHold,'HIDDEN_OR_ATTRIBUTE'):self.audit()

    def test_unclosed_citation_marker_fails(self):
        self.rewrite('preparedness/content/articles/article-01.body.html',
                     lambda b:'<p>{{cite:s1</p>',False)
        with self.assertRaisesRegex(gate.IntegrityHold,'MALFORMED_CITATION'):self.audit()

    def test_missing_source_use_fails(self):
        self.rewrite('preparedness/content/articles/article-01.meta.json',
                     lambda m:m.update(source_use={}))
        with self.assertRaisesRegex(gate.IntegrityHold,'SOURCE_USE_CROSSWALK'):self.audit()

    def test_blank_source_scope_fails(self):
        self.rewrite('preparedness/content/articles/article-01.meta.json',
                     lambda m:m['source_use'].update(s1='  '))
        with self.assertRaisesRegex(gate.IntegrityHold,'BLANK_READING_SCOPE'):self.audit()

    def test_unverified_official_source_fails(self):
        self.rewrite('preparedness/sources/register.json',
                     lambda m:m['sources'][0].update(verified_on=None))
        with self.assertRaisesRegex(gate.IntegrityHold,'UNCHECKED_SOURCE'):self.audit()

    def test_unknown_source_fails_when_note_present(self):
        self.rewrite('preparedness/content/articles/article-01.body.html',
                     lambda b:b.replace('{{cite:s1}}','{{cite:new}}'),False)
        self.rewrite('preparedness/content/articles/article-01.meta.json',
                     lambda m:m.update(source_use={'new':'A note but not registered'}))
        with self.assertRaisesRegex(gate.IntegrityHold,'UNCHECKED_SOURCE'):self.audit()

    def test_shared_group_approval_fails(self):
        self.rewrite('preparedness/sources/crosswalk.json',
                     lambda m:m['groups'][0].update(review_status='resolved'))
        with self.assertRaisesRegex(gate.IntegrityHold,'SOURCE_GROUP_UNREVIEWED_REQUIRED'):self.audit()

    def test_missing_article_file_fails(self):
        p=self.root/'preparedness/content/articles/article-01.body.html';p.unlink()
        with self.assertRaises((OSError,gate.IntegrityHold)):self.audit()

    def test_extra_article_not_in_manifest_fails(self):
        p=self.root/'preparedness/content/articles/sneaked.body.html';p.write_text('body')
        with self.assertRaisesRegex(gate.IntegrityHold,'UNMANIFESTED'):self.audit()

    def test_duplicate_taxonomy_slug_fails(self):
        self.rewrite('preparedness/taxonomy.json',
                     lambda m:m['slate'][0].update(slug='article-01'))
        with self.assertRaisesRegex(gate.IntegrityHold,'TAXONOMY_ROSTER_DRIFT'):self.audit()

    def test_bad_route_base_fails(self):
        self.rewrite('preparedness/taxonomy.json',
                     lambda m:m.update(base_path='/unapproved/'))
        with self.assertRaisesRegex(gate.IntegrityHold,'ROUTE_BASE_DRIFT'):self.audit()

    def test_manifest_path_traversal_fails(self):
        self.manifest['files'][0]['path']='preparedness/../../private'
        with self.assertRaisesRegex(gate.IntegrityHold,'BAD_FILE_MANIFEST'):self.audit()

    def test_manifest_bad_candidate_parent_fails(self):
        self.manifest['candidate_parent']='deadbeef'
        with self.assertRaisesRegex(gate.IntegrityHold,'CANDIDATE_PARENT_DRIFT'):self.audit()

    def test_duplicate_json_key_fails(self):
        path='preparedness/taxonomy.json'
        self._write(path,'{"base_path":"/preparedness/","base_path":"/bad/","slate":[]}',False)
        self.relock()
        with self.assertRaisesRegex(gate.IntegrityHold,'DUPLICATE_JSON_KEY'):self.audit()


def _make_snapshot_tamper_test(i):
    def test(self):
        path=f'preparedness/content/articles/article-{i:02d}.body.html'
        (self.root/path).write_bytes(self.files[path]+b'\n<!-- unexpected change -->')
        with self.assertRaisesRegex(gate.IntegrityHold,'GIT_BLOB_DRIFT'):
            self.audit()
    return test

for _i in range(35):
    setattr(SnapshotTests, f'test_immutable_blob_{_i:02d}', _make_snapshot_tamper_test(_i))

if __name__=='__main__':
    unittest.main()
