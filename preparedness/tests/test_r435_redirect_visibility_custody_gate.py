"""R435 synthetics only; never evidence of original content safety or verified commerce."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import quote

TOOL=Path(__file__).resolve().parents[1]/'tools'/'r435_redirect_visibility_custody_gate.py'
spec=importlib.util.spec_from_file_location('r435_redirect_visibility_custody_gate',TOOL)
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

def html(slug='guide-00',other='',head='',middle='',url=None):
    url=url or f'https://finalvestige.com/preparedness/{slug}/'
    return (f'<html><head><title>Verified? No.</title><link rel="canonical" href="{url}">'
            f'<meta property="og:url" content="{url}">{head}</head>'
            f'<body>{other}<main><h1>Family plan</h1><p>Plan the route '
            f'<cite data-source-id="official-a">Source</cite></p>'
            f'<p><a href="/preparedness/start-here/">Start here</a></p>{middle}'
            f'</main></body></html>').encode()

def fixtures(n=35):
    manifest={'release_state':'DRAFT_HARD_HOLD','approved':False,'articles':[]}
    lock={'release_state':'DRAFT_HARD_HOLD','approved':False,'articles':[]}
    exports={}
    for i in range(n):
        slug=f'guide-{i:02d}';raw=html(slug)
        manifest['articles'].append({'slug':slug,'canonical_path':f'/preparedness/{slug}/','sources':['official-a']})
        lock['articles'].append({'slug':slug,'canonical_path':f'/preparedness/{slug}/','source_ids':['official-a'],
            'wordpress_sha256':hashlib.sha256(raw).hexdigest(),'preview_sha256':hashlib.sha256(raw).hexdigest()})
        exports[slug]=(raw,raw)
    return manifest,exports,lock

def alter(m,e,l,raw,channel='preview'):
    slug=m['articles'][0]['slug'];raw=raw if isinstance(raw,bytes) else raw.encode()
    pair=list(e[slug]);j=1 if channel=='preview' else 0;pair[j]=raw;e[slug]=tuple(pair)
    l['articles'][0][('preview_sha256' if j else 'wordpress_sha256')]=hashlib.sha256(raw).hexdigest()

class TestBaseline(unittest.TestCase):
    def test_35_synthetic_parity_only(self):
        m,e,l=fixtures();v=r.audit(m,e,l)
        self.assertEqual(v['errors'],[]);self.assertTrue(v['r435_complete_link_and_visibility_parity'])
        self.assertFalse(v['publication_approved']);self.assertFalse(v['qualified_safety_approved'])
        self.assertFalse(v['commercial_offer_verified']);self.assertIsNone(v['merchant_orders_verified'])
        self.assertIsNone(v['net_revenue_per_1000_qualified_humans'])
    def test_deterministic_review_digest(self):
        m,e,l=fixtures();self.assertEqual(r.audit(m,e,l),r.audit(m,e,l))
    def test_no_evidence_holds(self):self.assertTrue(r.audit(None,None,None)['errors'])
    def test_cli_missing_evidence_stays_hold(self):
        with tempfile.TemporaryDirectory() as d:
            p=subprocess.run([sys.executable,'-I',str(TOOL),d+'/missing',d+'/lock',d],capture_output=True,text=True)
        self.assertEqual(p.returncode,2);self.assertFalse(json.loads(p.stdout)['publication_approved'])
    def test_real_href_and_relative_allowed(self):
        self.assertEqual(r.inspect(html(other='<a href="https://www.ready.gov/plan">official</a>'))['errors'],[])
    def test_main_link_parity_integrates_parent(self):
        m,e,l=fixtures();alter(m,e,l,html(middle='<a href="/other">go</a>'))
        self.assertIn('FULL_DOCUMENT_ANCHOR_DESTINATION_DRIFT:guide-00',r.audit(m,e,l)['errors'])
    def test_outside_main_drift_parent_blindspot(self):
        m,e,l=fixtures();alter(m,e,l,html(other='<a href="https://example.org/away">Elsewhere</a>'))
        self.assertEqual(r.load_parent().audit(m,e,l)['errors'],[])
        self.assertIn('FULL_DOCUMENT_ANCHOR_DESTINATION_DRIFT:guide-00',r.audit(m,e,l)['errors'])
    def test_duplicate_href_parent_blindspot(self):
        raw=html(other='<a href="https://payhip.com/b/unsafe" href="/preparedness/start-here/">X</a>')
        self.assertEqual(r.load_parent().inspect(raw,'guide-00')['errors'],[])
        self.assertIn('DUPLICATE_HTML_ATTRIBUTE:a:href',r.inspect(raw)['errors'])
    def test_nested_redirect_parent_blindspot(self):
        raw=html(other='<a href="https://example.org/go?next=https%3A%2F%2Fpayhip.com%2Fb%2Fx">X</a>')
        self.assertEqual(r.load_parent().inspect(raw,'guide-00')['errors'],[])
        self.assertIn('NESTED_COMMERCE_DESTINATION',r.inspect(raw)['errors'])
    def test_style_hides_warning_parent_blindspot(self):
        raw=html(head='<style>.emergency-warning {display: none}</style>')
        self.assertEqual(r.load_parent().inspect(raw,'guide-00')['errors'],[])
        self.assertIn('STYLESHEET_OR_INLINE_HIDING_REVIEW',r.inspect(raw)['errors'])
    def test_noindex_is_review(self):
        self.assertIn('ROBOT_DIRECTIVE_REVIEW',r.inspect(html(head='<meta name="robots" content="noindex">'))['errors'])
    def test_missing_closing_structure_review(self):
        raw=html().replace(b'</body></html>',b'')
        self.assertIn('UNCLOSED_STRUCTURAL_HTML',r.inspect(raw)['errors'])
    def test_opaque_redirect_param(self):
        self.assertIn('OPAQUE_REDIRECT_PARAMETER_REVIEW',r.nested_destination_errors('https://example.org/go?next=token123'))
    def test_whitelisted_campaign_utm(self):
        self.assertEqual(r.nested_destination_errors('https://example.org/?utm_campaign=preparedness&utm_content=asset123'),[])
    def test_pair_order_independent(self):
        a=r.inspect(html(other='<a href="/a">a</a><a href="/b">b</a>'))
        b=r.inspect(html(other='<a href="/b">b</a><a href="/a">a</a>'))
        self.assertEqual(a['anchor_digest'],b['anchor_digest'])
    def test_pair_multiplicity_matters(self):
        a=r.inspect(html(other='<a href="/a">a</a>'))
        b=r.inspect(html(other='<a href="/a">a</a><a href="/a">a</a>'))
        self.assertNotEqual(a['anchor_digest'],b['anchor_digest'])
    def test_non_release_for_small_fixtures(self):
        m,e,l=fixtures(1);self.assertFalse(r.audit(m,e,l,test_only=True)['r435_complete_link_and_visibility_parity'])
    def test_reject_nul(self):
        with self.assertRaises(ValueError):r.inspect(html()+b'\0')
    def test_reject_oversize(self):
        with self.assertRaises(ValueError):r.inspect(b'x'*(r.MAX+1))
    def test_reject_bad_utf8(self):
        with self.assertRaises(UnicodeError):r.inspect(html()+b'\xff')
    def test_duplicate_slug(self):
        m,e,l=fixtures();m['articles'][1]['slug']=m['articles'][0]['slug']
        self.assertIn('DUPLICATE_ARTICLE_IDENTITY',r.audit(m,e,l)['errors'])
    def test_no_unapproved_sale_metrics(self):
        x=r.held([]);self.assertFalse(x['publication_approved']);self.assertIsNone(x['merchant_orders_verified'])

class TestNestedAndVisibility(unittest.TestCase):pass

def makecase(name,fragment,expected,location='other'):
    def check(self):
        raw=html(**{location:fragment})
        self.assertIn(expected,r.inspect(raw)['errors'],(name,r.inspect(raw)['errors']))
        m,e,l=fixtures();alter(m,e,l,raw)
        self.assertTrue(any(expected in x for x in r.audit(m,e,l)['errors']))
        self.assertFalse(r.audit(m,e,l)['eligible'])
    check.__name__='test_'+name
    return check

cases=[
 ('next_checkout','<a href="https://example.org/out?next=https%3A%2F%2Fpayhip.com%2Fb%2FX">go</a>','NESTED_COMMERCE_DESTINATION'),
 ('next_stripe','<a href="https://example.org/out?next=https%3A%2F%2Fbuy.stripe.com%2Fx">go</a>','NESTED_COMMERCE_DESTINATION'),
 ('next_paypal','<a href="https://example.org/out?next=https%3A%2F%2Fpaypal.com%2Fx">go</a>','NESTED_COMMERCE_DESTINATION'),
 ('next_gumroad','<a href="https://example.org/out?next=https%3A%2F%2Fgumroad.com%2Fl%2Fx">go</a>','NESTED_COMMERCE_DESTINATION'),
 ('next_external','<a href="https://example.org/out?next=https%3A%2F%2Fother.org%2Fx">go</a>','NESTED_DESTINATION_REVIEW'),
 ('return_encoded','<a href="https://example.org/out?return_url=https%3A%2F%2Fother.org%2Fx">go</a>','NESTED_DESTINATION_REVIEW'),
 ('redirect_raw','<a href="https://example.org/out?redirect=https://another.org/x">go</a>','NESTED_DESTINATION_REVIEW'),
 ('target_raw','<a href="https://example.org/out?target=https://another.org/x">go</a>','NESTED_DESTINATION_REVIEW'),
 ('destination_raw','<a href="https://example.org/out?destination=https://another.org/x">go</a>','NESTED_DESTINATION_REVIEW'),
 ('checkout_raw','<a href="https://example.org/out?checkout=https://another.org/x">go</a>','NESTED_DESTINATION_REVIEW'),
 ('deep_encoding','<a href="https://example.org/out?next=https%25253A%25252F%25252Fpayhip.com%25252Fb">go</a>','NESTED_COMMERCE_DESTINATION'),
 ('relative_redirect','<a href="https://example.org/out?next=%2Flanding">go</a>','NESTED_DESTINATION_REVIEW'),
 ('redirect_opaque','<a href="https://example.org/out?next=campaign-token">go</a>','OPAQUE_REDIRECT_PARAMETER_REVIEW'),
 ('redirect_blank_safe','<a href="https://example.org/out?next=">go</a>','DOES_NOT_APPLY'),
 ('data_unspecified','<div data-open-url="https://payhip.com/b/X">go</div>','UNCLASSIFIED_DYNAMIC_URL_ATTRIBUTE_REVIEW'),
 ('data_vendor','<div data-vendor-href="https://gumroad.com/l/x">go</div>','UNCLASSIFIED_DYNAMIC_URL_ATTRIBUTE_REVIEW'),
 ('data_hop','<div data-go="https://other.example/x">go</div>','UNCLASSIFIED_DYNAMIC_URL_ATTRIBUTE_REVIEW'),
 ('duplicate_href','<a href="/safe" href="/other">go</a>','DUPLICATE_HTML_ATTRIBUTE:a:href'),
 ('duplicate_canonical','<link rel="canonical" href="/safe" href="/other">','DUPLICATE_HTML_ATTRIBUTE:link:href','head'),
 ('duplicate_action','<form action="/safe" action="/unsafe"></form>','DUPLICATE_HTML_ATTRIBUTE:form:action'),
 ('duplicate_style','<p style="color:black" style="display:none">Hidden</p>','DUPLICATE_HTML_ATTRIBUTE:p:style'),
 ('duplicate_event','<img onload="a()" onload="b()">','DUPLICATE_HTML_ATTRIBUTE:img:onload'),
 ('hidden_attr','<p hidden>Emergency warning</p>','POTENTIALLY_HIDDEN_OR_INERT_CONTENT_REVIEW'),
 ('inert_attr','<div inert>Emergency warning</div>','POTENTIALLY_HIDDEN_OR_INERT_CONTENT_REVIEW'),
 ('aria_hidden','<div aria-hidden="true">Warning</div>','POTENTIALLY_HIDDEN_OR_INERT_CONTENT_REVIEW'),
 ('aria_hidden_caps','<div aria-hidden="TRUE">Warning</div>','POTENTIALLY_HIDDEN_OR_INERT_CONTENT_REVIEW'),
 ('style_display_none','<style>.warning{display:none}</style>','STYLESHEET_OR_INLINE_HIDING_REVIEW','head'),
 ('style_visibility','<style>.warning{visibility:hidden}</style>','STYLESHEET_OR_INLINE_HIDING_REVIEW','head'),
 ('style_opacity','<style>.warning{opacity:0}</style>','STYLESHEET_OR_INLINE_HIDING_REVIEW','head'),
 ('style_clip','<style>.warning{clip-path:inset(100%)}</style>','STYLESHEET_OR_INLINE_HIDING_REVIEW','head'),
 ('style_font','<style>.warning{font-size:0px}</style>','STYLESHEET_OR_INLINE_HIDING_REVIEW','head'),
 ('style_color','<style>.warning{color:transparent}</style>','STYLESHEET_OR_INLINE_HIDING_REVIEW','head'),
 ('inline_display','<p style="display:none">Emergency warning</p>','STYLESHEET_OR_INLINE_HIDING_REVIEW'),
 ('inline_visibility','<p style="visibility:hidden">Emergency warning</p>','STYLESHEET_OR_INLINE_HIDING_REVIEW'),
 ('comment_link','<!-- https://payhip.com/b/x -->','COMMENT_CONTAINS_URL_OR_SAFETY_TEXT_REVIEW'),
 ('comment_warning','<!-- WARNING: do not share medication -->','COMMENT_CONTAINS_URL_OR_SAFETY_TEXT_REVIEW'),
 ('comment_carbon','<!-- carbon monoxide hazard -->','COMMENT_CONTAINS_URL_OR_SAFETY_TEXT_REVIEW'),
 ('comment_evacuate','<!-- evacuate now -->','COMMENT_CONTAINS_URL_OR_SAFETY_TEXT_REVIEW'),
 ('robots_noindex','<meta name="robots" content="noindex,follow">','ROBOT_DIRECTIVE_REVIEW','head'),
 ('robots_nofollow','<meta name="robots" content="index,nofollow">','ROBOT_DIRECTIVE_REVIEW','head'),
 ('googlebot','<meta name="googlebot" content="noindex">','ROBOT_DIRECTIVE_REVIEW','head'),
]
for name,fragment,error,*location in cases:
    if error=='DOES_NOT_APPLY':continue
    setattr(TestNestedAndVisibility,'test_'+name,makecase(name,fragment,error,location[0] if location else 'other'))

if __name__=='__main__':unittest.main()
