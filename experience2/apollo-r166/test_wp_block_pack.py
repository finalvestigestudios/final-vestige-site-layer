"""R167 actual Chromium test on source-derived Gutenberg editor fixture.
This is NOT an installed WordPress or genuine axe-core acceptance test.
"""
import hashlib
import json
import os
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
from wp_block_pack import package, START, END, TAG
from build_offline import REQUIRED_NASA

HERE = Path(__file__).resolve().parent
R166_TEST = (HERE / 'test_integrated_bridge.py').read_text(encoding='utf-8')
exec(compile(R166_TEST.split('class Integration(unittest.TestCase):')[0], 'r166-fixture', 'exec'), globals())
# The verified source excerpt and the old controller are combined into two Custom HTML blocks.

def original():
    # Existing WordPress page contains nine Custom HTML blocks; represented as two,
    # the last of which is its page behavior script.
    return START + '\n' + CSS + '\n' + EXCERPT + '\n' + END + ('\n' + START + '\n<section data-fixture=\"inert\"></section>\n' + END) * 7 + '\n' + START + '\n' + OLD + '\n' + END


class WordPressBlockPackaging(unittest.TestCase):
    def test_structure_and_determinism(self):
        src = original()
        out, manifest = package(src)
        out2, manifest2 = package(src)
        self.assertEqual((out, manifest), (out2, manifest2))
        self.assertEqual(manifest['gutenberg_custom_html_blocks'], 9)
        self.assertEqual(out.count('<!-- wp:html -->'), 9)
        self.assertEqual(out.count('<!-- /wp:html -->'), 9)
        self.assertIn(TAG, out[out.rfind(START):out.rfind(END)])
        self.assertTrue(all(u in out for u in REQUIRED_NASA))
        self.assertNotIn('const index = t < 6 ? 0 : (t < 11.3 ? 1 : 2);', out)
        self.assertEqual(out.count('Read original investigation'), src.count('Read original investigation'))
        self.assertRaises(ValueError, package, out)
        for damaged in (src.replace(END, '', 1),
                        src.replace('t < 6 ?', 't < 7 ?'),
                        src.replace(REQUIRED_NASA[0], 'https://example.invalid/'),
                        src + 'outside a WordPress block',
                        src.replace(START, '', 1)):
            self.assertRaises(ValueError, package, damaged)

    def test_chromium_source_navigation(self):
        source, receipt = package(original())
        screenshots = {}
        failures = []
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.getenv('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
            for width in (320, 360, 390, 768, 1440, 1920):
                for js in (False, True):
                    ctx = browser.new_context(viewport={'width': width, 'height': 800},java_script_enabled=js,reduced_motion='reduce',has_touch=True,is_mobile=(width < 768))
                    ctx.route('**/*', lambda route: route.abort())
                    page = ctx.new_page()
                    page.on('pageerror',lambda error: failures.append(str(error)))
                    page.set_content('<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><body>'+source+'</body></html>',wait_until='load')
                    page.wait_for_timeout(100)
                    figures=page.locator('[data-fvx-chrono-photo]')
                    self.assertEqual(figures.count(),3)
                    self.assertFalse(page.evaluate('document.documentElement.scrollWidth > innerWidth + 1'))
                    self.assertEqual(page.locator('figcaption a[href^="https://www.nasa.gov/"],figcaption a[href^="https://images.nasa.gov/"]').count(),3)
                    if js:
                        buttons=page.locator('.fvx-archive-choice__button')
                        self.assertEqual(buttons.count(),3)
                        buttons.nth(1).click()
                        self.assertTrue(figures.nth(1).is_visible())
                        page.locator('#fire').evaluate('(el)=>{el.value="12";el.dispatchEvent(new Event("input"))}')
                        self.assertTrue(figures.nth(1).is_visible())
                        buttons.nth(2).focus(); page.keyboard.press('Home')
                        self.assertTrue(figures.nth(0).is_visible())
                        self.assertGreaterEqual(page.locator('[data-fvx-image-fallback]').count(),1)
                        image=page.screenshot(full_page=True,animations='disabled')
                        screenshots[str(width)]=hashlib.sha256(image).hexdigest()
                    else:
                        self.assertTrue(all(figures.nth(i).is_visible() for i in range(3)))
                    ctx.close()
            browser.close()
        self.assertFalse(failures, failures)
        (HERE/'artifacts').mkdir(exist_ok=True)
        (HERE/'artifacts'/'r167_receipt.json').write_text(json.dumps({'mode':'CONTROLLED_GUTENBERG_FIXTURE','source_sha256':receipt['src_sha256'], 'output_sha256':receipt['out_sha256'], 'screenshots': screenshots,'page_errors': failures,'release':'HOLD'},indent=2,sort_keys=True))


if __name__=='__main__': unittest.main(verbosity=2)
