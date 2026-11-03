"""R92 adversarial review-only custody tests, synthetic and without network/filesystem writes."""
from __future__ import annotations
from copy import deepcopy
import csv
import importlib.util
import io
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('r92_synthetic_test',
 ROOT/'tools'/'r92_collision_claim_source_crosswalk.py')
r92=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r92)
URL='https://example.org/synthetic-preservation-record'


class FakeLibrary:
    def __init__(self):
        base={'id':'s','title':'Synthetic research 1','url':URL,
              'verified_on':'2026-10-01','supports':'Base summary only',
              'human_link_check':False}
        own={**base,'title':'Synthetic detailed research',
             'supports':'A longer independently authored reading'}
        self.source_variants={'s':[{**base,'_origin':'base'},
                                   {**own,'_origin':'start'}]}
        self.article_origins={'alpha':'start'}
        self.articles={'alpha':{'slug':'alpha','_body':'Synthetic words {{cite:s}}',
            'status':{'publish':'draft'},'kind':'article','section':'start-here'}}
        snapshots=[r92.source_row(x) for x in self.source_variants['s']]
        self.crosswalk={'groups':[{'url':URL,'variants':snapshots,
             'review_status':'pending-human-source-and-reading-scope-review'}],
             'raw_source_rows':2,'unique_source_urls':1,'duplicate_url_groups':1}
        self.crosswalk_groups={URL:self.crosswalk['groups'][0]}

    def source_for(self,meta,sid):
        return next(r for r in self.source_variants[sid]
                    if r['_origin']==self.article_origins[meta['slug']])

    def url_path(self,slug):
        return '/preparedness/start-here/'+slug+'/'


def sample():
    lib=FakeLibrary()
    row={'kind':'article','slug':'alpha','citation_ordinal':1,
         'literal_source_ID':'s','may_publish':False,
         'human_source_review':r92.REVIEW,'human_claim_support':r92.REVIEW,
         'qualified_safety_review':r92.REVIEW,'independent_QD_review':r92.REVIEW}
    parent={'schema':r92.PARENT_SCHEMA,'issue':136,'release_state':r92.HOLD,
         'may_publish':False,'medical_safety_approved':False,
         'human_source_approvals':0,'human_claim_approvals':0,
         'qualified_safety_approvals':0,'independent_QD_approvals':0,
         'complete_R90_original_evidence_UNABRIDGED_NOT_APPROVED':{},
         'all_literal_citation_claim_boundary_review_rows_NOT_APPROVED':[row],
         'counts':{'documents':1,'article':1,'tool':0,'citation_occurrences':1,
           'source_variant_edges':2,'complete_DOM_blocks':1,
           'distinct_source_variants':2,'unpaired_historical_reviews_preserved':0}}
    parent['sha256_seal']=r92.digest(parent)
    return lib,parent


