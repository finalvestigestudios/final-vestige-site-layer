"""Deterministic synthetic regression: R448 never certifies emergency/commerce advice."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PATH=Path(__file__).resolve().parents[1]/'tools'/'r448_article_readiness_matrix.py'
spec=importlib.util.spec_from_file_location('r448',PATH)
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)


def fixtures():
    pins=[{'branch':f'claude/prep-{i}','sha':f'{i+10:040x}'} for i in range(9)]
    articles=[{'slug':f'original-article-{i}', 'body_candidate_git_blobs':[f'{500+i:040x}']} for i in range(35)]
    articles[0]['body_candidate_git_blobs']*=3  # authentic multiplicity is not lost
    articles[1]['slug']='family-communication-plan'
    articles[2]['slug']='home-fire-escape-plan'
    refs=[]
    for i in range(203):
        sid=f'source-{i}'
        if i==0:sid='start-ready-plan'
        if i==1:sid='shelter-ready-plan'
        url=(r.FAMILY_SOURCE_URL if i in (0,1) else f'https://example.gov/research/{i}')
        refs.append({'source_id':sid,'variants':[{'branch':pins[0]['branch'],
          'source_blob':f'{1000+i:040x}','url':url}]})
    # 203 IDs, 280 appearances, 181 distinct URLs, 17 shared-URL groups
    # 1 family URL group + 16 pairs + 6 triple groups + 1 quadruple group = 22 URL reductions.
    # Set IDs 2..18 share URLs of 19..35 (17 pairs in total including the family group).
    for i in range(2,18):
        refs[i]['variants'][0]['url']=refs[i+17]['variants'][0]['url']
    # another five reductions on existing shared URL groups, not new groups
    for i in range(36,41): refs[i]['variants'][0]['url']=refs[19+i-36]['variants'][0]['url']
    # 203-1-16-5=181 URLs, 17 shared groups
    for j in range(77):
        ix=41+(j%162)
        refs[ix]['variants'].append({'branch':pins[1]['branch'],
          'source_blob':f'{3000+j:040x}','url':refs[ix]['variants'][0]['url']})
    urls={}
    for ref in refs:
        for v in ref['variants']:
            urls.setdefault(v['url'],set()).add(ref['source_id'])
    groups=[{'url':u,'ids':sorted(ids),'review_required':True} for u,ids in sorted(urls.items()) if len(ids)>1]
    assert (len(urls),len(groups),sum(len(x['variants']) for x in refs))==(181,17,280)
    disputed=['fsis-power-failure','loc-pioneer-diaries','loc-prairie-traveler','nchfp-home','nchfp-jerky']
    for i,sid in enumerate(disputed):
        refs[45+i]['source_id']=sid
    disputes=[]
    for i,sid in enumerate(disputed):
        vv=copy.deepcopy(refs[45+i]['variants'])
        vv.append({'branch':pins[2]['branch'], 'source_blob':f'{5000+i:040x}',
                   'url':vv[0]['url']})
        # Preserve total source counts using exactly two occurrences: replace a retained
        # repeat in source 41+i by moving the variant into disputed source.
        rv=refs[41+i]['variants']
        if len(rv)>1: rv.pop()
        else: raise AssertionError('fixture expected repeated source')
        refs[45+i]['variants']=vv
        disputes.append({'source_id':sid,'decision':'HUMAN_REVIEW_REQUIRED',
                         'selected_record':None,'variants':[
            {**v, 'supports_exact':'specific original claim',
             'reading_scope_notes_exact':'read full source'} for v in vv]})
    # 203 + 77 original occurrences (moved five variants, total unchanged)
    forks=[]
    for i in range(9):
        slug=['family-communication-plan','family-communication-plan',
              'home-fire-escape-plan','home-fire-escape-plan',
              'original-article-3','original-article-3',
              'original-article-4','original-article-4'][i] if i<8 else None
        path=(f'preparedness/content/articles/{slug}.'+('body.html' if i%2==0 else 'meta.json')
              if slug else 'preparedness/sources/fragments/shelter.json')
        forks.append({'path':path,'decision':'HUMAN_REVIEW_REQUIRED','selected_sha':None,
          'requires_reading_depth_review':True,'requires_source_citation_review':True,
          'variants':[{'branch':pins[j]['branch'],'git_blob_sha':f'{6000+10*i+j:040x}',
                      'byte_length':10000+j*1000} for j in range(2)]})
    d={'repo':r.REPO,'issue':136,'parent_conversion_issue':820,'schema':1,
       'release_state':r.STATE,'publication_approved':False,'qualified_safety_approved':False,
       'automatic_variant_selection':False,'merchant_offer_verified':False,
       'branch_pins':pins,'original_articles':articles,
       'all_original_source_id_crosswalk':refs,'shared_exact_url_review_groups':groups,
       'source_evidence_disputes':disputes,'original_fork_disputes':forks}
    p={'repo':r.REPO,'issue':136,'business_coordination_issue':820,
       'schema':'R446_ORIGINAL_ADJUDICATION_REVIEW_ONLY_v1','release_state':r.STATE,
       'original_docket':{'path':'preparedness/reviews/r397_original_source_fork_docket.json',
          'commit':'a22c8797da58ecf186f50fcf47063bd195fd3c17','git_blob':r.ORIGINAL_GIT_BLOB},
       'qualified_review_approved':False,'publishable':False,'safety_approved':False,
       'merchant_offer_verified':False,'branch_pins':copy.deepcopy(pins),
       'article_identities':copy.deepcopy(articles),
       'source_scope_review':[{'source_id':x['source_id'],'source_variants':[
          {**v,'supports_exact':'specific original claim','reading_scope_notes_exact':'read full source'}
            for v in refs[45+i]['variants']],
          'original_decision':'HUMAN_REVIEW_REQUIRED','proposed_selection':None}
          for i,x in enumerate(disputes)],
       'manuscript_fork_review':[{'path':f['path'],'original_variants':copy.deepcopy(f['variants'])}
                                 for f in forks],
       'duplicate_exact_url_review':[{'url':g['url'],'source_ids':copy.deepcopy(g['ids']),
          'decision':'UNSELECTED','merge_authorized':False} for g in groups]}
    heads={x['branch']:x['sha'] for x in pins}
    return d,p,heads


def evaluate(d=None,p=None,h=None,mutate=None):
    original,packet,heads=fixtures()
    if d is not None:original=d
    if p is not None:packet=p
    if h is not None:heads=h
    if mutate: mutate(original,packet,heads)
    a=r.canonical(original).encode();b=r.canonical(packet).encode()
    pinned_orig,pinned_packet=r.ORIGINAL_GIT_BLOB,r.PACKET_GIT_BLOB
    try:
        r.ORIGINAL_GIT_BLOB=r.git_blob(a)
        r.PACKET_GIT_BLOB=r.git_blob(b)
        packet['original_docket']['git_blob']=r.ORIGINAL_GIT_BLOB
        return r.audit(original,a,packet,b,heads)
    finally:
        r.ORIGINAL_GIT_BLOB=pinned_orig
        r.PACKET_GIT_BLOB=pinned_packet


class ReadinessTests(unittest.TestCase):
    def test_synthetic_baseline(self):
        a=evaluate()
        self.assertTrue(a['structural_evidence_pass'],a['errors'])
        self.assertEqual(a['counts']['article_identities'],35)
        self.assertEqual(a['counts']['source_ids'],203)
        self.assertEqual(a['counts']['source_occurrences'],280)
        self.assertEqual(a['counts']['literal_source_urls'],181)
        self.assertEqual(a['counts']['shared_url_review_groups'],17)
        self.assertEqual(a['counts']['source_disputes'],5)
        self.assertEqual(a['counts']['original_forks'],9)
        self.assertEqual(a['counts']['source_fragment_forks'],1)
        self.assertEqual(a['counts']['contributor_pins'],9)
        self.assertEqual(a['release_state'],r.STATE)
        self.assertFalse(a['publication_allowed'])
        self.assertFalse(a['qd_pass'])
        self.assertFalse(a['verified_paid_offer'])
        self.assertEqual(len(a['article_matrix']),35)
        self.assertIsNone(a['campaign_research_only']['grok_published_asset_id'])
        self.assertIsNone(a['campaign_research_only']['paid_preparedness_sku'])
    def test_original_citations_unknown_no_assumptions(self):
        a=evaluate()
        self.assertTrue(all(not v['article_source_usage_verified'] for v in a['article_matrix']))
        self.assertTrue(all(v['live_url'] is None for v in a['article_matrix']))
    def test_duplicate_blob_appearances_preserved(self):
        a=evaluate();x=next(x for x in a['article_matrix'] if x['slug']=='original-article-0')
        self.assertEqual(x['body_candidate_appearances'],3)
        self.assertEqual(x['distinct_body_git_blobs'],1)
    def test_family_unselected_fork_research_link_only(self):
        a=evaluate();c=a['campaign_research_only']
        self.assertTrue(c['original_article_unselected'])
        self.assertEqual(c['free_external_source_url'],r.FAMILY_SOURCE_URL)
        self.assertIn('NOT a current HTTP',c['free_source_provenance'])
    def test_untrusted_incoming_original_never_passes(self):
        d,p,h=fixtures()
        a=r.audit(d,r.canonical(d).encode(),p,r.canonical(p).encode(),h)
        self.assertIn('AUTHENTIC_R397_BLOB_NOT_PROVEN',a['errors'])
    def test_untrusted_packet_never_passes(self):
        d,p,h=fixtures()
        a=r.audit(d,None,p,None,h)
        self.assertIn('AUTHENTIC_R446_PACKET_NOT_PROVEN',a['errors'])
    def test_refuses_outside_release_state(self):
        self.assertEqual(r.STATE,'DRAFT_HARD_HOLD')
    def test_duplicate_json_key_fail_closed(self):
        with self.assertRaises(ValueError):
            json.loads('{"a":1,"a":2}',object_pairs_hook=r.object_unique)
    def test_git_blob_is_content_sensitive(self):
        self.assertNotEqual(r.git_blob(b'abc'),r.git_blob(b'abd'))
    def test_fork_dependency_is_local_not_global_for_article(self):
        a=evaluate()
        family=next(x for x in a['article_matrix'] if x['slug']=='family-communication-plan')
        other=next(x for x in a['article_matrix'] if x['slug']=='water-math') if any(x['slug']=='water-math' for x in a['article_matrix']) else a['article_matrix'][-1]
        self.assertTrue(family['local_fork_paths'])
        self.assertFalse(other['local_fork_paths'])
    def test_no_checkout_or_merchants_claimed(self):
        x=evaluate()['campaign_research_only']
        self.assertFalse(x['verified_checkout'])
        self.assertFalse(x['verified_merchant_order'])
        self.assertIsNone(x['verified_net_revenue'])
        self.assertIsNone(x['net_revenue_per_1000_qualified_sessions'])


MUTATIONS=[
 ('original_repo',lambda d,p,h:d.__setitem__('repo','other/repo'),'ORIGINAL_DOCKET_IDENTITY_DRIFT'),
 ('original_issue',lambda d,p,h:d.__setitem__('issue',777),'ORIGINAL_DOCKET_IDENTITY_DRIFT'),
 ('original_parent_issue',lambda d,p,h:d.__setitem__('parent_conversion_issue',999),'ORIGINAL_DOCKET_IDENTITY_DRIFT'),
 ('original_schema',lambda d,p,h:d.__setitem__('schema',99),'ORIGINAL_DOCKET_IDENTITY_DRIFT'),
 ('packet_repo',lambda d,p,h:p.__setitem__('repo','other/repo'),'REVIEW_PACKET_IDENTITY_DRIFT'),
 ('packet_issue',lambda d,p,h:p.__setitem__('issue',999),'REVIEW_PACKET_IDENTITY_DRIFT'),
 ('packet_820',lambda d,p,h:p.__setitem__('business_coordination_issue',999),'REVIEW_PACKET_IDENTITY_DRIFT'),
 ('packet_schema',lambda d,p,h:p.__setitem__('schema','fake'),'REVIEW_PACKET_IDENTITY_DRIFT'),
 ('docket_live',lambda d,p,h:d.__setitem__('release_state','LIVE'),'UNSUPPORTED_APPROVAL_OR_RELEASE_STATE'),
 ('packet_pass',lambda d,p,h:p.__setitem__('release_state','PASS'),'UNSUPPORTED_APPROVAL_OR_RELEASE_STATE'),
 ('docket_qd',lambda d,p,h:d.__setitem__('qualified_safety_approved',True),'UNSUPPORTED_APPROVAL_OR_RELEASE_STATE'),
 ('packet_qd',lambda d,p,h:p.__setitem__('qualified_review_approved',True),'UNSUPPORTED_APPROVAL_OR_RELEASE_STATE'),
 ('docket_publish',lambda d,p,h:d.__setitem__('publication_approved',True),'UNSUPPORTED_APPROVAL_OR_RELEASE_STATE'),
 ('packet_publish',lambda d,p,h:p.__setitem__('publishable',True),'UNSUPPORTED_APPROVAL_OR_RELEASE_STATE'),
 ('packet_safety',lambda d,p,h:p.__setitem__('safety_approved',True),'UNSUPPORTED_APPROVAL_OR_RELEASE_STATE'),
 ('docket_merchant',lambda d,p,h:d.__setitem__('merchant_offer_verified',True),'UNSUPPORTED_APPROVAL_OR_RELEASE_STATE'),
 ('packet_merchant',lambda d,p,h:p.__setitem__('merchant_offer_verified',True),'UNSUPPORTED_APPROVAL_OR_RELEASE_STATE'),
 ('docket_auto_pick',lambda d,p,h:d.__setitem__('automatic_variant_selection',True),'UNSUPPORTED_APPROVAL_OR_RELEASE_STATE'),
 ('branch_missing',lambda d,p,h:h.pop('claude/prep-0'),'NINE_CURRENT_CONTRIBUTOR_HEADS_UNVERIFIED'),
 ('branch_divergent',lambda d,p,h:h.__setitem__('claude/prep-0','f'*40),'NINE_CURRENT_CONTRIBUTOR_HEADS_UNVERIFIED'),
 ('packet_branch_drift',lambda d,p,h:p['branch_pins'][0].__setitem__('sha','f'*40),'PACKET_CONTRIBUTOR_PINS_DRIFT'),
 ('source_id_loss',lambda d,p,h:d['all_original_source_id_crosswalk'].pop(),'ORIGINAL_INVENTORY_COUNT_DRIFT'),
 ('source_relabel',lambda d,p,h:d['all_original_source_id_crosswalk'][2].__setitem__('source_id','source-3'),'DUPLICATE_SOURCE_ID'),
 ('source_http',lambda d,p,h:d['all_original_source_id_crosswalk'][2]['variants'][0].__setitem__('url','http://bad.example'),'SOURCE_PROVENANCE_OR_HTTPS_DRIFT'),
 ('source_branch_unknown',lambda d,p,h:d['all_original_source_id_crosswalk'][2]['variants'][0].__setitem__('branch','other'),'SOURCE_PROVENANCE_OR_HTTPS_DRIFT'),
 ('source_blob_bad',lambda d,p,h:d['all_original_source_id_crosswalk'][2]['variants'][0].__setitem__('source_blob','g'*40),'SOURCE_PROVENANCE_OR_HTTPS_DRIFT'),
 ('source_untracked',lambda d,p,h:d['all_original_source_id_crosswalk'][2].__setitem__('variants',[]),'SOURCE_VARIANTS_MISSING'),
 ('url_group_merge',lambda d,p,h:p['duplicate_exact_url_review'][0].__setitem__('merge_authorized',True),'PACKET_SHARED_URL_GROUP_MERGE_OR_LOSS'),
 ('url_group_select',lambda d,p,h:p['duplicate_exact_url_review'][0].__setitem__('decision','MERGE'),'PACKET_SHARED_URL_GROUP_MERGE_OR_LOSS'),
 ('url_group_drop',lambda d,p,h:p['duplicate_exact_url_review'].pop(),'PACKET_INVENTORY_COUNT_DRIFT'),
 ('url_group_waiver',lambda d,p,h:d['shared_exact_url_review_groups'][0].__setitem__('review_required',False),'SHARED_URL_REVIEW_WAIVED'),
 ('url_group_url_replaced',lambda d,p,h:d['shared_exact_url_review_groups'][0].__setitem__('url','https://fake.example'),'EXACT_SHARED_URL_CROSSWALK_DRIFT'),
 ('article_drop',lambda d,p,h:d['original_articles'].pop(),'ORIGINAL_INVENTORY_COUNT_DRIFT'),
 ('article_collide',lambda d,p,h:d['original_articles'][1].__setitem__('slug','original-article-0'),'DUPLICATE_ARTICLE_SLUG'),
 ('article_blob_replace',lambda d,p,h:p['article_identities'][0]['body_candidate_git_blobs'].__setitem__(0,'f'*40),'ARTICLE_BLOB_MULTIPLICITY_OR_IDENTITY_DRIFT'),
 ('article_appearance_loss',lambda d,p,h:p['article_identities'][0]['body_candidate_git_blobs'].pop(),'ARTICLE_BLOB_MULTIPLICITY_OR_IDENTITY_DRIFT'),
 ('article_bad_sha',lambda d,p,h:d['original_articles'][0]['body_candidate_git_blobs'].__setitem__(0,'bad'),'ARTICLE_BODY_BLOBS_UNVERIFIED'),
 ('article_bad_slug',lambda d,p,h:d['original_articles'][0].__setitem__('slug','UPPER'),'INVALID_ARTICLE_IDENTITY'),
 ('fork_removed',lambda d,p,h:d['original_fork_disputes'].pop(),'ORIGINAL_INVENTORY_COUNT_DRIFT'),
 ('fork_preselected',lambda d,p,h:d['original_fork_disputes'][0].__setitem__('selected_sha','f'*40),'FORK_REVIEW_PRESELECTED_OR_DEPTH_LOST'),
 ('fork_depth_lost',lambda d,p,h:d['original_fork_disputes'][0].__setitem__('requires_reading_depth_review',False),'FORK_REVIEW_PRESELECTED_OR_DEPTH_LOST'),
 ('fork_citations_lost',lambda d,p,h:d['original_fork_disputes'][0].__setitem__('requires_source_citation_review',False),'FORK_REVIEW_PRESELECTED_OR_DEPTH_LOST'),
 ('fork_path_replaced',lambda d,p,h:p['manuscript_fork_review'][0].__setitem__('path','preparedness/fake'),'NINE_ORIGINAL_FORK_IDENTITIES_DRIFT'),
 ('fork_variant_replaced',lambda d,p,h:p['manuscript_fork_review'][0]['original_variants'][0].__setitem__('byte_length',777),'FORK_VARIANT_READING_DEPTH_EVIDENCE_DRIFT'),
 ('source_dispute_removed',lambda d,p,h:d['source_evidence_disputes'].pop(),'ORIGINAL_INVENTORY_COUNT_DRIFT'),
 ('source_preselected',lambda d,p,h:d['source_evidence_disputes'][0].__setitem__('selected_record','fake'),'SOURCE_DISPUTE_MISSING_OR_SELECTED'),
 ('packet_source_preselected',lambda d,p,h:p['source_scope_review'][0].__setitem__('proposed_selection','fake'),'SOURCE_PACKET_PRESELECTED'),
 ('source_scope_erased',lambda d,p,h:p['source_scope_review'][0]['source_variants'][0].__setitem__('reading_scope_notes_exact',''),'SOURCE_READING_SCOPE_LOST'),
 ('source_claim_changed',lambda d,p,h:p['source_scope_review'][0]['source_variants'][0].__setitem__('source_blob','f'*40),'SOURCE_VARIANT_CROSSWALK_DRIFT'),
 ('family_source_moved',lambda d,p,h:d['all_original_source_id_crosswalk'][0]['variants'][0].__setitem__('url','https://other.example/source'),'FAMILY_FREE_GUIDE_NOT_IN_ORIGINAL_CROSSWALK'),
]


def build_case(name, mutate, expected):
    def test(self):
        x=evaluate(mutate=mutate)
        self.assertIn(expected,x['errors'],name+':'+str(x['errors']))
        self.assertFalse(x['structural_evidence_pass'])
        self.assertEqual(x['release_state'],r.STATE)
        self.assertFalse(x['publication_allowed'])
        self.assertFalse(x['qd_pass'])
    return test

for name,func,error in MUTATIONS:
    setattr(ReadinessTests,'test_mutation_'+name,build_case(name,func,error))


if __name__=='__main__': unittest.main()
