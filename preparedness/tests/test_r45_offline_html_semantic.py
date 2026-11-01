"""R45: private offline reviewer-HTML semantic and navigation safety QA.

Synthetic hostile markup and hostile *re-pinned* ZIPs are deliberately tested:
a forged replacement manifest can pass R44 byte custody if its anchor is also
replaced, but must still fail R45's independent exact HTML/link contract.
"""
from __future__ import annotations

from copy import deepcopy
from io import BytesIO
import sys
from pathlib import Path
import unittest
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from test_r43_offline_review_bundle import example, view
import reviewer_private_zip_gate as r44
import reviewer_html_semantic_gate as gate

class IndividualPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = r44.r43.page(
            'Synthetic article', '<section><h2>Evidence</h2>'
            '<p>Visible inert https://example.org/source?c=1&amp;r=2</p>'
            '</section>', '../index.html')

    def assertRejected(self, proposed):
        self.assertNotEqual(proposed, self.original, 'negative mutation is a no-op')
        with self.assertRaises((gate.SemanticHold, ValueError, TypeError)):
            gate.inspect_page('articles/synthetic.html', proposed)

    def test_valid_article_page(self):
        self.assertEqual(gate.inspect_page('articles/synthetic.html',
                         self.original), ('../index.html',))

    def test_legitimate_inert_source_url_is_not_outbound_navigation(self):
        self.assertIn('https://example.org/source', self.original)
        self.assertEqual(gate.inspect_page('articles/synthetic.html',
                         self.original), ('../index.html',))

    def test_historical_source_record_with_html_is_literal_when_escaped(self):
        payload = r44.r43.page(
            'Source evidence', '<section><pre>&lt;img src="https://evil.test"&gt;'
            '&lt;a href="javascript:alert(1)"&gt;</pre></section>',
            '../index.html')
        self.assertEqual(gate.inspect_page('articles/synthetic.html', payload),
                         ('../index.html',))

    def test_frozen_stylesheet_is_explicit_and_non_networked(self):
        self.assertIn(gate.CSS, self.original)
        self.assertNotIn('url(', gate.CSS)
        self.assertNotIn('@import', gate.CSS)
        self.assertNotIn('\\', gate.CSS)

