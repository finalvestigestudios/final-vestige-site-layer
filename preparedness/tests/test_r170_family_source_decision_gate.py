"""R170 synthetic-only tests. PASS never means claim, medical or QD approval."""
from __future__ import annotations
import copy
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
import r170_family_source_decision_gate as g
D = json.loads((ROOT/'review/r170/source-decision-docket.json').read_text())


def base():
    d=copy.deepcopy(D)
    fragment={'sources':[{'id':row['id'],'url':row['original_url']} for row in d['decisions']]}
    meta={'slug':'family-reunification-card','status':{'publish':'draft'},
          'safety_review':{'state':'pending'},
          'source_use':{row['id']:'Original use requires scope review.' for row in d['decisions']}}
    ids=list(meta['source_use'])
    html='<section>'+' '.join('{{cite:'+x+'}}' for x in ids+ids[:5])+'</section>'
    return d,fragment,meta,html


class TestR170(unittest.TestCase):
    def test_baseline_is_explicit_hold(self):
        r=g.evaluate(*base())
        self.assertEqual(r['still_pending_qualified_human_decisions'],11)
        self.assertEqual(r['card_citation_occurrences'],16)
        self.assertFalse(r['claim_adjudication_complete'])
        self.assertFalse(r['source_links_human_verified'])
        self.assertFalse(r['publication_authorized'])
    def test_no_checkout_or_approval_result(self):
        out=json.dumps(g.evaluate(*base()))
        self.assertNotIn('VERIFIED',out)
        self.assertNotIn('PASS',out)
        self.assertIn('DRAFT_HARD_HOLD',out)
    def test_missing_checkout_is_explicit_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            with redirect_stdout(StringIO()) as buf:
                code=g.main(['--repo',tmp])
            self.assertEqual(code,2)
            self.assertEqual(json.loads(buf.getvalue())['state'],'INVALID_HARD_HOLD')
    def test_missing_json_docket_fails_authentic(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises((ImportError,ValueError,FileNotFoundError)):
                g.authentic(Path(tmp))
    def test_full_git_identity_protection(self):
        self.assertEqual(g.git_blob(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')
    def test_reject_untrusted_http(self):
        with self.assertRaises(ValueError):g.url('http://www.cdc.gov/path')
    def test_reject_untrusted_credentials(self):
        with self.assertRaises(ValueError):g.url('https://user:p@www.cdc.gov/path')
    def test_reject_untrusted_query(self):
        with self.assertRaises(ValueError):g.url('https://www.cdc.gov/path?dump=yes')
    def test_reject_untrusted_whitespace(self):
        with self.assertRaises(ValueError):g.url('https://www.cdc.gov/path\n')
    def test_reject_untrusted_backslash(self):
        with self.assertRaises(ValueError):g.url('https://www.cdc.gov\\@evil.test/path')
    def test_reject_untrusted_fragment(self):
        with self.assertRaises(ValueError):g.url('https://www.cdc.gov/path#anchor')
    def test_reject_untrusted_scheme(self):
        with self.assertRaises(ValueError):g.url('javascript:alert(1)')
    def test_duplicate_registry_id_rejected(self):
        d,f,m,h=base();f['sources'].append(f['sources'][0]);
        with self.assertRaisesRegex(ValueError,'duplicate ID'):g.evaluate(d,f,m,h)
    def test_citation_replacement_rejected(self):
        d,f,m,h=base();h=h.replace('{{cite:shelter-fcc-comms}}','{{cite:not-real}}',1)
        with self.assertRaisesRegex(ValueError,'citation occurrence'):g.evaluate(d,f,m,h)
    def test_citation_drop_rejected(self):
        d,f,m,h=base();h=h.replace('{{cite:shelter-fcc-comms}}','',1)
        with self.assertRaisesRegex(ValueError,'citation occurrence'):g.evaluate(d,f,m,h)
    def test_nonstandard_citation_marker_rejected(self):
        d,f,m,h=base();h=h.replace('{{cite:shelter-fcc-comms}}','{{cite : shelter-fcc-comms}}',1)
        with self.assertRaisesRegex(ValueError,'citation occurrence'):g.evaluate(d,f,m,h)
    def test_duplicate_review_row_rejected(self):
        d,f,m,h=base();d['decisions'][0]=copy.deepcopy(d['decisions'][1]);
        with self.assertRaisesRegex(ValueError,'missing or duplicated'):g.evaluate(d,f,m,h)
    def test_missing_review_row_rejected(self):
        d,f,m,h=base();d['decisions'].pop()
        with self.assertRaisesRegex(ValueError,'11 source'):g.evaluate(d,f,m,h)
    def test_removed_original_use_rejected(self):
        d,f,m,h=base();m['source_use'].pop('shelter-ready-tech')
        with self.assertRaisesRegex(ValueError,'11 original'):g.evaluate(d,f,m,h)
    def test_extra_review_metadata_rejected(self):
        d,f,m,h=base();d['publisher_approved']=True
        with self.assertRaisesRegex(ValueError,'keys drift'):g.evaluate(d,f,m,h)


MODS = {
    'fake_qd_pass':lambda d,f,m,h:d.update(independent_qd_pass=True),
    'fake_publication':lambda d,f,m,h:d.update(publication_authorized=True),
    'fake_live_status':lambda d,f,m,h:d.update(state='LIVE'),
    'fake_date':lambda d,f,m,h:d.update(observed_on='2025-01-01'),
    'fake_scope':lambda d,f,m,h:d.update(scope='mind'),
    'fake_schema':lambda d,f,m,h:d.update(schema='other'),
    'fake_source_blob':lambda d,f,m,h:d.update(source_fragment_git_blob='f'*40),
    'fake_meta_blob':lambda d,f,m,h:d.update(card_meta_git_blob='f'*40),
    'fake_html_blob':lambda d,f,m,h:d.update(staged_html_git_blob='f'*40),
    'fake_meta_live':lambda d,f,m,h:m['status'].update(publish='publish'),
    'fake_safety_approved':lambda d,f,m,h:m['safety_review'].update(state='approved'),
    'fake_meta_slug':lambda d,f,m,h:m.update(slug='not-family'),
    'fake_meta_use':lambda d,f,m,h:m.update(source_use=[]),
    'fake_source_registry':lambda d,f,m,h:f.update(sources=None),
    'fake_source_link':lambda d,f,m,h:d['decisions'][0].update(original_url='https://example.org/replaced'),
    'fake_source_link_query':lambda d,f,m,h:d['decisions'][0].update(original_url=d['decisions'][0]['original_url']+'?tracking=x'),
    'fake_source_link_credentials':lambda d,f,m,h:d['decisions'][0].update(original_url='https://user:pass@www.fcc.gov/path'),
    'fake_source_link_type':lambda d,f,m,h:d['decisions'][0].update(original_url=True),
    'fake_unknown_source_id':lambda d,f,m,h:d['decisions'][0].update(id='unrecorded-source'),
    'fake_completed_review':lambda d,f,m,h:d['decisions'][0].update(review_state='APPROVED'),
    'fake_human_link_check':lambda d,f,m,h:d['decisions'][0].update(human_link_check=True),
    'fake_safety_review':lambda d,f,m,h:d['decisions'][0].update(qualified_safety_review=True),
    'fake_archived_source_approved':lambda d,f,m,h:next(x for x in d['decisions'] if x['id']=='shelter-fema-reunification').update(observation='CURRENT_PAGE_TEXT'),
    'fake_403_source_approved':lambda d,f,m,h:next(x for x in d['decisions'] if x['id']=='shelter-ready-tech').update(observation='CURRENT_PAGE_TEXT'),
    'fake_ncmec_scope_approved':lambda d,f,m,h:next(x for x in d['decisions'] if x['id']=='shelter-ncmec-hotline').update(observation='CURRENT_PAGE_TEXT'),
    'fake_colorado_universal':lambda d,f,m,h:next(x for x in d['decisions'] if x['id']=='shelter-co-oss-reunification').update(observation='CURRENT_PAGE_TEXT'),
    'fake_observation_category':lambda d,f,m,h:d['decisions'][0].update(observation='PASS'),
    'fake_observation_bool':lambda d,f,m,h:d['decisions'][0].update(observation=True),
    'fake_empty_scope':lambda d,f,m,h:d['decisions'][0].update(source_scope='ok'),
    'fake_premature_claim':lambda d,f,m,h:d['decisions'][0].update(source_scope='This is safe to publish for everyone.'),
    'fake_medical_approval':lambda d,f,m,h:d['decisions'][0].update(source_scope='This establishes medical approval.'),
    'fake_untrusted_alternative':lambda d,f,m,h:d['decisions'][0].update(alternative_current_page='https://notofficial.example/new'),
    'fake_alt_http':lambda d,f,m,h:d['decisions'][0].update(alternative_current_page='http://www.missingkids.org/contact'),
    'fake_alt_bool':lambda d,f,m,h:d['decisions'][0].update(alternative_current_page=True),
    'fake_extra_row_key':lambda d,f,m,h:d['decisions'][0].update(approved=True),
}

def mutation_test(name,mutator):
    def run(self):
        d,f,m,h=base();mutator(d,f,m,h)
        with self.assertRaises((ValueError,TypeError)):
            g.evaluate(d,f,m,h)
    run.__name__='test_reject_'+name
    return run

for name,mutator in MODS.items():
    setattr(TestR170,'test_reject_'+name,mutation_test(name,mutator))

# Each of the 11 source records must be immutable and pending, not just the first.
for j in range(11):
    def test_case(self, idx=j):
        d,f,m,h=base();d['decisions'][idx]['human_link_check']=True
        with self.assertRaisesRegex(ValueError,'unapproved reviewer'):g.evaluate(d,f,m,h)
    setattr(TestR170,f'test_each_source_{j+1:02d}_cannot_promote_link_check',test_case)

if __name__=='__main__':unittest.main()
