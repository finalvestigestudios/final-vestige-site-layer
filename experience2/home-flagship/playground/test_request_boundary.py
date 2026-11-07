"""Exact policy tests and one real local Chromium interception study.

These are browser-network fixture checks; they do not claim native WordPress
staging, actual media loads, WCAG or commerce acceptance.
"""
import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import unittest
from request_boundary import admit_request

PREVIEW='http://127.0.0.1:9400/'
GOOD_ORIGIN='https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp'
GOOD_CDN='https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg?fit=644%2C1024&ssl=1'

class RequestBoundaryTests(unittest.TestCase):
    def test_explicit_preview_origin(self):
        for u in ['http://127.0.0.1:9400/', 'http://127.0.0.1:9400/wp-content/themes/assembler/style.css',
                  'http://127.0.0.1:9400/wp-json/', 'http://127.0.0.1:9400/fv-ex2-review/?v=1']:
            with self.subTest(u=u):
                self.assertEqual(admit_request(u, PREVIEW), 'ISOLATED_PREVIEW_ORIGIN')
    def test_unexpected_loopback_port_and_production_qa(self):
        for u in ['http://127.0.0.1:9401/', 'http://localhost:9400/',
                  'https://finalvestige.com/', 'https://finalvestige.com/focus/?subscribe=true',
                  'https://vestigefinal-tezws.wpcomstaging.com/', 'http://127.0.0.1:9400.evil.example/']:
            with self.subTest(u=u), self.assertRaises(ValueError):
                admit_request(u, PREVIEW)
    def test_verified_media_origin_and_cdn(self):
        self.assertEqual(admit_request(GOOD_ORIGIN, PREVIEW),'APPROVED_ARCHIVE_ORIGIN')
        self.assertEqual(admit_request(GOOD_CDN, PREVIEW),'APPROVED_ARCHIVE_CDN')
    def test_block_disallowed_external_tracking_assets_and_changed_media(self):
        bad = ['https://analytics.ahrefs.com/analytics.js', 'https://evil.example/beacon?document=private',
               'https://www.awin1.com/cshow.php?s=1', 'https://finalvestige.com/wp-json/',
               'https://finalvestige.com/wp-content/uploads/2026/08/other.webp',
               GOOD_ORIGIN+'?utm_source=evil',
               GOOD_CDN.replace('644%2C1024','700%2C1000'),
               GOOD_CDN.replace('i0.wp.com','i0.wp.com.evil.example'),
               'http://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp',
               'https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp?fit=300%2C233&ssl=0']
        for u in bad:
            with self.subTest(u=u), self.assertRaises(ValueError): admit_request(u,PREVIEW)
    def test_main_navigation_cannot_become_offsite(self):
        for u in [GOOD_ORIGIN,GOOD_CDN, 'https://finalvestige.com/focus/']:
            with self.subTest(u=u),self.assertRaises(ValueError):
                admit_request(u,PREVIEW,navigation=True)
        self.assertEqual(admit_request(PREVIEW,PREVIEW,navigation=True),'ISOLATED_PREVIEW_ORIGIN')
    def test_non_network_inline_urls(self):
        self.assertEqual(admit_request('data:image/svg+xml,%3Csvg%3E',PREVIEW),'INLINE_NO_NETWORK')
        self.assertEqual(admit_request('blob:http://127.0.0.1:9400/abc',PREVIEW),'INLINE_NO_NETWORK')
        with self.assertRaises(ValueError):admit_request('javascript:alert(1)',PREVIEW)
        with self.assertRaises(ValueError):admit_request('data:text/html,evil',PREVIEW,navigation=True)

class BrowserInterceptionTests(unittest.TestCase):
    def test_chromium_intercepts_unapproved_requests_in_memory_fixture(self):
        """Real Chromium routing; set_content because container blocks localhost navigation."""
        from playwright.sync_api import sync_playwright
        blocked=[];allowed=[]
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':390,'height':800})
            def check(route):
                try:
                    label=admit_request(route.request.url,PREVIEW,
                        navigation=route.request.is_navigation_request() and route.request.frame==page.main_frame)
                except ValueError as e:
                    blocked.append((route.request.url,str(e)));route.abort()
                else:
                    allowed.append((route.request.url,label));route.continue_()
            page.route('**/*',check)
            html='''<!doctype html><html><body>
              <a href="https://finalvestige.com/focus/" id="f">Fieldbook</a>
              <img src="https://evil.example/bad.webp" id="bad">
              <script src="https://analytics.ahrefs.com/analytics.js"></script>
              <p id="ok">Visible content</p></body></html>'''
            page.set_content(html,wait_until='load')
            self.assertTrue(page.locator('#ok').is_visible())
            self.assertEqual(set(x[0] for x in blocked),
                {'https://evil.example/bad.webp','https://analytics.ahrefs.com/analytics.js'})
            self.assertEqual(allowed,[])
            # Clicking a staged CTA must not visit the live production destination.
            page.locator('#f').click()
            page.wait_for_timeout(150)
            self.assertNotIn('finalvestige.com',page.url)
            # This container may block navigation before Playwright sees it.
            # The separate navigation policy unit test covers that decision.
            browser.close()

if __name__=='__main__': unittest.main(verbosity=2)
