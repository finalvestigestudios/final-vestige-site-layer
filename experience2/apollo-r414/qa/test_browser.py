#!/usr/bin/env python3
"""Actual Chromium browser QA on PHP-rendered offline fixture, not HTTP/WordPress."""
import hashlib, json, subprocess, unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SHOTS=ROOT/'QA/screenshots'
HTML=subprocess.check_output(['php',str(ROOT/'qa/render_fixture.php')],text=True)
RECEIPTS=[]
class ApolloR414Browser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SHOTS.mkdir(parents=True,exist_ok=True)
        cls.pw=sync_playwright().start()
        cls.browser=cls.pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.pw.stop()
        (ROOT/'QA/browser_results.json').write_text(json.dumps(RECEIPTS,sort_keys=True,indent=2)+'\n')
    def page(self, width=390, js=True, touch=False, reduced='no-preference', forced='none', root_px=None):
        context=self.browser.new_context(viewport={'width':width,'height':870},java_script_enabled=js,has_touch=touch,is_mobile=touch,reduced_motion=reduced,forced_colors=forced)
        p=context.new_page();p.set_content(HTML,wait_until='load')
        if root_px: p.add_style_tag(content=f'html{{font-size:{root_px}px!important}}')
        return context,p
    def test_all_records_and_urls(self):
        context,p=self.page()
        self.assertEqual(p.locator('[data-fv-r414-gallery]').count(),2)
        self.assertEqual(p.locator('.fv-r414__card').count(),12)
        self.assertEqual(p.locator('.fv-r414 details').count(),12)
        self.assertEqual(p.locator('img,script,iframe,video,form,canvas').count(),0)
        ids=p.eval_on_selector_all('[id]','nodes=>nodes.map(n=>n.id)')
        self.assertEqual(len(ids),len(set(ids)))
        nav=p.eval_on_selector_all('.fv-r414__index a','nodes=>nodes.map(n=>n.hash.substring(1))')
        self.assertEqual(len(nav),12)
        self.assertTrue(all(t in ids for t in nav))
        urls=p.eval_on_selector_all('.fv-r414__links a','nodes=>nodes.map(n=>n.href)')
        self.assertEqual(len(urls),24)
        self.assertTrue(all(u.startswith('https://www.nasa.gov/') for u in urls))
        self.assertEqual(p.get_by_role('link',name='Continue to the free Apollo 1 investigation').count(),2)
        context.close()
    def test_keyboard_and_disclosure_no_js(self):
        context,p=self.page(width=320,js=False)
        link=p.locator('.fv-r414__index a').first
        link.focus();link.press('Enter')
        self.assertEqual(p.evaluate('location.hash'),'#fv-r414-gallery-1-01')
        disclosure=p.locator('.fv-r414 details').first
        disclosure.locator('summary').focus();disclosure.locator('summary').press('Enter')
        self.assertTrue(disclosure.get_attribute('open') is not None)
        self.assertTrue(disclosure.locator('p').is_visible())
        context.close()
    def test_touch_scroll_and_disclosure(self):
        context,p=self.page(width=390,touch=True)
        p.locator('.fv-r414__index a').nth(5).tap()
        self.assertEqual(p.evaluate('location.hash'),'#fv-r414-gallery-1-06')
        p.locator('#fv-r414-gallery-1-06 summary').tap()
        self.assertTrue(p.locator('#fv-r414-gallery-1-06 details').get_attribute('open') is not None)
        context.close()
    def test_sensitive_differences_visible(self):
        context,p=self.page()
        self.assertTrue(p.get_by_text('image rights not cleared',exact=False).first.is_visible())
        p.locator('.fv-r414 details').nth(4).locator('summary').click()
        self.assertTrue(p.get_by_text('A probable electrical arc must never',exact=False).first.is_visible())
        context.close()
    def test_responsive_and_special_contexts(self):
        cases=[(str(w),dict(width=w)) for w in [320,360,390,768,1024,1440,1920]]
        cases += [('390-touch',dict(width=390,touch=True)),('390-nojs',dict(width=390,js=False)),('390-reduced',dict(width=390,reduced='reduce')),('390-forced',dict(width=390,forced='active')),('320-root4x',dict(width=320,root_px=64))]
        for name,parameters in cases:
            with self.subTest(name=name):
                context,p=self.page(**parameters)
                shot=SHOTS/(name+'.png')
                p.screenshot(path=str(shot),full_page=True,animations='disabled',timeout=30000)
                d=p.evaluate('({viewport:document.documentElement.clientWidth,documentWidth:document.documentElement.scrollWidth,trackScroll:document.querySelector(".fv-r414__track").scrollWidth,trackClient:document.querySelector(".fv-r414__track").clientWidth})')
                self.assertLessEqual(d['documentWidth'],d['viewport'],f"document overflow {name}: {d}")
                self.assertEqual(p.locator('.fv-r414__card').count(),12)
                RECEIPTS.append({'scenario':name,'width':d['viewport'],'horizontal_overflow':max(0,d['documentWidth']-d['viewport']),'gallery_horizontal_scroller':d['trackScroll']>d['trackClient'],'screenshot_sha256':hashlib.sha256(shot.read_bytes()).hexdigest()})
                context.close()
    def test_print_has_all_cards(self):
        context,p=self.page(width=1024)
        p.emulate_media(media='print')
        self.assertEqual(p.locator('.fv-r414__card:visible').count(),12)
        self.assertEqual(p.locator('.fv-r414__index:visible').count(),0)
        context.close()
if __name__=='__main__':unittest.main(verbosity=2)
