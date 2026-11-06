"""R168 true Chromium controlled-fixture tests; not live WordPress acceptance.

Negative controls intentionally fail on changed editor content. Never access the
website, external NASA images, analytics or merchant systems.
"""
import hashlib
import json
import os
from pathlib import Path
import unittest
from io import BytesIO
from PIL import Image
from playwright.sync_api import sync_playwright
from wp_source_custody_gate import stage, validate_source, R168_TAG, WITNESS, digest
from test_wp_block_pack import original

HERE = Path(__file__).resolve().parent
WIDTHS = (320,360,390,768,1440,1920)


def fixture_witness(s):
    return {**WITNESS, 'source_sha256': digest(s), 'source_bytes_utf8': len(s.encode()),
            'wp_custom_html_blocks': 9, 'editor_scripts': 1}


class SourceCustody(unittest.TestCase):
    def setUp(self):
        self.source=original()
        self.witness=fixture_witness(self.source)

    def test_public_wordpress_witness_rejects_controlled_fixture(self):
        with self.assertRaisesRegex(ValueError,'HOLD'):
            validate_source(self.source)  # R168 hard-coded to actual WP raw SHA

    def test_pinned_staging_deterministic_and_preserves_links(self):
        output,receipt=stage(self.source,self.witness)
        output2,receipt2=stage(self.source,self.witness)
        self.assertEqual(output,output2)
        self.assertEqual(receipt,receipt2)
        self.assertIn(R168_TAG,output)
        self.assertEqual(output.count('<!-- wp:html -->'),9)
        self.assertEqual(output.count('<!-- /wp:html -->'),9)
        self.assertEqual(output.count('<a '),self.source.count('<a '))
        self.assertEqual(receipt['status'],'OFFLINE_STAGING_HOLD')
        self.assertFalse(receipt['approved_for_publish'])
        self.assertEqual(receipt['wordpress_writes'],0)
        self.assertEqual(receipt['source_witness']['source_sha256'],digest(self.source))
        self.assertNotIn('const index = t < 6 ? 0 : (t < 11.3 ? 1 : 2);',output)
        self.assertEqual(output.count('https://www.nasa.gov/image-detail/amf-s66-58038/'),self.source.count('https://www.nasa.gov/image-detail/amf-s66-58038/'))

    def test_drift_negative_controls(self):
        variants=[
            self.source+'\n',
            self.source.replace('t < 6 ?', 't < 7 ?'),
            self.source.replace('amf-s67-15717/','amf-s67-15717-updated/'),
            self.source.replace('<!-- /wp:html -->','',1),
            self.source.replace('<!-- wp:html -->','',1),
            self.source.replace('NASA S66-58038','NASA X66-58038',1),
        ]
        for variant in variants:
            with self.subTest(variant=hashlib.md5(variant.encode()).hexdigest()[:8]):
                with self.assertRaisesRegex(ValueError,'HOLD'):
                    stage(variant,self.witness)
        with self.assertRaisesRegex(ValueError,'HOLD'):
            stage(self.source,{**self.witness,'slug':'different-wp-page','source_sha256':'0'*64})

    @staticmethod
    def center_ink_pixels(png):
        im=Image.open(BytesIO(png)).convert('RGB')
        w,h=im.size
        core=im.crop((int(w*.42),int(h*.31),int(w*.58),int(h*.69)))
        return sum(max(rgb)<110 for rgb in core.get_flattened_data())

    def test_real_chromium_responsive_focus_forced_colors_and_nojs(self):
        html,receipt=stage(self.source,self.witness)
        counts=0
        screens={}
        pixel_witness={}
        errors=[]
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.getenv('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
            for width in WIDTHS:
                for js in (False,True):
                    ctx=browser.new_context(viewport={'width':width,'height':860},java_script_enabled=js,
                        reduced_motion='reduce', has_touch=True,is_mobile=width<768,
                        forced_colors='active' if js else 'none')
                    ctx.route('**/*',lambda route:route.abort())
                    page=ctx.new_page()
                    page.on('pageerror',lambda e: errors.append(str(e)))
                    page.set_content('<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><body><main class="fv-ex2-page">'+html+'</main></body></html>',wait_until='load')
                    page.wait_for_timeout(120)
                    photos=page.locator('[data-fvx-chrono-photo]')
                    self.assertEqual(photos.count(),3)
                    self.assertFalse(page.evaluate('document.documentElement.scrollWidth>innerWidth+1'))
                    self.assertEqual(page.locator('figcaption a[href^="https://www.nasa.gov/"],figcaption a[href^="https://images.nasa.gov/"]').count(),3)
                    if js:
                        controls=page.locator('.fvx-archive-choice__button')
                        self.assertEqual(controls.count(),3)
                        self.assertGreaterEqual(controls.nth(0).bounding_box()['height'],44)
                        self.assertEqual(controls.nth(0).get_attribute('aria-pressed'),'true')
                        controls.nth(1).click()
                        self.assertEqual(controls.nth(1).get_attribute('aria-pressed'),'true')
                        page.locator('#fire').evaluate('(el)=>{el.value="12";el.dispatchEvent(new Event("input"))}')
                        self.assertTrue(photos.nth(1).is_visible())
                        controls.nth(2).focus()
                        page.keyboard.press('Home')
                        self.assertTrue(photos.nth(0).is_visible())
                        self.assertEqual(controls.nth(0).get_attribute('aria-pressed'),'true')
                        controls.nth(0).focus()
                        self.assertEqual(page.evaluate('document.activeElement.classList.contains("fvx-archive-choice__button")'),True)
                        # Explicit system-color borders remain visible in forced-colors mode.
                        self.assertGreaterEqual(float(page.evaluate('getComputedStyle(document.querySelector(".fvx-archive-choice__button")).borderTopWidth').removesuffix('px')), 2.0)
                        page.evaluate('document.activeElement.blur()')
                        page.wait_for_timeout(100)
                        path=HERE/'artifacts-r168'
                        path.mkdir(exist_ok=True)
                        shot=page.screenshot(full_page=True,animations='disabled')
                        (path/('r168-'+str(width)+'.png')).write_bytes(shot)
                        screens[str(width)]=hashlib.sha256(shot).hexdigest()
                        if width == 390:
                            # Pixel witness: forced-color selection must render readable INK.
                            # Chromium's Highlight/HighlightText pairing previously rendered
                            # an EMPTY WHITE BAR over the entire control label.
                            good=self.center_ink_pixels(controls.nth(0).screenshot())
                            self.assertGreater(good,40, 'active archive label visually blank')
                            page.add_style_tag(content='.fv-ex2-page .fvx-archive-choice__button[aria-pressed=\"true\"]{background:Highlight!important;color:HighlightText!important;outline:none!important}')
                            bad=self.center_ink_pixels(controls.nth(0).screenshot())
                            self.assertLess(bad,5, 'negative control failed to recreate inaccessible label')
                            pixel_witness.update({'corrected_dark_pixels':good,'regression_dark_pixels':bad,'witness_viewport_css_px':390})
                    else:
                        self.assertTrue(all(photos.nth(i).is_visible() for i in range(3)))
                        self.assertEqual(page.locator('.fvx-archive-choice__button').count(),0)
                    counts+=1
                    ctx.close()
            browser.close()
        self.assertEqual(counts,12)
        self.assertEqual(errors,[])
        out={'kind':'CONTROLLED_GUTENBERG_FIXTURE_NOT_INSTALLED_WORDPRESS','contexts':counts,'widths':list(WIDTHS),
             'screenshots':screens,'pixel_witness':pixel_witness,'pageerrors':errors,'src_sha256':receipt['source_witness']['source_sha256'],
             'out_sha256':receipt['r168_preview_sha256'], 'axe_core':'NOT_EXECUTED_UNAVAILABLE',
             'actual_wordpress_browser':'NOT_EXECUTED','production_cwv':'NOT_MEASURED','release':'STAGING_HOLD'}
        (HERE/'artifacts-r168'/'r168-browser-receipt.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')

if __name__=='__main__':
    unittest.main(verbosity=2)
