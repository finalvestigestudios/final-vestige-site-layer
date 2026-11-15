"""R385 source-to-claim impact and hard-hold regression tests (synthetic inputs)."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

P = Path(__file__).resolve().parents[1] / 'tools' / 'r385_source_claim_blast_radius.py'
spec = importlib.util.spec_from_file_location('r385', P)
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)
S1='claude/prep-start-bbfeb8'
S2='claude/prep-food-ccdc55'
COL = sorted(G.EXPECTED_COLLISIONS)
B='a'*40
M='b'*40
P64='1'*64


def packet():
    articles=[]
    for i in range(35):
        articles.append({'slug':f'article-{i:02d}', 'variants':[
          {'branch':S1, 'body_sha':B, 'meta_sha':M, 'safety_state':'pending',
           'source_use':{'scope-a':'This source supports the exact paragraph'},
           'blocks':[{'tag':'p','text':'Readable supporting evidence','prose_sha256':P64,
                      'full_sha256':'2'*64,'words':4,'citations':['scope-a']}], 'words':4}]})
    return {'status':'REVIEW_PACKET_HARD_HOLD', 'errors':[],
       'publication_approved':False, 'qualified_safety_approved':False,
       'articles':articles, 'unselected_conflicts':[{'path':f'fork-{i}'} for i in range(9)]}


def idx():
    d={'scope-a':[{'origin':S1,'evidence_hash':'2'*64,'link_human_checked':False}],
       'base-only':[{'origin':'BASE','evidence_hash':'3'*64,'link_human_checked':False}],
       'foreign-only':[{'origin':S2,'evidence_hash':'4'*64,'link_human_checked':False}]}
    for i,s in enumerate(COL):
        d[s]=[{'origin':S1,'evidence_hash':f'{i+1:x}'*64,'link_human_checked':False},
              {'origin':S2,'evidence_hash':f'{i+6:x}'*64,'link_human_checked':False}]
    return d


def inject(p, slug=0, citations=None, scope=None, branch=S1):
    v=p['articles'][slug]['variants'][0]
    v['branch']=branch
    if citations is not None:
        v['blocks'][0]['citations']=citations
    if scope is not None: v['source_use']=scope
    return v


def result(p=None, index=None, collision_ids=None, strict=True):
    return G.claim_impact(p or packet(), index or idx(), G.EXPECTED_COLLISIONS if collision_ids is None else collision_ids,
                          original_enforcement=strict)


class SourceImpactTests(unittest.TestCase):
    def test_default_review_only(self):
        r=result(); self.assertEqual(r['status'],'SOURCE_IMPACT_REVIEW_HARD_HOLD')
        self.assertFalse(r['publication_approved']); self.assertFalse(r['qualified_safety_approved'])
        self.assertFalse(r['live_release_allowed']); self.assertFalse(r['merchant_offer_verified'])
    def test_count_and_no_duplicate_article(self):
        r=result(); self.assertEqual(r['counts']['original_articles'],35)
        self.assertEqual(r['counts']['citation_occurrences'],35)
    def test_keep_all_nine_conflicts(self):
        self.assertEqual(len(packet()['unselected_conflicts']),9)
    def test_reject_missing_original_article(self):
        p=packet(); p['articles'].pop(); self.assertIn('ORIGINAL_ARTICLE_COUNT_INVALID',result(p)['errors'])
    def test_reject_missing_fork(self):
        p=packet(); p['unselected_conflicts'].pop(); self.assertIn('ORIGINAL_FORK_CUSTODY_INVALID',result(p)['errors'])
    def test_reject_status_approval(self):
        p=packet();p['publication_approved']=True
        self.assertIn('ORIGINAL_REVIEW_PACKET_INVALID',result(p)['errors'])
    def test_reject_no_citations(self):
        p=packet()
        for a in p['articles']:a['variants'][0]['blocks'][0]['citations']=[]
        self.assertIn('EMPTY_CITATION_LEDGER',result(p)['errors'])
    def test_crosswalk_order_deterministic(self):
        a=result();p=packet();p['articles'].reverse()
        b=result(p)
        self.assertEqual(a['claim_ledger_sha256'],b['claim_ledger_sha256'])
    def test_not_mutate_inputs(self):
        p=packet();index=idx(); saved=json.dumps([p,index],sort_keys=True)
        result(p,index)
        self.assertEqual(saved,json.dumps([p,index],sort_keys=True))
    def test_collision_impacts_correct_article(self):
        p=packet();inject(p,2,[COL[0]],{COL[0]:'Citation source applies to this statement'})
        r=result(p);row=next(x for x in r['source_collisions'] if x['source_id']==COL[0])
        self.assertEqual(row['impacted_articles'],['article-02'])
        self.assertEqual(row['impacted_citation_occurrences'],1)
        self.assertEqual(row['affected_original_bodies'],[B])
        self.assertTrue(row['qualified_review_required'])
    def test_collisions_no_auto_approved(self):
        p=packet();inject(p,2,[COL[0]],{COL[0]:'Recheck'})
        a=next(x for x in result(p)['claims'] if x['article']=='article-02')
        self.assertEqual(a['review_status'],'CONFLICTING_SOURCE_EVIDENCE')
        self.assertFalse(a['human_adjudicated'])
    def test_missing_source_id(self):
        p=packet();inject(p,1,['no-source'],{'no-source':'scope'})
        self.assertIn('UNRESOLVED_SOURCE_ID',[x['review_status'] for x in result(p)['claims']])
    def test_missing_scope(self):
        p=packet();inject(p,1,['scope-a'],{})
        self.assertIn('MISSING_ARTICLE_SCOPE',[x['review_status'] for x in result(p)['claims']])
    def test_blank_scope(self):
        p=packet();inject(p,1,['scope-a'],{'scope-a':'  '})
        self.assertIn('MISSING_ARTICLE_SCOPE',[x['review_status'] for x in result(p)['claims']])
    def test_base_fallback_not_approved(self):
        p=packet();inject(p,1,['base-only'],{'base-only':'source usage'})
        self.assertIn('BASE_FALLBACK_CUSTODY_ONLY',[x['review_status'] for x in result(p)['claims']])
    def test_other_branch_cannot_claim_own(self):
        p=packet();inject(p,1,['foreign-only'],{'foreign-only':'source usage'})
        self.assertIn('OTHER_BRANCH_SOURCE_UNVERIFIED',[x['review_status'] for x in result(p)['claims']])
    def test_own_branch_custody(self):
        self.assertEqual(result()['claims'][0]['review_status'],'OWN_BRANCH_OR_BASE_CUSTODY_ONLY')
    def test_repeated_citation_occurrences_preserved(self):
        p=packet();inject(p,1,['scope-a','scope-a'])
        a=[c for c in result(p)['claims'] if c['article']=='article-01']
        self.assertEqual([x['citation_ordinal'] for x in a],[1,2])
    def test_review_ledger_has_no_raw_article_prose(self):
        self.assertNotIn('Readable supporting evidence',json.dumps(result()))
    def test_claim_has_stable_provenance(self):
        c=result()['claims'][0];self.assertEqual(c['body_blob'],B)
        self.assertEqual(c['claim_sha256'],P64);self.assertEqual(c['source_use_sha256'],G.stable_sha('This source supports the exact paragraph'))
    def test_missing_collision_payload_fails_closed(self):
        ix=idx();ix[COL[0]]=ix[COL[0]][:1]
        self.assertIn('COLLISION_EVIDENCE_MISSING_OR_CONVERGED:'+COL[0],result(index=ix)['errors'])
    def test_identical_collision_payload_fails_closed(self):
        ix=idx();ix[COL[0]][1]['evidence_hash']=ix[COL[0]][0]['evidence_hash']
        self.assertIn('COLLISION_EVIDENCE_MISSING_OR_CONVERGED:'+COL[0],result(index=ix)['errors'])
    def test_distinct_variant_blobs_not_erased(self):
        p=packet();inject(p,1,[COL[0]],{COL[0]:'scope'})
        c=next(x for x in result(p)['source_collisions'] if x['source_id']==COL[0]);self.assertEqual(len(c['original_variant_hashes']),2)
    def test_same_source_multiple_articles(self):
        p=packet()
        for n in (1,3,7): inject(p,n,[COL[1]],{COL[1]:'scope'})
        c=next(x for x in result(p)['source_collisions'] if x['source_id']==COL[1]);self.assertEqual(len(c['impacted_articles']),3)
    def test_drifted_count_source_denominator(self):
        r=result();self.assertEqual(r['counts']['source_collision_groups'],5)
    def test_invalid_block_fingerprint(self):
        p=packet();p['articles'][0]['variants'][0]['blocks'][0]['prose_sha256']='bad'
        self.assertIn('BLOCK_FINGERPRINT_INVALID:article-00',result(p)['errors'])
    def test_reject_duplicate_variant(self):
        p=packet();p['articles'][0]['variants'].append(copy.deepcopy(p['articles'][0]['variants'][0]))
        self.assertIn('DUPLICATE_ARTICLE_VARIANT:article-00',result(p)['errors'])
    def test_reject_bad_provenance(self):
        p=packet();p['articles'][0]['variants'][0]['body_sha']='fake'
        self.assertIn('ARTICLE_PROVENANCE_INVALID:article-00',result(p)['errors'])
    def test_reject_invalid_source_use(self):
        p=packet();p['articles'][0]['variants'][0]['source_use']=[]
        self.assertIn('SOURCE_USE_NOT_DICT:article-00',result(p)['errors'])
    def test_reject_bad_citation(self):
        p=packet();inject(p,1,['Source With Space'])
        self.assertIn('INVALID_CITATION_ID:article-01',result(p)['errors'])
    def test_fail_closed_command(self):
        r=subprocess.run(['python','-I',str(P),'--repo','/no/repo'],capture_output=True,text=True)
        self.assertEqual(r.returncode,2);self.assertIn('INVALID_HARD_HOLD',r.stdout)
    def test_index_duplicate_base(self):
        src={'id':'test','url':'https://example.org'}
        rows,err=G.source_index({'source_id_variants':[]},{'sources':[src,src]},set())
        self.assertIn('DUPLICATE_BASE_ID:test',err)
    def test_index_invalid_base(self):
        self.assertIn('BASE_REGISTRY_INVALID',G.source_index({}, {},set())[1])
    def test_index_invalid_source_group(self):
        self.assertIn('SOURCE_GROUP_INVALID',G.source_index({'source_id_variants':[None]}, {'sources':[]},set())[1])
    def test_index_reject_crosswalk_absent(self):
        self.assertIn('SOURCE_CROSSWALK_INVALID',G.source_index({}, {'sources':[]},set())[1])
    def test_index_unique_sources(self):
        row={'id':'scope-a','url':'https://example.org','supports':'text','human_link_check':False}
        rows,err=G.source_index({'source_id_variants':[]},{'sources':[row]},set())
        self.assertFalse(err);self.assertEqual(rows['scope-a'][0]['origin'],'BASE')
    def test_index_bad_source_id(self):
        self.assertIn('MALFORMED_SOURCE_RECORD',G.source_index({'source_id_variants':[]},{'sources':[{'id':'bad id'}]},set())[1])
    def test_collision_group_without_variant(self):
        group={'id':'nchfp-home','variants':[]}
        self.assertIn('EMPTY_SOURCE_GROUP:nchfp-home',G.source_index({'source_id_variants':[group]},{'sources':[]},{S1})[1])
    def test_crosswalk_duplicate_id_group(self):
        a={'id':'foo','variants':[{'id':'foo','branch':S1,'fragment':'preparedness/sources/fragments/test.json','source_blob':B}]}
        self.assertIn('DUPLICATE_OR_INVALID_SOURCE_GROUP:foo',G.source_index({'source_id_variants':[a,a]},{'sources':[]},{S1})[1])
    def test_source_variant_mismatched_id(self):
        a={'id':'foo','variants':[{'id':'bar','branch':S1,'fragment':'preparedness/sources/fragments/a.json'}]}
        self.assertIn('SOURCE_VARIANT_ID_MISMATCH:foo',G.source_index({'source_id_variants':[a]},{'sources':[]},{S1})[1])
    def test_source_variant_bad_branch(self):
        a={'id':'foo','variants':[{'id':'foo','branch':'wrong','fragment':'preparedness/sources/fragments/a.json'}]}
        self.assertIn('SOURCE_VARIANT_ORIGIN_INVALID:foo',G.source_index({'source_id_variants':[a]},{'sources':[]},{S1})[1])
    def test_source_variant_bad_blob(self):
        a={'id':'foo','variants':[{'id':'foo','branch':S1,'fragment':'preparedness/sources/fragments/a.json','source_blob':'bad'}]}
        self.assertIn('SOURCE_BLOB_INVALID:foo',G.source_index({'source_id_variants':[a]},{'sources':[]},{S1})[1])
    def test_source_variant_dup_origin(self):
        v={'id':'foo','branch':S1,'fragment':'preparedness/sources/fragments/a.json','source_blob':B}
        a={'id':'foo','variants':[v,v]}
        self.assertIn('DUPLICATE_SOURCE_VARIANT_ORIGIN:foo',G.source_index({'source_id_variants':[a]},{'sources':[]},{S1})[1])
    def test_git_blob_sha(self):
        self.assertEqual(G.git_blob(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_stable_source_digests(self):
        self.assertEqual(G.stable_sha({'b':1,'a':2}), G.stable_sha({'a':2,'b':1}))
    def test_hash_of_scope_changes(self):
        self.assertNotEqual(G.stable_sha('claim A'),G.stable_sha('claim B'))


# Independent per-collision branches make missing coverage visible as five tests.
for ident in COL:
    def generated(self, source_id=ident):
        p=packet();inject(p,4,[source_id],{source_id:'Article-specific supporting claim'})
        out=result(p)
        impacted=next(c for c in out['source_collisions'] if c['source_id']==source_id)
        self.assertEqual(impacted['impacted_articles'],['article-04'])
        self.assertEqual(impacted['impacted_citation_occurrences'],1)
        self.assertFalse(out['publication_approved'])
    setattr(SourceImpactTests,'test_individual_collision_'+ident.replace('-','_'),generated)


if __name__=='__main__': unittest.main()
