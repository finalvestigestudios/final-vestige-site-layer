"""R169 negative-control tests and real Chromium source-custody interaction checks.

Controlled source-derived Gutenberg fixture only; no genuine WordPress/axe/CDN.
"""
import hashlib
import json
import os
from pathlib import Path
import unittest

from playwright.sync_api import sync_playwright
from apollo_source_conversion_gate import offline_preflight, verify, SOURCE_IDS
from wp_source_custody_gate import WITNESS, digest
from test_wp_block_pack import original

HERE=Path(__file__).resolve().parent
WIDTHS=(320,360,390,768,1440,1920)
CTA_URL='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'


def controlled():
    source=original()
    # Test an actual existing-editor anchor preservation contract instead of
    # relying on the predecessor fixture's zero investigation links.
    anchor='<p class="archive-next"><a href="'+CTA_URL+'">Read original investigation</a></p>'
    assert source.count('<!-- /wp:html -->')==9
    source=source.replace('<!-- /wp:html -->',anchor+'\n<!-- /wp:html -->',1)
    witness={**WITNESS,'source_sha256':digest(source),'source_bytes_utf8':len(source.encode('utf-8')),
             'wp_custom_html_blocks':9,'editor_scripts':1}
    return source,witness


class CustodyAndConversion(unittest.TestCase):
    def test_pinned_source_and_semantic_lock(self):
        src,witness=controlled()
        with self.assertRaisesRegex(ValueError,'HOLD'):
            offline_preflight(src) # real WordPress pin must reject synthetic fixture
        out,receipt=offline_preflight(src,witness)
        self.assertEqual(verify(src,out),receipt['r169'])
        self.assertEqual(receipt['r169']['new_affiliate_or_checkout_links'],0)
        self.assertIn(CTA_URL,out)
        self.assertFalse(receipt['r169']['approved_for_publish'])
        self.assertEqual(receipt['r169']['commercial_activation'],'HOLD_NO_VERIFIED_APOLLO_OFFER')
        self.assertEqual(offline_preflight(src,witness)[0],out)

    def test_mutations_caught_even_when_link_count_unchanged(self):
        src,w=controlled()
        staged,_=offline_preflight(src,w)
        cases={
            'new checkout destination':staged.replace(CTA_URL,'https://payhip.com/b/not-a-verified-product'),
            'missing NASA source':staged.replace(SOURCE_IDS[0],'https://example.invalid/forged/'),
            'caption rewrite':staged.replace('The crew before the test','A photo from the fire'),
            'broken alt':staged.replace('alt="Apollo 1 prime crew','alt="Fire crew'),
            'new affiliate link':staged.replace('Read original investigation</a>','<a href="https://www.awin1.com/">BUY NOW</a></a>'),
            'changed link security':staged.replace('rel="noopener noreferrer"','rel="nofollow"',1),
            'block deletion':staged.replace('<!-- /wp:html -->','',1),
            'unverified urgency claim':staged.replace('These three archival photographs are independent','Buy within 30 minutes! These three archival photographs are independent'),
        }
        for label,mutant in cases.items():
            with self.subTest(label=label):
                self.assertNotEqual(mutant,staged)
                with self.assertRaisesRegex(ValueError,'HOLD'):
                    verify(src,mutant)

    def test_chromium_six_widths_sources_and_context_cta(self):
        src,witness=controlled()
        staged,receipt=offline_preflight(src,witness)
        screens={}; errors=[]; assertions=0
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.getenv('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
            for width in WIDTHS:
                for enabled in (False,True):
                    context=browser.new_context(viewport={'width':width,'height':860},
                        java_script_enabled=enabled,reduced_motion='reduce',has_touch=True,is_mobile=width<768)
                    context.route('**/*',lambda route:route.abort())
                    page=context.new_page();page.on('pageerror',lambda err: errors.append(str(err)))
                    page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body><main class="fv-ex2-page">'+staged+'</main></body></html>')
                    page.wait_for_timeout(70)
                    self.assertFalse(page.evaluate('document.documentElement.scrollWidth>innerWidth+1'));assertions+=1
                    self.assertEqual(page.locator('.archive-next a').count(),1);assertions+=1
                    self.assertEqual(page.locator('.archive-next a').get_attribute('href'),CTA_URL);assertions+=1
                    links=page.locator('figcaption a[href]')
                    self.assertEqual(links.count(),3);assertions+=1
                    self.assertEqual([links.nth(i).get_attribute('href') for i in range(3)],list(SOURCE_IDS));assertions+=1
                    figures=page.locator('[data-fvx-chrono-photo]')
                    self.assertEqual(figures.count(),3);assertions+=1
                    if enabled:
                        controls=page.locator('.fvx-archive-choice__button')
                        self.assertEqual(controls.count(),3);assertions+=1
                        controls.nth(1).click();self.assertTrue(figures.nth(1).is_visible());assertions+=1
                        page.locator('#fire').evaluate('(e)=>{e.value="12";e.dispatchEvent(new Event("input"))}')
                        self.assertTrue(figures.nth(1).is_visible());assertions+=1
                        controls.nth(2).focus();page.keyboard.press('Home')
                        self.assertTrue(figures.nth(0).is_visible());assertions+=1
                        self.assertEqual(page.locator('.fvx-archive-choice__button[aria-pressed="true"]').count(),1);assertions+=1
                        page.evaluate('document.activeElement && document.activeElement.blur()')
                        page.wait_for_timeout(90)
                        shot=page.screenshot(full_page=True,animations='disabled')
                        (HERE/'artifacts').mkdir(exist_ok=True)
                        (HERE/'artifacts'/f'archive-{width}.png').write_bytes(shot)
                        screens[str(width)]=hashlib.sha256(shot).hexdigest()
                    else:
                        self.assertEqual(page.locator('.fvx-archive-choice__button').count(),0);assertions+=1
                        for i in range(3): self.assertTrue(figures.nth(i).is_visible());assertions+=3
                    context.close()
            browser.close()
        self.assertEqual(errors,[])
        result={'status':'CONTROLLED_FIXTURE_PASS_NOT_WORDPRESS_ACCEPTANCE',
            'assertions':assertions,'contexts':12,'responsive_widths':list(WIDTHS),
            'screenshots_sha256':screens,'page_errors':errors,
            'source_sha256':receipt['r169']['source_sha256'],
            'preview_sha256':receipt['r169']['preview_sha256'],
            'axe_core':'NOT_EXECUTED_NO_LIBRARY', 'real_wordpress':'NOT_TESTED',
            'real_cwv':'NOT_MEASURED', 'merchant_orders':'NOT_OBSERVED', 'release':'STAGING_HOLD'}
        (HERE/'artifacts'/'r169-browser-receipt.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')

if __name__=='__main__':unittest.main(verbosity=2)
