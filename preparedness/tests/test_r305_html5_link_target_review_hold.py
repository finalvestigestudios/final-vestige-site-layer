"""R305 review-only adversarial controls. All fixtures in memory/temp sandbox."""
from __future__ import annotations
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[2]
R303=ROOT/'preparedness/tools/r303_inline_semantic_aria_hold.py'
R305=ROOT/'preparedness/tools/r305_html5_link_target_review_hold.py'
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod
m303=load(R303,'r305_repaired_inline')
up=m303.load_predecessor(ROOT)
mod=load(R305,'r305_static_urls')


def pair(body):
    a='<section><h2>Plans</h2><p>'+body+'{{cite:agency-one}}</p></section>'
    b='<div id="pa-main"><section><h2>Plans</h2><p>'+body+'<sup class="pa-cite"><a href="#src-1">[1]</a></sup></p></section></div><ol><li id="src-1">Agency</li></ol>'
    return a,b


def previous():
    return {'state':'DRAFT_HARD_HOLD','errors':[],'article_inline_semantic_matches':35,
        'publication_authorized':False,'independent_qd_pass':False,
        'medical_safety_verified':False,'privacy_verified':False,
        'all_41_exports_independently_approved':False}


class Html5NonVoid(unittest.TestCase):
    def test_plain_valid_pair(self):
        self.assertEqual(m303.inline_compare(*pair('<strong>Warnings</strong>'),up),[])
    def test_nonvoid_pair_is_rejected_even_when_identical(self):
        self.assertIn('HTML5_NONVOID_SELF_CLOSED:strong',m303.inline_compare(*pair('Check <strong/> first'),up))
    def test_nonvoid_export_is_rejected(self):
        a,b=pair('<em>Carefully</em>')
        self.assertIn('HTML5_NONVOID_SELF_CLOSED:em',m303.inline_compare(a,b.replace('<em>Carefully</em>','<em/>Carefully'),up))
    def test_void_explicit_close_invalid(self):
        self.assertIn('HTML5_VOID_EXPLICIT_CLOSE:br',m303.inline_compare(*pair('Check<br></br> again'),up))
    def test_valid_br_slash_allowed(self):
        self.assertEqual(m303.inline_compare(*pair('Check<br/> again'),up),[])
    def test_valid_img_slash_allowed(self):
        self.assertEqual(m303.inline_compare(*pair('<img alt="Test" src="https://example.gov/x.png"/>'),up),[])
    def test_wbr_slash_allowed(self):
        self.assertEqual(m303.inline_compare(*pair('long<wbr/>word'),up),[])
    def test_svg_selfclose_not_rejected_as_html_nonvoid(self):
        self.assertNotIn('HTML5_NONVOID_SELF_CLOSED:svg',m303.inline_compare(*pair('<svg/>'),up))
    def test_no_real_source_approval_on_empty_checkout(self):
        with TemporaryDirectory() as d:
            r=mod.main(['--repo-root',d])
            self.assertEqual(r,1)


