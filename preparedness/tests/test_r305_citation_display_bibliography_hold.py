"""R305: synthetic-only citation/Bibliography parity; no site, CMS or source writes."""
from __future__ import annotations
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('r305',ROOT/'preparedness/tools/r305_citation_display_bibliography_hold.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


def doc(title='Agency & Services',url='https://www.ready.gov/plan',count=1):
    citations=''.join(f'<p>Prepare <sup class="pa-cite"><a href="#src-1" aria-label="Source 1: {title}">[1]</a></sup>.</p>' for _ in range(count))
    return (f'<div class="pa"><div class="pa-body" id="pa-main">{citations}</div>'
        f'<section class="pa-sources" aria-labelledby="sources-h"><h2 id="sources-h">Sources and verification</h2>'
        f'<p>Machine check is not independent review.</p><ol>'
        f'<li id="src-1"><a href="{url}" rel="noopener">{title}</a>. Agency.'
        f'<span class="pa-src-meta">Machine-checked November 11, 2026 · Human source-link check pending</span>'
        f'<span class="pa-src-use">Used for: Planning guidance</span></li></ol></section></div>')


def baseline_slugs():
    return [{'slug':f'guide-{i:02d}'} for i in range(35)]


def success_upstream():
    return {'state':'DRAFT_HARD_HOLD','errors':[],'article_inline_semantic_matches':35,
        'publication_authorized':False,'independent_qd_pass':False,'medical_safety_verified':False,
        'all_41_exports_independently_approved':False}


class R305Checks(unittest.TestCase):
    def assertFlag(self,html,flag):
        self.assertIn(flag,mod.compare_document(html))
    def test_one_source(self):self.assertEqual(mod.compare_document(doc()),[])
    def test_repeat_citation(self):self.assertEqual(mod.compare_document(doc(count=3)),[])
    def test_source_title_entities(self):self.assertEqual(mod.compare_document(doc(title='Agency &amp; Services')),[])
    def test_visible_number_mismatch(self):self.assertFlag(doc().replace('>[1]</a>','>[9]</a>'),'VISIBLE_CITATION_NUMBER_MISMATCH')
    def test_visible_number_missing(self):self.assertFlag(doc().replace('>[1]</a>','></a>'),'VISIBLE_CITATION_NUMBER_MISMATCH')
    def test_visible_number_extra(self):self.assertFlag(doc().replace('>[1]</a>','>[1][1]</a>'),'VISIBLE_CITATION_NUMBER_MISMATCH')
    def test_aria_number_mismatch(self):self.assertFlag(doc().replace('Source 1:','Source 9:'),'CITATION_ACCESSIBLE_TITLE_MISMATCH')
    def test_aria_title_mismatch(self):self.assertFlag(doc().replace('aria-label="Source 1: Agency & Services"','aria-label="Source 1: Other"'),'CITATION_ACCESSIBLE_TITLE_MISMATCH')
    def test_aria_title_missing(self):self.assertFlag(doc().replace('aria-label="Source 1: Agency & Services"',''),'CITATION_ACCESSIBLE_TITLE_MISMATCH')
    def test_li_title_changed(self):self.assertFlag(doc().replace('>Agency & Services</a>. Agency.','>Changed title</a>. Agency.'),'CITATION_ACCESSIBLE_TITLE_MISMATCH')
    def test_wrong_target(self):self.assertFlag(doc().replace('href="#src-1"','href="#src-4"'),'CITATION_BIBLIOGRAPHY_TARGET_MISSING')
    def test_missing_bib(self):self.assertFlag(doc().replace('id="src-1"','id="other"'),'CITATION_BIBLIOGRAPHY_TARGET_MISSING')
    def test_bad_target_zero(self):self.assertFlag(doc().replace('href="#src-1"','href="#src-0"'),'CITATION_TARGET_INVALID')
    def test_javascript_bib(self):self.assertFlag(doc(url='javascript:alert(1)'),'BIBLIOGRAPHY_URL_UNSAFE_OR_INVALID')
    def test_data_bib(self):self.assertFlag(doc(url='data:text/html,hi'),'BIBLIOGRAPHY_URL_UNSAFE_OR_INVALID')
    def test_file_bib(self):self.assertFlag(doc(url='file:///tmp/source'),'BIBLIOGRAPHY_URL_UNSAFE_OR_INVALID')
    def test_relative_bib(self):self.assertFlag(doc(url='/local/source'),'BIBLIOGRAPHY_URL_UNSAFE_OR_INVALID')
    def test_bib_userinfo(self):self.assertFlag(doc(url='https://example.org@evil.com/'),'BIBLIOGRAPHY_URL_UNSAFE_OR_INVALID')
    def test_bib_whitespace(self):self.assertFlag(doc(url='https://ready.gov/a\nb'),'BIBLIOGRAPHY_URL_UNSAFE_OR_INVALID')
    def test_bib_whitespace_space(self):self.assertFlag(doc(url='https://ready.gov/a b'),'BIBLIOGRAPHY_URL_UNSAFE_OR_INVALID')
    def test_bib_noopener_missing(self):self.assertFlag(doc().replace('rel="noopener"',''),'BIBLIOGRAPHY_NOOPENER_MISSING')
    def test_bib_noopener_noreferrer_allowed(self):self.assertEqual(mod.compare_document(doc().replace('rel="noopener"','rel="noopener noreferrer"')),[])
    def test_missing_status(self):self.assertFlag(doc().replace('Human source-link check pending',''),'BIBLIOGRAPHY_REVIEW_SCOPE_OR_HUMAN_LINK_STATUS_MISSING')
    def test_human_complete_label_allowed(self):self.assertEqual(mod.compare_document(doc().replace('Human source-link check pending','Human source-link check complete')),[])
    def test_missing_used_for(self):self.assertFlag(doc().replace('Used for:','Reading notes:'),'BIBLIOGRAPHY_REVIEW_SCOPE_OR_HUMAN_LINK_STATUS_MISSING')
    def test_empty_title(self):self.assertFlag(doc(title=''),'BIBLIOGRAPHY_TITLE_EMPTY')
    def test_duplicate_bibliography_ids(self):
        d=doc();part=d[d.index('<li id="src-1"'):d.index('</li>')+5];self.assertFlag(d.replace('</ol>',part+'</ol>'),'DUPLICATE_BIBLIOGRAPHY_ID')
    def test_duplicate_generated_target_id(self):self.assertFlag(doc().replace('</div>','<span id="src-1"></span></div>',1),'DUPLICATE_SOURCE_TARGET_ID')
    def test_duplicate_citation_attribute(self):self.assertFlag(doc().replace('href="#src-1"','href="#src-1" href="#src-1"'),'DUPLICATE_CITATION_ATTRIBUTE')
    def test_multiple_sources_blocks(self):
        d=doc();part=d[d.index('<section class="pa-sources"'):d.rindex('</section>')+10]
        self.assertFlag(d.replace('</div>',part+'</div>',1),'SOURCES_BLOCK_COUNT_INVALID')
    def test_no_sources_block(self):self.assertFlag(doc().replace('class="pa-sources"','class="other"'),'SOURCES_BLOCK_COUNT_INVALID')
    def test_no_citations(self):self.assertFlag(doc().replace('class="pa-cite"','class="other"'),'NO_VISIBLE_CITATIONS')
    def test_http_allowed_no_unverified_https_upgrade(self):self.assertEqual(mod.compare_document(doc(url='http://nchfp.uga.edu/how/dry/recipes/jerky/')),[])
    def test_unapproved_link_unsafe_private_port(self):self.assertFlag(doc(url='https://example.org:444/test'),'BIBLIOGRAPHY_URL_UNSAFE_OR_INVALID')
    def test_safe_source_link_types(self):
        for u in ('',None,'http://','https://x/thing\telse','javascript:evil()','https://user:pass@example.org'):
            self.assertFalse(mod.safe_source_link(u),u)
    def test_valid_slug(self):self.assertIsNotNone(mod.SLUG.fullmatch('family-contact-plan'))
    def test_invalid_slug(self):self.assertIsNone(mod.SLUG.fullmatch('../unsafe'))
    def test_incomplete_root_not_approval(self):
        with TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'PINNED_PREDECESSOR_OR_CUSTODY_MISSING_OR_CHANGED'):
                mod.run(Path(td))


