"""R307 isolated regression tests; never write to actual Preparedness sources."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[2]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod
r305=load('r307_fragment_scan',ROOT/'preparedness/tools/r305_html5_link_target_review_hold.py')
r307=load('r307_body_proofs',ROOT/'preparedness/tools/r307_frozen_normalization_proof_hold.py')

def predecessor():
    return {'state':'DRAFT_HARD_HOLD','errors':[],
        'integrated_file_blobs_verified':70,'body_changes':14,
        'metadata_changes':12,'both_changed':9,'line_endings_only_observed':4,
        'publication_authorized':False,'independent_qd_pass':False,
        'medical_safety_verified':False,'privacy_verified':False,
        'paid_offer_approved':False,'all_41_native_exports_verified':False}

class ProvenanceControls(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        src=self.root/'preparedness/content/articles';src.mkdir(parents=True)
        self.proofs={};self.rows=[];self.orig={}
        for i,slug in enumerate(r307.PROOFS,1):
            body=(f'<section>Document {i}: résumé, historical source.</section>\n'*5).encode('utf-8')
            old=body.replace(b'\n',b'\r\n')
            (src/(slug+'.body.html')).write_bytes(body)
            self.orig[slug]=body
            frozen=r307.git_blob(old);current=r307.git_blob(body)
            self.proofs[slug]=(frozen,current,hashlib.sha256(body).hexdigest(),len(body),5)
            self.rows.append({'slug':slug,'line_endings_only_observed':True,
                'review_state':'FORMAT_ONLY_OBSERVED_QA_PENDING',
                'frozen_body_blob':frozen,'integrated_body_blob':current})
        for i in range(31):
            self.rows.append({'slug':f'other-{i:02d}', 'line_endings_only_observed':False})
        self.ledger={'state':'DRAFT_HARD_HOLD','articles':self.rows,
            'publication_authorized':False,'independent_qd_pass':False,
            'medical_safety_verified':False,'privacy_verified':False,
            'paid_offer_approved':False,'all_41_native_exports_verified':False}
        self.prior=predecessor()

    def result(self):return r307.audit(self.root,self.ledger,self.prior,self.proofs)
    def invalid(self,part=None):
        r=self.result()
        self.assertEqual(r['state'],'INVALID_HARD_HOLD')
        self.assertFalse(r['publication_authorized'])
        self.assertFalse(r['independent_qd_pass'])
        self.assertIsNone(r['confirmed_paid_orders'])
        if part:self.assertTrue(any(part in x for x in r['errors']),r['errors'])

    def test_valid_fixture_stays_draft_not_pass(self):
        r=self.result();self.assertEqual(r['errors'],[])
        self.assertEqual(r['state'],'DRAFT_HARD_HOLD')
        self.assertEqual(r['bound_format_proofs'],4)
        self.assertEqual(r['substantive_body_differences_unadjudicated'],10)
        self.assertEqual(r['metadata_differences_unadjudicated'],12)
        self.assertFalse(r['all_41_drafts_verified'])
    def test_no_real_data_writes(self):
        self.result()
        for slug,body in self.orig.items():
            self.assertEqual((self.root/'preparedness/content/articles'/f'{slug}.body.html').read_bytes(),body)
    def test_absent_native_repo_rejects(self):
        with TemporaryDirectory() as tmp:self.assertEqual(r307.main(['--repo-root',tmp]),1)
    def test_swapped_flags_still_four_rejected(self):
        self.rows[0]['line_endings_only_observed']=False
        self.rows[4]['line_endings_only_observed']=True
        self.invalid('FORMAT_ONLY_ATTESTATIONS_MOVED')
    def test_reassigned_slug_rejected(self):
        self.rows[0]['slug']='other-00'
        self.invalid('PROOF_ROW_NOT_UNIQUE')
    def test_fake_qd_ledger(self):
        self.ledger['independent_qd_pass']=True;self.invalid('LEDGER_FALSE_APPROVAL')
    def test_fake_safety_ledger(self):
        self.ledger['medical_safety_verified']=True;self.invalid('LEDGER_FALSE_APPROVAL')
    def test_fake_privacy_ledger(self):
        self.ledger['privacy_verified']=True;self.invalid('LEDGER_FALSE_APPROVAL')
    def test_fake_merchant_ledger(self):
        self.ledger['paid_offer_approved']=True;self.invalid('LEDGER_FALSE_APPROVAL')
    def test_fake_wp_ledger(self):
        self.ledger['all_41_native_exports_verified']=True;self.invalid('LEDGER_FALSE_APPROVAL')
    def test_fake_publish_ledger(self):
        self.ledger['publication_authorized']=True;self.invalid('LEDGER_FALSE_APPROVAL')
    def test_fake_qd_upstream(self):
        self.prior['independent_qd_pass']=True;self.invalid('R306_FALSE_RELEASE')
    def test_wrong_upstream_count(self):
        self.prior['metadata_changes']=11;self.invalid('R306_COUNT_UNVERIFIED')
    def test_upstream_errors(self):
        self.prior['errors']=['source missing'];self.invalid('R306_PREDECESSOR_UNVERIFIED')
    def test_missing_upstream(self):
        self.prior=None;self.invalid('R306_PREDECESSOR_UNVERIFIED')
    def test_missing_row(self):
        self.rows.pop();self.invalid('BAD_35_ARTICLE_LEDGER')
    def test_duplicate_slug(self):
        self.rows[5]=copy.deepcopy(self.rows[4]);self.invalid('SLUG_INVENTORY_DRIFT')
    def test_false_review_state(self):
        self.rows[0]['review_state']='QD_PASS';self.invalid('UNAPPROVED_FORMAT_STATUS')
    def test_missing_provenance_ledger(self):
        self.ledger=None;self.invalid('BAD_35_ARTICLE_LEDGER')

def mutated(slug,action):
    def test(self):
        row=next(r for r in self.rows if r.get('slug')==slug)
        p=self.root/'preparedness/content/articles'/f'{slug}.body.html'
        if action=='old_oid':
            row['frozen_body_blob']='0'*40;self.invalid('FROZEN_BLOB_REASSIGNED')
        elif action=='new_oid':
            row['integrated_body_blob']='f'*40;self.invalid('INTEGRATED_BLOB_REASSIGNED')
        elif action=='body_append':
            p.write_bytes(p.read_bytes()+b' risk changed');self.invalid('SOURCE_GIT_BLOB_CHANGED')
        elif action=='crlf':
            p.write_bytes(p.read_bytes().replace(b'\n',b'\r\n'));self.invalid('INTEGRATED_NOT_PURE_LF')
        elif action=='truncate':
            p.write_bytes(p.read_bytes()[:-1]);self.invalid('NORMALIZED_LENGTH_CHANGED')
        elif action=='delete':
            p.unlink();self.invalid('MISSING_OR_SYMLINK_BODY')
        elif action=='symlink':
            p.unlink();p.symlink_to(self.root/'preparedness/content/articles'/f'{next(iter(self.orig))}.body.html')
            self.invalid('MISSING_OR_SYMLINK_BODY')
        elif action=='digest':
            proof=list(self.proofs[slug]);proof[2]='0'*64;self.proofs[slug]=tuple(proof)
            self.invalid('FROZEN_NORMALIZED_PROOF_MISMATCH')
    return test

for slug in r307.PROOFS:
    for action in ('old_oid','new_oid','body_append','crlf','truncate','delete','symlink','digest'):
        setattr(ProvenanceControls,'test_'+slug.replace('-','_')+'_'+action,mutated(slug,action))

class FragmentControls(unittest.TestCase):
    def good(self,fragment,target):
        html=f'<a href="#{fragment}">Jump</a><h2 id="{target}">Plan</h2>'
        e,_=r305.scan(html,'export');self.assertEqual(e,[],e)
    def bad(self,fragment,code):
        e,_=r305.scan(f'<a href="#{fragment}">Jump</a>','export')
        self.assertTrue(any(code in x for x in e),e)
    def test_encoded_hyphen(self):self.good('family%2Dcontact','family-contact')
    def test_encoded_hyphen_lower(self):self.good('family%2dcontact','family-contact')
    def test_encoded_space(self):self.good('family%20contact','family contact')
    def test_encoded_unicode(self):self.good('caf%C3%A9','café')
    def test_literal_unicode(self):self.good('café','café')
    def test_entity_in_attribute(self):
        e,_=r305.scan('<a href="#a&amp;b">Jump</a><h2 id="a&amp;b">Plan</h2>','export')
        self.assertEqual(e,[])
    def test_encoded_hash(self):self.good('a%23b','a#b')
    def test_encoded_percent(self):self.good('a%25b','a%b')
    def test_encoded_id_not_url_decoded(self):self.bad('a%2Db','MISSING_SAME_DOCUMENT_TARGET')
    def test_real_missing_target(self):self.bad('missing%20contact','MISSING_SAME_DOCUMENT_TARGET')
    def test_bad_escape(self):self.bad('a%XZ','INVALID_PERCENT_ENCODED_FRAGMENT')
    def test_truncated_escape(self):self.bad('a%F','INVALID_PERCENT_ENCODED_FRAGMENT')
    def test_lonely_percent(self):self.bad('a%','INVALID_PERCENT_ENCODED_FRAGMENT')
    def test_invalid_utf8(self):self.bad('%C3%28','INVALID_UTF8_FRAGMENT')
    def test_encoded_null(self):self.bad('a%00b','UNSAFE_DECODED_FRAGMENT')
    def test_encoded_tab(self):self.bad('a%09b','UNSAFE_DECODED_FRAGMENT')
    def test_encoded_newline(self):self.bad('a%0Ab','UNSAFE_DECODED_FRAGMENT')
    def test_js_scheme_remains_blocked(self):
        self.assertEqual(r305.url_problem('javascript:x'),'UNAPPROVED_URL_SCHEME')
    def test_exact_case_required(self):
        e,_=r305.scan('<a href="#Plan">Jump</a><h2 id="plan">Plan</h2>','export')
        self.assertIn('MISSING_SAME_DOCUMENT_TARGET:Plan',e)

if __name__=='__main__':unittest.main()
