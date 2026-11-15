"""R390 synthetic adversarial fixtures, never authentic emergency source or QD review."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'tools' / 'r390_all_export_custody.py'
spec = importlib.util.spec_from_file_location('r390_all', MODULE)
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)
ARTICLES = [f'article-{i:02d}' for i in range(1,36)]
EXTRAS = [f'hub-{i:02d}' for i in range(1,16)]


def content(slug, *, article=False):
    kind = 'pa-article' if article else 'pa-tool'
    return f'<div class="{kind}" data-slug="{slug}"><h1>{slug}</h1><p>Draft and review required.</p></div>'


def wp(slug, *, article=False):
    return '<!-- wp:html -->\n' + content(slug, article=article) + '\n<!-- /wp:html -->'


def preview(slug, *, article=False):
    return '<!doctype html><html><head><meta name="robots" content="noindex,nofollow"></head><body>' + content(slug, article=article) + '</body></html>'


class ExportCustody(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.wpdir = Path(self.tmp.name) / 'wp'
        self.prdir = Path(self.tmp.name) / 'preview'
        self.wpdir.mkdir(); self.prdir.mkdir()
        for slug in ARTICLES + EXTRAS:
            self.put(slug)

    def put(self, slug):
        (self.wpdir / (slug + '.html')).write_text(wp(slug, article=slug in ARTICLES))
        (self.prdir / (slug + '.html')).write_text(preview(slug, article=slug in ARTICLES))

    def mutate(self, slug, replace, *, side='wp'):
        folder = self.wpdir if side == 'wp' else self.prdir
        path = folder / (slug + '.html')
        path.write_text(replace(path.read_text()))

    def gate(self, original=None, **kw):
        return G.audit(self.wpdir, self.prdir, ARTICLES if original is None else original, **kw)

    def assertBad(self, error_fragment):
        res = self.gate()
        self.assertEqual(res['status'], 'INVALID_HARD_HOLD')
        self.assertTrue(any(error_fragment in s for s in res['errors']), res['errors'])
        self.assertFalse(res['publication_approved'])
        self.assertFalse(res['qualified_safety_approved'])

    def test_complete_private_docket_remains_hold(self):
        d = self.gate()
        self.assertEqual(d['status'], 'ALL_EXPORT_BYTES_REVIEW_HARD_HOLD')
        self.assertEqual(d['counts']['matched_export_pairs'], 50)
        self.assertEqual(d['counts']['supplemental_exports_needing_independent_review'], 15)
        self.assertEqual(len(d['exports']), 50)
        self.assertFalse(d['merchant_offer_verified'])
        self.assertFalse(d['live_release_allowed'])

    def test_same_inputs_have_same_digest_and_order(self):
        x, y = self.gate(), self.gate()
        self.assertEqual(x['evidence_sha256'], y['evidence_sha256'])
        self.assertEqual([r['slug'] for r in x['exports']], sorted(ARTICLES+EXTRAS))

    def test_mutation_changes_digest_without_external_action(self):
        before = self.gate()['evidence_sha256']
        self.mutate('hub-01',lambda s:s.replace('Draft and review', 'Draft and reviews'),side='preview')
        self.assertNotEqual(before, self.gate()['evidence_sha256'])
        self.assertBad('SUPPLEMENTAL_WORDPRESS_PREVIEW_CONTENT_DRIFT')

    def test_all_supplementals_have_review_only_type(self):
        d = self.gate()
        for r in d['exports']:
            self.assertEqual(r['kind'], 'original_article' if r['slug'] in ARTICLES else 'unreviewed_supplemental')
            self.assertTrue(r['qualified_review_required'])
            self.assertFalse(r['release_allowed'])

    def test_reject_missing_original_slug(self):
        (self.wpdir / 'article-01.html').unlink()
        self.assertBad('ORIGINAL_ARTICLE_OUTPUT_MISSING')

    def test_reject_extra_only_one_side(self):
        (self.wpdir / 'extra-16.html').write_text(wp('extra-16'))
        self.assertBad('EXACT_EXPORT_FILENAME_SET_MISMATCH')

    def test_reject_extra_missing_both_sides(self):
        (self.wpdir / 'hub-15.html').unlink();(self.prdir / 'hub-15.html').unlink()
        self.assertBad('INSUFFICIENT_PRIVATE_EXPORT_PAIRS')

    def test_reject_34_original_metadata(self):
        x = self.gate(ARTICLES[:-1])
        self.assertIn('ORIGINAL_35_SLUG_SET_INVALID', x['errors'])

    def test_reject_duplicate_original_metadata(self):
        x = self.gate(ARTICLES[:-1]+[ARTICLES[0]])
        self.assertIn('ORIGINAL_35_SLUG_SET_INVALID', x['errors'])

    def test_reject_invalid_original_metadata(self):
        x = self.gate(ARTICLES[:-1]+['../bad'])
        self.assertIn('ORIGINAL_35_SLUG_SET_INVALID', x['errors'])

    def test_detect_inline_event_attribute(self):
        self.mutate('hub-01', lambda s:s.replace('<h1>', '<h1 onclick="alert(1)">'))
        self.assertBad('INLINE_EVENT_HANDLER')

    def test_detect_script_in_supplemental(self):
        self.mutate('hub-01', lambda s:s.replace('</p>', '</p><script>alert(1)</script>'))
        self.assertBad('ACTIVE_CONTENT:script')

    def test_detect_checkout_link(self):
        self.mutate('hub-01', lambda s:s.replace('</p>', '</p><a href="https://payhip.com/b/abc">Buy</a>'))
        self.assertBad('UNVERIFIED_COMMERCE_DESTINATION')

    def test_detect_data_link(self):
        self.mutate('hub-01', lambda s:s.replace('</p>', '</p><a href="data:text/html,hello">x</a>'))
        self.assertBad('UNSAFE_LINK_SCHEME')

    def test_detect_protocol_relative_link(self):
        self.mutate('hub-01', lambda s:s.replace('</p>', '</p><a href="//example.org">x</a>'))
        self.assertBad('UNSAFE_LINK_SCHEME')

    def test_detect_form_in_supplemental(self):
        self.mutate('hub-01', lambda s:s.replace('</p>', '</p><form action="/checkout"></form>'))
        self.assertBad('ACTIVE_CONTENT:form')

    def test_detect_preview_missing_noindex(self):
        self.mutate('hub-01', lambda s:s.replace('noindex,nofollow', 'index,follow'), side='preview')
        self.assertBad('PREVIEW_NOINDEX_NOFOLLOW_MISSING')

    def test_detect_bad_wordpress_wrapper(self):
        self.mutate('hub-01', lambda s:s.replace('<!-- wp:html -->', '<!-- no-block -->'))
        self.assertBad('WORDPRESS_DRAFT_WRAPPER_MISSING')

    def test_detect_missing_preview_doctype(self):
        self.mutate('hub-01', lambda s:s.replace('<!doctype html>', ''), side='preview')
        self.assertBad('PREVIEW_DOCTYPE_MISSING')

    def test_detect_supplemental_slug_swap(self):
        self.mutate('hub-01', lambda s:s.replace('data-slug="hub-01"','data-slug="hub-02"'))
        self.assertBad('SUPPLEMENTAL_SLUG_PROVENANCE_UNVERIFIED')

    def test_detect_missing_draft_review_warning(self):
        self.mutate('hub-01', lambda s:s.replace('Draft and review required', 'Helpful checklist'))
        self.assertBad('SUPPLEMENTAL_REVIEW_WARNING_MISSING')

    def test_detect_multiple_content_roots(self):
        self.mutate('hub-01',lambda s:s.replace('\n<!-- /wp:html -->',content('hub-01')+'\n<!-- /wp:html -->'))
        self.assertBad('CONTENT_ROOT_COUNT:2')

    def test_detect_missing_content_root(self):
        self.mutate('hub-01',lambda s:s.replace('pa-tool','not-a-root'))
        self.assertBad('CONTENT_ROOT_COUNT:0')

    def test_detect_orphan_html_close(self):
        self.mutate('hub-01',lambda s:s.replace('</div>', '</div></span>'))
        self.assertBad('ORPHAN_CLOSE')

    def test_detect_non_html_file(self):
        (self.wpdir / 'notes.json').write_text('{}')
        self.assertBad('UNEXPECTED_EXPORT_FILENAME')

    def test_detect_nested_directory(self):
        (self.wpdir / 'nested').mkdir()
        self.assertBad('UNSAFE_EXPORT_ENTRY')

    def test_detect_oversized_extra(self):
        (self.wpdir / 'hub-01.html').write_text('x'*(G.SIZE_LIMIT+1))
        self.assertBad('EXPORT_SIZE_INVALID')

    def test_detect_zero_byte_extra(self):
        (self.wpdir / 'hub-01.html').write_bytes(b'')
        self.assertBad('EXPORT_SIZE_INVALID')

    def test_detect_bad_utf8(self):
        (self.wpdir / 'hub-01.html').write_bytes(b'\xff\xff')
        self.assertBad('MALFORMED_EXPORT')

    def test_detect_duplicate_canonical(self):
        add='<link rel="canonical" href="https://finalvestige.com/preparedness/same/">'
        for slug in ('hub-01','hub-02'):
            for d in (self.wpdir,self.prdir):
                p=d/(slug+'.html');p.write_text(p.read_text().replace('<div',add+'<div',1))
        self.assertBad('DUPLICATE_CANONICAL_URL')

    def test_detect_cross_preview_canonical_drift(self):
        self.mutate('hub-01',lambda s:s.replace('<div','<link rel="canonical" href="https://finalvestige.com/preparedness/a/"><div',1))
        self.mutate('hub-01',lambda s:s.replace('<div','<link rel="canonical" href="https://finalvestige.com/preparedness/b/"><div',1),side='preview')
        self.assertBad('CROSS_EXPORT_CANONICAL_DRIFT')

    def test_symlink_is_not_followed(self):
        (self.wpdir/'hub-01.html').unlink()
        (self.wpdir/'hub-01.html').symlink_to(self.prdir/'hub-01.html')
        self.assertBad('UNSAFE_EXPORT_ENTRY')

    def test_direct_scan_rejects_symlink_directory(self):
        fake=Path(self.tmp.name)/'wp-link';fake.symlink_to(self.wpdir)
        _,errors=G.scan(fake)
        self.assertIn('INVALID_EXPORT_DIRECTORY',errors)

    def test_missing_directory_fails_closed(self):
        x=G.audit(self.wpdir, Path(self.tmp.name)/'not-present', ARTICLES)
        self.assertEqual(x['status'],'INVALID_HARD_HOLD')
        self.assertIn('PREVIEW:INVALID_EXPORT_DIRECTORY',x['errors'])

    def test_safe_local_relative_link_does_not_look_like_purchase(self):
        for d in (self.wpdir,self.prdir):
            path=d/'hub-01.html';path.write_text(path.read_text().replace('</p>','</p><a href="/preparedness/">Archive</a>'))
        self.assertEqual(self.gate()['status'],'ALL_EXPORT_BYTES_REVIEW_HARD_HOLD')

    def test_no_network_and_no_fs_mutation(self):
        before=sorted((p.relative_to(self.tmp.name).as_posix(),p.read_bytes()) for p in Path(self.tmp.name).rglob('*.html'))
        self.gate()
        after=sorted((p.relative_to(self.tmp.name).as_posix(),p.read_bytes()) for p in Path(self.tmp.name).rglob('*.html'))
        self.assertEqual(before,after)

    def test_sha_is_real_sha256(self):
        import hashlib
        x=hashlib.sha256(b'hello').hexdigest()
        self.assertEqual(G.sha(b'hello'),x)
        self.assertTrue(G.SHA.fullmatch(x))

    def test_exports_do_not_include_source_html(self):
        data=self.gate()
        self.assertFalse(any('Draft and review required' in str(row) for row in data['exports']))

    def test_reject_background_embed(self):
        self.mutate('hub-01',lambda s:s.replace('</p>','</p><iframe src="https://example.org"></iframe>'))
        self.assertBad('ACTIVE_CONTENT:iframe')

    def test_reject_named_event_handler_in_article(self):
        self.mutate('article-01',lambda s:s.replace('<h1>','<h1 onload="go()">'))
        self.assertBad('INLINE_EVENT_HANDLER')


# Run the 35 original and 15 supplemental mutation cases separately: a route
# accidentally exempted from the source gate must fail, regardless of position.
def _generate_missing_original(slug):
    def run(self):
        (self.prdir / (slug + '.html')).unlink()
        self.assertBad('EXACT_EXPORT_FILENAME_SET_MISMATCH')
    return run


def _generate_unreviewed_extra(slug):
    def run(self):
        self.mutate(slug, lambda s: s.replace('Draft and review required.', 'Practical checklist.'))
        self.assertBad('SUPPLEMENTAL_REVIEW_WARNING_MISSING')
    return run

for _slug in ARTICLES:
    setattr(ExportCustody, 'test_missing_preview_' + _slug.replace('-','_'), _generate_missing_original(_slug))
for _slug in EXTRAS:
    setattr(ExportCustody, 'test_extra_warning_' + _slug.replace('-','_'), _generate_unreviewed_extra(_slug))

if __name__ == '__main__':
    unittest.main()


# Native wiring: demonstrate R389's historical 50-one-byte-file false positive
# is rejected by R390, without altering legacy isolated-validator test semantics.
class IntegratedGate(unittest.TestCase):
    def setUp(self):
        from copy import deepcopy
        spec2 = importlib.util.spec_from_file_location('r389_for_r390', MODULE.with_name('r389_integrated_candidate_custody.py'))
        self.r389 = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(self.r389)
        src = Path(__file__).with_name('test_r389_integrated_candidate_custody.py')
        test_spec = importlib.util.spec_from_file_location('r389_fixture_for_r390', src)
        mod = importlib.util.module_from_spec(test_spec); test_spec.loader.exec_module(mod)
        self.data = mod.fixture(); self.deep = deepcopy
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.wpdir = Path(self.tmp.name)/'wp';self.prdir = Path(self.tmp.name)/'preview'
        self.wpdir.mkdir(); self.prdir.mkdir()
        self.orig = [f'guide-{i:02d}' for i in range(35)]
        self.extras = [f'tool-{i:02d}' for i in range(15)]
        for slug in self.orig+self.extras:
            (self.wpdir/(slug+'.html')).write_text('x')
            (self.prdir/(slug+'.html')).write_text('x')
        self.full = {'status':'ALL_EXPORT_BYTES_REVIEW_HARD_HOLD','release_state':'DRAFT_HARD_HOLD',
                     'publication_approved':False,'qualified_safety_approved':False,
                     'merchant_offer_verified':False,'live_release_allowed':False,
                     'errors':[], 'evidence_sha256':'a'*64,
                     'counts':{'original_articles':35,'matched_export_pairs':50,
                               'supplemental_exports_needing_independent_review':15},
                     'exports':[{'slug':s, 'kind':'original_article' if s in self.orig else 'unreviewed_supplemental',
                                 'errors':[], 'qualified_review_required':True,
                                 'release_allowed':False,'merchant_verified':False}
                                for s in self.orig+self.extras]}

    def wrapper(self, d=None):
        return self.r389.reconcile_with_all_exports(*self.data, self.wpdir, self.prdir, self.full if d is None else d)

    def invalid(self, d, target):
        outcome=self.wrapper(d)
        self.assertEqual(outcome['status'],'INVALID_HARD_HOLD')
        self.assertIn(target,outcome['errors'])
        self.assertFalse(outcome['publication_approved'])

    def test_old_one_byte_supplementals_fail_new_native_gate(self):
        self.assertEqual(self.r389.reconcile(*self.data,self.wpdir,self.prdir)['status'],'INTEGRATED_REVIEW_HARD_HOLD')
        real=G.audit(self.wpdir,self.prdir,self.orig)
        self.assertEqual(real['status'],'INVALID_HARD_HOLD')
        self.invalid(real,'R390_ALL_EXPORT_CUSTODY_NOT_PASSED')

    def test_all_matching_review_reports_still_never_approve_release(self):
        d=self.wrapper()
        self.assertEqual(d['status'],'INTEGRATED_REVIEW_HARD_HOLD')
        self.assertIn('SUPPLEMENTAL_EXPORTS_REQUIRE_INDEPENDENT_REVIEW',d['release_blockers'])
        self.assertFalse(d['publication_approved'])

    def test_missing_full_custody_rejected(self):
        self.invalid({},'R390_ALL_EXPORT_CUSTODY_NOT_PASSED')

    def test_disallowed_merchant_state_rejected(self):
        d=self.deep(self.full);d['merchant_offer_verified']=True
        self.invalid(d,'R390_INAPPROPRIATE_RELEASE_STATE')

    def test_disallowed_publication_state_rejected(self):
        d=self.deep(self.full);d['publication_approved']=True
        self.invalid(d,'R390_INAPPROPRIATE_RELEASE_STATE')

    def test_extra_output_count_drift_rejected(self):
        d=self.deep(self.full);d['counts']['supplemental_exports_needing_independent_review']=14
        self.invalid(d,'R390_COUNTS_NOT_RECONCILED')

    def test_missing_output_report_rejected(self):
        d=self.deep(self.full);d['exports'].pop()
        self.invalid(d,'R390_EXPORT_IDENTITIES_NOT_RECONCILED')

    def test_approval_hidden_in_export_row_rejected(self):
        d=self.deep(self.full);d['exports'][0]['release_allowed']=True
        self.invalid(d,'R390_UNVERIFIED_OUTPUT_OR_APPROVAL')

    def test_malformed_export_digest_rejected(self):
        d=self.deep(self.full);d['evidence_sha256']='not-hex'
        self.invalid(d,'R390_EVIDENCE_DIGEST_MISSING')

    def test_wrong_extra_slug_rejected(self):
        d=self.deep(self.full);d['exports'][-1]['slug']='impostor'
        self.invalid(d,'R390_EXPORT_IDENTITIES_NOT_RECONCILED')

    def test_cross_source_flagged_error_fails(self):
        d=self.deep(self.full);d['errors']=['false-pass']
        self.invalid(d,'R390_ALL_EXPORT_CUSTODY_NOT_PASSED')
