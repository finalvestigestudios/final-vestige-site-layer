"""R200 exact-code offline synthetic regression tests, NOT content or safety approval."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PATH=Path(__file__).resolve().parents[1] / 'tools/r200_full_slate_custody.py'
spec=importlib.util.spec_from_file_location('r200_full_slate', PATH)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def bytes_json(d):return (json.dumps(d,ensure_ascii=False,sort_keys=True)+'\n').encode()

def scenario():
    slugs=['article-one','article-two','article-three']
    slate=[{'n':i,'slug':slug,'section':'start-here','track':'modern'} for i,slug in enumerate(slugs,1)]
    taxonomy_bytes=bytes_json({'slate':slate})
    blobs={};rows=[]
    for i,slug in enumerate(slugs,1):
        body=(f'<h1>{slug}</h1><p>This is a substantial educational historical document '
              + 'with source evidence {{cite:base-source}} and a clear reference to '
              + '{{link:' + slugs[i%3] + '|another topic}}.</p>').encode()
        meta=bytes_json({'n':i,'slug':slug,'section':'start-here','track':'modern',
                          'status':{'publish':'draft'},
                          'safety_review':{'state':'pending','reviewer':None,'date':None},
                          'source_use':{'base-source':'A real claim-support explanation.'}})
        bo,mo=gate.git_oid(body),gate.git_oid(meta)
        blobs[bo]=body;blobs[mo]=meta
        rows.append({'n':i,'slug':slug,'section':'start-here','track':'modern',
                     'route':f'/preparedness/start-here/{slug}/',
                     'source_cluster':'start','branch_sha':gate.HEADS['start'],
                     'body_oid':bo,'meta_oid':mo,'body_bytes':len(body),'meta_bytes':len(meta),
                     'also_in':['start']})
    manifest={'schema':gate.SCHEMA,'issue':136,'conversion_issue':820,'state':gate.HOLD,
              'publication_authorized':False,'independent_qd_pass':False,
              'human_source_approved':False,'medical_safety_verified':False,
              'merchant_offer_verified':False,'verified_paid_orders':None,
              'realized_net_revenue':None,'taxonomy_blob_sha1':gate.git_oid(taxonomy_bytes),
              'branch_heads':copy.deepcopy(gate.HEADS),'artifact_count':3,
              'export_target_count_with_six_tools':9,'articles':rows}
    return manifest,taxonomy_bytes,blobs

class Tests(unittest.TestCase):
    def setUp(self):
        self.manifest,self.taxonomy,self.blobs=scenario()
        self.old_taxonomy_sha=gate.TAXONOMY_SHA
        gate.TAXONOMY_SHA=gate.git_oid(self.taxonomy)
    def tearDown(self):gate.TAXONOMY_SHA=self.old_taxonomy_sha
    def result(self):return gate.check(self.manifest,self.taxonomy,self.blobs.__getitem__,strict=False)
    def deny(self):
        result=self.result()
        self.assertEqual(result['state'],gate.INVALID,result)
        self.assertEqual(result['articles'],[])
        self.assertFalse(result['publication_authorized'])
        self.assertTrue(result['errors'])
    def modify_meta(self,i,callback):
        row=self.manifest['articles'][i]
        d=json.loads(self.blobs[row['meta_oid']].decode())
        callback(d)
        raw=bytes_json(d);oid=gate.git_oid(raw)
        self.blobs[oid]=raw;row['meta_oid']=oid;row['meta_bytes']=len(raw)
    def modify_body(self,i,body):
        row=self.manifest['articles'][i]
        raw=body.encode();oid=gate.git_oid(raw)
        self.blobs[oid]=raw;row['body_oid']=oid;row['body_bytes']=len(raw)
    def test_positive_stays_hard_hold(self):
        r=self.result()
        self.assertEqual(r['state'],gate.HOLD,r)
        self.assertEqual(r['summary']['articles'],3)
        self.assertEqual(r['summary']['canonical_routes'],3)
        self.assertEqual(r['summary']['citations'],3)
        self.assertEqual(r['summary']['links'],3)
        self.assertFalse(r['independent_qd_pass'])
    def test_repeat_deterministic(self):
        self.assertEqual(self.result(),self.result())
    def test_full_slate_not_faked(self):
        self.assertEqual(gate.check(self.manifest,self.taxonomy,self.blobs.__getitem__)['state'],gate.INVALID)
    def test_manifest_git_object(self):
        self.assertEqual(gate.git_oid(b'test content\n'),'d670460b4b4aece5915caf5c68d12f560a9fe3e4')
    def test_unknown_blob_rejected(self):
        self.blobs.pop(self.manifest['articles'][0]['body_oid']);self.deny()
    def test_tampered_blob_rejected(self):
        k=self.manifest['articles'][0]['body_oid'];self.blobs[k]=b'nonsense';self.deny()
    def test_truncated_taxonomy_rejected(self):
        self.taxonomy=b'{}';self.deny()
    def test_reorder_rows_rejected(self):
        self.manifest['articles'].reverse();self.deny()
    def test_duplicate_article_rejected(self):
        self.manifest['articles'][1]=copy.deepcopy(self.manifest['articles'][0]);self.deny()
    def test_fake_manifest_approval_rejected(self):
        self.manifest['independent_qd_pass']=True;self.deny()
    def test_fake_merchant_rejected(self):
        self.manifest['merchant_offer_verified']=True;self.deny()
    def test_fake_sales_rejected(self):
        self.manifest['verified_paid_orders']=2;self.deny()
    def test_legacy_collision_needs_human(self):
        self.modify_meta(0,lambda m:m['source_use'].update({'nchfp-jerky':'A contested source explanation.'}))
        r=self.result();self.assertEqual(r['state'],gate.HOLD)
        self.assertEqual(r['review_required'],[{'source_id':'nchfp-jerky','article_count':1,'human_review':'PENDING'}])
    def test_blank_source_explanation_rejected(self):
        self.modify_meta(0,lambda m:m['source_use'].update({'base-source':' '}));self.deny()
    def test_metadata_publish_approved_rejected(self):
        self.modify_meta(0,lambda m:m['status'].update({'publish':'published'}));self.deny()
    def test_unapproved_safety_label_rejected(self):
        self.modify_meta(0,lambda m:m['safety_review'].update({'state':'QD_PASS'}));self.deny()
    def test_approved_author_metadata_not_independent_approval(self):
        self.modify_meta(0,lambda m:m['safety_review'].update({'state':'approved'}))
        r=self.result();self.assertEqual(r['state'],gate.HOLD)
        self.assertFalse(r['independent_qd_pass'])
    def test_duplicate_json_keys(self):
        with self.assertRaises(gate.CustodyError):gate.strict_json(b'{"a":1,"a":2}')
    def test_nan_json_rejected(self):
        with self.assertRaises(gate.CustodyError):gate.strict_json(b'{"a":NaN}')
    def test_malformed_citation_rejected(self):
        self.modify_body(0,'<p>abc {{cite:bad id}}</p>');self.deny()
    def test_unexplained_citation_rejected(self):
        self.modify_body(0,'<p>abc {{cite:unknown}}</p>');self.deny()
    def test_dangling_internal_link_rejected(self):
        self.modify_body(0,'<p>abc {{cite:base-source}} {{link:not-in-slate|x}}</p>');self.deny()
    def test_malformed_internal_link_rejected(self):
        self.modify_body(0,'<p>abc {{cite:base-source}} {{link:article-two}}</p>');self.deny()
    def test_zero_reading_depth_rejected(self):
        self.modify_body(0,'{{cite:base-source}} {{link:article-two|x}}');self.deny()
    def test_missing_slate_article_rejected(self):
        self.manifest['articles'].pop();self.deny()
    def test_missing_branch_head_rejected(self):
        del self.manifest['branch_heads']['hist-food'];self.deny()
    def test_wrong_count_rejected(self):
        self.manifest['export_target_count_with_six_tools']=1;self.deny()

# Twelve dangerous per-article custody mutations x three articles = 36 extra tests.
def mutation(i,kind):
    def test(self):
        r=self.manifest['articles'][i]
        if kind=='route':r['route']='/preparedness/other-route/'
        elif kind=='section':r['section']='lost-ways'
        elif kind=='track':r['track']='lost-ways'
        elif kind=='owner':r['source_cluster']='not-a-cluster'
        elif kind=='head':r['branch_sha']='0'*40
        elif kind=='body_oid':r['body_oid']='0'*40
        elif kind=='meta_oid':r['meta_oid']='0'*40
        elif kind=='body_size':r['body_bytes']+=1
        elif kind=='meta_size':r['meta_bytes']+=1
        elif kind=='also_empty':r['also_in']=[]
        elif kind=='also_duplicate':r['also_in']=['start','start']
        elif kind=='n':r['n']+=1
        else:raise AssertionError(kind)
        self.deny()
    return test
for i in range(3):
    for kind in ('route','section','track','owner','head','body_oid','meta_oid','body_size',
                 'meta_size','also_empty','also_duplicate','n'):
        setattr(Tests,f'test_mutation_{i}_{kind}',mutation(i,kind))

if __name__=='__main__':unittest.main()