class R92HappyPath(unittest.TestCase):
    def test_001_index_read_only(self):
        lib,p=sample(); a=deepcopy((lib.source_variants,lib.articles,lib.crosswalk,p))
        r92.index(lib,p); self.assertEqual(a,(lib.source_variants,lib.articles,lib.crosswalk,p))
    def test_002_deterministic_same_input(self):
        lib,p=sample(); self.assertEqual(r92.index(lib,p),r92.index(lib,p))
    def test_003_one_collision(self):
        lib,p=sample(); self.assertEqual(r92.index(lib,p)['counts']['shared_url_groups'],1)
    def test_004_two_source_records_preserved(self):
        lib,p=sample(); d=r92.index(lib,p)['all_literal_shared_URL_review_dossiers_NOT_APPROVED'][0]
        self.assertEqual(len(d['all_distinct_original_source_readings_UNABRIDGED_NOT_APPROVED']),2)
    def test_005_citation_linked_to_own_reading(self):
        lib,p=sample(); d=r92.index(lib,p)['all_literal_shared_URL_review_dossiers_NOT_APPROVED'][0]
        self.assertEqual(d['all_literal_release_candidate_citation_links_NOT_APPROVED'][0]['source_origin'],'start')
    def test_006_reading_scope_diff_cue(self):
        lib,p=sample(); d=r92.index(lib,p)['all_literal_shared_URL_review_dossiers_NOT_APPROVED'][0]
        self.assertIn('READING_SCOPE_STATEMENTS_DIFFER',d['review_risk_cues_NOT_VERDICTS'])
    def test_007_source_id_reuse_cue(self):
        lib,p=sample(); d=r92.index(lib,p)['all_literal_shared_URL_review_dossiers_NOT_APPROVED'][0]
        self.assertIn('REPEATED_ORIGIN_SPECIFIC_SOURCE_ID',d['review_risk_cues_NOT_VERDICTS'])
    def test_008_url_literal(self):
        lib,p=sample(); d=r92.index(lib,p)['all_literal_shared_URL_review_dossiers_NOT_APPROVED'][0]
        self.assertEqual(d['literal_url_UNMODIFIED'],URL)
    def test_009_no_approval_assertions(self):
        lib,p=sample(); report=r92.index(lib,p)
        self.assertFalse(report['may_publish']); self.assertEqual(report['qualified_safety_approvals'],0)
    def test_010_report_fingerprint(self):
        lib,p=sample(); r=r92.index(lib,p)
        self.assertEqual(r['sha256_seal'],r92.digest({k:v for k,v in r.items() if k!='sha256_seal'}))
    def test_011_verify_complete(self):
        lib,p=sample();r=r92.index(lib,p);r92.verify(r,lib,p)
    def test_012_csv_is_metadata_only(self):
        lib,p=sample();r=r92.index(lib,p)
        rows=list(csv.DictReader(io.StringIO(r92.private_csv(r,lib,p))))
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['may_publish'],'FALSE')
    def test_013_csv_has_no_source_reading(self):
        lib,p=sample();r=r92.index(lib,p)
        self.assertNotIn('Base summary only',r92.private_csv(r,lib,p))
    def test_014_strict_synthetic_census(self):
        lib,p=sample();r92.index(lib,p,expected={'documents':1,'shared_url_groups':1})
    def test_015_count_one_collision_citation(self):
        lib,p=sample();self.assertEqual(r92.index(lib,p)['counts']['shared_url_citation_occurrences'],1)
    def test_016_citation_original_ordinal(self):
        lib,p=sample();d=r92.index(lib,p)['all_literal_shared_URL_review_dossiers_NOT_APPROVED'][0]
        self.assertEqual(d['all_literal_release_candidate_citation_links_NOT_APPROVED'][0]['citation_ordinal'],1)
    def test_017_csv_injection_escape(self):
        self.assertEqual(r92.protect_csv('  =SUM(1,2)'),"'  =SUM(1,2)")
    def test_018_csv_safe_url(self):
        self.assertEqual(r92.protect_csv(URL),URL)
    def test_019_different_original_reading_hashes(self):
        lib,p=sample();d=r92.index(lib,p)['all_literal_shared_URL_review_dossiers_NOT_APPROVED'][0]
        self.assertEqual(len(set(d['distinct_source_record_SHA256'])),2)
    def test_020_no_human_source_claim(self):
        lib,p=sample();d=r92.index(lib,p)['all_literal_shared_URL_review_dossiers_NOT_APPROVED'][0]
        self.assertEqual(d['human_url_review'],r92.REVIEW)
    def test_021_parent_held_in_full(self):
        lib,p=sample();r=r92.index(lib,p)
        self.assertEqual(r['complete_R91_original_evidence_UNABRIDGED_NOT_APPROVED'],p)
    def test_022_verify_rejects_resealed_fabrication(self):
        lib,p=sample();r=r92.index(lib,p)
        r['all_literal_shared_URL_review_dossiers_NOT_APPROVED'][0]['source_ID_count']=99
        r['sha256_seal']=r92.digest({k:v for k,v in r.items() if k!='sha256_seal'})
        with self.assertRaises(r92.Gate):r92.verify(r,lib,p)
    def test_023_resolved_status_never_auto_approved(self):
        lib,p=sample();d=r92.index(lib,p)['all_literal_shared_URL_review_dossiers_NOT_APPROVED'][0]
        self.assertEqual(d['human_reading_scope_review'],r92.REVIEW)
    def test_024_report_rows_always_private(self):
        lib,p=sample();r=r92.index(lib,p)
        self.assertTrue(all(x['may_publish'] is False for x in r['all_literal_shared_URL_review_dossiers_NOT_APPROVED']))


