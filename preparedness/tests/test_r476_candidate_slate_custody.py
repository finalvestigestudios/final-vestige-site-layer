"""R476 unit fixtures: reject regressions but NEVER certify live safety or revenue."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('r476', BASE / 'tools/r476_candidate_slate_custody.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def example(number=1, slug='alpha'):
    html = ('<h1>First aid reading</h1>' + '<p>Full explanation and detailed context {{cite:source-a}}</p>' * 8).encode()
    meta = {'n': number, 'slug': slug, 'title': 'Substantive article', 'section': 'food',
            'track': 'modern', 'status': {'publish': 'draft'},
            'safety_review': {'state': 'pending', 'reviewer': None},
            'source_use': {'source-a': 'Exact agency reading scope, not just a homepage.'}}
    raw = json.dumps(meta).encode()
    return html, raw, meta

def snapshot(count=1):
    articles = []
    for i in range(count):
        slug = 'a' + str(i).zfill(2)
        html, raw, _ = example(i + 1, slug)
        articles.append({'slug': slug, 'body': {'path': f'content/articles/{slug}.body.html',
                'git_blob': gate.git_blob(html), 'bytes': len(html)},
            'meta': {'path': f'content/articles/{slug}.meta.json',
                'git_blob': gate.git_blob(raw), 'bytes': len(raw)}})
    return {'schema': gate.SCHEMA, 'repository': gate.REPO, 'candidate_parent_sha': gate.PARENT,
            'release': gate.STATE, 'permission': 'STRUCTURAL_EVIDENCE_ONLY_NOT_QD_PASS',
            'articles': articles, 'commerce': {'verified_purchasable_preparedness_sku': None,
              'published_grok_asset_id': None, 'paid_order_verified': None,
              'realized_net_revenue_per_1000_qualified_sessions': None},
            'review_state': {'qualified_qd_pass': False, 'native_35_article_build_pass': False,
              'wordpress_export_parity_pass': False, 'medical_food_child_privacy_approved': False,
              'publish_authorized': False, 'source_disputes_resolved': False}}

class CandidateTests(unittest.TestCase):
    def test_single_manifest_shape_passes(self):
        self.assertEqual(len(gate.check_manifest(snapshot(), 1)), 1)
    def test_git_blob(self):
        self.assertEqual(gate.git_blob(b'hello'), 'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_duplicate_key_rejected(self):
        with self.assertRaises(gate.Hold): gate.strict_json(b'{"x":1,"x":2}')
    def test_nan_rejected(self):
        with self.assertRaises(gate.Hold): gate.strict_json(b'{"x":NaN}')
    def test_unbound_citation_rejected(self):
        html,raw,_=example()
        with self.assertRaises(gate.Hold):gate.check_article('alpha',html.replace(b'source-a',b'unknown-b'),raw,set())
    def test_number_duplicate_rejected(self):
        html,raw,_=example()
        with self.assertRaises(gate.Hold):gate.check_article('alpha',html,raw,{1})
    def test_cli_always_holds(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(gate.main(['--root',d]), 2)
    def test_missing_native_files_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(gate.Hold): gate.check_native(Path(d), snapshot(), 1)
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'target').write_bytes(b'hello');(root/'alias').symlink_to(root/'target')
            with self.assertRaises(gate.Hold):gate.read_pinned(root,{'path':'alias','git_blob':gate.git_blob(b'hello'),'bytes':5})
    def test_working_fixture_native_pair(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'content/articles';p.mkdir(parents=True)
            m=snapshot()
            html,raw,_=example(1,'a00')
            (p/'a00.body.html').write_bytes(html)
            (p/'a00.meta.json').write_bytes(raw)
            result=gate.check_native(root,m,1)
            self.assertEqual(result['native_candidate_article_pairs_checked'],1)
            self.assertFalse(result['native_build_pass'])
            self.assertFalse(result['publication_authorized'])
    def test_authentic_lost_ways_track_accepted(self):
        html,_,meta=example()
        meta['track']='lost-ways'
        result=gate.check_article('alpha',html,json.dumps(meta).encode(),set())
        self.assertEqual(result['track'],'lost-ways')
    def test_authentic_historical_not_required_does_not_make_qd_pass(self):
        html,_,meta=example()
        meta['track']='lost-ways'
        meta['safety_review']['state']='not-required'
        result=gate.check_article('alpha',html,json.dumps(meta).encode(),set())
        self.assertEqual(result['authored_safety_state'],'not-required')
        self.assertFalse(result['qualified_qd_approval_verified'])
    def test_unscoped_founder_chat_approved_is_not_qd_pass(self):
        html,_,meta=example()
        meta['safety_review']['state']='approved'
        meta['safety_review']['reviewer']="Founder chat reply 'approved' (name unconfirmed; scope unconfirmed)"
        result=gate.check_article('alpha',html,json.dumps(meta).encode(),set())
        self.assertEqual(result['authored_safety_state'],'approved')
        self.assertFalse(result['qualified_qd_approval_verified'])
    def test_metadata_citation_body_no_silent_promotion(self):
        html,raw,meta=example()
        r=gate.check_article('alpha',html,raw,set())
        self.assertEqual(r['source_use_ids'],1)
        self.assertEqual(r['literal_citation_occurrences'],8)

# Every mutation must be rejected; parameterized dynamic tests count as distinct unittest cases.
mutations = {}
for k,v in [('schema','future'),('repository','unknown/repo'),('candidate_parent_sha','0'*40),
            ('release','PUBLISHED'),('permission','QD_PASS')]:
    mutations['manifest_'+k] = lambda m,k=k,v=v:m.__setitem__(k,v)
for k in snapshot()['review_state']:
    mutations['review_'+k] = lambda m,k=k:m['review_state'].__setitem__(k,True)
for k in snapshot()['commerce']:
    mutations['commerce_'+k] = lambda m,k=k:m['commerce'].__setitem__(k,'verified' if not k.endswith('sessions') else 1)
mutations['missing_record'] = lambda m:m.__setitem__('articles',[])
mutations['extra_record'] = lambda m:m['articles'].append(copy.deepcopy(m['articles'][0]))
mutations['unsafe_slug'] = lambda m:m['articles'][0].__setitem__('slug','../escape')
mutations['wrong_body_path'] = lambda m:m['articles'][0]['body'].__setitem__('path','content/articles/misroute.body.html')
mutations['wrong_meta_path'] = lambda m:m['articles'][0]['meta'].__setitem__('path','content/articles/misroute.meta.json')
mutations['wrong_sha'] = lambda m:m['articles'][0]['body'].__setitem__('git_blob','z'*40)
mutations['short_sha'] = lambda m:m['articles'][0]['body'].__setitem__('git_blob','a')
mutations['negative_bytes'] = lambda m:m['articles'][0]['body'].__setitem__('bytes',-1)
mutations['boolean_bytes'] = lambda m:m['articles'][0]['body'].__setitem__('bytes',True)
mutations['huge_bytes'] = lambda m:m['articles'][0]['body'].__setitem__('bytes',999999)
mutations['extra_key'] = lambda m:m.__setitem__('approved',True)
mutations['extra_row_key'] = lambda m:m['articles'][0].__setitem__('approved',True)
mutations['extra_pin_key'] = lambda m:m['articles'][0]['body'].__setitem__('approved',True)
for name, mutate in mutations.items():
    def test(self,mutate=mutate):
        m=snapshot(); mutate(m)
        with self.assertRaises(gate.Hold):gate.check_manifest(m,1)
    setattr(CandidateTests,'test_manifest_mutation_'+name,test)

metadata_mutations={}
for k,v in [('slug','someone-else'),('n',0),('n',36),('n',True),('title',''),('section',''),('track','unreviewed')]:
    metadata_mutations[f'{k}_{str(v)}']=lambda m,k=k,v=v:m.__setitem__(k,v)
metadata_mutations['publish_live']=lambda m:m['status'].__setitem__('publish','publish')
metadata_mutations['publish_approved']=lambda m:m['status'].__setitem__('publish','approved')
metadata_mutations['safety_pass']=lambda m:m['safety_review'].__setitem__('state','passed')
metadata_mutations['safety_reviewer']=lambda m:m['safety_review'].__setitem__('reviewer','model')
metadata_mutations['source_missing']=lambda m:m.__setitem__('source_use',{})
metadata_mutations['source_blank']=lambda m:m['source_use'].__setitem__('source-a','')
metadata_mutations['source_untrusted_id']=lambda m:m.__setitem__('source_use',{'Bad ID':'Reading'})
for name, mutate in metadata_mutations.items():
    def test(self,mutate=mutate):
        html,_,meta=example();mutate(meta);raw=json.dumps(meta).encode()
        with self.assertRaises(gate.Hold):gate.check_article('alpha',html,raw,set())
    setattr(CandidateTests,'test_metadata_mutation_'+name,test)

if __name__=='__main__':unittest.main()
