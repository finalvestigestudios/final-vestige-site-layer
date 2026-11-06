"""Offline R172 Gutenberg acceptance. Genuine Chromium, NOT installed WordPress.

Run: python -m unittest -v experience2/apollo-r172/test_apollo_reviewed_caption_bridge.py
Axe-core is mandatory at installed staging but is not vendored or faked here.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import unittest

from playwright.sync_api import sync_playwright
from apollo_reviewed_caption_bridge import (
    build_preview, verify_reviewed, reviewed_extension, NASA_LINKS,
    MARKER, WITNESS, _sha
)
from test_apollo_source_conversion_gate import controlled
from apollo_executable_custody_gate import preflight as r170_preflight
from apollo_source_conversion_gate import verify as verify_editorial

HERE = Path(__file__).resolve().parent
WIDTHS = (320, 360, 390, 768, 1440, 1920)
CTA = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'


def html_document(body):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<style>html{background:#171715;color:#f4efe6;font:16px/1.6 system-ui}'
            '.fv-ex2-page{max-width:960px;margin:auto}body{margin:16px}'
            'a{color:#e8c98f}img{max-width:100%}</style></head>'
            '<body><main class="fv-ex2-page"><h1>Apollo 1: The Evidence Atlas</h1>'
            + body + '</main></body></html>')


class ReviewedCaptionBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original, cls.witness = controlled()
        cls.legacy, cls.legacy_receipt = r170_preflight(cls.original, cls.witness)
        cls.preview, cls.receipt = build_preview(cls.original, cls.witness)

    def test_pinned_witness_and_deterministic_chain(self):
        with self.assertRaisesRegex(ValueError, 'HOLD'):
            build_preview(self.original)  # Synthetic fixture must fail real-site witness.
        again, receipt = build_preview(self.original, self.witness)
        self.assertEqual(self.preview, again)
        self.assertEqual(self.receipt['r172'], receipt['r172'])
        self.assertFalse(receipt['r172']['approved_for_publish'])
        self.assertEqual(receipt['r172']['additional_tracking_scripts'], 0)
        self.assertEqual(receipt['r172']['caption_count'], 3)
        self.assertEqual(receipt['r172']['unchanged_script_count'], 2)
        self.assertEqual(self.preview.count(MARKER), 1)
        self.assertEqual(self.preview.count('<!-- wp:html -->'), 9)
        self.assertEqual(self.preview.count('<!-- /wp:html -->'), 9)
        self.assertIn(CTA, self.preview)
        self.assertEqual(self.preview.count('class="fvx-archive-caption__body"'), 3)
        self.assertEqual([self.preview.count(url) for url in NASA_LINKS], [1,1,1])
        self.assertEqual(verify_editorial(self.original, self.preview)['gate'], 'PASS_OFFLINE_ONLY')

    def test_mutation_controls_reject_all_unauthorized_changes(self):
        original, legacy, proposed = self.original, self.legacy, self.preview
        attacks = {
            'one changed NASA citation': proposed.replace(NASA_LINKS[0], 'https://example.invalid/forged', 1),
            'switch original investigation to unverified checkout': proposed.replace(CTA, 'https://payhip.com/b/unknown', 1),
            'change description': proposed.replace('does not depict the January 27 fire', 'shows the fire', 1),
            'change source caption label': proposed.replace('Original NASA record', 'Officially NASA-approved product', 1),
            'tamper caption structural HTML': proposed.replace('fvx-archive-caption__body', 'fvx-archive-caption__bogus', 1),
            'inject script': proposed.replace('</script>', 'fetch("https://tracking.invalid/");</script>', 1),
            'inject form': proposed.replace('</figcaption>', '</figcaption><form action="/buy"></form>', 1),
            'inject markup event handler': proposed.replace('fvx-archive-caption__body', 'fvx-archive-caption__body" onclick="alert(1)', 1),
            'change CSS': proposed.replace('overflow-wrap:anywhere', 'overflow-wrap:normal', 1),
            'add CSS beacon': proposed.replace('.fv-ex2-page .fvx-archive-caption{', '.fv-ex2-page .fvx-archive-caption{background:url(https://tracker.invalid/t);', 1),
            'duplicate marker': proposed.replace(MARKER, MARKER + MARKER, 1),
            'remove block end': proposed.replace('<!-- /wp:html -->', '', 1),
            'inject unverified urgency': proposed.replace('Read original investigation', 'BUY TODAY—LAST CHANCE', 1),
        }
        for label, attack in attacks.items():
            with self.subTest(label=label):
                self.assertNotEqual(attack, proposed)
                with self.assertRaisesRegex(ValueError, 'HOLD'):
                    verify_reviewed(original, legacy, attack)
        with self.assertRaisesRegex(ValueError, 'HOLD'):
            reviewed_extension(proposed)  # idempotence protects against duplicate styles
        with self.assertRaisesRegex(ValueError, 'HOLD'):
            build_preview(self.original.replace('NASA S66-58038','fabricated source'), self.witness)

    def test_chromium_accessibility_gallery_cta_and_geometry(self):
        screens, observations, failures = {}, [], []
        checks = 0
        source_html = html_document(self.preview)
        HERE.joinpath('artifacts').mkdir(exist_ok=True)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True, executable_path=os.getenv('CHROMIUM_PATH', '/usr/bin/chromium'),
                args=['--no-sandbox'])
            for width in WIDTHS:
                for enabled in (False, True):
                    ctx = browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,
                        java_script_enabled=enabled, has_touch=(width < 768),is_mobile=(width < 768),
                        reduced_motion='reduce')
                    ctx.route('**/*', lambda route: route.abort())
                    page = ctx.new_page()
                    page.on('pageerror', lambda exception: failures.append(str(exception)))
                    # Performance observer must be installed before painting for a
                    # lab-only signal; this is not a real-page LCP/CLS assertion.
                    if enabled:
                        page.add_init_script('''(() => {
                          window.__r172vitals={lcp:[],cls:0};
                          new PerformanceObserver(l=>{for(const e of l.getEntries())window.__r172vitals.lcp.push(e.startTime)})
                              .observe({type:'largest-contentful-paint',buffered:true});
                          new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__r172vitals.cls+=e.value})
                              .observe({type:'layout-shift',buffered:true});
                        })()''')
                    page.set_content(source_html, wait_until='load')
                    if enabled:
                        page.evaluate('''() => {window.__r172vitals = {lcp: [],cls:0}; new PerformanceObserver(list => {for(const e of list.getEntries())window.__r172vitals.lcp.push(e.startTime)}).observe({type:'largest-contentful-paint',buffered:true}); new PerformanceObserver(list => {for(const e of list.getEntries())if(!e.hadRecentInput)window.__r172vitals.cls+=e.value}).observe({type:'layout-shift',buffered:true})}''')
                    page.wait_for_timeout(110)
                    self.assertFalse(page.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')); checks+=1
                    photos=page.locator('[data-fvx-chrono-photo]')
                    self.assertEqual(photos.count(),3);checks+=1
                    self.assertEqual(page.locator('.fvx-archive-caption__body').count(),3);checks+=1
                    self.assertEqual(page.locator('a[href="'+CTA+'"]').count(),1);checks+=1
                    for index,url in enumerate(NASA_LINKS):
                        cap=photos.nth(index).locator('figcaption')
                        self.assertEqual(cap.locator('a').get_attribute('href'),url);checks+=1
                        self.assertEqual(cap.locator('strong').count(),1);checks+=1
                        self.assertEqual(cap.locator('.fvx-archive-caption__body').count(),1);checks+=1
                    if enabled:
                        controls=page.locator('.fvx-archive-choice__button')
                        self.assertEqual(controls.count(),3);checks+=1
                        controls.nth(1).click()
                        self.assertTrue(photos.nth(1).is_visible());checks+=1
                        controls.nth(1).focus();page.keyboard.press('End')
                        self.assertTrue(photos.nth(2).is_visible());checks+=1
                        controls.nth(2).focus();page.keyboard.press('Home')
                        self.assertTrue(photos.nth(0).is_visible());checks+=1
                        # Chronicle slider must NOT switch the archival photograph.
                        fire=page.locator('#fire')
                        self.assertEqual(fire.count(),1);checks+=1
                        fire.evaluate('(e)=>{e.value="18";e.dispatchEvent(new Event("input", {bubbles:true}))}')
                        self.assertTrue(photos.nth(0).is_visible());checks+=1
                        # CSS separates attribution into readable block lines.
                        figure=photos.first
                        strong=figure.locator('strong').bounding_box()
                        body=figure.locator('.fvx-archive-caption__body').bounding_box()
                        small=figure.locator('.fvx-archive-caption__source').bounding_box()
                        self.assertIsNotNone(strong);self.assertIsNotNone(body);self.assertIsNotNone(small);checks+=3
                        self.assertGreaterEqual(body['y'], strong['y']+strong['height']+3);checks+=1
                        self.assertGreaterEqual(small['y'], body['y']+body['height']+3);checks+=1
                        body_font=figure.locator('.fvx-archive-caption__body').evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)')
                        self.assertGreaterEqual(body_font, 16);checks+=1
                        page.evaluate('document.activeElement?.blur()')
                        page.wait_for_timeout(80)
                        shot=page.screenshot(full_page=True, animations='disabled')
                        path=HERE/'artifacts'/f'r172-{width}.png';path.write_bytes(shot)
                        screens[str(width)]=hashlib.sha256(shot).hexdigest()
                        observations.append({'viewport':width,'javascript':True,
                            'offline_lcp_observed_ms':page.evaluate('window.__r172vitals.lcp'),
                            'offline_cls_observed':page.evaluate('window.__r172vitals.cls')})
                        checks+=1
                    else:
                        self.assertEqual(page.locator('.fvx-archive-choice__button').count(),0);checks+=1
                        self.assertTrue(all(photos.nth(i).is_visible() for i in range(3)));checks+=1
                        self.assertEqual(page.locator('.fvx-archive-caption__source').count(),3);checks+=1
                    ctx.close()
            # Windows emulated high contrast: active control label must remain visible.
            ctx=browser.new_context(viewport={'width':390,'height':900},forced_colors='active',
                reduced_motion='reduce',java_script_enabled=True,is_mobile=True,has_touch=True)
            ctx.route('**/*',lambda route:route.abort())
            pg=ctx.new_page();pg.set_content(source_html)
            pressed=pg.locator('.fvx-archive-choice__button[aria-pressed="true"]')
            self.assertEqual(pressed.count(),1);checks+=1
            self.assertTrue(pressed.first.is_visible());checks+=1
            self.assertGreaterEqual(pressed.first.bounding_box()['height'],24);checks+=1
            ctx.close();browser.close()
        self.assertEqual(failures,[])
        receipt={'kind':'OFFLINE_SOURCE_DERIVED_GUTENBERG_FIXTURE_NOT_INSTALLED_WP',
                 'real_chromium_contexts':13,'viewport_widths':WIDTHS,'assertions':checks,
                 'screenshot_sha256':screens,'pageerrors':failures,'vitals':observations,
                 'source_sha256':_sha(self.original),'staging_preview_sha256':_sha(self.preview),
                 'axe_core':'NOT_EXECUTED_LIBRARY_NOT_AVAILABLE',
                 'installed_wordpress_staging':'NOT_EXECUTED','actual_nasa_media':'NOT_VERIFIED',
                 'real_page_lcp_cls':'NOT_MEASURED','qualified_visits':'UNKNOWN',
                 'verified_paid_orders':'UNKNOWN','release':'STAGING_HOLD'}
        (HERE/'artifacts'/'r172-browser.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')

if __name__=='__main__':
    unittest.main(verbosity=2)
