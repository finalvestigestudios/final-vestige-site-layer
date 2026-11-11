"""Synthetic / isolated regression tests: no source tree writes, no browser, no CMS."""
from __future__ import annotations
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

SOURCE=Path(__file__).resolve().parents[1]/'tools/r302_semantic_structure_citation_context_hold.py'
spec=importlib.util.spec_from_file_location('r302',SOURCE)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


def docs(text='Household contact plan.',citations=True):
    source='<section class="pa-act" aria-label="Practical guidance"><h2 id="now">What to do now</h2>'
    export='<div class="pa pa-article"><div class="pa-body" id="pa-main"><section class="pa-act" aria-label="Practical guidance"><h2 id="now">What to do now</h2>'
    source+='<p>'+text
    export+='<p>'+text
    if citations:
        source+='{{cite:first}}'
        export+='<sup class="pa-cite"><a href="#src-1" aria-label="Source 1">[1]</a></sup>'
    source+='</p><ol start="2"><li>Write it down.{{cite:second}}</li><li>Practice.</li></ol>'
    export+='</p><ol start="2"><li>Write it down.<sup class="pa-cite"><a href="#src-2">[2]</a></sup></li><li>Practice.</li></ol>'
    source+='<div class="pa-tablewrap"><table><caption>Contact methods</caption><tbody><tr><th scope="row">Phone</th><td>Primary</td></tr></tbody></table></div></section>'
    export+='<div class="pa-tablewrap"><table><caption>Contact methods</caption><tbody><tr><th scope="row">Phone</th><td>Primary</td></tr></tbody></table></div></section></div></div>'
    return source,export