class FullBundle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet, cls.expected = example(uncited=True)
        cls.pin42 = cls.packet['fingerprint_sha256']
        cls.desk = view(cls.packet, cls.expected)
        cls.pin43 = cls.desk['manifest']['fingerprint_sha256']
        cls.bundle = r44.build_private_zip(cls.packet,
                    trusted_r42_sha256=cls.pin42, expected=cls.expected)
        with ZipFile(BytesIO(cls.bundle['zip_bytes'])) as z:
            cls.pages = {name: z.read(name) for name in
                         cls.desk['manifest']['files']}
        cls.first_article = sorted(n for n in cls.pages
                                   if n.startswith('articles/'))[0]

    def test_full_synthetic_zip_navigation_audit(self):
        report = gate.audit_private_zip_html(
            self.bundle['zip_bytes'], trusted_r42_sha256=self.pin42,
            trusted_r43_sha256=self.pin43, expected=self.expected)
        self.assertEqual(report['release_state'], 'HOLD')
        self.assertEqual(report['pages_checked'], self.expected[0] +
                         self.expected[1] + 2)
        self.assertEqual(report['private_local_links_checked'],
                         2 * (self.expected[0] + self.expected[1]) + 2)
        self.assertFalse(report['may_publish'])
        self.assertFalse(report['qualified_safety_clearance'])
        self.assertFalse(report['independent_QD_approval'])
        self.assertFalse(report['human_review_started'])
        self.assertFalse(report['external_or_active_links_allowed'])

    def test_deterministic_semantic_report(self):
        args = dict(trusted_r42_sha256=self.pin42,
                    trusted_r43_sha256=self.pin43, expected=self.expected)
        self.assertEqual(gate.audit_private_zip_html(self.bundle['zip_bytes'], **args),
                         gate.audit_private_zip_html(self.bundle['zip_bytes'], **args))

    def test_all_synthetic_pages_accepted_individually(self):
        for name, body in self.pages.items():
            self.assertIsInstance(gate.inspect_page(name, body.decode()), tuple)

    def test_invalid_external_source_pin_rejected(self):
        with self.assertRaises(gate.SemanticHold):
            gate.audit_private_zip_html(self.bundle['zip_bytes'],
                trusted_r42_sha256='a'*64,
                trusted_r43_sha256=self.pin43, expected=self.expected)

    def test_invalid_rendered_manifest_pin_rejected(self):
        with self.assertRaises(gate.SemanticHold):
            gate.audit_private_zip_html(self.bundle['zip_bytes'],
                trusted_r42_sha256=self.pin42,
                trusted_r43_sha256='a'*64, expected=self.expected)

    def test_wrong_article_census_rejected(self):
        wrong = list(self.expected)
        wrong[0] += 1
        with self.assertRaises(gate.SemanticHold):
            gate.audit_private_zip_html(self.bundle['zip_bytes'],
                trusted_r42_sha256=self.pin42,
                trusted_r43_sha256=self.pin43, expected=tuple(wrong))

    def forge_zip(self, name, altered):
        """Attacker re-hashes BOTH manifests: simulate stolen R43 signing pin.

        Verify the forged bytes actually satisfy R44 when the trust pin itself
        is replaced. R45 must still reject the unsafe HTML or broken links.
        """
        members = dict(self.pages)
        members[name] = altered.encode('utf-8')
        manifest = deepcopy(self.bundle['manifest'])
        source = manifest['source_R43_manifest']
        source['files'][name] = {
            'sha256_utf8': r44.sha(members[name]),
            'bytes_utf8': len(members[name])}
        source['fingerprint_sha256'] = r44.sha(r44.canonical({
            k: v for k, v in source.items() if k != 'fingerprint_sha256'}))
        newpin = source['fingerprint_sha256']
        manifest['parent_R43_fingerprint_sha256'] = newpin
        manifest['fingerprint_sha256'] = r44.sha(r44.canonical({
            k: v for k, v in manifest.items() if k != 'fingerprint_sha256'}))
        members['review-manifest.json'] = r44.canonical(manifest) + b'\n'
        raw = r44._archive(members)
        checked = r44.verify_private_zip(raw,
            trusted_r42_sha256=self.pin42,
            trusted_r43_sha256=newpin, expected=self.expected)
        self.assertEqual(checked, manifest, 'R44 did not accept synthetic forgery')
        return raw, newpin

    def assertForgeryRejected(self, name, bad):
        self.assertNotEqual(bad.encode(), self.pages[name])
        raw, pin = self.forge_zip(name, bad)
        with self.assertRaises(gate.SemanticHold):
            gate.audit_private_zip_html(raw,
                trusted_r42_sha256=self.pin42, trusted_r43_sha256=pin,
                expected=self.expected)

    def test_forged_index_external_navigation_rejected(self):
        html = self.pages['index.html'].decode()
        self.assertForgeryRejected('index.html',
            html.replace('href="global-source-variants.html"',
                         'href="https://attacker.invalid/"', 1))

    def test_forged_index_dropped_article_rejected(self):
        html = self.pages['index.html'].decode()
        self.assertForgeryRejected('index.html',
            html.replace('href="' + self.first_article + '"',
                         'href="global-source-variants.html"', 1))

    def test_forged_index_duplicate_article_rejected(self):
        html = self.pages['index.html'].decode()
        fragment = '<li><a href="' + self.first_article + '">DUPLICATE</a></li>'
        self.assertForgeryRejected('index.html',
            html.replace('</ol>', fragment + '</ol>', 1))

    def test_forged_article_external_back_link_rejected(self):
        html = self.pages[self.first_article].decode()
        self.assertForgeryRejected(self.first_article,
            html.replace('href="../index.html"',
                         'href="https://attacker.invalid/"', 1))

    def test_forged_article_extra_link_rejected(self):
        html = self.pages[self.first_article].decode()
        self.assertForgeryRejected(self.first_article,
            html.replace('</main>',
                         '<a href="../index.html">Extra</a></main>', 1))

    def test_forged_visible_warning_class_removed_rejected(self):
        html = self.pages[self.first_article].decode()
        self.assertForgeryRejected(self.first_article,
            html.replace('<p class="hold">', '<p>', 1))

    def test_forged_weaker_csp_rejected(self):
        html = self.pages[self.first_article].decode()
        self.assertForgeryRejected(self.first_article,
            html.replace("default-src 'none'", "default-src 'self'", 1))

    def test_forged_css_url_fetch_rejected(self):
        html = self.pages[self.first_article].decode()
        self.assertForgeryRejected(self.first_article,
            html.replace('background:#f5f5f1',
                         'background:url(https://attacker.invalid/h)', 1))

    def test_forged_autofocus_unsafe_attribute_rejected(self):
        html = self.pages[self.first_article].decode()
        self.assertForgeryRejected(self.first_article,
            html.replace('<a href=', '<a autofocus href=', 1))

    def test_forged_meta_refresh_rejected(self):
        html = self.pages[self.first_article].decode()
        self.assertForgeryRejected(self.first_article,
            html.replace('</head>', '<meta http-equiv="refresh" '
                         'content="0;url=https://attacker.invalid/"></head>', 1))

    def test_forged_external_stylesheet_rejected(self):
        html = self.pages[self.first_article].decode()
        self.assertForgeryRejected(self.first_article,
            html.replace('</head>', '<link rel="stylesheet" '
                         'href="https://attacker.invalid/a.css"></head>', 1))

    def test_forged_source_text_active_link_rejected(self):
        html = self.pages[self.first_article].decode()
        self.assertForgeryRejected(self.first_article,
            html.replace('</main>', '<a href="https://attacker.invalid/">'
                         'Original source</a></main>', 1))


