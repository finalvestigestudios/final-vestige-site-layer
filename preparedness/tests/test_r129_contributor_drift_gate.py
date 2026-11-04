"""R129 synthetic three-way immutable-drift tests (no repository writes)."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

PATH=Path(__file__).resolve().parents[1]/'tools/r129_contributor_drift_gate.py'
spec=importlib.util.spec_from_file_location('r129',PATH)
g=importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
BODY='preparedness/content/articles/pemmican-and-dried-meats.body.html'
META='preparedness/content/articles/pemmican-and-dried-meats.meta.json'
SOURCE='preparedness/sources/fragments/hist-food.json'
DOC='preparedness/docs/CLUSTER-hist-food.md'
TEST='preparedness/tests/test_preparedness.py'

def body(cite='one',words='Example words',n=1):return ('<p>'+words+'{{cite:'+cite+'}}</p>') .encode()*n

def meta(slug='pemmican-and-dried-meats',state='pending',publish='draft',sources=None):
    return json.dumps({'slug':slug,'safety_review':{'state':state},'status':{'publish':publish},
                       'source_use':sources or {'one':'Author has read the stated material.'}}).encode()

def sources(rows=None):
    if rows is None: rows=[{'id':'one','url':'https://example.org/one','notes':'read intro','supports':'claim A',
                             'verified_on':'2026-11-01','human_link_check':False}]
    return json.dumps({'sources':rows}).encode()

class TestStatic(unittest.TestCase):
    def test_protected_clusters(self):self.assertEqual(len(g.BRANCHES),7)
    def test_freeze_current_are_full_sha(self):
        for a,b,_ in g.BRANCHES.values():self.assertRegex(a,r'^[0-9a-f]{40}$');self.assertRegex(b,r'^[0-9a-f]{40}$')
    def test_start_and_shelter_no_changed_paths(self):
        self.assertEqual(g.DIFF_PATHS['start'],[]);self.assertEqual(g.DIFF_PATHS['shelter'],[])
    def test_unique_path_observations(self):
        self.assertEqual(sum(map(len,g.DIFF_PATHS.values())),23)
        self.assertEqual(len(set(x for v in g.DIFF_PATHS.values() for x in v)),22)
    def test_blob(self):self.assertEqual(g.blob_sha(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_no_duplicate_json_keys(self):
        with self.assertRaisesRegex(g.Hold,'DUPLICATE_JSON_KEY'):g.parse_json(b'{"a":1,"a":2}')
    def test_bad_json(self):
        with self.assertRaisesRegex(g.Hold,'CORRUPT_JSON'):g.parse_json(b'not-json')
    def test_non_utf8(self):
        with self.assertRaisesRegex(g.Hold,'CORRUPT_JSON'):g.parse_json(b'\xff')
    def test_citation_counter(self):
        z=g.describe(body(n=3),'article_body');self.assertEqual(z['citation_occurrences'],3)
    def test_exact_ids(self):self.assertEqual(g.describe(body(),'article_body')['unique_citation_ids'],['one'])
    def test_citations_missing(self):
        with self.assertRaisesRegex(g.Hold,'CITATIONS_MISSING'):g.describe(b'<p>Hello</p>','article_body')
    def test_malformed_citation(self):
        with self.assertRaisesRegex(g.Hold,'MALFORMED_CITATION'):g.describe(b'<p>{{cite:one</p>','article_body')
    def test_publish_remains_draft(self):self.assertEqual(g.describe(meta(),'article_metadata')['publish_state'],'draft')
    def test_source_record(self):self.assertIn('one',g.source_record(sources()))
    def test_missing_row_fails(self):
        with self.assertRaisesRegex(g.Hold,'SOURCE_REGISTER_SHAPE'):g.source_record(b'{}')
    def test_changed_path_kinds(self):
        self.assertEqual(g.classify(BODY),'article_body');self.assertEqual(g.classify(META),'article_metadata')
        self.assertEqual(g.classify(SOURCE),'source_register');self.assertEqual(g.classify(DOC),'documentation')
        self.assertEqual(g.classify(TEST),'test')
    def test_unexpected_path(self):
        with self.assertRaises(g.Hold):g.classify('homepage/index.html')
    def test_no_ci_or_qd_claim(self):
        def reader(commit,path):
            if path.endswith('body.html'):return body()
            if path.endswith('meta.json'):return meta()
            if path.startswith('preparedness/sources/') and path.endswith('.json'):return sources()
            return b'Doc fixture.'
        x=g.make_docket(reader);self.assertFalse(x['may_merge']);self.assertFalse(x['may_publish'])
        self.assertFalse(x['independent_QD_PASS']);self.assertFalse(x['medical_safety_verified'])
        self.assertFalse(x['commercial_conversion_verified'])
        self.assertEqual(x['changed_path_observations'],23);self.assertEqual(x['outstanding_review_paths'],23)
    def test_incomplete_branch_roster(self):
        h={k:x[1] for k,x in g.BRANCHES.items()};h.pop('food')
        with self.assertRaisesRegex(g.Hold,'INCOMPLETE_CLUSTER_ROSTER'):
            g.validate_header({k:x[0] for k,x in g.BRANCHES.items()},h,g.CANDIDATE,g.DIFF_PATHS)
    def test_wrong_candidate(self):
        with self.assertRaisesRegex(g.Hold,'CANDIDATE_SHA_DRIFT'):
            g.validate_header({k:x[0] for k,x in g.BRANCHES.items()},
                              {k:x[1] for k,x in g.BRANCHES.items()},'f'*40,g.DIFF_PATHS)
    def test_branch_head_drift(self):
        h={k:x[1] for k,x in g.BRANCHES.items()};h['food']='a'*40
        with self.assertRaisesRegex(g.Hold,'BRANCH_HEAD_DRIFT'):
            g.validate_header({k:x[0] for k,x in g.BRANCHES.items()},h,g.CANDIDATE,g.DIFF_PATHS)
    def test_paths_missing(self):
        p=copy.deepcopy(g.DIFF_PATHS);p['hist-home'].pop()
        with self.assertRaisesRegex(g.Hold,'DUPLICATE|INCOMPLETE_CHANGED_PATHS|CHANGED_PATH'):
            g.validate_header({k:x[0] for k,x in g.BRANCHES.items()},
                              {k:x[1] for k,x in g.BRANCHES.items()},g.CANDIDATE,p)
    def test_missing_object(self):
        with self.assertRaisesRegex(g.Hold,'MISSING_PROTECTED_PATH'):
            g.compare_three_way(BODY,None,body(),body())
    def test_object_fetch_error(self):
        def reader(c,p):raise subprocess.CalledProcessError(1,'git show')
        with self.assertRaisesRegex(g.Hold,'GIT_OBJECT_UNAVAILABLE'):g.make_docket(reader)

class TestThreeWay(unittest.TestCase):
    def test_old(self):self.assertEqual(g.compare_three_way(BODY,body(),body('two'),body())['comparison'],'CANDIDATE_MATCHES_OLD_HEAD')
    def test_new(self):self.assertEqual(g.compare_three_way(BODY,body(),body('two'),body('two'))['comparison'],'CANDIDATE_MATCHES_NEW_HEAD')
    def test_third(self):self.assertEqual(g.compare_three_way(BODY,body(),body('two'),body('three'))['comparison'],'CANDIDATE_IS_THIRD_VERSION')
    def test_no_review_approval_when_match(self):
        x=g.compare_three_way(BODY,body(),body(),body());self.assertEqual(x['review_state'],'OPEN_HUMAN_ADJUDICATION')
    def test_removed_source_citation(self):
        x=g.compare_three_way(BODY,body('old'),body('new'),body('old'))
        self.assertEqual(x['removed_citation_ids'],['old']);self.assertEqual(x['added_citation_ids'],['new'])
    def test_changed_citation_occurrences(self):
        x=g.compare_three_way(BODY,body(n=1),body(n=3),body(n=1));self.assertEqual(x['citation_delta'],2)
    def test_word_delta(self):
        x=g.compare_three_way(BODY,body(words='short'),body(words='short has more words'),body(words='short'))
        self.assertGreater(x['approx_word_delta'],0)
    def test_meta_added_source(self):
        x=g.compare_three_way(META,meta(),meta(sources={'one':'a','two':'b'}),meta())
        self.assertEqual(x['added_source_explanations'],['two'])
    def test_meta_removed_source(self):
        x=g.compare_three_way(META,meta(sources={'one':'a','two':'b'}),meta(),meta())
        self.assertEqual(x['removed_source_explanations'],['two'])
    def test_meta_changed_source(self):
        x=g.compare_three_way(META,meta(sources={'one':'a'}),meta(sources={'one':'b'}),meta())
        self.assertEqual(x['changed_source_explanations'],['one'])
    def test_meta_safety_state_held(self):
        x=g.compare_three_way(META,meta(state='pending'),meta(state='approved'),meta())
        self.assertEqual(x['review_state'],'BLOCKED_SAFETY_STATE_TRANSITION')
    def test_meta_slug_changed(self):
        with self.assertRaisesRegex(g.Hold,'ARTICLE_SLUG_DRIFT'):
            g.compare_three_way(META,meta(),meta(slug='changed'),meta())
    def test_missing_author_note(self):
        with self.assertRaises(g.Hold):g.describe(meta(sources={'one':' '}),'article_metadata')
    def test_publish_change(self):
        with self.assertRaisesRegex(g.Hold,'PUBLISH_STATUS_NOT_DRAFT'):
            g.compare_three_way(META,meta(),meta(publish='publish'),meta())
    def test_source_added(self):
        arr=[{'id':'one','url':'https://one.com'},{'id':'two','url':'https://two.com'}]
        x=g.compare_three_way(SOURCE,sources(rows=arr[:1]),sources(rows=arr),sources(rows=arr[:1]))
        self.assertEqual(x['added_source_ids'],['two'])
    def test_source_removed(self):
        arr=[{'id':'one','url':'https://one.com'},{'id':'two','url':'https://two.com'}]
        x=g.compare_three_way(SOURCE,sources(rows=arr),sources(rows=arr[:1]),sources(rows=arr))
        self.assertEqual(x['removed_source_ids'],['two'])
    def test_source_url_changed(self):
        a=[{'id':'one','url':'https://one.com'}];b=[{'id':'one','url':'https://two.com'}]
        x=g.compare_three_way(SOURCE,sources(rows=a),sources(rows=b),sources(rows=a))
        self.assertEqual(x['source_url_changes'],['one'])
    def test_source_interpretation_changed(self):
        a=[{'id':'one','url':'https://one.com','supports':'A'}];b=[{'id':'one','url':'https://one.com','supports':'B'}]
        x=g.compare_three_way(SOURCE,sources(rows=a),sources(rows=b),sources(rows=a))
        self.assertEqual(x['interpretation_changes'],['one'])
    def test_source_duplicate_id(self):
        arr=[{'id':'one','url':'https://one.com'},{'id':'one','url':'https://two.com'}]
        with self.assertRaisesRegex(g.Hold,'DUPLICATE_SOURCE_ID_IN_FILE'):g.source_record(sources(rows=arr))
    def test_source_bad_url(self):
        with self.assertRaisesRegex(g.Hold,'INVALID_SOURCE_URL'):
            g.source_record(sources(rows=[{'id':'one','url':'ftp://one.com'}]))

# 24 additional independent input-mutation tests, with explicit expected HOLD codes.
def invalid_case(label,record,kind,code):
    def test(self):
        with self.assertRaisesRegex(g.Hold,code):g.describe(record,kind)
    setattr(TestThreeWay,'test_mutation_'+label,test)
for label,record,kind,code in [
 ('no_cite',b'<h1>heading only</h1>','article_body','CITATIONS_MISSING'),
 ('unterminated',b'{{cite:one','article_body','MALFORMED_CITATION'),
 ('upper',b'{{cite:ONE}}','article_body','MALFORMED_CITATION'),
 ('underscore',b'{{cite:one_two}}','article_body','MALFORMED_CITATION'),
 ('space',b'{{cite:one two}}','article_body','MALFORMED_CITATION'),
 ('blank',b'{{cite:}}','article_body','MALFORMED_CITATION'),
 ('empty_meta',b'{}','article_metadata','EMPTY_AUTHOR_SOURCE_USE'),
 ('bad_state',meta(state='safely-approved'),'article_metadata','SAFETY_REVIEW_STATE_INVALID'),
 ('bad_publish',meta(publish='published'),'article_metadata','PUBLISH_STATUS_NOT_DRAFT'),
 ('blank_note',meta(sources={'one':'   '}),'article_metadata','BLANK_AUTHOR_SOURCE_USE'),
 ('not_json',b'not-json','article_metadata','CORRUPT_JSON'),
 ('duplicated_meta',b'{"source_use":{"one":"a"},"source_use":{"two":"b"}}','article_metadata','DUPLICATE_JSON_KEY'),
 ('not_sources',b'{"sources":{}}','source_register','SOURCE_REGISTER_SHAPE'),
 ('sources_array',b'[]','source_register','SOURCE_REGISTER_SHAPE'),
 ('sources_null',b'{"sources":null}','source_register','SOURCE_REGISTER_SHAPE'),
 ('sources_empty_id',sources(rows=[{'id':5,'url':'https://one.com'}]),'source_register','INVALID_SOURCE_ROW'),
 ('sources_no_id',sources(rows=[{'url':'https://one.com'}]),'source_register','INVALID_SOURCE_ROW'),
 ('sources_no_url',sources(rows=[{'id':'one'}]),'source_register','INVALID_SOURCE_ROW'),
 ('sources_not_url',sources(rows=[{'id':'one','url':5}]),'source_register','INVALID_SOURCE_ROW'),
 ('sources_local',sources(rows=[{'id':'one','url':'file:///tmp/test'}]),'source_register','INVALID_SOURCE_URL'),
 ('sources_javascript',sources(rows=[{'id':'one','url':'javascript:alert(1)'}]),'source_register','INVALID_SOURCE_URL'),
 ('sources_dup',sources(rows=[{'id':'one','url':'https://a.org'},{'id':'one','url':'https://a.org'}]),'source_register','DUPLICATE_SOURCE_ID_IN_FILE'),
 ('sources_duplicate_topkey',b'{"sources":[],"sources":{}}','source_register','DUPLICATE_JSON_KEY'),
 ('invalid_meta_unicode',b'\xff','article_metadata','CORRUPT_JSON'),
]:invalid_case(label,record,kind,code)

if __name__=='__main__':unittest.main()