class SemanticTests(unittest.TestCase):
    def assertFailCode(self,a,b,code):
        self.assertIn(code,mod.compare(a,b))
    def test_baseline(self):
        a,b=docs();self.assertEqual(mod.compare(a,b),[])
    def test_html_entities(self):
        a,b=docs('A &amp; B with <strong>everyone</strong>.');self.assertEqual(mod.compare(a,b),[])
    def test_unrelated_outside_main_ignored(self):
        a,b=docs();self.assertEqual(mod.compare(a,b+'<h2>Unrelated recommendations</h2>'),[])
    def test_internal_link_token(self):
        a,b=docs('Open {{link:family-reunification-card|the contact card}}.')
        b=b.replace('{{link:family-reunification-card|the contact card}}','<a href="/preparedness/x/family-reunification-card/">the contact card</a>')
        self.assertEqual(mod.compare(a,b),[])
    def test_inline_script_token_in_plain_text(self):
        a,b=docs('Guidance {{inline-js:plan_builder.js}} stays.')
        b=b.replace('{{inline-js:plan_builder.js}}','<script>window.x=42;</script>')
        self.assertEqual(mod.compare(a,b),[])
    def test_hidden_script_not_read(self):
        a,b=docs('Original <script>var a=1;</script> text.')
        b=b.replace('var a=1;','var a=2;')
        self.assertEqual(mod.compare(a,b),[])
    def test_missing_paragraph_boundary(self):
        a,b=docs();b=b.replace('<p>Household','<div>Household').replace('</sup></p>','</sup></div>',1)
        self.assertFailCode(a,b,'SEMANTIC_HTML_STRUCTURE_DRIFT')
    def test_paragraph_presentation_changed_but_same_text(self):
        a,b=docs();b=b.replace('<p>Household','<h3>Household').replace('</sup></p>','</sup></h3>',1)
        self.assertFailCode(a,b,'SEMANTIC_HTML_STRUCTURE_DRIFT')
    def test_changed_list_order_type(self):
        a,b=docs();self.assertFailCode(a,b.replace('<ol start="2">','<ul>'),'SEMANTIC_HTML_STRUCTURE_DRIFT')
    def test_changed_heading_level(self):
        a,b=docs();b=b.replace('<h2 id="now">','<h3 id="now">').replace('</h2>','</h3>')
        self.assertFailCode(a,b,'SEMANTIC_HTML_STRUCTURE_DRIFT')
    def test_changed_heading_id(self):
        a,b=docs();self.assertFailCode(a,b.replace('id="now"','id="gone"'),'SEMANTIC_HTML_STRUCTURE_DRIFT')
    def test_changed_list_reversed(self):
        a,b=docs();self.assertFailCode(a,b.replace('start="2"','start="1"'),'SEMANTIC_HTML_STRUCTURE_DRIFT')
    def test_changed_table_scope(self):
        a,b=docs();self.assertFailCode(a,b.replace('scope="row"','scope="col"'),'SEMANTIC_HTML_STRUCTURE_DRIFT')
    def test_changed_warning_class(self):
        a,b=docs();self.assertFailCode(a,b.replace('class="pa-act"','class="pa-history"'),'SEMANTIC_HTML_STRUCTURE_DRIFT')
    def test_changed_ariana_label(self):
        a,b=docs();self.assertFailCode(a,b.replace('aria-label="Practical guidance"','aria-label="Historical observations"'),'SEMANTIC_HTML_STRUCTURE_DRIFT')
    def test_lost_table_caption(self):
        a,b=docs();self.assertFailCode(a,b.replace('<caption>','').replace('</caption>',''),'SEMANTIC_HTML_STRUCTURE_DRIFT')
    def test_same_cites_different_claim(self):
        a,b=docs();b=b.replace('Household contact plan.','Household contact plan. ').replace('Write it down.','Write it down.')
        self.assertEqual(mod.compare(a,b),[])  # whitespace normalized intentionally
    def test_same_citation_count_different_location(self):
        a,b=docs();c='<sup class="pa-cite"><a href="#src-1" aria-label="Source 1">[1]</a></sup>'
        b=b.replace(c,'',1).replace('Write it down.',c+'Write it down.',1)
        self.assertFailCode(a,b,'CITATION_PLACEMENT_OR_BLOCK_ORDER_DRIFT')
    def test_same_text_different_blocks(self):
        a,b=docs();b=b.replace('<li>Practice.</li>','<li></li><p>Practice.</p>')
        self.assertFailCode(a,b,'SEMANTIC_HTML_STRUCTURE_DRIFT')
    def test_missing_main(self):
        a,b=docs();self.assertFailCode(a,b.replace('id="pa-main"','id="wrong"'),'MAIN_BODY_NOT_CLOSED')
    def test_extra_main(self):
        a,b=docs();self.assertFailCode(a,b+'<div id="pa-main">Another</div>','MULTIPLE_MAIN_BODIES')
    def test_no_matching_citation(self):
        a,b=docs();self.assertFailCode(a,b.replace('href="#src-1"','href="#src-9"'),'SOURCE_CITATION_OCCURRENCE_DRIFT')
    def test_malformed_citation(self):
        a,b=docs();self.assertFailCode(a,b.replace('href="#src-1"','href="/external"'),'BAD_INLINE_SOURCE_ANCHOR')
    def test_missing_citation_ref(self):
        a,b=docs();self.assertFailCode(a,b.replace('href="#src-1"','class="skip"'),'SOURCE_ANCHOR_MISSING')
    def test_missing_structural_close(self):
        a,b=docs();self.assertFailCode(a,b.replace('</ol>','',1),'UNCLOSED_SEMANTIC_BLOCK')
    def test_return_flag_never_approval(self):
        self.assertFalse(mod.safe_file(Path('/definitely/not/found'),mod.PREV))


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.root=Path(self.temp.name)
        a,b=docs();self.custody={'articles':[]}
        for i in range(35):
            slug='article-%02d'%i
            p=self.root/f'preparedness/content/articles/{slug}.body.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(a)
            q=self.root/f'preparedness/build/wp/{slug}.html';q.parent.mkdir(parents=True,exist_ok=True);q.write_text(b)
            self.custody['articles'].append({'slug':slug})
        self.previous={'state':'DRAFT_HARD_HOLD','errors':[],'body_pins_matched':35,'article_reader_parity_matched':35,
            'publication_authorized':False,'independent_qd_pass':False,
            'medical_safety_verified':False,'all_41_exports_independently_approved':False}
    def tearDown(self):self.temp.cleanup()
    def audit(self,previous='default',custody=None):
        return mod.audit(self.root,self.custody if custody is None else custody,self.previous if previous=='default' else previous)
    def test_all_35_draft_only(self):
        x=self.audit();self.assertEqual(x['state'],'DRAFT_HARD_HOLD');self.assertEqual(x['errors'],[])
        self.assertEqual(x['article_semantic_matches'],35);self.assertFalse(x['publication_authorized'])
        self.assertFalse(x['independent_qd_pass']);self.assertFalse(x['medical_safety_verified'])
        self.assertIsNone(x['confirmed_paid_orders']);self.assertIsNone(x['net_revenue_per_1000_qualified_sessions'])
    def test_missing_body(self):
        (self.root/'preparedness/content/articles/article-00.body.html').unlink()
        self.assertIn('BODY_MISSING_OR_SYMLINK:article-00',self.audit()['errors'])
    def test_missing_export(self):
        (self.root/'preparedness/build/wp/article-00.html').unlink()
        self.assertIn('DRAFT_MISSING_OR_SYMLINK:article-00',self.audit()['errors'])
    def test_symlink_export(self):
        p=self.root/'preparedness/build/wp/article-00.html';p.unlink();p.symlink_to(self.root/'preparedness/build/wp/article-01.html')
        self.assertIn('DRAFT_MISSING_OR_SYMLINK:article-00',self.audit()['errors'])
    def test_symlink_body(self):
        p=self.root/'preparedness/content/articles/article-00.body.html';p.unlink();p.symlink_to(self.root/'preparedness/content/articles/article-01.body.html')
        self.assertIn('BODY_MISSING_OR_SYMLINK:article-00',self.audit()['errors'])
    def test_incomplete_inventory(self):
        self.assertIn('R200_35_ARTICLE_SLATE_MISSING',self.audit(custody={'articles':self.custody['articles'][:-1]})['errors'])
    def test_duplicate_slug(self):
        rows=[*self.custody['articles'][:-1],self.custody['articles'][0]]
        self.assertIn('DUPLICATE_ARTICLE_SLUG',self.audit(custody={'articles':rows})['errors'])
    def test_invalid_upstream(self):
        self.assertIn('R301_UPSTREAM_BODY_CUSTODY_UNVERIFIED',self.audit(previous=dict(self.previous,independent_qd_pass=True))['errors'])
    def test_upstream_missing_count(self):
        self.assertIn('R301_UPSTREAM_BODY_CUSTODY_UNVERIFIED',self.audit(previous=dict(self.previous,body_pins_matched=34))['errors'])
    def test_upstream_wrong_state(self):
        self.assertIn('R301_UPSTREAM_BODY_CUSTODY_UNVERIFIED',self.audit(previous=dict(self.previous,state='PASS'))['errors'])
    def test_context_changed_one(self):
        p=self.root/'preparedness/build/wp/article-00.html';p.write_text(p.read_text().replace('<h2 id="now">','<h3 id="now">'))
        self.assertIn('SEMANTIC_HTML_STRUCTURE_DRIFT:article-00',self.audit()['errors'])


