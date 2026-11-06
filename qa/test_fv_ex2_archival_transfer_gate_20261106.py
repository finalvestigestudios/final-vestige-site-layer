"""Native Chromium negative controls for evidence receipts (synthetic assets)."""
import base64
import hashlib
import unittest
from playwright.sync_api import sync_playwright
from fv_ex2_archival_transfer_gate_20261106 import audit_archival_transfers

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9WsK3uQAAAAASUVORK5CYII=')
PREFIX = 'https://synthetic-archive.test/'


def example_html(apollo=True, franklin=True, alt=True, responsive=False):
    def img(name):
        src = PREFIX + name
        variants = f' srcset="{src}?width=390 390w, {src}?width=1440 1440w" sizes="100vw"' if responsive else ''
        a = ('Simulated archive photo' if alt else '')
        return f'<img src="{src}" {variants} alt="{a}" width="500" height="500">'
    return '<html><body>' + (img('s67-19766.webp') if apollo else '') + ('<div style="height:1200px"></div>' + img('Franklinexpeditionnote.jpg') if franklin else '') + '</body></html>'


class ArchivalGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def assess(self, *, apollo=True, franklin=True, alt=True, responsive=False, status=200,
               body=PNG, keep_receipts=True):
        context = self.browser.new_context(viewport={'width':390,'height':844})
        page = context.new_page()
        transfers = {}

        def receive(response):
            if not keep_receipts:
                return
            try:
                b = response.body()
                transfers[response.url] = {'status':response.status,
                    'actual_body_bytes':len(b), 'sha256':hashlib.sha256(b).hexdigest()}
            except Exception:
                return

        page.on('response', receive)
        page.route('**/synthetic-archive.test/**', lambda r: r.fulfill(status=status,
                  content_type='image/png', body=body))
        try:
            page.set_content(example_html(apollo,franklin,alt,responsive), wait_until='load')
            return audit_archival_transfers(page,transfers)
        finally:
            context.close()

    def test_two_valid_synthetic_images(self):
        proof=self.assess()
        self.assertTrue(proof['passed'], proof)
        self.assertEqual(len(proof['widths']),2)
        self.assertEqual(proof['rights_clearance'],'NOT_ASSESSED')

    def test_responsive_urls_preserve_bytes_and_hide_queries(self):
        proof=self.assess(responsive=True)
        self.assertTrue(proof['passed'],proof)
        self.assertTrue(all('?' not in e['selected_url'] for w in proof['widths'].values() for e in w.values()))
        self.assertTrue(all(e['body_bytes']>0 and len(e['sha256'])==64 for w in proof['widths'].values() for e in w.values()))

    def test_missing_apollo_is_blocked(self):
        self.assertFalse(self.assess(apollo=False)['passed'])

    def test_missing_franklin_is_blocked(self):
        self.assertFalse(self.assess(franklin=False)['passed'])

    def test_404_is_blocked(self):
        self.assertFalse(self.assess(status=404)['passed'])

    def test_empty_image_is_blocked(self):
        self.assertFalse(self.assess(body=b'')['passed'])

    def test_empty_alt_is_blocked(self):
        self.assertFalse(self.assess(alt=False)['passed'])

    def test_no_http_receipt_is_blocked(self):
        self.assertFalse(self.assess(keep_receipts=False)['passed'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
