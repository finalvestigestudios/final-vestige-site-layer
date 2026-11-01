"""Adversarial exact-source checks for private HTTP visual replay completeness.

Only synthetic HTTP/image resources: no WordPress production or historical media.
"""
import asyncio
from pathlib import Path
import tempfile
import unittest
from replay_wordpress_stage_browser import Capture, Hold, audit_css_dependencies, browser_review, passing
from test_replay_wordpress_stage_browser import ProbeServer


class ReplayResourceCompleteness(unittest.TestCase):
    def test_linked_css_background_unverified_refused(self):
        with ProbeServer() as s:
            s.data['/assets/style.css'] = (b'main { background:url("/unverified.jpg") }', 'text/css')
            with self.assertRaisesRegex(Hold, 'CSS url'):
                Capture(s.url, s.manifest).assemble()

    def test_inline_style_unverified_refused(self):
        with ProbeServer() as s:
            page = s.data['/'][0].decode().replace('<main ', '<main style="background:url(/rogue.jpg)" ')
            s.data['/'] = (page.encode(), 'text/html')
            with self.assertRaisesRegex(Hold, 'inline style attribute'):
                Capture(s.url, s.manifest).assemble()

    def test_inline_style_tag_remote_font_refused(self):
        with ProbeServer() as s:
            page = s.data['/'][0].decode().replace('</head>', '<style>@font-face{src:url(https://bad.example/font.woff2)}</style></head>')
            s.data['/'] = (page.encode(), 'text/html')
            with self.assertRaisesRegex(Hold, 'inline stylesheet'):
                Capture(s.url, s.manifest).assemble()

    def test_css_import_fails_before_replay(self):
        with ProbeServer() as s:
            s.data['/assets/style.css'] = (b'@import url("/theme.css");', 'text/css')
            with self.assertRaisesRegex(Hold, 'CSS @import'):
                Capture(s.url, s.manifest).assemble()

    def test_iframe_external_refused(self):
        with ProbeServer() as s:
            page = s.data['/'][0].decode().replace('</main>', '<iframe src="https://bad.example/" title="unverified"></iframe></main>')
            s.data['/'] = (page.encode(), 'text/html')
            with self.assertRaisesRegex(Hold, 'embedded/picture/media'):
                Capture(s.url, s.manifest).assemble()

    def test_picture_srcset_refused(self):
        with ProbeServer() as s:
            page = s.data['/'][0].decode().replace('</main>', '<picture><source srcset="/unverified.webp"><img alt="x" src="/media/c0.gif"></picture></main>')
            s.data['/'] = (page.encode(), 'text/html')
            with self.assertRaisesRegex(Hold, 'embedded/picture/media'):
                Capture(s.url, s.manifest).assemble()

    def test_preload_refused(self):
        with ProbeServer() as s:
            page = s.data['/'][0].decode().replace('</head>', '<link rel="preload" as="image" href="/unknown.png"></head>')
            s.data['/'] = (page.encode(), 'text/html')
            with self.assertRaisesRegex(Hold, 'preloaded'):
                Capture(s.url, s.manifest).assemble()

    def test_data_and_fragment_css_allowed(self):
        audit_css_dependencies('a{background:url(data:image/gif;base64,AA==)}b{filter:url(#mask)}', 'test')

    def test_linked_stylesheet_media_preserved(self):
        with ProbeServer() as s:
            page = s.data['/'][0].decode().replace('rel="stylesheet"', 'rel="stylesheet" media="print"')
            s.data['/'] = (page.encode(), 'text/html')
            html, _ = Capture(s.url, s.manifest).assemble()
            self.assertIn('media="print"', html)
            self.assertNotIn('<link rel="stylesheet"', html)

    def test_dynamic_script_remote_request_is_recorded_as_failure(self):
        with ProbeServer() as s, tempfile.TemporaryDirectory() as d:
            s.data['/assets/flagship.js'] = (b'fetch("https://bad.example/nope").catch(()=>{});', 'text/javascript')
            html, _ = Capture(s.url, s.manifest).assemble()
            _, checks = asyncio.run(browser_review(html, Path(d), '/usr/bin/chromium'))
            self.assertFalse(passing(checks))
            self.assertFalse(checks['390']['no_unverified_network'])
            self.assertTrue(any('bad.example' in x['url'] for x in checks['390']['blocked_requests']))

    def test_delayed_script_request_cannot_create_false_visual_pass(self):
        with ProbeServer() as s, tempfile.TemporaryDirectory() as d:
            s.data['/assets/flagship.js'] = (
                b'setTimeout(()=>fetch("https://bad.example/delayed").catch(()=>{}),260);',
                'text/javascript')
            html, _ = Capture(s.url, s.manifest).assemble()
            _, checks = asyncio.run(browser_review(html, Path(d), '/usr/bin/chromium'))
            self.assertFalse(passing(checks), 'deferred network was silently ignored')
            self.assertTrue(any('bad.example/delayed' in v['url']
                                for v in checks['390']['blocked_requests']))

    def test_visual_capture_for_local_whitelisted_assets_still_passes(self):
        with ProbeServer() as s, tempfile.TemporaryDirectory() as d:
            html, report = Capture(s.url, s.manifest).assemble()
            _, checks = asyncio.run(browser_review(html, Path(d), '/usr/bin/chromium'))
            self.assertTrue(passing(checks), checks)
            self.assertEqual(report['archival_images_verified'], 3)
            self.assertTrue(all(c['no_unverified_network'] for c in checks.values()))


if __name__ == '__main__':
    unittest.main()