# 72 independent adversarial mutations, all isolated in memory; 0 real-source writes.
for i in range(24):
    def changed_structure(self,i=i):
        a,b=docs('Practice section '+str(i)+'.')
        b=b.replace('<li>Practice.</li>',f'<p class="item{i}">Practice.</p>')
        self.assertIn('SEMANTIC_HTML_STRUCTURE_DRIFT',mod.compare(a,b))
    setattr(SemanticTests,'test_adversarial_structure_%02d'%i,changed_structure)
for i in range(24):
    def changed_claim(self,i=i):
        a,b=docs('Prepare at step '+str(i)+'.')
        b=b.replace(f'Prepare at step {i}.',f'Prepare carefully at step {i}.')
        self.assertIn('BLOCK_LOCAL_READER_TEXT_DRIFT',mod.compare(a,b))
    setattr(SemanticTests,'test_adversarial_reader_text_%02d'%i,changed_claim)
for i in range(24):
    def shifted_citation(self,i=i):
        a,b=docs('Emergency preparation step '+str(i)+'.')
        marker='<sup class="pa-cite"><a href="#src-1" aria-label="Source 1">[1]</a></sup>'
        b=b.replace(marker,'',1).replace('<ol start="2"><li>','<ol start="2">'+marker+'<li>',1)
        self.assertIn('CITATION_PLACEMENT_OR_BLOCK_ORDER_DRIFT',mod.compare(a,b))
    setattr(SemanticTests,'test_adversarial_citation_context_%02d'%i,shifted_citation)

if __name__=='__main__':unittest.main()
