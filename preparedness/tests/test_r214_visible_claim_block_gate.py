"""R214 synthetic tests (not original 35 authored article tests or qualified safety)."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import unittest

MODULE=Path(__file__).resolve().parents[1]/'tools'/'r214_visible_claim_block_gate.py'
spec=importlib.util.spec_from_file_location('r214',MODULE)
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

S7='cdc-find-clean-water'
S20='start-ready-plan'


def fixture(left='Fresh water is different from heating-system water and should be assessed carefully.',
            right='Unknown chemical or fuel pollution cannot be made safe by ordinary filtration.',
            separate='Planning should account for languages spoken in the household and communication preferences.'):
    b7=(f'<section><h2>Household water</h2><ol><li><strong>Check suitable sources.</strong> {left}'
        f'{{{{cite:{S7}}}}}</li><li><strong>Identify contaminants.</strong> {right}'
        f'{{{{cite:{S7}}}}}</li></ol></section>').encode('utf-8')
    b20=(f'<section><h2>Accessible planning</h2><p>{separate}'
         f'{{{{cite:{S20}}}}}</p></section>').encode('utf-8')
    claims=[]
    for article,body,source in ((7,b7,S7),(20,b20,S20)):
        start=0; occ=0
        while 1:
            index=body.find(('{{cite:'+source+'}}').encode(),start)
            if index<0:break
            occ+=1
            claims.append({'article':article,'citation_occurrence':occ,'source_id':source,
                           'source_url':'https://example.org/'+source,
                           'body_git_blob_sha1':r.blob_sha(body),
                           'source_start_byte':index,
                           'source_end_byte':index+len('{{cite:'+source+'}}'),
                           'receipt_sha256':hashlib.sha256(f'{article}-{occ}-{source}'.encode()).hexdigest()})
            start=index+1
    docket={'schema':'fv-preparedness-r213-held-claim-context-v1','state':r.HOLD,
            'claims':claims,'publication_authorized':False,'independent_qd_pass':False,
            'medically_safe':False,'review_complete':False}
    return docket,{7:b7,20:b20}

class TestR214(unittest.TestCase):
    def test_intact_held_not_approved(self):
        d,b=fixture();z=r.evaluate_from_docket(d,b)
        self.assertEqual(z['state'],r.HOLD,z)
        self.assertEqual([c['article'] for c in z['claims']],[7,7,20])
        for c in z['claims']:
            self.assertEqual(c['human_source_claim_review'],'REQUIRED')
            self.assertEqual(c['editorial_decision'],'PENDING')
            self.assertTrue(c['visible_claim_text'])
            self.assertNotIn('<li',c['visible_claim_text'])
            self.assertLess(c['claim_block_span_bytes'][0],c['citation_span_bytes'][0])
            self.assertGreater(c['claim_block_span_bytes'][1],c['citation_span_bytes'][1])
        for k in ('human_claim_verified','medical_safety_verified','independent_qd_pass','publication_authorized'):
            self.assertIs(z[k],False)
    def test_exact_blocks_not_ambiguous_window(self):
        d,b=fixture();z=r.evaluate_from_docket(d,b)
        self.assertEqual(z['state'],r.HOLD,z)
        self.assertIn('Fresh water',z['claims'][0]['visible_claim_text'])
        self.assertNotIn('Unknown chemical',z['claims'][0]['visible_claim_text'])
        self.assertIn('Unknown chemical',z['claims'][1]['visible_claim_text'])
        self.assertNotIn('Fresh water',z['claims'][1]['visible_claim_text'])
        self.assertIn('Planning should account',z['claims'][2]['visible_claim_text'])
    def test_determinism(self):
        d,b=fixture();self.assertEqual(r.evaluate_from_docket(d,b),r.evaluate_from_docket(d,b))
    def test_utf8_offsets_and_html_entities(self):
        d,b=fixture('One household — &amp; another one with language needs should plan appropriately.',
                    'Only safe sources are appropriate; take advice from local authorities.',
                    'Communications may involve Español &amp; ASL depending on needs.')
        z=r.evaluate_from_docket(d,b)
        self.assertEqual(z['state'],r.HOLD,z)
        self.assertIn('Español & ASL',z['claims'][2]['visible_claim_text'])
    def test_reject_unauthorized_docket_state(self):
        for key in ('publication_authorized','independent_qd_pass','medically_safe','review_complete'):
            with self.subTest(key=key):
                d,b=fixture();d[key]=True
                self.assertEqual(r.evaluate_from_docket(d,b)['state'],r.INVALID)
    def test_reject_missing_or_duplicate_receipts(self):
        for variation in ('missing','duplicate','corrupted','wrong_order'):
            with self.subTest(variation=variation):
                d,b=fixture()
                if variation=='missing':d['claims']=d['claims'][:2]
                if variation=='duplicate':d['claims'][1]['receipt_sha256']=d['claims'][0]['receipt_sha256']
                if variation=='corrupted':d['claims'][0]['receipt_sha256']='notsha'
                if variation=='wrong_order':d['claims'].reverse()
                self.assertEqual(r.evaluate_from_docket(d,b)['state'],r.INVALID)
    def test_reject_citation_in_html_comment(self):
        d,b=fixture();body=b[7].replace(b'<li><strong>Check',b'<!-- {{cite:cdc-find-clean-water}} --><li><strong>Check')
        d['claims'][0]['body_git_blob_sha1']=r.blob_sha(body)
        d['claims'][1]['body_git_blob_sha1']=r.blob_sha(body)
        # For a real changed body all exact spans would also need regenerating;
        # a fail-closed outcome is the only valid behavior here.
        self.assertEqual(r.evaluate_from_docket(d,{7:body,20:b[20]})['state'],r.INVALID)
    def test_reject_citation_inside_attribute(self):
        d,b=fixture();bad=b[7].replace(b'<li><strong>Check',b'<li data-note="{{cite:cdc-find-clean-water}}"><strong>Check')
        self.assertEqual(r.evaluate_from_docket(d,{7:bad,20:b[20]})['state'],r.INVALID)
    def test_reject_unclosed_claim_block(self):
        d,b=fixture();bad=b[20].replace(b'</p>',b'')
        self.assertEqual(r.evaluate_from_docket(d,{7:b[7],20:bad})['state'],r.INVALID)
    def test_reject_nonbyte_sources(self):
        d,b=fixture();b[20]=b[20].decode()
        self.assertEqual(r.evaluate_from_docket(d,b)['state'],r.INVALID)
    def test_reject_extra_articles(self):
        d,b=fixture();b[21]=b[7]
        self.assertEqual(r.evaluate_from_docket(d,b)['state'],r.INVALID)
    def test_reject_docket_without_schema(self):
        d,b=fixture();del d['schema'];self.assertEqual(r.evaluate_from_docket(d,b)['state'],r.INVALID)
    def test_reject_oversized_claim_block(self):
        d,b=fixture(left='a'*17000)
        self.assertEqual(r.evaluate_from_docket(d,b)['state'],r.INVALID)
    def test_35_individual_claim_edits_hard_fail(self):
        d,b=fixture()
        self.assertEqual(r.evaluate_from_docket(d,b)['state'],r.HOLD)
        for i in range(35):
            with self.subTest(i=i):
                body=bytearray(b[7]);position=b[7].index(b'Fresh water')+i
                body[position]=ord('X') if body[position]!=ord('X') else ord('Y')
                mutated=dict(b,**{})
                mutated[7]=bytes(body)
                out=r.evaluate_from_docket(d,mutated)
                self.assertEqual(out['state'],r.INVALID)
                self.assertTrue(any('source blob identity changed' in s for s in out['errors']),out)
    def test_35_individual_citation_span_mutations_hard_fail(self):
        d,b=fixture()
        self.assertEqual(r.evaluate_from_docket(d,b)['state'],r.HOLD)
        for i in range(35):
            with self.subTest(i=i):
                altered=copy.deepcopy(d)
                offset=-(i//2+1) if i%2 else (i//2+1)
                altered['claims'][0]['source_start_byte']+=offset
                altered['claims'][0]['source_end_byte']+=offset
                out=r.evaluate_from_docket(altered,b)
                self.assertEqual(out['state'],r.INVALID,out)

# Individually discoverable tests, not just subTest assertions (70 new methods).
def _edit_case(i):
    def test(self):
        d,b=fixture()
        self.assertEqual(r.evaluate_from_docket(d,b)['state'],r.HOLD)
        changed=bytearray(b[7]); p=b[7].index(b'Fresh water')+i
        changed[p] = ord('X') if changed[p] != ord('X') else ord('Y')
        bad=dict(b);bad[7]=bytes(changed)
        z=r.evaluate_from_docket(d,bad)
        self.assertEqual(z['state'],r.INVALID)
        self.assertIn('source blob identity changed',' '.join(z['errors']))
    return test

def _offset_case(i):
    def test(self):
        d,b=fixture()
        self.assertEqual(r.evaluate_from_docket(d,b)['state'],r.HOLD)
        altered=copy.deepcopy(d)
        offset=-(i//2+1) if i%2 else (i//2+1)
        altered['claims'][0]['source_start_byte']+=offset
        altered['claims'][0]['source_end_byte']+=offset
        self.assertEqual(r.evaluate_from_docket(altered,b)['state'],r.INVALID)
    return test

for _i in range(35):
    setattr(TestR214,f'test_individual_body_mutation_{_i:02d}',_edit_case(_i))
    setattr(TestR214,f'test_individual_citation_span_mutation_{_i:02d}',_offset_case(_i))

if __name__=='__main__':unittest.main()
