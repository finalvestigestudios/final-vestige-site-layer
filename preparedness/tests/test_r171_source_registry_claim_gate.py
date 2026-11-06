"""Synthetic adversarial evidence tests; never a QD/claim/medical safety PASS."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r171_source_registry_claim_gate as g


def sample():
    ss = {
      'base': [{'id':'base-a','url':'https://example.org/a','human_link_check':False},
               {'id':'base-shared','url':'https://example.org/shared','human_link_check':False}],
      'start':[{'id':'start-1','url':'https://example.org/shared','human_link_check':False}],
      'food':[{'id':'food-1','url':'https://example.org/food','human_link_check':False}],
      'shelter':[{'id':'shelter-1','url':'https://example.org/shelter','human_link_check':False}],
      'health':[{'id':'health-1','url':'https://example.org/health','human_link_check':False}],
      'hist-field':[{'id':'field-1','url':'https://example.org/field','human_link_check':False}],
      'hist-food':[{'id':'histfood-1','url':'https://example.org/histfood','human_link_check':False}],
      'hist-home':[{'id':'home-1','url':'https://example.org/home','human_link_check':False}]}
    inventory={f:{'sha':hashlib.sha1(f.encode()).hexdigest(),'sources':items} for f,items in ss.items()}
    entries=[{'origin':f,'path':g.SOURCES[f], 'git_blob_sha':inventory[f]['sha'],
              'count':len(ss[f])} for f in g.FRAGS]
    twins=[{'origin':f,'source_file':g.SOURCES[f],'row_index':i,'source':s}
           for f in g.FRAGS for i,s in enumerate(ss[f]) if s['url']=='https://example.org/shared']
    group={'url':'https://example.org/shared',
           'review_status':'pending-human-source-and-reading-scope-review',
           'reviewer':None,'reviewed_on':None,
           'canonical_url':'https://example.org/shared','variants':twins,
           'identities':[{'origin':r['origin'],'id':r['source']['id'],'row_index':r['row_index']}
                         for r in twins]}
    x={'schema_version':1,'status':'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
       'source_files':entries,'groups':[group], 'raw_source_rows':9,
       'unique_source_urls':8, 'duplicate_url_groups':1,'duplicate_id_groups':0}
    meta={
      'article-one':{'slug':'article-one','section':'start-here','status':{'publish':'draft'},
                     'source_use':{'base-a':'This original source supports the claim.',
                                   'start-1':'This other source contextualizes it.'}},
      'article-two':{'slug':'article-two','section':'lost-ways','status':{'publish':'draft'},
                     'source_use':{'food-1':'This original source supports this claim.'}}}
    legacy={'schema':'fv-preparedness-r151-v1','decision':'DRAFT_HARD_HOLD',
            'qd_pass':False,'qualified_safety_review':False,
            'branch_heads':{f:hashlib.sha1(f.encode()).hexdigest() for f in g.FRAGS if f!='base'},
            'metadata_blobs':{slug:'1'*40 for slug in meta}}
    custody={'schema':'fv-preparedness-r161-body-custody-v1', 'status':'DRAFT_HARD_HOLD',
             'articles':{k:{} for k in meta},'article_count':2,
             'article_source_relationships':3}
    return x,inventory,meta,legacy,custody


def assert_invalid(t, fn):
    data=list(sample())
    fn(data)
    with t.assertRaises((ValueError, TypeError, KeyError, AttributeError)):
        g.evaluate(*data,strict=False)


class TestR171(unittest.TestCase):
    def test_valid_synthetic_only_ends_in_hold(self):
        result=g.evaluate(*sample(),strict=False)
        self.assertEqual(result['state'],'DRAFT_HARD_HOLD')
        self.assertEqual(result['article_routes'],2)
        self.assertEqual(result['article_source_uses'],3)
        self.assertEqual(result['shared_url_groups_pending_human_review'],1)
        self.assertFalse(result['source_urls_independently_human_checked'])
        self.assertFalse(result['independent_qd_pass'])
        self.assertFalse(result['paid_product_verified'])
        self.assertFalse(result['publication_authorized'])
    def test_group_order_does_not_affect_identity(self):
        data=list(sample())
        data[0]['groups'][0]['variants'].reverse()
        data[0]['groups'][0]['identities'].reverse()
        result=g.evaluate(*data,strict=False)
        self.assertEqual(result['state'],'DRAFT_HARD_HOLD')
    def test_strict_baseline_rejects_fixture_counts(self):
        with self.assertRaises(ValueError):g.evaluate(*sample())
    def test_invalid_checkout_returns_exit_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            with redirect_stdout(StringIO()) as out:
                code=g.main(['--repo',tmp])
            self.assertEqual(code,2)
            report=json.loads(out.getvalue())
            self.assertEqual(report['state'],'INVALID_HARD_HOLD')
            self.assertFalse(report['publication_authorized'])
    def test_identity_linkage_receipt_is_deterministic(self):
        a=g.evaluate(*sample(),strict=False)
        b=g.evaluate(*sample(),strict=False)
        self.assertEqual(a['article_source_link_receipt_sha256'],b['article_source_link_receipt_sha256'])
    def test_missing_pinned_file_returns_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):g.verify(Path(tmp))
    def test_url_rejects_non_https_and_credentials(self):
        for url in ('http://foo.org','javascript:alert(1)','https://user:pass@foo.org',
                    'https://foo.org/#a','https://foo.org/hello world','https://foo..org'):
            with self.subTest(url=url),self.assertRaises(ValueError):g.valid_url(url)


def mutate_variants(group, name, value):
    group[name]=value


MUTANTS = {
    'schema_version_str':lambda d:d[0].__setitem__('schema_version','1'),
    'schema_version_zero':lambda d:d[0].__setitem__('schema_version',0),
    'schema_version_missing':lambda d:d[0].pop('schema_version'),
    'crosswalk_approved':lambda d:d[0].__setitem__('status','APPROVED'),
    'crosswalk_null':lambda d:d[0].__setitem__('status',None),
    'crosswalk_files_missing':lambda d:d[0].pop('source_files'),
    'crosswalk_files_empty':lambda d:d[0].__setitem__('source_files',[]),
    'crosswalk_duplicate_origin':lambda d:d[0]['source_files'][0].__setitem__('origin','start'),
    'crosswalk_file_renamed':lambda d:d[0]['source_files'][0].__setitem__('path','/etc/passwd'),
    'crosswalk_file_sha_bad':lambda d:d[0]['source_files'][0].__setitem__('git_blob_sha','foo'),
    'crosswalk_file_sha_drift':lambda d:d[0]['source_files'][0].__setitem__('git_blob_sha','f'*40),
    'crosswalk_file_count_bad':lambda d:d[0]['source_files'][0].__setitem__('count',0),
    'crosswalk_file_count_float':lambda d:d[0]['source_files'][0].__setitem__('count',2.0),
    'source_register_missing':lambda d:d[1].pop('start'),
    'source_register_bad_shape':lambda d:d[1].__setitem__('start',{'sha':'a'*40}),
    'source_register_count_drift':lambda d:d[1]['start']['sources'].append({'id':'extra','url':'https://example.org/extra','human_link_check':False}),
    'source_missing_id':lambda d:d[1]['food']['sources'][0].pop('id'),
    'source_missing_url':lambda d:d[1]['food']['sources'][0].pop('url'),
    'source_id_malformed':lambda d:d[1]['food']['sources'][0].__setitem__('id','unsafe id'),
    'source_non_https':lambda d:d[1]['food']['sources'][0].__setitem__('url','http://example.org/food'),
    'source_credentials':lambda d:d[1]['food']['sources'][0].__setitem__('url','https://u:p@example.org/food'),
    'source_js_url':lambda d:d[1]['food']['sources'][0].__setitem__('url','javascript:alert(1)'),
    'source_fake_human_approved':lambda d:d[1]['food']['sources'][0].__setitem__('human_link_check',True),
    'source_human_approved_null':lambda d:d[1]['food']['sources'][0].__setitem__('human_link_check',None),
    'source_conflicting_duplicate_id':lambda d:d[1]['start']['sources'][0].__setitem__('id','base-a'),
    'source_dupe_id_conflict_same_origin':lambda d:d[1]['base']['sources'][0].__setitem__('id','base-shared'),
    'group_missing':lambda d:d[0].__setitem__('groups',[]),
    'group_fabricated_approval':lambda d:d[0]['groups'][0].__setitem__('review_status','approved'),
    'group_reviewed_date_fabricated':lambda d:d[0]['groups'][0].__setitem__('reviewed_on','2026-11-06'),
    'group_reviewer_fabricated':lambda d:d[0]['groups'][0].__setitem__('reviewer','person'),
    'group_url_swapped':lambda d:d[0]['groups'][0].__setitem__('url','https://example.org/food'),
    'group_canonical_swapped':lambda d:d[0]['groups'][0].__setitem__('canonical_url','https://example.org/food'),
    'group_variant_removed':lambda d:d[0]['groups'][0]['variants'].pop(),
    'group_identity_removed':lambda d:d[0]['groups'][0]['identities'].pop(),
    'group_variant_source_swapped':lambda d:d[0]['groups'][0]['variants'][0]['source'].__setitem__('url','https://attacker.org'),
    'group_variant_origin_swapped':lambda d:d[0]['groups'][0]['variants'][0].__setitem__('origin','health'),
    'group_identity_bad_id':lambda d:d[0]['groups'][0]['identities'][0].__setitem__('id','wrong'),
    'group_id_double':lambda d:d[0]['groups'].append(copy.deepcopy(d[0]['groups'][0])),
    'group_census_bad':lambda d:d[0].__setitem__('duplicate_url_groups',2),
    'group_duplicate_id_census_bad':lambda d:d[0].__setitem__('duplicate_id_groups',1),
    'group_unique_urls_bad':lambda d:d[0].__setitem__('unique_source_urls',100),
    'group_rows_bad':lambda d:d[0].__setitem__('raw_source_rows',10),
    'meta_missing_article':lambda d:d[2].pop('article-one'),
    'meta_missing_sources':lambda d:d[2]['article-one'].pop('source_use'),
    'meta_missing_one_source_use':lambda d:d[2]['article-one']['source_use'].pop('base-a'),
    'meta_extra_orphan_source_id':lambda d:d[2]['article-one']['source_use'].__setitem__('invented-id','Explanation for missing source.'),
    'meta_empty_source_note':lambda d:d[2]['article-one']['source_use'].__setitem__('base-a',''),
    'meta_short_source_note':lambda d:d[2]['article-one']['source_use'].__setitem__('base-a','tiny'),
    'meta_slug_corrupt':lambda d:d[2]['article-one'].__setitem__('slug','article-two'),
    'meta_slug_invalid':lambda d:d[2]['article-one'].__setitem__('slug','article/one'),
    'meta_published':lambda d:d[2]['article-one']['status'].__setitem__('publish','publish'),
    'meta_route_duplicate':lambda d:d[2]['article-two'].__setitem__('slug','article-one'),
    'meta_section_missing':lambda d:d[2]['article-one'].pop('section'),
    'meta_section_bad':lambda d:d[2]['article-one'].__setitem__('section','/admin'),
    'legacy_schema_drift':lambda d:d[3].__setitem__('schema','made-up'),
    'legacy_decision_approved':lambda d:d[3].__setitem__('decision','APPROVED'),
    'legacy_qd_false_promotion':lambda d:d[3].__setitem__('qd_pass',True),
    'legacy_safety_false_promotion':lambda d:d[3].__setitem__('qualified_safety_review',True),
    'legacy_branch_missing':lambda d:d[3]['branch_heads'].pop('food'),
    'legacy_branch_unexpected':lambda d:d[3]['branch_heads'].__setitem__('extra','f'*40),
    'legacy_branch_invalid_sha':lambda d:d[3]['branch_heads'].__setitem__('food','xyz'),
    'legacy_meta_missing':lambda d:d[3]['metadata_blobs'].pop('article-one'),
    'custody_schema_drift':lambda d:d[4].__setitem__('schema','other'),
    'custody_state_approved':lambda d:d[4].__setitem__('status','APPROVED'),
    'custody_article_count_changed':lambda d:d[4].__setitem__('article_count',999),
    'custody_source_edges_changed':lambda d:d[4].__setitem__('article_source_relationships',2),
    'custody_article_missing':lambda d:d[4]['articles'].pop('article-one'),
}

def add_test(name,fn):
    def run(self):assert_invalid(self,fn)
    run.__name__='test_reject_'+name
    setattr(TestR171,run.__name__,run)

for name,fn in MUTANTS.items():add_test(name,fn)

if __name__=='__main__':unittest.main()