class URLSecurity(unittest.TestCase):
    def test_good_root_and_https(self):
        for url in ('/preparedness/','/preparedness/water/','/#top','#top',
            'https://www.ready.gov/', 'https://example.gov/x?q=a%20b',
            'https://example.gov:443/resource','mailto:family@example.org','tel:+18005550123'):
            with self.subTest(url=url):self.assertIsNone(mod.url_problem(url))
    def test_unsafe_schemes(self):
        for url in ('javascript:alert(1)','JaVaScRiPt:alert(1)','data:text/html,hi','file:///tmp/a',
                    'ftp://example.gov/x','http://example.gov/x','blob:https://site/a',
                    'vbscript:msgbox(1)','chrome://settings'):
            with self.subTest(url=url):self.assertEqual(mod.url_problem(url),'UNAPPROVED_URL_SCHEME')
    def test_traversals(self):
        for url in ('/preparedness/../admin','/preparedness/%2e%2e/admin',
                    '/preparedness/%2Fetc','/preparedness/%5cprivate'):
            with self.subTest(url=url):self.assertEqual(mod.url_problem(url),'RELATIVE_PATH_TRAVERSAL')
    def test_network_relative(self):
        self.assertEqual(mod.url_problem('//example.gov/x'),'PROTOCOL_RELATIVE_URL')
    def test_js_scheme_entity_decoded(self):
        e,_=mod.scan('<a href="java&#x73;cript:alert(1)">Link</a>','source')
        self.assertTrue(any('UNAPPROVED_URL_SCHEME' in x for x in e))
    def test_https_credentials(self):
        self.assertEqual(mod.url_problem('https://user:pass@example.gov/'),'HTTPS_HOST_USERINFO_OR_PORT_INVALID')
    def test_unapproved_port(self):
        self.assertEqual(mod.url_problem('https://example.gov:444/'),'HTTPS_HOST_USERINFO_OR_PORT_INVALID')
    def test_url_control_char(self):
        self.assertEqual(mod.url_problem('java\tscript:alert(1)'),'AMBIGUOUS_URL_ENCODING')
    def test_backslash_url(self):
        self.assertEqual(mod.url_problem('https:\\example.gov'),'AMBIGUOUS_URL_ENCODING')
    def test_relative_url_different_scope(self):
        self.assertEqual(mod.url_problem('other-article.html'),'UNSCOPED_RELATIVE_URL')
    def test_external_link_not_verified_as_source(self):
        e,diag=mod.scan('<a href="https://example.gov">Official</a>','source')
        self.assertEqual(e,[]);self.assertEqual(diag['link_count'],1)
    def test_bad_attr_duplicated(self):
        e,_=mod.scan('<a href="https://example.gov" href="javascript:x">Text</a>','source')
        self.assertIn('DUPLICATE_HTML_ATTRIBUTE:a',e)
    def test_empty_href(self):
        e,_=mod.scan('<a href="">Text</a>','source')
        self.assertIn('EMPTY_OR_VALUELESS_URL:a:href',e)
    def test_bad_event_handler(self):
        e,_=mod.scan('<p onclick="post()">Text</p>','source')
        self.assertIn('UNREVIEWED_INLINE_EVENT_HANDLER:p:onclick',e)
    def test_source_script_held(self):
        e,_=mod.scan('<script>run()</script>','source')
        self.assertIn('ACTIVE_ELEMENT_IN_AUTHORED_ARTICLE:script',e)
    def test_export_script_not_unconditionally_held(self):
        e,_=mod.scan('<script>document.querySelector("h1")</script>','export')
        self.assertEqual(e,[])
    def test_form_in_source_held(self):
        e,_=mod.scan('<form><input name="x"></form>','source')
        self.assertIn('ACTIVE_ELEMENT_IN_AUTHORED_ARTICLE:form',e)
    def test_iframe_source_held(self):
        e,_=mod.scan('<iframe src="https://example.gov/"></iframe>','source')
        self.assertIn('UNREVIEWED_ACTIVE_EMBED:iframe',e)
    def test_no_duplicate_html_id(self):
        e,_=mod.scan('<div id="key"></div><section id="key"></section>','export')
        self.assertIn('DUPLICATE_HTML_ID:key',e)
    def test_resolved_anchor(self):
        e,d=mod.scan('<a href="#part">Part</a><h2 id="part">Part</h2>','export')
        self.assertEqual(e,[]);self.assertEqual(d['in_page_links'],1)
    def test_unresolved_anchor(self):
        e,_=mod.scan('<a href="#missing">Bad</a>','export')
        self.assertIn('MISSING_SAME_DOCUMENT_TARGET:missing',e)
    def test_bad_srcset_member(self):
        e,_=mod.scan('<img srcset="https://example.gov/a 1x, javascript:evil 2x">','export')
        self.assertIn('UNAPPROVED_URL_SCHEME:img:srcset',e)
    def test_plain_srcset_ok(self):
        e,_=mod.scan('<img srcset="https://example.gov/a 1x, https://example.gov/b 2x">','export')
        self.assertEqual(e,[])
    def test_bad_formaction(self):
        e,_=mod.scan('<button formaction="data:text/html,z">Go</button>','export')
        self.assertIn('UNAPPROVED_URL_SCHEME:button:formaction',e)
    def test_non_storage_commerce_guard(self):
        self.assertIsNone(mod.url_problem('https://example.gov/safe'))


