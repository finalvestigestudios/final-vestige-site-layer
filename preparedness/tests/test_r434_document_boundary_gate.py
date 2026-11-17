"""R434 synthetic HTML boundary adversarial tests; never production/QD proof."""
import hashlib
import importlib.util
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

TOOL=Path(__file__).resolve().parents[1]/'tools'/'r434_document_boundary_gate.py'
spec=importlib.util.spec_from_file_location('r434_document_boundary_gate',TOOL)
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

def html(slug='guide-00',head='',body='',other='',url=None):
    if url is None:url=f'https://finalvestige.com/preparedness/{slug}/'
    return (f'<html><head><title>Preparedness guide</title>'
            f'<link rel="canonical" href="{url}">'
            f'<meta property="og:url" content="{url}">{head}</head>'
            f'<body>{other}<main><h1>Family plan</h1><p>Plan the route '
            f'<cite data-source-id="official-a">Source</cite></p>'
            f'<p><a href="/preparedness/start-here/">Start here</a></p>{body}'
            f'</main></body></html>').encode()

def fixture(n=35):
    m={'schema':1,'release_state':'DRAFT_HARD_HOLD','approved':False,'articles':[]}
    l={'schema':1,'release_state':'DRAFT_HARD_HOLD','approved':False,'articles':[]}
    e={}
    for i in range(n):
        s=f'guide-{i:02d}';b=html(s)
        m['articles'].append({'slug':s,'canonical_path':f'/preparedness/{s}/','sources':['official-a']})
        l['articles'].append({'slug':s,'canonical_path':f'/preparedness/{s}/','source_ids':['official-a'],
                              'wordpress_sha256':hashlib.sha256(b).hexdigest(),'preview_sha256':hashlib.sha256(b).hexdigest()})
        e[s]=(b,b)
    return m,e,l

def mutate(m,e,l,body,channel='preview'):
    s=m['articles'][0]['slug'];b=body if isinstance(body,bytes) else body.encode()
    wp,pr=e[s]
    if channel=='wordpress':wp=b
    else:pr=b
    e[s]=(wp,pr)
    l['articles'][0][channel+'_sha256']=hashlib.sha256(b).hexdigest()

def injecting(fragment,location='other'):
    return html(**{location:fragment})

