#!/usr/bin/env python3
"""Real Playwright Chromium on local PHP-rendered content.
No HTTP navigation is asserted: this runtime blocks all page.goto calls.
These are genuine browser DOM, layout, keyboard, touch and print tests via set_content.
"""
from __future__ import annotations
import hashlib, json, re, subprocess, unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA'
SHOTS=QA/'screenshots'
REPORT=[]
HTML=subprocess.run(['php',str(ROOT/'qa/render_fixture.php')],check=True,capture_output=True,text=True,timeout=15).stdout

class EvidencePlateChromium(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SHOTS.mkdir(parents=True,exist_ok=True)
        cls.play=sync_playwright().start()
        cls.browser=cls.play.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.play.stop()
        (QA/'browser_results.json').write_text(json.dumps(REPORT,indent=2,sort_keys=True)+'\n')
    def page(self,width=390,height=860,js=True,touch=False,motion='no-preference',forced='none',font=16):
        ctx=self.browser.new_context(viewport={'width':width,'height':height},java_script_enabled=js,has_touch=touch,is_mobile=touch,reduced_motion=motion,forced_colors=forced)
        page=ctx.new_page()
        page.set_content(HTML,wait_until='load')
        if font!=16:
            page.add_style_tag(content=f'html{{font-size:{font}px!important}}')
        return ctx,page
    def test_full_source_custody_and_unique_anchor_targets(self):
        ctx,p=self.page()
        self.assertEqual(p.locator('[data-fv-r413-plate]').count(),2)
        self.assertEqual(p.locator('.fv-r413__card').count(),12)
        ids=p.eval_on_selector_all('[id]','els=>els.map(e=>e.id)')
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(p.locator('a[href^="#fv-r413-"]').count(),12)
        targets=p.eval_on_selector_all('a[href^="#fv-r413-"]','els=>els.map(e=>e.hash.slice(1))')
        self.assertTrue(all(t in ids for t in targets))
        self.assertEqual(p.get_by_role('link',name='Continue with the free Apollo 1 investigation').count(),2)
        self.assertEqual(p.locator('script,img,iframe,form,video,canvas').count(),0)
        self.assertEqual(p.locator('.fv-r413__limit:visible').count(),12)
        urls=p.eval_on_selector_all('.fv-r413__sources a','els=>els.map(e=>e.href)')
        self.assertEqual(len(urls),24)
        self.assertTrue(all(u.startswith('https://www.nasa.gov/') for u in urls))
        ctx.close()
    def test_keyboard_fragment_and_focus(self):
        ctx,p=self.page()
        nav=p.locator('.fv-r413__jump').first
        a=nav.get_by_role('link').nth(4)
        a.focus();self.assertTrue(a.evaluate('(e)=>e===document.activeElement'))
        a.press('Enter');self.assertEqual(p.evaluate('location.hash'),'#fv-r413-evidence-1-05')
        self.assertEqual(p.locator('.fv-r413__card:target').count(),1)
        self.assertTrue(p.locator('#fv-r413-evidence-1-05').is_visible())
        ctx.close()
    def test_touch_target_and_readable_source(self):
        ctx,p=self.page(width=390,height=844,touch=True)
        p.locator('.fv-r413__jump').first.get_by_role('link').nth(5).tap()
        self.assertEqual(p.evaluate('location.hash'),'#fv-r413-evidence-1-06')
        self.assertTrue(p.locator('#fv-r413-evidence-1-06 .fv-r413__limit').is_visible())
        ctx.close()
    def test_no_js_has_all_evidence_and_one_cta(self):
        ctx,p=self.page(width=320,height=760,js=False)
        self.assertEqual(p.locator('.fv-r413__claim:visible').count(),12)
        self.assertEqual(p.locator('.fv-r413__limit:visible').count(),12)
        self.assertEqual(p.get_by_role('link',name='Continue with the free Apollo 1 investigation').count(),2)
        ctx.close()
    def test_responsive_screenshots_overflow(self):
        for w in [320,360,390,768,1024,1440,1920]:
            with self.subTest(width=w):
                ctx,p=self.page(width=w,height=900)
                p.screenshot(path=str(SHOTS/f'{w}.png'),full_page=True,animations='disabled')
                measured=p.evaluate('({viewport:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth})')
                self.assertLessEqual(measured['scroll'],measured['viewport'],f'overflow at {w}: {measured}')
                REPORT.append({'scenario':str(w),'width':w,'overflow_px':max(0,measured['scroll']-measured['viewport']),'image_sha256':hashlib.sha256((SHOTS/f'{w}.png').read_bytes()).hexdigest()})
                ctx.close()
    def test_reduced_motion_forced_colors_and_large_type(self):
        for scenario,params in [('390-reduced',dict(width=390,motion='reduce')),('390-forced',dict(width=390,forced='active')),('320-root4x',dict(width=320,font=64)),('390-touch',dict(width=390,touch=True))]:
            with self.subTest(scenario=scenario):
                ctx,p=self.page(**params)
                p.screenshot(path=str(SHOTS/f'{scenario}.png'),full_page=True,animations='disabled')
                d=p.evaluate('({viewport:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth})')
                self.assertLessEqual(d['scroll'],d['viewport'],f'{scenario}: {d}')
                self.assertEqual(p.locator('.fv-r413__card').count(),12)
                REPORT.append({'scenario':scenario,'overflow_px':max(0,d['scroll']-d['viewport']),'image_sha256':hashlib.sha256((SHOTS/f'{scenario}.png').read_bytes()).hexdigest()})
                ctx.close()
    def test_print_media_keeps_claim_and_limit(self):
        ctx,p=self.page(width=1024)
        p.emulate_media(media='print')
        self.assertEqual(p.locator('.fv-r413__limit:visible').count(),12)
        self.assertEqual(p.locator('.fv-r413__claim:visible').count(),12)
        self.assertEqual(p.locator('.fv-r413__jump:visible').count(),0)
        ctx.close()

if __name__=='__main__': unittest.main(verbosity=2)
