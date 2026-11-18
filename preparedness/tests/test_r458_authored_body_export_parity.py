"""R458 tests: isolated adversarial body-custody oracle, NEVER QD clearance."""
from __future__ import annotations

from html import escape
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'tools' / 'r458_authored_body_export_parity.py'
spec = importlib.util.spec_from_file_location('r458_exact', MODULE)
r458 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r458)


class Library:
    def __init__(self):
        self.articles = {'family-communication-plan': {}, 'three-day-kit': {}}
        self.register = {'ready-plan': {}, 'fcc-contact': {}}
        self.sources = {
            'ready-plan': {'id': 'ready-plan', 'title': 'A & B "Plan"'},
            'fcc-contact': {'id': 'fcc-contact', 'title': 'FCC Communications'},
        }

    def source_for(self, meta, sid):
        return self.sources[sid]

    def url_path(self, slug):
        return '/preparedness/' + slug + '/'


BASE = '''<section class="pa-act" aria-labelledby="act-h">
<h2 id="act-h">What to do now</h2>
<ol><li><strong>Make a plan</strong> and call 911 for life-threatening emergencies.{{cite:ready-plan}}</li>
<li>Keep a backup contact, not a single phone.</li></ol>
<p class="pa-act-note">Children need a trusted adult and school consent; this is NOT a diagnosis.</p>
</section>
<h2 id="about">Why this matters</h2>
<p>Family reunification and emergency preparedness matter: 4 hours, 40°F, 2 weeks and 24 hours are not interchangeable.</p>
<table><caption>Critical source differences</caption><thead><tr><th scope="col">Source</th><th>Advice</th></tr></thead>
<tbody><tr><td>One</td><td>Follow local officials first.{{cite:fcc-contact}}</td></tr></tbody></table>
<p>Read the <a href="https://www.ready.gov/plan">original guide</a> and {{link:three-day-kit|the kit checklist}}.</p>
'''
BASE += '\n'.join(f'<p class="pa-constraint">Reader warning {i:02d}: retain original caveat-{i:02d} and context.</p>' for i in range(64))


def wrapper(body):
    return '<!-- wp:html -->\n<div class="pa pa-article"><div class="pa-body" id="pa-main">' + body + '</div></div>\n<!-- /wp:html -->'


def preview(body):
    return '<!doctype html><html><head><script>let x="</div>";</script></head><body>' + wrapper(body) + '</body></html>'