class R305FullInventory(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.root=Path(self.temp.name)
        p=self.root/'preparedness/build/wp';p.mkdir(parents=True)
        self.rows=baseline_slugs()
        for row in self.rows:(p/(row['slug']+'.html')).write_text(doc(),encoding='utf-8')
    def tearDown(self):self.temp.cleanup()
    def audit(self,rows=None,upstream=None):
        return mod.audit(self.root,{'articles':self.rows if rows is None else rows},success_upstream() if upstream is None else upstream)
    def test_35_intact_citation_gate_does_not_authorize_release(self):
        a=self.audit();self.assertEqual(a['state'],'DRAFT_HARD_HOLD');self.assertEqual(a['errors'],[])
        self.assertEqual(a['citation_display_and_bibliography_matches'],35)
        for f in ('publication_authorized','independent_qd_pass','medical_safety_verified','privacy_verified','merchant_approved','all_41_exports_independently_approved'):
            self.assertIs(a[f],False)
        self.assertIsNone(a['net_revenue_per_1000_qualified_sessions'])
    def test_missing_draft(self):
        (self.root/'preparedness/build/wp/guide-02.html').unlink()
        self.assertIn('MISSING_OR_SYMLINKED_WORDPRESS_DRAFT:guide-02',self.audit()['errors'])
    def test_symlink_draft(self):
        p=self.root/'preparedness/build/wp/guide-02.html';p.unlink();p.symlink_to(self.root/'preparedness/build/wp/guide-01.html')
        self.assertIn('MISSING_OR_SYMLINKED_WORDPRESS_DRAFT:guide-02',self.audit()['errors'])
    def test_bad_upstream(self):self.assertIn('R304_UPSTREAM_INTEGRITY_UNRECONCILED',self.audit(upstream={'state':'PASS'})['errors'])
    def test_wrong_count(self):self.assertIn('AUTHENTIC_35_ARTICLE_CUSTODY_MISSING',self.audit(rows=self.rows[:-1])['errors'])
    def test_duplicate_slug(self):self.assertIn('INVALID_OR_DUPLICATE_SLUG',self.audit(rows=self.rows[:-1]+[self.rows[0]])['errors'])
    def test_nonstring_slug(self):self.assertIn('INVALID_OR_DUPLICATE_SLUG',self.audit(rows=self.rows[:-1]+[{'slug':4}])['errors'])
    def test_draft_mutated_in_35(self):
        p=self.root/'preparedness/build/wp/guide-07.html';p.write_text(doc().replace('>[1]</a>','>[5]</a>'))
        self.assertIn('VISIBLE_CITATION_NUMBER_MISMATCH:guide-07',self.audit()['errors'])


class TwoSourceCrosswalk(unittest.TestCase):
    def base(self):
        x=doc()
        p='<sup class="pa-cite"><a href="#src-2" aria-label="Source 2: School Reunification">[2]</a></sup>'
        row=('<li id="src-2"><a href="https://www.ed.gov/school-safety" rel="noopener">School Reunification</a>. Education.'
            '<span>Machine-checked · Human source-link check pending</span><span>Used for: school handoffs</span></li>')
        return x.replace('Prepare <sup','Prepare '+p+' and <sup').replace('</ol>',row+'</ol>')
    def test_two_sources(self):self.assertEqual(mod.compare_document(self.base()),[])
    def test_missing_second_source(self):
        s=self.base().replace('id="src-2"','id="src-3"')
        self.assertIn('CITATION_BIBLIOGRAPHY_TARGET_MISSING',mod.compare_document(s))
    def test_swapped_titles(self):
        s=self.base().replace('>School Reunification</a>','>Other School Advice</a>')
        self.assertIn('CITATION_ACCESSIBLE_TITLE_MISMATCH',mod.compare_document(s))
    def test_second_visible_number_wrong(self):
        s=self.base().replace('>[2]</a>','>[1]</a>')
        self.assertIn('VISIBLE_CITATION_NUMBER_MISMATCH',mod.compare_document(s))
    def test_reused_number_allowed(self):
        s=self.base().replace('<p>Prepare','<p>Prepare <sup class="pa-cite"><a href="#src-2" aria-label="Source 2: School Reunification">[2]</a></sup>')
        self.assertEqual(mod.compare_document(s),[])
    def test_unused_second_source_detected(self):
        s=self.base().replace('Prepare <sup class="pa-cite"><a href="#src-2" aria-label="Source 2: School Reunification">[2]</a></sup> and','Prepare')
        self.assertIn('CITATION_SEQUENCE_OR_UNUSED_SOURCE',mod.compare_document(s))
    def test_invalid_second_bib_url(self):
        s=self.base().replace('https://www.ed.gov/school-safety','javascript:alert(2)')
        self.assertIn('BIBLIOGRAPHY_URL_UNSAFE_OR_INVALID',mod.compare_document(s))
    def test_arbitrary_order_of_bib_li_detects_number_target_but_current_order_not_critical(self):
        self.assertEqual(mod.compare_document(self.base()),[])
    def test_duplicate_source_anchor_inside_li(self):
        s=self.base().replace('>School Reunification</a>', '>School Reunification</a><a href="https://other.example">Other</a>')
        self.assertIn('BIBLIOGRAPHY_LINK_COUNT_INVALID',mod.compare_document(s))
    def test_missing_second_source_review_label(self):
        s=self.base().replace('Machine-checked · Human source-link check pending</span><span>Used for: school handoffs','Machine-checked</span><span>Used for: school handoffs')
        self.assertIn('BIBLIOGRAPHY_REVIEW_SCOPE_OR_HUMAN_LINK_STATUS_MISSING',mod.compare_document(s))


class R305Matrix(unittest.TestCase):pass
for k in range(1,33):
    def altered(self,k=k):
        html=doc(count=1)
        if k%4==0:html=html.replace('>[1]</a>','>['+str(k)+']</a>')
        elif k%4==1:html=html.replace('Source 1: Agency & Services','Source '+str(k)+': Agency & Services')
        elif k%4==2:html=html.replace('href="#src-1"','href="#src-'+str(k)+'"')
        else:html=html.replace('rel="noopener"','rel="noreferrer"')
        expected=['VISIBLE_CITATION_NUMBER_MISMATCH','CITATION_ACCESSIBLE_TITLE_MISMATCH','CITATION_BIBLIOGRAPHY_TARGET_MISSING','BIBLIOGRAPHY_NOOPENER_MISSING'][k%4]
        if k==1: return self.assertEqual(mod.compare_document(html),[])
        self.assertIn(expected,mod.compare_document(html))
    setattr(R305Matrix,f'test_adversarial_{k:02d}',altered)

if __name__=='__main__':unittest.main()
