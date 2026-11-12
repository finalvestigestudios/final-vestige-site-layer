"""R303 synthetic tests: private TemporaryDirectory only; no CMS/GitHub/production writes."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
FILE = ROOT / 'preparedness/tools/r303_inline_semantic_aria_hold.py'
spec = importlib.util.spec_from_file_location('r303', FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
R302 = mod.load_predecessor(ROOT)


def docs(content='<strong>Emergency</strong> <em>contact</em> for <span role="note" aria-label="Family guidance" lang="en">all households</span>.'):
    left = '<section aria-label="Emergency planning"><h2 id="plan">Plan first</h2><p>' + content + '{{cite:first-source}}</p>'
    right = '<div class="pa-body" id="pa-main"><section aria-label="Emergency planning"><h2 id="plan">Plan first</h2><p>' + content + '<sup class="pa-cite"><a href="#src-1">[1]</a></sup></p>'
    left += '<p>Read the {{link:family-communication-plan|family guide}} now.</p><ul><li>Review <mark>every six months</mark>.</li></ul></section>'
    right += '<p>Read the <a href="/preparedness/family-communication/family-communication-plan/">family guide</a> now.</p><ul><li>Review <mark>every six months</mark>.</li></ul></section></div>'
    return left, right


def valid_upstream():
    return {'state':'DRAFT_HARD_HOLD','errors':[],'article_semantic_matches':35,
        'publication_authorized':False,'independent_qd_pass':False,
        'medical_safety_verified':False,'privacy_verified':False,
        'all_41_exports_independently_approved':False}


class InlineTests(unittest.TestCase):
    def failure(self, source, output, code):
        self.assertIn(code, mod.inline_compare(source,output,R302))

    def test_baseline_semantic(self):
        self.assertEqual(mod.inline_compare(*docs(),R302),[])
    def test_prior_r302_cannot_see_lost_emphasis(self):
        a,b=docs();b=b.replace('<strong>Emergency</strong>','Emergency')
        self.assertEqual(R302.compare(a,b),[])
        self.failure(a,b,'INLINE_MARKUP_OR_ARIA_DRIFT')
    def test_same_text_different_emphasis_span(self):
        a,b=docs();b=b.replace('<em>contact</em>','contact')
        self.failure(a,b,'INLINE_MARKUP_OR_ARIA_DRIFT')
    def test_source_role_removed(self):
        a,b=docs();b=b.replace('role="note" ','')
        self.failure(a,b,'INLINE_MARKUP_OR_ARIA_DRIFT')
    def test_source_aria_label_changed(self):
        a,b=docs();b=b.replace('aria-label="Family guidance"','aria-label="Advertising"')
        self.failure(a,b,'INLINE_MARKUP_OR_ARIA_DRIFT')
    def test_source_hidden_added(self):
        a,b=docs();b=b.replace('<span role="note"','<span hidden role="note"')
        self.failure(a,b,'INLINE_MARKUP_OR_ARIA_DRIFT')
    def test_source_style_hide_added(self):
        a,b=docs();b=b.replace('<span role="note"','<span style="display:none" role="note"')
        self.failure(a,b,'INLINE_MARKUP_OR_ARIA_DRIFT')
    def test_source_lang_changed(self):
        a,b=docs();b=b.replace('lang="en"','lang="fr"')
        self.failure(a,b,'INLINE_MARKUP_OR_ARIA_DRIFT')
    def test_author_sup_preserved(self):
        a,b=docs('First<sup>st</sup> contact.')
        self.assertEqual(mod.inline_compare(a,b,R302),[])
        self.failure(a,b.replace('<sup>st</sup>','st'),'INLINE_MARKUP_OR_ARIA_DRIFT')
    def test_generated_sup_citation_not_false_positive(self):
        a,b=docs('First contact.');self.assertEqual(mod.inline_compare(a,b,R302),[])
    def test_marked_phrase_changed_scope(self):
        a,b=docs('<em>Call</em> or visit.')
        b=b.replace('<em>Call</em> or visit.','Call or <em>visit</em>.')
        self.failure(a,b,'INLINE_SCOPE_OR_CITATION_CONTEXT_DRIFT')
    def test_nested_scope_change(self):
        a,b=docs('<strong>Keep <em>both</em></strong> numbers.')
        b=b.replace('<strong>Keep <em>both</em></strong>','<strong>Keep </strong><em>both</em>')
        self.failure(a,b,'INLINE_MARKUP_OR_ARIA_DRIFT')
    def test_emphasis_reordered(self):
        a,b=docs('<strong><em>Plan</em></strong>.')
        b=b.replace('<strong><em>Plan</em></strong>','<em><strong>Plan</strong></em>')
        self.failure(a,b,'INLINE_MARKUP_OR_ARIA_DRIFT')
    def test_unbalanced_nested_markup(self):
        a,b=docs();b=b.replace('</em>','</strong>',1)
        self.failure(a,b,'INLINE_STRUCTURE_UNBALANCED:strong')
    def test_aria_hidden_flip(self):
        a,b=docs('<span aria-hidden="false">Read this</span>.')
        b=b.replace('aria-hidden="false"','aria-hidden="true"')
        self.failure(a,b,'INLINE_MARKUP_OR_ARIA_DRIFT')
    def test_source_markup_equal_with_attribute_reorder(self):
        a,b=docs()
        b=b.replace('role="note" aria-label="Family guidance" lang="en"','lang="en" aria-label="Family guidance" role="note"')
        self.assertEqual(mod.inline_compare(a,b,R302),[])
    def test_sanitization_strips_user_span(self):
        a,b=docs('<span class="pa-tag pa-tag--unc">Uncertain</span>.')
        self.failure(a,b.replace('<span class="pa-tag pa-tag--unc">','').replace('</span>.','.'),'INLINE_MARKUP_OR_ARIA_DRIFT')
    def test_link_token_generated_anchor_allowed(self):
        a,b=docs();self.assertEqual(mod.inline_compare(a,b,R302),[])
    def test_regular_script_inert(self):
        a,b=docs('<strong>Plan</strong><script>var a=1</script>')
        b=b.replace('var a=1','var a=2')
        self.assertEqual(mod.inline_compare(a,b,R302),[])
    def test_refuses_block_drift(self):
        a,b=docs();b=b.replace('<h2 id="plan">','<h3 id="plan">').replace('</h2>','</h3>')
        self.failure(a,b,'SEMANTIC_HTML_STRUCTURE_DRIFT')
    def test_refuses_citation_relocation(self):
        a,b=docs();cite='<sup class="pa-cite"><a href="#src-1">[1]</a></sup>'
        b=b.replace(cite,'').replace('<p>Read the ','<p>'+cite+'Read the ')
        self.failure(a,b,'CITATION_PLACEMENT_OR_BLOCK_ORDER_DRIFT')
    def test_does_not_suppress_changed_copy(self):
        a,b=docs();b=b.replace('all households','select households')
        self.failure(a,b,'BLOCK_LOCAL_READER_TEXT_DRIFT')
    def test_void_wbr_passes(self):
        a,b=docs('long<wbr>word')
        self.assertEqual(mod.inline_compare(a,b,R302),[])
    def test_void_wbr_missing(self):
        a,b=docs('long<wbr>word');self.failure(a,b.replace('<wbr>',''),'INLINE_MARKUP_OR_ARIA_DRIFT')
    def test_void_wbr_extra_endtag(self):
        a,b=docs('long<wbr>word');self.failure(a,b.replace('<wbr>','<wbr></wbr>'),'INLINE_VOID_CLOSED:wbr')
    def test_entities_normalized(self):
        a,b=docs('<abbr title="Federal Emergency Management Agency">FEMA</abbr> &amp; local teams')
        self.assertEqual(mod.inline_compare(a,b,R302),[])
    def test_no_approval_on_valid_fixture(self):
        with TemporaryDirectory() as directory:
            root=Path(directory); p=root/'preparedness/content/articles';q=root/'preparedness/build/wp'
            p.mkdir(parents=True);q.mkdir(parents=True)
            a,b=docs();rows=[]
            for i in range(35):
                slug='article-%02d'%i;rows.append({'slug':slug})
                (p/(slug+'.body.html')).write_text(a)
                (q/(slug+'.html')).write_text(b)
            r=mod.audit(root,{'articles':rows},R302,valid_upstream())
            self.assertEqual(r['errors'],[])
            self.assertEqual(r['article_inline_semantic_matches'],35)
            self.assertEqual(r['state'],'DRAFT_HARD_HOLD')
            for flag in ('publication_authorized','independent_qd_pass','medical_safety_verified',
                         'privacy_verified','merchant_approved','all_41_exports_independently_approved'):
                self.assertIs(r[flag],False)


class SourceControls(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.root=Path(self.temp.name)
        self.a,self.b=docs();self.rows=[]
        source=self.root/'preparedness/content/articles';draft=self.root/'preparedness/build/wp'
        source.mkdir(parents=True);draft.mkdir(parents=True)
        for i in range(35):
            slug=f'article-{i:02d}';self.rows.append({'slug':slug})
            (source/(slug+'.body.html')).write_text(self.a)
            (draft/(slug+'.html')).write_text(self.b)
    def tearDown(self):
        self.temp.cleanup()
    def audit(self,previous=None,rows=None):
        return mod.audit(self.root,{'articles':self.rows if rows is None else rows},R302,valid_upstream() if previous is None else previous)
    def test_missing_source(self):
        (self.root/'preparedness/content/articles/article-00.body.html').unlink()
        self.assertIn('AUTHORED_BODY_MISSING_OR_SYMLINK:article-00',self.audit()['errors'])
    def test_missing_export(self):
        (self.root/'preparedness/build/wp/article-00.html').unlink()
        self.assertIn('WORDPRESS_DRAFT_MISSING_OR_SYMLINK:article-00',self.audit()['errors'])
    def test_changed_inline_export(self):
        p=self.root/'preparedness/build/wp/article-02.html'
        p.write_text(self.b.replace('<strong>Emergency</strong>','Emergency'))
        self.assertIn('INLINE_MARKUP_OR_ARIA_DRIFT:article-02',self.audit()['errors'])
    def test_does_not_change_original_files(self):
        self.audit();self.assertEqual((self.root/'preparedness/content/articles/article-00.body.html').read_text(),self.a)
    def test_symlink_source(self):
        p=self.root/'preparedness/content/articles/article-00.body.html';p.unlink()
        p.symlink_to(self.root/'preparedness/content/articles/article-01.body.html')
        self.assertIn('AUTHORED_BODY_MISSING_OR_SYMLINK:article-00',self.audit()['errors'])
    def test_symlink_export(self):
        p=self.root/'preparedness/build/wp/article-00.html';p.unlink()
        p.symlink_to(self.root/'preparedness/build/wp/article-01.html')
        self.assertIn('WORDPRESS_DRAFT_MISSING_OR_SYMLINK:article-00',self.audit()['errors'])
    def test_bad_inventory(self):
        self.assertIn('AUTHENTIC_35_ARTICLE_CUSTODY_MISSING',self.audit(rows=self.rows[:34])['errors'])
    def test_duplicate_slug(self):
        rows=self.rows[:34]+[self.rows[0]]
        self.assertIn('DUPLICATE_ARTICLE_SLUG:article-00',self.audit(rows=rows)['errors'])
    def test_traversal_slug(self):
        rows=[{'slug':'../outside'}]+self.rows[1:]
        self.assertIn('INVALID_ARTICLE_SLUG',self.audit(rows=rows)['errors'])
    def test_upstream_false_approval(self):
        prev=dict(valid_upstream(),independent_qd_pass=True)
        self.assertIn('R302_PREDECESSOR_NOT_RECONCILED',self.audit(previous=prev)['errors'])
    def test_upstream_unverified_count(self):
        prev=dict(valid_upstream(),article_semantic_matches=34)
        self.assertIn('R302_PREDECESSOR_NOT_RECONCILED',self.audit(previous=prev)['errors'])
    def test_upstream_error(self):
        prev=dict(valid_upstream(),errors=['UNRESOLVED'])
        self.assertIn('R302_PREDECESSOR_NOT_RECONCILED',self.audit(previous=prev)['errors'])
    def test_upstream_wrong_state(self):
        prev=dict(valid_upstream(),state='PASS')
        self.assertIn('R302_PREDECESSOR_NOT_RECONCILED',self.audit(previous=prev)['errors'])
    def test_upstream_missing(self):
        self.assertEqual(self.audit(previous={})['state'],'INVALID_HARD_HOLD')
    def test_incomplete_real_chain_fails(self):
        with self.assertRaisesRegex(ValueError,'PINNED_R302_PREDECESSOR_MISSING_OR_SYMLINK'):
            mod.run(self.root)
    def test_r302_pin_loads(self):
        self.assertEqual(mod.git_blob((ROOT/mod.PREDECESSOR).read_bytes()),mod.PREDECESSOR_OID)
    def test_source_custody_pin_constant(self):
        self.assertEqual(len(mod.CUSTODY_OID),40)
    def test_no_unsanctioned_checkout_action(self):
        self.assertIsNone(self.audit()['confirmed_paid_orders'])
        self.assertIsNone(self.audit()['realized_net_revenue_per_1000_qualified_sessions'])


# 80 synthetically generated mutation cases: independent examples, no source-tree changes.
for index in range(20):
    def test_aria(self,index=index):
        a,b=docs(f'<span aria-label="Agency guidance {index}" role="note">Read carefully</span>')
        b=b.replace(f'Agency guidance {index}',f'Promotion {index}')
        self.assertIn('INLINE_MARKUP_OR_ARIA_DRIFT',mod.inline_compare(a,b,R302))
    setattr(InlineTests,f'test_generated_aria_{index:02d}',test_aria)
for index in range(20):
    def test_emphasis(self,index=index):
        a,b=docs(f'<strong>Safety step {index}</strong>.')
        b=b.replace(f'<strong>Safety step {index}</strong>',f'Safety step {index}')
        self.assertIn('INLINE_MARKUP_OR_ARIA_DRIFT',mod.inline_compare(a,b,R302))
    setattr(InlineTests,f'test_generated_emphasis_{index:02d}',test_emphasis)
for index in range(20):
    def test_scope(self,index=index):
        a,b=docs(f'<em>Call</em> helper {index}.')
        b=b.replace(f'<em>Call</em> helper {index}',f'Call <em>helper</em> {index}')
        self.assertIn('INLINE_SCOPE_OR_CITATION_CONTEXT_DRIFT',mod.inline_compare(a,b,R302))
    setattr(InlineTests,f'test_generated_scope_{index:02d}',test_scope)
for index in range(20):
    def test_label(self,index=index):
        a,b=docs(f'<abbr title="Safety organization {index}">SO</abbr>')
        b=b.replace(f'Safety organization {index}',f'Sales organization {index}')
        self.assertIn('INLINE_MARKUP_OR_ARIA_DRIFT',mod.inline_compare(a,b,R302))
    setattr(InlineTests,f'test_generated_abbr_{index:02d}',test_label)

if __name__ == '__main__':
    unittest.main()
