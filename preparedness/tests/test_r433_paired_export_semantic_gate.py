"""R433 synthetic-only parity and release HOLD adversarial regression tests."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOL = Path(__file__).resolve().parents[1]/'tools'/'r433_paired_export_semantic_gate.py'
spec=importlib.util.spec_from_file_location('r433_paired_export_semantic_gate',TOOL)
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

def html(body='Plan <b>the</b> route.', cite='official-a', link='/preparedness/start-here/', extra='', main='main'):
    return (f'<html><body><{main}><h1>Family plan</h1><p>{body} '
            f'<cite data-source-id="{cite}">Evidence</cite></p>'
            f'<p><a href="{link}">Start here</a></p>{extra}</{main}></body></html>').encode()

def fixture(n=35):
    manifest={'schema':1,'release_state':'DRAFT_HARD_HOLD','approved':False,'articles':[]}
    lock={'schema':1,'issue':136,'release_state':'DRAFT_HARD_HOLD','approved':False,'articles':[]}
    exports={}
    for i in range(n):
        slug=f'guide-{i:02d}';b=html()
        manifest['articles'].append({'slug':slug,'canonical_path':f'/preparedness/{slug}/','sources':['official-a']})
        lock['articles'].append({'slug':slug,'canonical_path':f'/preparedness/{slug}/', 'source_ids':['official-a'],
            'wordpress_sha256':hashlib.sha256(b).hexdigest(),'preview_sha256':hashlib.sha256(b).hexdigest()})
        exports[slug]=(b,b)
    return manifest,exports,lock

def mutate(m,e,l, channel='preview', payload=None, relock=True):
    slug=m['articles'][0]['slug'];wp,pr=e[slug]
    if channel=='wordpress':wp=payload
    else:pr=payload
    e[slug]=(wp,pr)
    if relock and isinstance(payload,bytes): l['articles'][0][channel+'_sha256']=hashlib.sha256(payload).hexdigest()

class TestR433(unittest.TestCase):
    def test_baseline_35_structural_only(self):
        m,e,l=fixture();x=r.audit(m,e,l)
        self.assertEqual(x['errors'],[]);self.assertTrue(x['structural_pair_parity'])
        self.assertEqual(len(x['review_rows']),35)
        self.assertFalse(x['eligible']);self.assertFalse(x['publication_approved']);self.assertFalse(x['qualified_safety_approved'])
        self.assertFalse(x['merchant_offer_verified']);self.assertIsNone(x['verified_paid_orders']);self.assertIsNone(x['net_revenue_per_1000_qualified_humans'])
        self.assertEqual(x['release_state'],'DRAFT_HARD_HOLD')
    def test_determinism(self):
        m,e,l=fixture(); a=r.audit(m,e,l);b=r.audit(m,e,l)
        self.assertEqual(a,b)
    def test_schema_contract(self):
        x=r.held(['MISSING'])
        self.assertEqual(x['native_build'],'NOT_RUN_BY_R433')
        self.assertEqual(x['export_authenticity'],'NOT_ESTABLISHED_BY_R433')
    def test_cli_fail_closed_no_files(self):
        with tempfile.TemporaryDirectory() as d:
            p=subprocess.run([sys.executable,'-I',str(TOOL),d+'/missing',d+'/missing2',d],capture_output=True,text=True)
            self.assertEqual(p.returncode,2)
            out=json.loads(p.stdout)
            self.assertEqual(out['release_state'],'DRAFT_HARD_HOLD')
            self.assertFalse(out['publication_approved'])
    def test_presentation_whitespace_only(self):
        m,e,l=fixture();mutate(m,e,l,payload=html(body='Plan    <b>the</b>\nroute.'))
        self.assertEqual(r.audit(m,e,l)['errors'],[])

    def test_citation_mismatch(self):
        m,e,l=fixture();mutate(m,e,l,payload=html(cite='different'))
        x=r.audit(m,e,l)
        self.assertTrue(any('CITATION' in t for t in x['errors']))
    def test_extra_article(self):
        m,e,l=fixture();e['extra']=(html(),html())
        self.assertIn('NOT_35_COMPLETE_EXPORT_PAIRS',r.audit(m,e,l)['errors'])
    def test_no_live_claim(self):
        m,e,l=fixture();m['approved']=True
        self.assertIn('FORGED_RELEASE_APPROVAL',r.audit(m,e,l)['errors'])


def make_case(name, transformation, fragment, channel='preview'):
    def test(self):
        m,e,l=fixture(); b=transformation(html())
        mutate(m,e,l,channel,payload=b)
        out=r.audit(m,e,l)
        self.assertFalse(out['publication_approved'])
        self.assertTrue(any(fragment in x for x in out['errors']), (name,out['errors']))
    test.__name__='test_adversarial_'+name
    return test

SCENARIOS=[
('missing_safety_sentence',lambda b:b.replace(b'Plan <b>the</b> route.',b'Plan route.'),'EDITORIAL_PASSAGE_PARITY'),
('extra_safety_sentence',lambda b:b.replace(b'Plan <b>the</b> route.',b'Plan <b>the</b> route. Extra advice.'),'EDITORIAL_PASSAGE_PARITY'),
('change_h1',lambda b:b.replace(b'Family plan',b'Other plan'),'EDITORIAL_PASSAGE_PARITY'),
('added_list',lambda b:b.replace(b'</main>',b'<ul><li>new step</li></ul></main>'),'EDITORIAL_PASSAGE_PARITY'),
('added_quote',lambda b:b.replace(b'</main>',b'<blockquote>Important note</blockquote></main>'),'EDITORIAL_PASSAGE_PARITY'),
('added_heading',lambda b:b.replace(b'</main>',b'<h2>Deep reading</h2></main>'),'EDITORIAL_PASSAGE_PARITY'),
('added_table',lambda b:b.replace(b'</main>',b'<table><tr><td>1 hour</td></tr></table></main>'),'EDITORIAL_PASSAGE_PARITY'),
('changed_link',lambda b:b.replace(b'/preparedness/start-here/',b'/preparedness/foo/'),'LINK_DESTINATION_PARITY'),
('changed_query',lambda b:b.replace(b'/preparedness/start-here/',b'/preparedness/start-here/?x=1'),'LINK_DESTINATION_PARITY'),
('changed_fragment',lambda b:b.replace(b'/preparedness/start-here/',b'/preparedness/start-here/#later'),'LINK_DESTINATION_PARITY'),
('hidden_notice',lambda b:b.replace(b'</main>',b'<p hidden>Warning text</p></main>'),'HIDDEN_MAIN_TEXT_REVIEW'),
('hidden_aria',lambda b:b.replace(b'</main>',b'<div aria-hidden="true"><p>Hidden warning</p></div></main>'),'HIDDEN_MAIN_TEXT_REVIEW'),
('hidden_display',lambda b:b.replace(b'</main>',b'<p style="display: none">Secret warning</p></main>'),'HIDDEN_MAIN_TEXT_REVIEW'),
('hidden_visibility',lambda b:b.replace(b'</main>',b'<p style="visibility:hidden">Secret warning</p></main>'),'HIDDEN_MAIN_TEXT_REVIEW'),
('removed_main',lambda b:b.replace(b'<main>',b'<div>').replace(b'</main>',b'</div>'),'MAIN_MISSING_OR_DUPLICATED'),
('two_mains',lambda b:b.replace(b'</main>',b'</main><main><p>extra</p></main>'),'MAIN_MISSING_OR_DUPLICATED'),
('form',lambda b:b.replace(b'</main>',b'<form action="/signup/"><input></form></main>'),'UNAPPROVED_FORM_IN_EXPORT'),
('javascript_link',lambda b:b.replace(b'/preparedness/start-here/',b'javascript:alert(1)'),'UNSAFE_LINK_SCHEME_OR_HOST'),
('data_link',lambda b:b.replace(b'/preparedness/start-here/',b'data:text/html,x'),'UNSAFE_LINK_SCHEME_OR_HOST'),
('mailto_link',lambda b:b.replace(b'/preparedness/start-here/',b'mailto:foo@bar.com'),'UNSAFE_LINK_SCHEME_OR_HOST'),
('ftp_link',lambda b:b.replace(b'/preparedness/start-here/',b'ftp://example.org/x'),'UNSAFE_LINK_SCHEME_OR_HOST'),
('protocol_relative_link',lambda b:b.replace(b'/preparedness/start-here/',b'//payhip.com/b/product'),'UNSAFE_LINK_SCHEME_OR_HOST'),
('http_link',lambda b:b.replace(b'/preparedness/start-here/',b'http://example.org/resource'),'NON_HTTPS_EDITORIAL_LINK'),
('payhip_link',lambda b:b.replace(b'/preparedness/start-here/',b'https://payhip.com/b/abc'),'UNAPPROVED_CHECKOUT_IN_REVIEW_EXPORT'),
('payhip_subdomain',lambda b:b.replace(b'/preparedness/start-here/',b'https://store.payhip.com/b/abc'),'UNAPPROVED_CHECKOUT_IN_REVIEW_EXPORT'),
('stripe_link',lambda b:b.replace(b'/preparedness/start-here/',b'https://buy.stripe.com/test'),'UNAPPROVED_CHECKOUT_IN_REVIEW_EXPORT'),
('stripe_checkout',lambda b:b.replace(b'/preparedness/start-here/',b'https://checkout.stripe.com/test'),'UNAPPROVED_CHECKOUT_IN_REVIEW_EXPORT'),
('paypal_link',lambda b:b.replace(b'/preparedness/start-here/',b'https://paypal.com/checkout'),'UNAPPROVED_CHECKOUT_IN_REVIEW_EXPORT'),
('userinfo_link',lambda b:b.replace(b'/preparedness/start-here/',b'https://user:pass@example.org/x'),'UNSAFE_LINK_SCHEME_OR_HOST'),
('broken_utf8',lambda b:b+b'\xff','PARSE_ERROR'),
('nul_byte',lambda b:b+b'\x00','PARSE_ERROR'),
('too_short',lambda b:b'X','PARSE_ERROR'),
('missing_source_marker',lambda b:b.replace(b'data-source-id="official-a"',b'data-x="official-a"'),'CITATION_COVERAGE_DRIFT'),
('malformed_source_marker',lambda b:b.replace(b'official-a',b'not a valid id'),'INVALID_CITATION_MARKER'),
('duplicate_source_marker',lambda b:b.replace(b'</main>',b'<cite data-source-id="official-a"></cite></main>'),'CITATION_ORDER_PARITY'),
('source_marker_reorder',lambda b:b.replace(b'data-source-id="official-a"',b'data-citation-id="official-a" data-source-id="official-b"'),'CITATION_ORDER_PARITY'),
('text_outside_p',lambda b:b.replace(b'<h1>Family plan</h1>',b'<h1>Family plan</h1><p>New content</p>'),'EDITORIAL_PASSAGE_PARITY'),
('css_hidden_span',lambda b:b.replace(b'</main>',b'<span hidden>Hidden phrase</span></main>'),'HIDDEN_MAIN_TEXT_REVIEW'),
('empty_href',lambda b:b.replace(b'href="/preparedness/start-here/"',b'href=""'),'EMPTY_OR_CONTROL_LINK'),
('missing_href',lambda b:b.replace(b'href="/preparedness/start-here/"',b''),'EMPTY_OR_CONTROL_LINK'),
('external_destination',lambda b:b.replace(b'/preparedness/start-here/',b'https://archive.example.org/'),'LINK_DESTINATION_PARITY'),
('source_body_loss_in_wp',lambda b:b.replace(b'Plan <b>the</b> route.',b''),'EDITORIAL_PASSAGE_PARITY','wordpress'),
('link_poison_in_wp',lambda b:b.replace(b'/preparedness/start-here/',b'https://payhip.com/b/payload'),'UNAPPROVED_CHECKOUT_IN_REVIEW_EXPORT','wordpress'),
('form_in_wp',lambda b:b.replace(b'</main>',b'<form></form></main>'),'UNAPPROVED_FORM_IN_EXPORT','wordpress'),
]
for name,change,error,*channel in SCENARIOS:
    setattr(TestR433,'test_adversarial_'+name,make_case(name,change,error,channel[0] if channel else 'preview'))

class TestR433Structure(unittest.TestCase):
    def test_article_duplicate_slug(self):
        m,e,l=fixture();m['articles'][1]['slug']=m['articles'][0]['slug']
        self.assertTrue(any('DUPLICATE' in a for a in r.audit(m,e,l)['errors']))
    def test_lock_duplicate_slug(self):
        m,e,l=fixture();l['articles'][1]['slug']=l['articles'][0]['slug']
        self.assertTrue(any('DUPLICATE' in a for a in r.audit(m,e,l)['errors']))
    def test_lock_bad_hash(self):
        m,e,l=fixture();l['articles'][0]['preview_sha256']='0'*64
        self.assertTrue(any('BYTE_LOCK' in a for a in r.audit(m,e,l)['errors']))
    def test_missing_export(self):
        m,e,l=fixture();del e['guide-00']
        self.assertIn('MISSING_OR_EXTRA_ARTICLE_IDENTITIES',r.audit(m,e,l)['errors'])
    def test_missing_source_manifest(self):
        m,e,l=fixture();m['articles'][0]['sources']=[];l['articles'][0]['source_ids']=[]
        self.assertTrue(any('INVALID_MANIFEST_SOURCE_IDS' in x for x in r.audit(m,e,l)['errors']))
    def test_not_35_full(self):
        m,e,l=fixture(2)
        self.assertIn('NOT_35_COMPLETE_EXPORT_PAIRS',r.audit(m,e,l)['errors'])
        self.assertFalse(r.audit(m,e,l)['structural_pair_parity'])
    def test_explicit_test_small(self):
        m,e,l=fixture(2)
        self.assertEqual(r.audit(m,e,l,test_only=True)['errors'],[])
        self.assertFalse(r.audit(m,e,l,test_only=True)['structural_pair_parity'])
    def test_forced_approval_in_lock(self):
        m,e,l=fixture();l['approved']=True
        self.assertIn('FORGED_RELEASE_APPROVAL',r.audit(m,e,l)['errors'])
    def test_invalid_root(self):
        self.assertIn('INVALID_EVIDENCE_OBJECT',r.audit([],{},{} )['errors'])
    def test_no_untrusted_export_shortcut(self):
        m,e,l=fixture();e['guide-00']=(b'',html())
        self.assertTrue(any('PARSE_ERROR' in x for x in r.audit(m,e,l)['errors']))

if __name__=='__main__':unittest.main()