# Each independently named test guards a concrete evidence-tampering mutation.
MUTATIONS={
    'parent_schema':lambda l,p:p.__setitem__('schema','untrusted'),
    'parent_issue':lambda l,p:p.__setitem__('issue',137),
    'parent_release':lambda l,p:p.__setitem__('release_state','READY'),
    'parent_may_publish':lambda l,p:p.__setitem__('may_publish',True),
    'parent_safety_approved':lambda l,p:p.__setitem__('medical_safety_approved',True),
    'parent_source_approval':lambda l,p:p.__setitem__('human_source_approvals',1),
    'parent_claim_approval':lambda l,p:p.__setitem__('human_claim_approvals',1),
    'parent_qualified_approval':lambda l,p:p.__setitem__('qualified_safety_approvals',1),
    'parent_qd_approval':lambda l,p:p.__setitem__('independent_QD_approvals',1),
    'parent_missing_ancestor':lambda l,p:p.pop('complete_R90_original_evidence_UNABRIDGED_NOT_APPROVED'),
    'parent_missing_rows':lambda l,p:p.pop('all_literal_citation_claim_boundary_review_rows_NOT_APPROVED'),
    'parent_citation_added':lambda l,p:p['all_literal_citation_claim_boundary_review_rows_NOT_APPROVED'].append(deepcopy(p['all_literal_citation_claim_boundary_review_rows_NOT_APPROVED'][0])),
    'parent_citation_removed':lambda l,p:p['all_literal_citation_claim_boundary_review_rows_NOT_APPROVED'].clear(),
    'parent_citation_id_changed':lambda l,p:p['all_literal_citation_claim_boundary_review_rows_NOT_APPROVED'][0].__setitem__('literal_source_ID','forged'),
    'parent_citation_review_fake':lambda l,p:p['all_literal_citation_claim_boundary_review_rows_NOT_APPROVED'][0].__setitem__('human_source_review','APPROVED'),
    'parent_citation_publish_fake':lambda l,p:p['all_literal_citation_claim_boundary_review_rows_NOT_APPROVED'][0].__setitem__('may_publish',True),
    'parent_citation_count':lambda l,p:p['counts'].__setitem__('citation_occurrences',2),
    'crosswalk_missing':lambda l,p:l.crosswalk.__setitem__('groups',[]),
    'crosswalk_count_tamper':lambda l,p:l.crosswalk.__setitem__('duplicate_url_groups',2),
    'crosswalk_raw_tamper':lambda l,p:l.crosswalk.__setitem__('raw_source_rows',3),
    'crosswalk_unique_tamper':lambda l,p:l.crosswalk.__setitem__('unique_source_urls',2),
    'crosswalk_forged_url':lambda l,p:l.crosswalk['groups'][0].__setitem__('url','https://example.org/other'),
    'crosswalk_approved_without_evidence':lambda l,p:l.crosswalk['groups'][0].__setitem__('review_status','resolved'),
    'crosswalk_source_missing':lambda l,p:l.crosswalk['groups'][0]['variants'].pop(),
    'crosswalk_reading_scope_forged':lambda l,p:l.crosswalk['groups'][0]['variants'][0]['source'].__setitem__('supports','Artificially expanded claim'),
    'crosswalk_source_origin_forged':lambda l,p:l.crosswalk['groups'][0]['variants'][0].__setitem__('origin','other'),
    'crosswalk_source_id_forged':lambda l,p:l.crosswalk['groups'][0]['variants'][0]['source'].__setitem__('id','new'),
    'source_variant_deleted':lambda l,p:l.source_variants['s'].pop(),
    'source_variant_id_drift':lambda l,p:l.source_variants['s'][0].__setitem__('id','not-s'),
    'source_variant_url_drift':lambda l,p:l.source_variants['s'][0].__setitem__('url','https://different.org'),
    'source_variant_origin_empty':lambda l,p:l.source_variants['s'][0].__setitem__('_origin',''),
    'source_variant_title_empty':lambda l,p:l.source_variants['s'][0].__setitem__('title',''),
    'source_variant_link_claim_approved':lambda l,p:l.source_variants['s'][0].__setitem__('human_link_check',True),
    'article_body_citation_drift':lambda l,p:l.articles['alpha'].__setitem__('_body','Synthetic words {{cite:not-s}}'),
    'article_body_extra_citation':lambda l,p:l.articles['alpha'].__setitem__('_body','Synthetic words {{cite:s}} {{cite:s}}'),
    'article_body_deleted_citation':lambda l,p:l.articles['alpha'].__setitem__('_body','Synthetic words'),
    'article_published_without_review':lambda l,p:l.articles['alpha']['status'].__setitem__('publish','published'),
    'article_slug_nontext':lambda l,p:l.articles['alpha'].__setitem__('_body',None),
    'article_origin_unrelated':lambda l,p:l.article_origins.__setitem__('alpha','unrelated'),
    'source_id_missing':lambda l,p:l.source_variants.__setitem__('s',[]),
    'source_row_fake_id':lambda l,p:l.source_variants['s'][1].__setitem__('id','other'),
    'source_row_non_https':lambda l,p:l.source_variants['s'][1].__setitem__('url','http://example.org/synthetic-preservation-record'),
}


def _test_mutation(name, fn):
    def testcase(self):
        lib,parent=sample()
        fn(lib,parent)
        with self.assertRaises((r92.Gate, KeyError, TypeError, StopIteration),msg=name):
            r92.index(lib,parent)
    testcase.__name__='test_adversarial_'+name
    return testcase


class R92Adversarial(unittest.TestCase):
    pass


for _name,_fn in MUTATIONS.items():
    setattr(R92Adversarial,'test_adversarial_'+_name,_test_mutation(_name,_fn))

if __name__=='__main__':
    unittest.main()