class Snapshot(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.root=Path(self.tmp.name)
        self.src=self.root/'preparedness/content/articles';self.dst=self.root/'preparedness/build/wp'
        self.src.mkdir(parents=True);self.dst.mkdir(parents=True)
        self.rows=[]
        a,b=pair('<a href="https://example.gov">Government</a>')
        for i in range(35):
            slug=f'article-{i:02d}';self.rows.append({'slug':slug})
            (self.src/(slug+'.body.html')).write_text(a,encoding='utf-8')
            (self.dst/(slug+'.html')).write_text(b,encoding='utf-8')
        self.original=a
    def tearDown(self):self.tmp.cleanup()
    def inspect(self,rows=None,prev=None):
        return mod.audit(self.root,{'articles':self.rows if rows is None else rows},previous() if prev is None else prev)
    def test_35_pass_still_draft_hard_hold(self):
        r=self.inspect();self.assertEqual(r['article_link_target_checks'],35)
        self.assertEqual(r['state'],'DRAFT_HARD_HOLD')
        self.assertFalse(r['publication_authorized']);self.assertFalse(r['independent_qd_pass'])
        self.assertFalse(r['medical_safety_verified']);self.assertFalse(r['privacy_verified'])
        self.assertIsNone(r['realized_net_revenue_per_1000_qualified_sessions'])
    def test_original_not_rewritten(self):
        self.inspect();self.assertEqual((self.src/'article-00.body.html').read_text(),self.original)
    def test_bad_export_js_link_held(self):
        p=self.dst/'article-01.html';p.write_text(p.read_text().replace('https://example.gov','javascript:alert(1)'))
        r=self.inspect();self.assertEqual(r['state'],'INVALID_HARD_HOLD')
        self.assertTrue(any('UNAPPROVED_URL_SCHEME:a:href:draft:article-01'==x for x in r['errors']))
    def test_unverified_predecessor_held(self):
        p=previous();p['independent_qd_pass']=True
        self.assertIn('R304_UPSTREAM_NOT_RECONCILED',self.inspect(prev=p)['errors'])
    def test_unexpected_predecessor_success_held(self):
        p=previous();p['state']='PASS'
        self.assertIn('R304_UPSTREAM_NOT_RECONCILED',self.inspect(prev=p)['errors'])
    def test_missing_35th_body(self):
        (self.src/'article-34.body.html').unlink()
        self.assertIn('SOURCE_MISSING_OR_SYMLINK:article-34',self.inspect()['errors'])
    def test_34_custody_rows(self):
        self.assertIn('35_ARTICLE_CUSTODY_INVALID',self.inspect(rows=self.rows[:34])['errors'])
    def test_duplicate_slug(self):
        self.assertIn('DUPLICATE_CUSTODY_SLUG:article-00',self.inspect(rows=self.rows[:34]+[self.rows[0]])['errors'])
    def test_non_slug(self):
        self.assertIn('INVALID_CUSTODY_SLUG',self.inspect(rows=[{'slug':'../x'}]+self.rows[1:])['errors'])
    def test_symlink_body(self):
        p=self.src/'article-00.body.html';p.unlink();p.symlink_to(self.src/'article-01.body.html')
        self.assertIn('SOURCE_MISSING_OR_SYMLINK:article-00',self.inspect()['errors'])
    def test_symlink_export(self):
        p=self.dst/'article-00.html';p.unlink();p.symlink_to(self.dst/'article-01.html')
        self.assertIn('DRAFT_MISSING_OR_SYMLINK:article-00',self.inspect()['errors'])

# HTML5 non-void slash spoofing used to pass because HTMLParser auto-closed them.
NONVOID_TAGS=('strong','em','span','b','i','mark','abbr','time','q','cite','sub','sup',
              'u','s','del','ins','bdi','bdo','data','ruby','rt','rp','kbd','samp',
              'var','p','section','h2','li','table','td','a','button','label','form')
for idx,tag in enumerate(NONVOID_TAGS):
    def selfclose(self,tag=tag):
        a,b=pair(f'Warning <{tag}/> and note')
        self.assertIn('HTML5_NONVOID_SELF_CLOSED:'+tag,m303.inline_compare(a,b,up))
    setattr(Html5NonVoid,f'test_nonvoid_tag_{idx:02d}_{tag}',selfclose)

# Adversarial unsafe external links: no network contact or live writes.
BAD_SCHEMES=('javascript:','data:','ftp:','file:','http:','blob:','vbscript:','chrome:','ws:','wss:',
             'about:','facetime:','ms-settings:','intent:','smb:','ssh:','telnet:','view-source:',
             'localhost:','app:')
for idx,scheme in enumerate(BAD_SCHEMES):
    def unsafe(self,scheme=scheme):
        self.assertEqual(mod.url_problem(scheme+'example.com/x'),'UNAPPROVED_URL_SCHEME')
    setattr(URLSecurity,f'test_unapproved_scheme_{idx:02d}',unsafe)

if __name__=='__main__':unittest.main()