class TestBodyParity(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'preparedness'
        (self.root / 'tools').mkdir(parents=True)
        self.lib = Library()
        self.meta = {'slug': 'family-communication-plan', '_body': BASE}
        self.resolved, self.order = r458.independently_resolve_body(self.root, self.lib, self.meta, BASE)
        self.wp = wrapper(self.resolved)
        self.prev = preview(self.resolved)

    def test_full_body_both_surfaces_pass_structurally(self):
        result = r458.audit_pair(self.root, self.lib, self.meta, self.wp, self.prev)
        self.assertEqual(result['source_ids'], ['ready-plan', 'fcc-contact'])
        self.assertEqual(result['wordpress_body_sha256'], result['preview_body_sha256'])

    def test_citation_escapes_title_and_retains_first_use_order(self):
        self.assertIn('Source 1: A &amp; B &quot;Plan&quot;', self.resolved)
        self.assertIn('Source 2: FCC Communications', self.resolved)
        self.assertEqual(self.order, ['ready-plan', 'fcc-contact'])

    def test_link_to_known_article_resolves(self):
        self.assertIn('<a href="/preparedness/three-day-kit/">the kit checklist</a>', self.resolved)

    def test_link_to_missing_article_returns_plain_label(self):
        body = '<p>{{link:absent-page|Read the official page}}</p>'
        self.assertEqual(r458.independently_resolve_body(self.root, self.lib, self.meta, body)[0], '<p>Read the official page</p>')

    def test_unresolved_macro_holds(self):
        with self.assertRaises(r458.BodyHold):
            r458.independently_resolve_body(self.root, self.lib, self.meta, 'Unknown {{bad:token}}')

    def test_missing_source_holds(self):
        with self.assertRaises(r458.BodyHold):
            r458.independently_resolve_body(self.root, self.lib, self.meta, '{{cite:not-known}}')

    def test_source_identity_reassignment_holds(self):
        self.lib.sources['ready-plan']['id'] = 'another-id'
        with self.assertRaises(r458.BodyHold):
            r458.independently_resolve_body(self.root, self.lib, self.meta, BASE)

    def test_duplicate_body_holds(self):
        with self.assertRaises(r458.BodyHold):
            r458.extract_authored_region(self.wp + '<div class="pa-body" id="pa-main">COPY</div>')

    def test_missing_body_holds(self):
        with self.assertRaises(r458.BodyHold):
            r458.extract_authored_region('<div class="pa">No article body</div>')

    def test_empty_body_holds(self):
        with self.assertRaises(r458.BodyHold):
            r458.extract_authored_region('<div class="pa-body" id="pa-main"></div>')

    def test_unclosed_nested_div_holds(self):
        with self.assertRaises(r458.BodyHold):
            r458.extract_authored_region('<div class="pa-body" id="pa-main"><div>Unclosed</div>')

    def test_nested_divs_allowed(self):
        content = '<div><div>Keep actual 911 instructions</div></div><p>Text</p>'
        self.assertEqual(r458.extract_authored_region(wrapper(content)), content)

    def test_script_text_does_not_end_div(self):
        content = '<script>const s = "</div>";</script><p>Body follows.</p>'
        self.assertEqual(r458.extract_authored_region(wrapper(content)), content)

    def test_html_entities_preserved(self):
        body = '<p>Tom &amp; Ann &lt;3 emergency response</p>'
        self.assertEqual(r458.extract_authored_region(wrapper(body)), body)

    def test_wordpress_surface_truncated_holds(self):
        with self.assertRaises(r458.BodyHold):
            r458.audit_pair(self.root, self.lib, self.meta, wrapper(self.resolved[:-1]), self.prev)

    def test_preview_surface_truncated_holds(self):
        with self.assertRaises(r458.BodyHold):
            r458.audit_pair(self.root, self.lib, self.meta, self.wp, preview(self.resolved[:-1]))

    def test_change_only_in_preview_holds(self):
        with self.assertRaises(r458.BodyHold):
            r458.audit_pair(self.root, self.lib, self.meta, self.wp, self.prev.replace('40°F', '45°F'))

    def test_change_only_in_wp_holds(self):
        with self.assertRaises(r458.BodyHold):
            r458.audit_pair(self.root, self.lib, self.meta, self.wp.replace('call 911', 'call 411'), self.prev)

    def test_substituted_bibliography_not_body_no_false_pass(self):
        tampered = self.wp + '<section class="pa-sources">Correct words in footer</section>'
        with self.assertRaises(r458.BodyHold):
            r458.audit_pair(self.root, self.lib, self.meta, tampered.replace('call 911', 'call 411'), self.prev)

    def test_inline_js_exact_byte_roundtrip(self):
        (self.root / 'tools' / 'helper.js').write_text('const x="&amp;";\n', encoding='utf-8')
        resolved, _ = r458.independently_resolve_body(self.root, self.lib, self.meta, '<script>{{inline-js:helper.js}}</script>')
        self.assertEqual(resolved, '<script>const x="&amp;";\n</script>')

    def test_inline_js_missing_holds(self):
        with self.assertRaises(r458.BodyHold):
            r458.independently_resolve_body(self.root, self.lib, self.meta, '<script>{{inline-js:missing.js}}</script>')

    def test_inline_js_symlink_holds(self):
        src = self.root / 'tools' / 'real.js'
        src.write_text('console.log(1)')
        (self.root / 'tools' / 'helper.js').symlink_to(src)
        with self.assertRaises(r458.BodyHold):
            r458.independently_resolve_body(self.root, self.lib, self.meta, '{{inline-js:helper.js}}')

    def test_inline_js_parent_tools_symlink_holds(self):
        root = self.root / 'linked_root'
        root.mkdir()
        (root / 'tools').symlink_to(self.root / 'tools', target_is_directory=True)
        with self.assertRaises(r458.BodyHold):
            r458.checked_inline_js(root, 'helper.js')

    def test_missing_root_native_holds(self):
        with self.assertRaises(r458.BodyHold):
            r458.verify_native(self.root / 'absent')

    def test_missing_native_build_hold_cli_exit2(self):
        run = subprocess.run([sys.executable, '-I', str(MODULE), '--root', str(self.root)],
                             capture_output=True, text=True, check=False)
        self.assertEqual(run.returncode, 2)
        self.assertIn('DRAFT_HARD_HOLD', run.stdout)
        self.assertIn('"qualified_qd_pass": false', run.stdout)

    def test_class_order_does_not_change_body_identity(self):
        s = wrapper('text').replace('class="pa-body" id="pa-main"', 'id="pa-main" class="custom pa-body"')
        self.assertEqual(r458.extract_authored_region(s), 'text')

    def test_duplicate_source_occurrence_preserves_numbers(self):
        body = '<p>{{cite:ready-plan}} repeated {{cite:ready-plan}} then {{cite:fcc-contact}}</p>'
        expanded, ids = r458.independently_resolve_body(self.root, self.lib, self.meta, body)
        self.assertEqual(ids, ['ready-plan', 'fcc-contact'])
        self.assertEqual(expanded.count('href="#src-1"'), 2)

    def test_source_html_attribute_quote_escape(self):
        self.lib.sources['ready-plan']['title'] = '<script>" &'
        expanded, _ = r458.independently_resolve_body(self.root, self.lib, self.meta, '{{cite:ready-plan}}')
        self.assertIn('&lt;script&gt;&quot; &amp;', expanded)


# Each generated method is its OWN unittest (not a subTest), verifying loss of
# a different original 64-paragraph reading-scope/safety caveat in ONE export.
def _make_missing_caveat_test(n, target):
    def test(self):
        old = f'caveat-{n:02d}'
        replacement = f'REDACTED-{n:02d}'
        bad = self.resolved.replace(old, replacement)
        self.assertNotEqual(bad, self.resolved)
        with self.assertRaises(r458.BodyHold):
            if target == 'wp':
                r458.audit_pair(self.root, self.lib, self.meta, wrapper(bad), self.prev)
            else:
                r458.audit_pair(self.root, self.lib, self.meta, self.wp, preview(bad))
    return test


for n in range(64):
    setattr(TestBodyParity, f'test_adversarial_caveat_loss_{n:02d}',
            _make_missing_caveat_test(n, 'wp' if n % 2 == 0 else 'preview'))


if __name__ == '__main__':
    unittest.main()
