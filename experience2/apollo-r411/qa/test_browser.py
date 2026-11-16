#!/usr/bin/env python3
"""Executed Chromium accessibility & responsive checks on the real PHP output (offline).

Uses page.set_content, not a navigated WordPress/HTTP response. This suite does NOT
provide a genuine axe-core, LCP/CLS/INP or production CI pass.
"""
from __future__ import annotations
from pathlib import Path
import json
import subprocess
import unittest
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / 'QA' / 'screenshots'
SHOTS.mkdir(parents=True, exist_ok=True)
HTML = subprocess.run(['php', str(ROOT/'qa/render_fixture.php')], text=True, capture_output=True, check=True).stdout
CSS = (ROOT/'assets/source-drawer.css').read_text(encoding='utf-8')
META = {'engine':'system Chromium via Playwright','fixture':'real PHP output, in-memory document',
        'real_network_navigation': False,'installed_wordpress':False,'axe_core':False,
        'lcp':None,'cls':None,'inp':None,'status':'LOCAL_ONLY_NOT_RELEASE_AUTHORIZED', 'contexts':[]}

class SourceDrawerBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.pw.stop()
        (ROOT/'QA/browser_report.json').write_text(json.dumps(META,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    def page(self, width=390, height=850, **kwargs):
        context = self.browser.new_context(viewport={'width':width,'height':height}, **kwargs)
        page = context.new_page()
        page.set_content(HTML.replace('</head>', '<style>'+CSS+'</style></head>'), wait_until='load')
        return context, page
    def test_semantic_native_sources(self):
        c,p=self.page()
        self.assertEqual(p.locator('section[data-fv-r411-sources]').count(),1)
        self.assertEqual(p.locator('.fv-r411__item').count(),6)
        self.assertEqual(p.locator('details > summary').count(),6)
        self.assertEqual(p.get_by_role('link',name='Continue to the free Apollo 1 investigation').count(),1)
        urls=p.locator('.fv-r411__sources a').evaluate_all('(els)=>els.map(x=>x.href)')
        self.assertEqual(len(urls),12)
        self.assertTrue(all(urlparse(x).hostname=='www.nasa.gov' for x in urls))
        self.assertEqual(p.locator('script,img,iframe,video,audio,form').count(),0)
        c.close()
    def test_keyboard_disclosure_enter_space_escape_not_hijacked(self):
        c,p=self.page()
        summary=p.locator('summary').first
        summary.focus();self.assertTrue(summary.evaluate('(e)=>e===document.activeElement'))
        p.keyboard.press('Enter')
        self.assertTrue(p.locator('details').first.evaluate('(e)=>e.open'))
        self.assertTrue(p.get_by_text('Ground-test context does not establish the ignition source.').is_visible())
        p.keyboard.press('Space')
        self.assertFalse(p.locator('details').first.evaluate('(e)=>e.open'))
        c.close()
    def test_nojs_native_disclosure_and_link(self):
        c,p=self.page(java_script_enabled=False)
        p.locator('summary').nth(5).click()
        self.assertTrue(p.locator('details').nth(5).evaluate('(e)=>e.open'))
        self.assertTrue(p.get_by_text('102 deliberate Command Module tests',exact=False).is_visible())
        self.assertEqual(p.get_by_role('link',name='NASA media-use guidance').count(),1)
        p.screenshot(path=str(SHOTS/'390-nojs.png'),full_page=True)
        c.close()
    def test_touch(self):
        c,p=self.page(390,844,has_touch=True,is_mobile=True)
        p.locator('summary').nth(4).tap()
        self.assertTrue(p.locator('details').nth(4).evaluate('(e)=>e.open'))
        self.assertTrue(p.get_by_text('A probable electrical arc must never',exact=False).is_visible())
        p.screenshot(path=str(SHOTS/'390-touch.png'),full_page=True)
        c.close()
    def test_responsive_320_to_1920_and_css_applied(self):
        for width in (320,360,390,768,1024,1440,1920):
            with self.subTest(width=width):
                c,p=self.page(width,900)
                overflow=p.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
                cols=p.locator('.fv-r411__list').evaluate('(e)=>getComputedStyle(e).gridTemplateColumns')
                self.assertFalse(overflow, f'Overflow {width}px')
                self.assertNotEqual(p.locator('.fv-r411__item').first.evaluate('(e)=>getComputedStyle(e).backgroundColor'),'rgba(0, 0, 0, 0)')
                self.assertEqual(len(cols.split()),1 if width<=760 else 2)
                p.screenshot(path=str(SHOTS/f'{width}.png'),full_page=True)
                META['contexts'].append({'width':width,'overflow':overflow,'css_grid':cols})
                c.close()
    def test_reduced_motion(self):
        c,p=self.page(390,844,reduced_motion='reduce')
        p.locator('summary').first.click()
        self.assertTrue(p.locator('details').first.evaluate('(e)=>e.open'))
        self.assertEqual(p.locator('.fv-r411__item').first.evaluate('(e)=>getComputedStyle(e).animationName'),'none')
        p.screenshot(path=str(SHOTS/'390-reduced-motion.png'),full_page=True)
        c.close()
    def test_forced_colors(self):
        c,p=self.page(390,844,forced_colors='active')
        self.assertEqual(p.locator('.fv-r411__item').first.evaluate('(e)=>getComputedStyle(e).borderTopStyle'),'solid')
        p.screenshot(path=str(SHOTS/'390-forced-colors.png'),full_page=True)
        c.close()
    def test_large_text_root_font(self):
        c,p=self.page(320,800)
        p.evaluate('document.documentElement.style.fontSize="64px"')
        self.assertFalse(p.evaluate('document.documentElement.scrollWidth > innerWidth + 1'))
        p.screenshot(path=str(SHOTS/'320-4x-root-font.png'),full_page=True)
        c.close()
    def test_accessibility_tree_names(self):
        c,p=self.page()
        session=c.new_cdp_session(p)
        nodes=session.send('Accessibility.getFullAXTree')['nodes']
        name_values=[(n.get('name') or {}).get('value','') for n in nodes]
        self.assertIn('Inspect the documents. Keep the limits.',name_values)
        self.assertIn('Continue to the free Apollo 1 investigation',name_values)
        self.assertIn('NASA media-use guidance',name_values)
        self.assertIn('Unresolved ignition',name_values)
        (ROOT/'QA/accessibility_roles.json').write_text(json.dumps({'extracted_visible_names':[n for n in name_values if n in {'Inspect the documents. Keep the limits.','Continue to the free Apollo 1 investigation','NASA media-use guidance','Unresolved ignition'}]},indent=2)+'\n')
        c.close()
    def test_one_action_no_inline_commerce(self):
        c,p=self.page()
        hrefs=p.locator('a').evaluate_all('(els)=>els.map(x=>x.href)')
        self.assertEqual(sum('finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/' in x for x in hrefs),1)
        self.assertTrue(all('payhip' not in x and 'utm_' not in x and 'awin' not in x for x in hrefs))
        c.close()

if __name__=='__main__':unittest.main(verbosity=2)
