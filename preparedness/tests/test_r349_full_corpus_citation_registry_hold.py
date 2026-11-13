"""R349 read-only synthetic tests; no canonical source or CMS mutations."""
from __future__ import annotations
from copy import deepcopy
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import json
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'tools'/'r349_full_corpus_citation_registry_hold.py'
spec=spec_from_file_location('r349',SCRIPT)
r=module_from_spec(spec)
spec.loader.exec_module(r)


def source(sid='source-one'):
    return {'source_identity_sha256':r.hexhash(sid),
            'canonical_source_url':'https://example.org/'+sid,
            'verified_on':'2026-10-20','human_link_check':False}


def make(kind='articles',idx=0,sid='source-one'):
    slug=f'fake-{kind}-{idx:02}'
    return {'kind':kind,'slug':slug,
            'meta':{'slug':slug,'status':{'publish':'draft'},
                    'safety_review':{'state':'pending'},'track':'modern',
                    'source_use':{sid:'synthetic source-use declaration'}},
            'body':'<section><p>PRIVATE_CLAIM '+ '{{cite:'+sid+'}}'+'</p></section>'}


def slate():
    return [make('articles',i) for i in range(35)]+[make('tools',i) for i in range(6)]


class TestFullCorpus(unittest.TestCase):
    def setUp(self):
        self.docs=slate()
        self.catalog={'errors':[],'rows':{'source-one':source()}}
    def run_audit(self):
        return r.join_documents(self.docs,self.catalog)
    def test_41_held_documents(self):
        x=self.run_audit()
        self.assertEqual(x['documents_inspected'],41)
        self.assertEqual(x['occurrences_count'],41)
        self.assertEqual(x['status'],'DRAFT_CROSSWALK_ONLY_HARD_HOLD')
    def test_order_repeatability(self):
        a=self.run_audit();self.docs.reverse();b=self.run_audit()
        self.assertEqual(a,b)
    def test_no_private_claim_text(self):
        self.assertNotIn('PRIVATE_CLAIM',json.dumps(self.run_audit()))
    def test_no_raw_source_url(self):
        self.assertNotIn('https://example.org/',json.dumps(self.run_audit()))
    def test_false_gates_never_upgrade(self):
        for key in r.HOLD:self.assertIs(self.run_audit()[key],False)
    def test_exact_source_identity(self):
        self.assertEqual(self.run_audit()['all_citations'][0]['source_identity_sha256'],r.hexhash('source-one'))
    def test_duplicate_citation_has_distinct_ordinal(self):
        self.docs[0]['body']='<p>{{cite:source-one}} and {{cite:source-one}}</p>'
        x=self.run_audit()
        self.assertEqual(x['occurrences_count'],42)
        self.assertNotEqual(x['all_citations'][0]['occurrence_sha256'],x['all_citations'][1]['occurrence_sha256'])
    def test_declared_only_is_not_citation(self):
        self.docs[0]['meta']['source_use']['source-two']='not cited'
        self.catalog['rows']['source-two']=source('source-two')
        x=self.run_audit()
        self.assertEqual(x['occurrences_count'],41)
        self.assertEqual(len(x['declared_only_source_uses']),1)
    def test_source_collision_persists(self):
        self.catalog['errors'].append('VERIFIED_SOURCE_ID_MULTI_FRAGMENT_CONFLICT:source-one')
        self.assertEqual(self.run_audit()['status'],'INVALID_HARD_HOLD')
    def test_no_purchasable_offer_inference(self):
        self.docs[0]['meta']['commerce']={'sales':999999,'sku':'fake'}
        self.assertNotIn('999999',json.dumps(self.run_audit()))
        self.assertFalse(self.run_audit()['commerce_offer_verified'])
    def test_historical_not_required_is_not_qd(self):
        self.docs[0]['meta']['track']='lost-ways'
        self.docs[0]['meta']['safety_review']={'state':'not-required'}
        x=self.run_audit()
        self.assertEqual(x['errors'],[])
        self.assertFalse(x['qualified_qd_pass'])
    def test_disputed_source_quarantined(self):
        self.docs[0]=make(sid='fsis-power-failure')
        self.catalog['rows']['fsis-power-failure']=source('fsis-power-failure')
        x=self.run_audit()
        self.assertEqual(x['disputed_occurrences'],1)
        self.assertFalse(x['independent_claim_support_verified'])
    def test_cross_type_slug_collision(self):
        self.docs[-1]['slug']=self.docs[0]['slug']
        self.docs[-1]['meta']['slug']=self.docs[0]['slug']
        self.assertTrue(any('CROSS_TYPE_SLUG_COLLISION' in e for e in self.run_audit()['errors']))
    def test_duplicate_canonical_document_rejected(self):
        self.docs[-1]=deepcopy(self.docs[-2])
        self.assertTrue(any('DUPLICATE_CANONICAL_DOCUMENT_ID' in e for e in self.run_audit()['errors']))
    def test_no_native_checkout_hard_hold(self):
        with tempfile.TemporaryDirectory() as tmp:
            x=r.audit_native(Path(tmp))
            self.assertEqual(x['status'],'INVALID_HARD_HOLD')
            self.assertFalse(x['native_export_verified'])


class TestMutations(unittest.TestCase):
    pass


