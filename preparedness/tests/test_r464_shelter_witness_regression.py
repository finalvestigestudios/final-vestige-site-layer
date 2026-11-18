"""R464 read-only Shelter candidate/origin mutation matrix; not clinical or QD approval."""
import importlib.util
from pathlib import Path
import unittest

path=Path(__file__).resolve().parents[1]/'tools/r464_shelter_witness_delta.py'
spec=importlib.util.spec_from_file_location('r464',path)
r=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
BASE=b'<h2>Household plan</h2><p>Never run a generator indoors {{cite:cdc}}.</p><p>Write family contacts {{cite:ready}}.</p><a href="https://example.org/official" rel="noopener">Official source</a>'
CAND=b'<h2>Household plan</h2><p>Never run a generator indoors {{cite:cdc}}.</p><p>Write family contacts on paper {{cite:ready}}.</p><a href="https://example.org/official" rel="noopener">Official source</a>'

def fixture():
    data={};pins={'schema':1,'state':r.HOLD,'qd_pass':False,'articles':{}}
    for slug in r.SLUGS:
        pins['articles'][slug]={}
        for kind in (*r.VARIANTS,'candidate'):
            raw=CAND if kind=='candidate' else BASE
            data[(slug,kind)]=raw
            pins['articles'][slug][kind]=r.git_blob(raw)
    return pins,data

def mutate(n, pins, data):
    slug=r.SLUGS[n%4];kind=(*r.VARIANTS,'candidate')[n%4]
    if n<4:pins['articles'].pop(slug)
    elif n<8:pins['articles'][slug].pop(kind)
    elif n<12:pins['articles'][slug]['other']='0'*40
    elif n<16:pins['articles'][slug][kind]='0'*40
    elif n<20:data.pop((slug,kind))
    elif n<24:data[(slug,kind)]=data[(slug,kind)]+b'<p>Fake evidence</p>'
    elif n<28:data[(slug,kind)]=data[(slug,kind)].replace(b'Never',b'Always')
    elif n<32:data[(slug,kind)]=data[(slug,kind)].replace(b'generator',b'heater')
    elif n<36:data[(slug,kind)]=data[(slug,kind)].replace(b'indoors',b'outside')
    elif n<40:data[(slug,kind)]=data[(slug,kind)].replace(b'{{cite:cdc}}',b'{{cite:fake}}')
    elif n<44:data[(slug,kind)]=data[(slug,kind)].replace(b'https://example.org/official',b'https://unsafe.example')
    elif n<48:data[(slug,kind)]=b'<p>Excerpt only</p>'

class NativeShape(unittest.TestCase):
    def test_all_twelve_are_review_only(self):
        pins, data=fixture();out=r.audit(pins,data)
        self.assertEqual(out['review_count'],12)
        self.assertEqual(out['release_state'],r.HOLD)
        self.assertFalse(out['qualified_qd_pass'])
        self.assertFalse(out['candidate_winner_selected'])
        self.assertFalse(out['may_publish'])
    def test_no_automatic_publication_when_same_bytes(self):
        out=r.difference(BASE,BASE,r.git_blob(BASE),r.git_blob(BASE),slug=r.SLUGS[0],variant='original')
        self.assertTrue(out['whole_body_identical'])
        self.assertTrue(out['review_required'])
        self.assertFalse(out['qualified_safety_approval'])
    def test_changed_text_with_same_citation_count(self):
        out=r.difference(BASE,CAND,r.git_blob(BASE),r.git_blob(CAND),slug=r.SLUGS[0],variant='original')
        self.assertFalse(out['block_sequence_identical'])
        self.assertTrue(out['citation_sequence_identical'])
        self.assertEqual(out['witness_citation_count'],out['candidate_citation_count'])
    def test_changed_url_with_same_visible_text(self):
        changed=BASE.replace(b'https://example.org/official',b'https://different.example')
        out=r.difference(BASE,changed,r.git_blob(BASE),r.git_blob(changed),slug=r.SLUGS[0],variant='original')
        self.assertTrue(out['visible_text_identical'])
        self.assertFalse(out['link_sequence_identical'])
    def test_hidden_warning_class_not_ignored(self):
        changed=BASE.replace(b'<p>Never',b'<p hidden>Never')
        out=r.difference(BASE,changed,r.git_blob(BASE),r.git_blob(changed),slug=r.SLUGS[0],variant='original')
        self.assertFalse(out['tag_attributes_identical'])
        self.assertTrue(out['block_sequence_identical'])
    def test_malformed_citation_hard_hold(self):
        with self.assertRaises(r.WitnessHold):r.parse_fragment(b'<p>{{cite:INVALID}}</p>')
    def test_unbalanced_safety_block_hard_hold(self):
        with self.assertRaises(r.WitnessHold):r.parse_fragment(b'<p>Warning')
    def test_duplicate_manifest_key_hard_hold(self):
        with self.assertRaises(r.WitnessHold):r.exact_json('{"state":"HOLD","state":"PASS"}')
    def test_unknown_branch_hard_hold(self):
        with self.assertRaises(r.WitnessHold):r.difference(BASE,BASE,r.git_blob(BASE),r.git_blob(BASE),slug=r.SLUGS[0],variant='winner')
    def test_unknown_article_hard_hold(self):
        with self.assertRaises(r.WitnessHold):r.difference(BASE,BASE,r.git_blob(BASE),r.git_blob(BASE),slug='fake',variant='original')
    def test_github_blob_hash_reference(self):
        self.assertEqual(r.git_blob(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')
    def test_synthetic_safety_not_merchant_verification(self):
        out=r.difference(BASE,CAND,r.git_blob(BASE),r.git_blob(CAND),slug=r.SLUGS[0],variant='followup')
        self.assertFalse(out['paid_offer_verified'])
        self.assertFalse(out['paid_revenue_verified'])

class TamperMatrix(unittest.TestCase):pass
for i in range(48):
    def make(index):
        def test(self):
            pins,data=fixture();mutate(index,pins,data)
            with self.assertRaises((r.WitnessHold,KeyError,ValueError,TypeError)):
                r.audit(pins,data)
        return test
    setattr(TamperMatrix,f'test_mismatch_{i:02d}',make(i))

class SubtleContentDrift(unittest.TestCase):pass
for i,(old,new) in enumerate([
        (b'Never',b'Always'),(b'generator',b'fuel'),(b'indoors',b'outdoors'),
        (b'{{cite:cdc}}',b'{{cite:ready}}'),(b'contacts',b'payments'),
        (b'href=',b'data-href='),(b'rel="noopener"',b'rel="ugc"'),
        (b'<p>Never',b'<p hidden>Never'),(b'Official source',b'Purchase now'),
        (b'paper',b'phone'),(b'Household plan',b'Safety approval'),
        (b'https://example.org/official',b'https://example.org/other')]):
    def make(a,b):
        def test(self):
            changed=CAND.replace(a,b)
            self.assertNotEqual(changed,CAND)
            out=r.difference(CAND,changed,r.git_blob(CAND),r.git_blob(changed),slug=r.SLUGS[0],variant='followup')
            self.assertFalse(out['whole_body_identical'])
            self.assertTrue(out['review_required'])
            self.assertFalse(out['may_publish'])
        return test
    setattr(SubtleContentDrift,f'test_drift_{i:02d}',make(old,new))

if __name__=='__main__':unittest.main()