# Each mutation is an independent negative unittest: source safety regressions
# should be identifiable individually, rather than hidden inside subTest counts.
BAD_TAGS = {
    'script': '<script>fetch("https://attacker.invalid")</script>',
    'iframe': '<iframe src="https://attacker.invalid"></iframe>',
    'img': '<img src="https://attacker.invalid/track">',
    'form': '<form action="https://attacker.invalid/"></form>',
    'input': '<input autofocus value="secret">',
    'object': '<object data="https://attacker.invalid/"></object>',
    'embed': '<embed src="https://attacker.invalid/">',
    'link': '<link rel="preload" href="https://attacker.invalid/">',
    'base': '<base href="https://attacker.invalid/">',
    'svg': '<svg><a href="https://attacker.invalid/">x</a></svg>',
    'video': '<video src="https://attacker.invalid/x"></video>',
    'audio': '<audio src="https://attacker.invalid/x"></audio>',
    'canvas': '<canvas></canvas>',
    'table': '<table><tr><td>x</td></tr></table>',
    'noscript': '<noscript><a href="x">r</a></noscript>',
    'template': '<template><img src="x"></template>',
    'style_extra': '<style>@import "https://attacker.invalid"</style>',
    'meta_refresh': '<meta http-equiv="refresh" content="0;url=//x">',
    'details': '<details open><summary>secret</summary></details>',
    'button': '<button onclick="alert(1)">x</button>',
}
BAD_ATTRIBUTES = {
    'body_onload': ('<body>', '<body onload="alert(1)">'),
    'html_onmousemove': ('<html lang="en">', '<html lang="en" onmousemove="x">'),
    'h1_event': ('<h1>', '<h1 onclick="alert(1)">'),
    'main_event': ('<main>', '<main onmouseover="x">'),
    'anchor_target': ('href="../index.html"', 'href="../index.html" target="_blank"'),
    'anchor_download': ('href="../index.html"', 'href="../index.html" download'),
    'anchor_event': ('href="../index.html"', 'href="../index.html" onclick="x"'),
    'anchor_rel': ('href="../index.html"', 'href="../index.html" rel="external"'),
    'anchor_duplicate_href': ('href="../index.html"',
                              'href="../index.html" href="https://attacker.invalid"'),
    'paragraph_style': ('<p class="hold">', '<p class="hold" style="display:none">'),
    'heading_style': ('<h1>', '<h1 style="display:none">'),
    'main_hidden': ('<main>', '<main hidden>'),
    'main_dir': ('<main>', '<main dir="auto">'),
    'style_nonce': ('<style>', '<style nonce="forged">'),
    'meta_event': ('<meta charset="utf-8">',
                   '<meta charset="utf-8" onload="alert(1)">'),
}
BAD_LINKS = (
    'https://attacker.invalid/', 'http://attacker.invalid/', '//attacker.invalid',
    'javascript:alert(1)', 'data:text/html,%3Cscript%3E',
    'file:///etc/passwd', 'mailto:test@example.org', 'tel:+15551234567',
    '../../index.html', 'articles/../index.html', '/preparedness/',
    '#fragment', 'index.html', '../global-source-variants.html',
    '?autoplay=1', '\\\\attacker.invalid\\share',
)
BAD_DOCUMENT = {
    'removed_doctype': lambda s: s.replace('<!doctype html>', '', 1),
    'changed_doctype': lambda s: s.replace('doctype html', 'DOCTYPE svg', 1),
    'added_comment': lambda s: s.replace('<head>', '<head><!-- x -->', 1),
    'added_pi': lambda s: s.replace('<head>', '<head><?debug on?>', 1),
    'removed_final_html': lambda s: s.replace('</html>\n', '', 1),
    'broken_main': lambda s: s.replace('</main>', '</section>', 1),
    'unbalanced_h1': lambda s: s.replace('</h1>', '</h2>', 1),
    'duplicate_charset': lambda s: s.replace('</head>',
        '<meta charset="utf-8"></head>', 1),
    'missing_charset': lambda s: s.replace('<meta charset="utf-8">', '', 1),
    'changed_charset': lambda s: s.replace('charset="utf-8"', 'charset="iso-8859-1"', 1),
    'removed_warning_class': lambda s: s.replace('<p class="hold">', '<p>', 1),
    'suppressed_warning': lambda s: s.replace(
        'PRIVATE / UNVERIFIED / HOLD.', 'EDITORIALLY APPROVED.', 1),
    'weaken_default_src': lambda s: s.replace(
        "default-src 'none'", "default-src 'self'", 1),
    'weaken_connect_src': lambda s: s.replace(
        "connect-src 'none'", "connect-src *", 1),
    'weaken_form_action': lambda s: s.replace(
        "form-action 'none'", "form-action *", 1),
    'weaken_base_uri': lambda s: s.replace(
        "base-uri 'none'", "base-uri *", 1),
    'weaken_img_src': lambda s: s.replace(
        "img-src 'none'", "img-src https:", 1),
    'css_remote_url': lambda s: s.replace(
        'background:#f5f5f1', 'background:url(https://attacker.invalid/x)', 1),
    'css_hidden_banner': lambda s: s.replace(
        'font-weight:700}', 'font-weight:700;display:none}', 1),
    'css_import': lambda s: s.replace(
        '<style>', '<style>@import "https://attacker.invalid";', 1),
}

def negative_method(name, transform):
    def execute(self):
        self.assertRejected(transform(self.original))
    execute.__name__ = 'test_reject_' + name
    return execute

for _label, _html in BAD_TAGS.items():
    setattr(IndividualPage, 'test_reject_tag_' + _label,
            negative_method('tag_'+_label,
                lambda src, addition=_html: src.replace('</main>',
                    addition + '</main>', 1)))
for _label, (_old, _new) in BAD_ATTRIBUTES.items():
    setattr(IndividualPage, 'test_reject_attr_' + _label,
            negative_method('attr_'+_label,
                lambda src, a=_old, b=_new: src.replace(a, b, 1)))
for _number, _href in enumerate(BAD_LINKS):
    setattr(IndividualPage, 'test_reject_link_' + str(_number).zfill(2),
            negative_method('link_' + str(_number),
                lambda src, target=_href: src.replace(
                    'href="../index.html"', 'href="' + target + '"', 1)))
for _label, _func in BAD_DOCUMENT.items():
    setattr(IndividualPage, 'test_reject_document_' + _label,
            negative_method('document_'+_label, _func))

if __name__ == '__main__':
    unittest.main()