class TestR434(unittest.TestCase):
    def test_clean_35_structural_only_not_release(self):
        m,e,l=fixture();x=r.audit(m,e,l)
        self.assertEqual(x['errors'],[])
        self.assertTrue(x['r433_structural_pair_parity'])
        self.assertTrue(x['r434_document_boundary_parity'])
        self.assertEqual(len(x['review_rows']),35)
        self.assertFalse(x['eligible']);self.assertFalse(x['publication_approved'])
        self.assertFalse(x['qualified_safety_approved']);self.assertFalse(x['commercial_offer_verified'])
        self.assertIsNone(x['merchant_orders_verified']);self.assertIsNone(x['net_revenue_per_1000_qualified_humans'])
        self.assertEqual(x['release_state'],'DRAFT_HARD_HOLD')
    def test_determinism(self):
        m,e,l=fixture();self.assertEqual(r.audit(m,e,l),r.audit(m,e,l))
    def test_cli_always_holds_with_missing_inputs(self):
        with tempfile.TemporaryDirectory() as t:
            p=subprocess.run([sys.executable,'-I',str(TOOL),t+'/m',t+'/l',t],capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertFalse(json.loads(p.stdout)['publication_approved'])
    def test_missing_evidence(self):
        self.assertTrue(r.audit(None,None,None)['errors'])
    def test_clean_relative_href(self):
        self.assertIsNone(r.clean_url('/preparedness/start-here/')[0])
    def test_clean_fragment_href(self):
        self.assertIsNone(r.clean_url('#sources')[0])
    def test_clean_official_https(self):
        self.assertIsNone(r.clean_url('https://www.ready.gov/plan')[0])
    def test_unknown_merchant_not_sale(self):
        self.assertFalse(r.held([])['commercial_offer_verified'])
    def test_og_url_missing_allowed_as_unverified(self):
        s=html().replace(b'<meta property="og:url" content="https://finalvestige.com/preparedness/guide-00/">',b'')
        self.assertEqual(r.inspect(s,'guide-00')['errors'],[])
    def test_clean_same_domain_images(self):
        self.assertEqual(r.inspect(injecting('<img src="https://finalvestige.com/image.webp">'),'guide-00')['errors'],[])
    def test_clean_spelling(self):
        self.assertEqual(r.canonical_target('/preparedness/guide-00/','guide-00'),None)
    def test_duplicate_export_slug(self):
        m,e,l=fixture();e['rogue']=(html(),html())
        self.assertIn('EXTRA_OR_MISSING_EXPORT_SLUGS',r.audit(m,e,l)['errors'])
    def test_missing_export_pair(self):
        m,e,l=fixture();del e['guide-00']
        self.assertTrue(any('MISSING_PAIR' in a for a in r.audit(m,e,l)['errors']))
    def test_incomplete_slate(self):
        m,e,l=fixture(1)
        self.assertIn('INCOMPLETE_DOCUMENT_BOUNDARY_SLATE',r.audit(m,e,l)['errors'])
    def test_synthetic_small_does_not_claim_parity(self):
        m,e,l=fixture(1)
        self.assertFalse(r.audit(m,e,l,test_only=True)['r434_document_boundary_parity'])
    def test_malformed_utf8(self):
        with self.assertRaises(UnicodeError):r.inspect(html()+b'\xff','guide-00')
    def test_nul_rejected(self):
        with self.assertRaises(ValueError):r.inspect(html()+b'\0','guide-00')
    def test_sha_lock_is_not_active_content_approval(self):
        m,e,l=fixture();mutate(m,e,l,injecting('<script>alert(1)</script>'))
        x=r.audit(m,e,l)
        self.assertTrue(any('ACTIVE_ELEMENT_REVIEW:script' in z for z in x['errors']))
        self.assertFalse(x['r434_document_boundary_parity'])
    def test_proved_r433_script_outside_main_blindspot(self):
        m,e,l=fixture();mutate(m,e,l,injecting('<script src="https://example.org/a.js"></script>'))
        prior=r.load_r433().audit(m,e,l)
        self.assertEqual(prior['errors'],[])  # exact prior gate did not inspect outside <main>
        self.assertTrue(any('ACTIVE_ELEMENT_REVIEW:script' in a for a in r.audit(m,e,l)['errors']))
    def test_proved_r433_checkout_outside_main_blindspot(self):
        m,e,l=fixture();mutate(m,e,l,injecting('<a href="https://payhip.com/b/unapproved">Buy</a>'))
        self.assertEqual(r.load_r433().audit(m,e,l)['errors'],[])
        self.assertTrue(any('UNAPPROVED_COMMERCE_DESTINATION' in a for a in r.audit(m,e,l)['errors']))
    def test_proved_r433_canonical_spoof_outside_main_blindspot(self):
        m,e,l=fixture();mutate(m,e,l,html(url='https://offsite.example/preparedness/guide-00/'))
        self.assertEqual(r.load_r433().audit(m,e,l)['errors'],[])
        self.assertTrue(any('CANONICAL_FOREIGN_HOST' in a for a in r.audit(m,e,l)['errors']))
    def test_r433_passage_removal_still_blocked(self):
        m,e,l=fixture();mutate(m,e,l,html().replace(b'Plan the route',b'Plan route'))
        self.assertTrue(any('EDITORIAL_PASSAGE_PARITY' in z for z in r.audit(m,e,l)['errors']))

def injected_case(name, payload, expected,location='other',channel='preview'):
    def run(self):
        m,e,l=fixture(); mutate(m,e,l,injecting(payload,location),channel)
        errors=r.audit(m,e,l)['errors']
        self.assertTrue(any(expected in a for a in errors),(name,errors))
        self.assertFalse(r.audit(m,e,l)['publication_approved'])
    run.__name__='test_'+name
    return run

CASES=[
('script_outside_main','<script src="https://example.org/a.js"></script>','ACTIVE_ELEMENT_REVIEW:script'),
('script_inside_main','<script>alert(1)</script>','ACTIVE_ELEMENT_REVIEW:script','body'),
('jsonld_script','<script type="application/ld+json">{"@type":"Article"}</script>','ACTIVE_ELEMENT_REVIEW:script'),
('iframe','<iframe src="https://example.org"></iframe>','ACTIVE_ELEMENT_REVIEW:iframe'),
('object','<object data="/x"></object>','ACTIVE_ELEMENT_REVIEW:object'),
('embed','<embed src="/a">','ACTIVE_ELEMENT_REVIEW:embed'),
('applet','<applet></applet>','ACTIVE_ELEMENT_REVIEW:applet'),
('form_outside_main','<form action="/signup"><input></form>','ACTIVE_ELEMENT_REVIEW:form'),
('form_inside_main','<form action="/signup"></form>','ACTIVE_ELEMENT_REVIEW:form','body'),
('portal','<portal src="/x"></portal>','ACTIVE_ELEMENT_REVIEW:portal'),
('base','<base href="https://evil.example/">','BASE_URL_REWRITE','head'),
('meta_refresh','<meta http-equiv="refresh" content="0;url=https://evil.example">','META_REFRESH_REDIRECT','head'),
('handler_onclick','<a onclick="alert(1)" href="/x">x</a>','INLINE_EVENT_HANDLER:onclick'),
('handler_onload','<img src="/a" onload="go()">','INLINE_EVENT_HANDLER:onload'),
('handler_onerror','<img src="/a" onerror="go()">','INLINE_EVENT_HANDLER:onerror'),
('handler_onfocus','<input onfocus="go()">','INLINE_EVENT_HANDLER:onfocus'),
('handler_onpointerenter','<a onpointerenter="go()" href="/x">x</a>','INLINE_EVENT_HANDLER:onpointerenter'),
('handler_onsubmit','<form onsubmit="go()"></form>','INLINE_EVENT_HANDLER:onsubmit'),
('srcdoc','<iframe srcdoc="<script>x</script>"></iframe>','EMBEDDED_HTML_SRCDOC'),
('style_import','<p style="@import url(https://evil.example/x)">x</p>','CSS_EXTERNAL_OR_EXECUTABLE_REFERENCE'),
('css_url','<p style="background:url(https://evil.example/a)">x</p>','CSS_EXTERNAL_OR_EXECUTABLE_REFERENCE'),
('css_expression','<p style="width:expression(alert(1))">x</p>','CSS_EXTERNAL_OR_EXECUTABLE_REFERENCE'),
('css_moz_binding','<p style="-moz-binding:url(https://evil.example)">x</p>','CSS_EXTERNAL_OR_EXECUTABLE_REFERENCE'),
('css_behavior','<p style="behavior:url(x)">x</p>','CSS_EXTERNAL_OR_EXECUTABLE_REFERENCE'),
('css_opacity_hidden','<p style="opacity:0">Warning</p>','POTENTIALLY_CONCEALED_CONTENT_REVIEW'),
('css_font_zero','<p style="font-size:0px">Warning</p>','POTENTIALLY_CONCEALED_CONTENT_REVIEW'),
('css_clip_inset','<p style="clip-path:inset(100%)">Warning</p>','POTENTIALLY_CONCEALED_CONTENT_REVIEW'),
('css_text_indent','<p style="text-indent:-9999px">Warning</p>','POTENTIALLY_CONCEALED_CONTENT_REVIEW'),
('css_color_transparent','<p style="color:transparent">Warning</p>','POTENTIALLY_CONCEALED_CONTENT_REVIEW'),
('srcset_review','<img src="/a" srcset="/a 1x, /b 2x">','RESPONSIVE_SRCSET_REVIEW'),
('noscript_review','<noscript>Text absent with JS</noscript>','NOSCRIPT_FALLBACK_REVIEW'),
('template_review','<template><p>private</p></template>','DORMANT_TEMPLATE_REVIEW'),
('payment_data_attr','<div data-payment-id="x">x</div>','UNREVIEWED_COMMERCE_DATA_ATTRIBUTE'),
('purchase_data_attr','<div data-purchase="payhip">x</div>','UNREVIEWED_COMMERCE_DATA_ATTRIBUTE'),
('merchant_data_attr','<div data-merchant="example">x</div>','UNREVIEWED_COMMERCE_DATA_ATTRIBUTE'),
('javascript_href','<a href="javascript:alert(1)">x</a>','UNSAFE_SCHEME_AUTHORITY_OR_PORT'),
('javascript_entities','<a href="java&#115;cript:alert(1)">x</a>','UNSAFE_SCHEME_AUTHORITY_OR_PORT'),
('mailto_href','<a href="mailto:x@example.org">x</a>','UNSAFE_SCHEME_AUTHORITY_OR_PORT'),
('protocol_relative','<img src="//example.org/a">','AMBIGUOUS_URL_ENCODING'),
('payhip_outside_main','<a href="https://payhip.com/b/xxx">buy</a>','UNAPPROVED_COMMERCE_DESTINATION'),
('payhip_subdomain','<a href="https://shop.payhip.com/b/xxx">buy</a>','UNAPPROVED_COMMERCE_DESTINATION'),
('payhip_trailing_dot','<a href="https://payhip.com./b/xxx">buy</a>','UNAPPROVED_COMMERCE_DESTINATION'),
('payhip_percent_dot','<a href="https://payhip%2ecom/b/xxx">buy</a>','UNAPPROVED_COMMERCE_DESTINATION'),
('payhip_double_encoded','<a href="https://payhip%252ecom/b/xxx">buy</a>','UNAPPROVED_COMMERCE_DESTINATION'),
('payhip_upper','<a href="HTTPS://PAYHIP.COM/b/xxx">buy</a>','UNAPPROVED_COMMERCE_DESTINATION'),
('stripe','<a href="https://checkout.stripe.com/b/test">go</a>','UNAPPROVED_COMMERCE_DESTINATION'),
('paypal','<a href="https://paypal.com/pay">go</a>','UNAPPROVED_COMMERCE_DESTINATION'),
('gumroad','<a href="https://gumroad.com/l/item">buy</a>','UNAPPROVED_COMMERCE_DESTINATION'),
('coffee','<a href="https://buymeacoffee.com/item">buy</a>','UNAPPROVED_COMMERCE_DESTINATION'),
('formaction','<button formaction="https://payhip.com/b/x">send</button>','UNAPPROVED_COMMERCE_DESTINATION'),
('data_href','<div data-href="https://payhip.com/b/x">x</div>','UNAPPROVED_COMMERCE_DESTINATION'),
('data_redirect','<div data-redirect="https://payhip.com/b/x">x</div>','UNAPPROVED_COMMERCE_DESTINATION'),
('data_checkout','<div data-checkout-url="https://payhip.com/b/x">x</div>','UNAPPROVED_COMMERCE_DESTINATION'),
('data_src','<div data-src="javascript:foo()">x</div>','UNSAFE_SCHEME_AUTHORITY_OR_PORT'),
('userinfo','<a href="https://user:pass@example.org/x">go</a>','UNSAFE_SCHEME_AUTHORITY_OR_PORT'),
('non_https','<a href="http://example.org/a">go</a>','UNSAFE_SCHEME_AUTHORITY_OR_PORT'),
('backslash','<a href="https:\\\\payhip.com/b/x">go</a>','AMBIGUOUS_URL_ENCODING'),
('control_entity','<a href="https://example.org/&#10;x">go</a>','EMPTY_OR_CONTROL_URL'),
]
for name,payload,error,*args in CASES:
    setattr(TestR434,'test_inject_'+name,injected_case(name,payload,error,args[0] if args else 'other'))

class TestCanonicals(unittest.TestCase):
    def test_missing_canonical(self):
        x=r.inspect(html().replace(b'<link rel="canonical" href="https://finalvestige.com/preparedness/guide-00/">',b''),'guide-00')
        self.assertIn('CANONICAL_MISSING_OR_DUPLICATE',x['errors'])
    def test_duplicate_canonical(self):
        x=r.inspect(html(head='<link rel="canonical" href="/preparedness/guide-00/">'),'guide-00')
        self.assertIn('CANONICAL_MISSING_OR_DUPLICATE',x['errors'])
    def test_canonical_offsite(self):
        self.assertEqual(r.canonical_target('https://other.example/preparedness/guide-00/','guide-00'),'CANONICAL_FOREIGN_HOST')
    def test_canonical_query(self):
        self.assertEqual(r.canonical_target('/preparedness/guide-00/?utm_source=bad','guide-00'),'CANONICAL_ROUTE_DRIFT')
    def test_canonical_fragment(self):
        self.assertEqual(r.canonical_target('/preparedness/guide-00/#x','guide-00'),'CANONICAL_ROUTE_DRIFT')
    def test_canonical_wrong_slug(self):
        self.assertEqual(r.canonical_target('/preparedness/guide-01/','guide-00'),'CANONICAL_ROUTE_DRIFT')
    def test_canonical_bad_port(self):
        self.assertEqual(r.canonical_target('https://finalvestige.com:8443/preparedness/guide-00/','guide-00'),'UNSAFE_SCHEME_AUTHORITY_OR_PORT')
    def test_canonical_html_attribute_entity(self):
        x=r.inspect(html().replace(b'/guide-00/',b'/guide-01/'),'guide-00')
        self.assertIn('CANONICAL_ROUTE_DRIFT',x['errors'])
    def test_social_meta_wrong_url(self):
        x=r.inspect(html().replace(b'property="og:url" content="https://finalvestige.com/preparedness/guide-00/"',b'property="og:url" content="https://other.example/preparedness/guide-00/"'),'guide-00')
        self.assertIn('SOCIAL_META_CANONICAL_FOREIGN_HOST',x['errors'])
    def test_meta_count_drift(self):
        m,e,l=fixture();mutate(m,e,l,html().replace(b'<meta property="og:url" content="https://finalvestige.com/preparedness/guide-00/">',b''))
        self.assertIn('SOCIAL_META_COUNT_DRIFT:guide-00',r.audit(m,e,l)['errors'])
    def test_canonical_channel_drift(self):
        m,e,l=fixture();mutate(m,e,l,html(url='/preparedness/guide-00/'))
        self.assertIn('CANONICAL_CHANNEL_DRIFT:guide-00',r.audit(m,e,l)['errors'])
    def test_invalid_port_is_error_not_crash(self):
        error,_=r.clean_url('https://example.org:invalid/path')
        self.assertEqual(error,'UNSAFE_SCHEME_AUTHORITY_OR_PORT')

if __name__=='__main__':unittest.main()