MUTATIONS={
 'publish_state':lambda d,c:d['meta']['status'].update({'publish':'publish'}),
 'publish_null':lambda d,c:d['meta'].update({'status':None}),
 'publish_missing':lambda d,c:d['meta'].pop('status'),
 'safety_approved':lambda d,c:d['meta']['safety_review'].update({'state':'approved'}),
 'safety_null':lambda d,c:d['meta'].update({'safety_review':None}),
 'safety_missing':lambda d,c:d['meta'].pop('safety_review'),
 'modern_not_required':lambda d,c:d['meta']['safety_review'].update({'state':'not-required'}),
 'slug_mismatch':lambda d,c:d['meta'].update({'slug':'other'}),
 'source_use_missing':lambda d,c:d['meta'].pop('source_use'),
 'source_use_null':lambda d,c:d['meta'].update({'source_use':None}),
 'source_use_list':lambda d,c:d['meta'].update({'source_use':[]}),
 'source_use_value_numeric':lambda d,c:d['meta'].update({'source_use':{'source-one':2}}),
 'source_use_id_numeric':lambda d,c:d['meta'].update({'source_use':{2:'bad'}}),
 'metadata_unregistered_source':lambda d,c:d['meta']['source_use'].update({'unknown-source':'none'}),
 'missing_registered_source':lambda d,c:c['rows'].pop('source-one'),
 'unverified_source':lambda d,c:c['rows']['source-one'].update({'verified_on':None}),
 'false_human_link_flag':lambda d,c:c['rows']['source-one'].update({'human_link_check':True}),
 'registry_conflict':lambda d,c:c['errors'].append('VERIFIED_SOURCE_ID_MULTI_FRAGMENT_CONFLICT:source-one'),
 'unknown_source_token':lambda d,c:d.update({'body':d['body'].replace('source-one','other-source')}),
 'malformed_cite_token':lambda d,c:d.update({'body':'<p>{{cite:source-one}</p>'}),
 'cite_in_comment':lambda d,c:d.update({'body':'<p>Text</p><!-- {{cite:source-one}} -->'}),
 'cite_in_attribute':lambda d,c:d.update({'body':'<p title="{{cite:source-one}}">Text</p>'}),
 'cite_in_url':lambda d,c:d.update({'body':'<a href="{{cite:source-one}}">Text</a>'}),
 'script_cite':lambda d,c:d.update({'body':'<script>{{cite:source-one}}</script>'}),
 'style_cite':lambda d,c:d.update({'body':'<style>{{cite:source-one}}</style>'}),
 'iframe':lambda d,c:d.update({'body':'<iframe></iframe>'+d['body']}),
 'active_form':lambda d,c:d.update({'body':'<form>'+d['body']+'</form>'}),
 'cite_outside_region':lambda d,c:d.update({'body':'<section>{{cite:source-one}}</section>'}),
 'cite_outside_html':lambda d,c:d.update({'body':'{{cite:source-one}}'}),
 'unexpected_end_tag':lambda d,c:d.update({'body':d['body']+'</li>'}),
 'unclosed_tag':lambda d,c:d.update({'body':'<p>'+d['body']}),
 'cite_uppercase':lambda d,c:d.update({'body':d['body'].replace('source-one','SOURCE-ONE')}),
 'cite_unicode':lambda d,c:d.update({'body':d['body'].replace('source-one','école')}),
 'cite_whitespace':lambda d,c:d.update({'body':d['body'].replace('source-one','source one')}),
 'cite_empty':lambda d,c:d.update({'body':d['body'].replace('source-one','')}),
 'split_cite':lambda d,c:d.update({'body':'<p>{{cite:<span>source-one</span>}}</p>'}),
 'body_null':lambda d,c:d.update({'body':None}),
 'meta_null':lambda d,c:d.update({'meta':None}),
 'injected_script':lambda d,c:d.update({'body':'<p>{{cite:source-one}}</p><script>0</script>'}),
 'broken_nesting':lambda d,c:d.update({'body':'<p><span>{{cite:source-one}}</p></span>'}),
}


for name,mutation in MUTATIONS.items():
    def case_fn(f):
        def test(self):
            d=make();c={'rows':{'source-one':source()},'errors':[]}
            f(d,c)
            x=r.join_documents([d],c,complete=False)
            self.assertEqual(x['status'],'INVALID_HARD_HOLD')
            self.assertTrue(x['errors'])
            self.assertFalse(x['may_publish'])
        return test
    setattr(TestMutations,'test_reject_'+name,case_fn(mutation))


class TestCorpusFiles(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.prep=Path(self.tmp.name)/'preparedness'
        for doc in slate():
            folder=self.prep/'content'/doc['kind']
            folder.mkdir(parents=True,exist_ok=True)
            (folder/(doc['slug']+'.body.html')).write_text(doc['body'])
            (folder/(doc['slug']+'.meta.json')).write_text(json.dumps(doc['meta']))
    def file(self,kind='articles',idx=0,suffix='.body.html'):
        return self.prep/'content'/kind/(f'fake-{kind}-{idx:02}'+suffix)
    def test_complete_readonly(self):
        docs,errors=r.read_documents(self.prep)
        self.assertEqual(len(docs),41)
        self.assertEqual(errors,[])
    def test_missing_body(self):
        self.file().unlink()
        self.assertTrue(r.read_documents(self.prep)[1])
    def test_missing_metadata(self):
        self.file(suffix='.meta.json').unlink()
        self.assertTrue(r.read_documents(self.prep)[1])
    def test_corrupt_json(self):
        self.file(suffix='.meta.json').write_text('{bad')
        self.assertTrue(r.read_documents(self.prep)[1])
    def test_symlinked_source(self):
        file=self.file();file.unlink();file.symlink_to('/etc/passwd')
        self.assertTrue(r.read_documents(self.prep)[1])
    def test_no_writes_to_manuscript(self):
        before=self.file().read_bytes()
        r.read_documents(self.prep)
        self.assertEqual(before,self.file().read_bytes())


if __name__=='__main__':
    unittest.main()
