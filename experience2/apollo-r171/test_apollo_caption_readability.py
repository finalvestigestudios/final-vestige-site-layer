"""Real Chromium acceptance for R171, SOURCE-DERIVED OFFLINE fixture only.

RUN: python -m unittest -v test_apollo_caption_readability.py
No network calls, WordPress writes, or claim of production acceptance.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
from apollo_caption_readability import transform, NASA_LINKS

HERE=Path(__file__).resolve().parent
R166=HERE.parent/'apollo-r166'
R168=HERE.parent/'apollo-r168'
WIDTHS=(320,360,390,768,1440,1920)

def source():
    return (R166/'verified_gallery_excerpt.html').read_text(encoding='utf-8')

def css():
    parts=[(R166/'gallery-independent.css').read_text(),
           (R166/'gallery-fallback.css').read_text(),
           (R166/'gallery-fallback-flow.r167.css').read_text(),
           (HERE/'apollo_caption_readability.css').read_text()]
    a=R168/'archive-accessibility.r168.css'
    if a.exists():parts.append(a.read_text())
    return '\n'.join(parts)

def scripts():
    return '\n'.join((R166/n).read_text() for n in ('gallery-independent.js','gallery-fallback.js'))

def document(snippet, script_enabled=True, style=True):
    # Controlled WP-like wrapper. The original historical gallery excerpt is
    # actual read-only editor-source markup; surrounding theme is NOT identical.
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<style>html{background:#171715;color:#f4efe6;font:16px/1.6 system-ui}'
            'body{margin:16px}.fv-ex2-page{max-width:960px;margin:auto}'
            '.fvx-chrono-gallery__figure{margin:1rem 0}.fvx-chrono-gallery__image{max-width:100%}'
            'a{color:#e8c98f}input{display:block}</style>'
            +(('<style>'+css()+'</style>') if style else '')+'</head><body><main class="fv-ex2-page">'
            + '<h1>Apollo 1: The Evidence Atlas</h1>'
            + snippet.replace('Moving the slider changes the archival view for exploration only.',
              'These three archival photographs are independent of the chronology slider; each retains its original NASA source record.')
            + '<label for="fire">Fire seconds</label><input id="fire" type="range" min="0" max="20" value="0">'
            + '<p><a class="fvx-continue" href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read original investigation</a></p>'
            + ('<script>'+scripts()+'</script>' if script_enabled else '')
            +'</main></body></html>')

class CaptionReadability(unittest.TestCase):
    def test_custody_and_idempotence_hold(self):
        original=source();candidate,receipt=transform(original)
        self.assertEqual(len(receipt['captions']),3)
        self.assertEqual(receipt['commercial_activation'],'HOLD')
        self.assertNotIn('payhip.com',candidate)
        self.assertEqual([candidate.count(url) for url in NASA_LINKS],[1,1,1])
        for mutation in [original.replace('NASA S66-58038','NASA fabricated record'),
                         original.replace(NASA_LINKS[1],'https://invalid.example/'),
                         original.replace('The original hatch, preserved','Fire-time hatch photo'),
                         original.replace('rel="noopener noreferrer"','rel="noopener"',1),
                         original.replace('</figcaption>','</figcaption><figcaption class="fvx-chrono-gallery__caption">x</figcaption>',1)]:
            with self.assertRaisesRegex(ValueError,'HOLD'):transform(mutation)
        with self.assertRaisesRegex(ValueError,'HOLD'):transform(candidate)
        self.assertEqual(transform(original)[0],candidate)

    def test_negative_control_old_caption_merges_words_without_css(self):
        original=source();candidate,_=transform(original)
        # Markup-only accessible reading improvement, even without CSS/JS.
        self.assertIn('test</strong>NASA',original)
        self.assertNotIn('test</strong>NASA',candidate)
        self.assertIn('test</strong>\n  <span',candidate)
        self.assertEqual(candidate.count('fvx-archive-caption__body'),3)

    def test_real_chromium_semantic_separation_six_widths(self):
        original=source();candidate,receipt=transform(original)
        artifacts=HERE/'artifacts';artifacts.mkdir(exist_ok=True)
        screenshots={}; errors=[]; metrics=[];check_count=0
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
            for width in WIDTHS:
                for enabled in (False,True):
                    context=browser.new_context(viewport={'width':width,'height':900},
                      device_scale_factor=1,java_script_enabled=enabled,
                      is_mobile=width<768,has_touch=width<768,reduced_motion='reduce')
                    context.route('**/*', lambda route:route.abort())
                    page=context.new_page();page.on('pageerror',lambda exc:errors.append(str(exc)))
                    page.set_content(document(candidate,enabled))
                    if enabled:
                        page.evaluate("""() => { window.__apollo_vitals={lcp:[],cls:0};
                           new PerformanceObserver(list=>{for(const e of list.getEntries())
                             window.__apollo_vitals.lcp.push(e.startTime)}).observe({type:'largest-contentful-paint',buffered:true});
                           new PerformanceObserver(list=>{for(const e of list.getEntries())
                             if(!e.hadRecentInput)window.__apollo_vitals.cls+=e.value}).observe({type:'layout-shift',buffered:true});
                        }""")
                    page.wait_for_timeout(100)
                    self.assertFalse(page.evaluate('document.documentElement.scrollWidth>innerWidth+1'));check_count+=1
                    figures=page.locator('[data-fvx-chrono-photo]')
                    self.assertEqual(figures.count(),3);check_count+=1
                    self.assertEqual(page.locator('.fvx-archive-caption__body').count(),3);check_count+=1
                    for i in range(3):
                        figure=figures.nth(i)
                        self.assertEqual(figure.locator('figcaption a').get_attribute('href'),NASA_LINKS[i]);check_count+=1
                        self.assertEqual(figure.locator('figcaption strong').count(),1);check_count+=1
                        self.assertEqual(figure.locator('figcaption small').count(),1);check_count+=1
                        # Inspect geometry even for the temporarily hidden frames.
                        if i==0:
                            strong=figure.locator('strong').bounding_box()
                            body=figure.locator('.fvx-archive-caption__body').bounding_box()
                            small=figure.locator('small').bounding_box()
                            self.assertIsNotNone(strong);self.assertIsNotNone(body);self.assertIsNotNone(small);check_count+=3
                            self.assertGreaterEqual(body['y'],strong['y']+strong['height']+4);check_count+=1
                            self.assertGreaterEqual(small['y'],body['y']+body['height']+4);check_count+=1
                            body_size=figure.locator('.fvx-archive-caption__body').evaluate('e=>parseFloat(getComputedStyle(e).fontSize)')
                            self.assertGreaterEqual(body_size,16);check_count+=1
                            fallback=figure.locator('[data-fvx-image-fallback]')
                            if fallback.count():
                                fb=fallback.bounding_box()
                                self.assertLessEqual(fb['y']+fb['height']+4,strong['y']);check_count+=1
                    if enabled:
                        controls=page.locator('.fvx-archive-choice__button')
                        self.assertEqual(controls.count(),3);check_count+=1
                        controls.nth(1).click()
                        self.assertTrue(figures.nth(1).is_visible());check_count+=1
                        controls.nth(1).focus();page.keyboard.press('End')
                        self.assertTrue(figures.nth(2).is_visible());check_count+=1
                        page.locator('#fire').evaluate('(e)=>{e.value="18";e.dispatchEvent(new Event("input"))}')
                        self.assertTrue(figures.nth(2).is_visible());check_count+=1
                        controls.first.click()
                        page.evaluate('document.activeElement.blur()')
                        # PerformanceObserver records are laboratory only.
                        m=page.evaluate('window.__apollo_vitals')
                        metrics.append({'width':width,'local_lcp_observed_ms':m['lcp'],'local_cls_observed':m['cls']})
                        shot=page.screenshot(full_page=True,animations='disabled')
                        (artifacts/f'caption-{width}.png').write_bytes(shot)
                        screenshots[str(width)]=hashlib.sha256(shot).hexdigest()
                    else:
                        self.assertEqual(page.locator('.fvx-archive-choice__button').count(),0);check_count+=1
                        self.assertEqual(sum(figures.nth(i).is_visible() for i in range(3)),3);check_count+=1
                    context.close()
            # Check high contrast selected label, no-JS still text separated without CSS.
            fc=browser.new_context(viewport={'width':390,'height':900},forced_colors='active')
            pg=fc.new_page();pg.set_content(document(candidate))
            self.assertEqual(pg.locator('.fvx-archive-choice__button[aria-pressed="true"]').count(),1);check_count+=1
            fc.close()
            bare=browser.new_context(viewport={'width':390,'height':900},java_script_enabled=False)
            pg=bare.new_page();pg.set_content(document(candidate,False,False))
            self.assertIn('test NASA',pg.locator('figcaption').first.inner_text().replace('\n',' '));check_count+=1
            bare.close()
            browser.close()
        self.assertEqual(errors,[])
        (artifacts/'r171-browser.json').write_text(json.dumps({
          'source_sha256':receipt['before_sha256'],'candidate_sha256':receipt['after_sha256'],
          'contexts':14,'widths':WIDTHS,'checks':check_count,'pageerrors':errors,
          'screenshots_sha256':screenshots,'performance_entries':metrics,
          'genuine_axe':'NOT_EXECUTED_NO_BINARY','installed_wordpress':'NOT_TESTED',
          'production_lcp_cls':'NOT_MEASURED','release':'STAGING_HOLD'},sort_keys=True,indent=2)+'\n')

if __name__=='__main__':unittest.main(verbosity=2)
