"""R166 exact-source integration smoke. Controlled source excerpt, never WordPress acceptance."""
import hashlib
import json
import os
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
from build_offline import build, REQUIRED_NASA

HERE = Path(__file__).resolve().parent
WIDTHS = (320,360,390,768,1440,1920)
EXCERPT = (HERE/'verified_gallery_excerpt.html').read_text(encoding='utf8')
OLD = '''<label>Fire seconds<input id="fire" type="range" min="0" max="14" value="0"></label><script>
(()=>{const box=document.querySelector('[data-fvx-chrono-gallery]');
const range=document.querySelector('#fire');const update=()=>{const t=Number(range.value);
        /* Historical context views: these photos are NOT time-stamped fire evidence. */
const photos = box.querySelectorAll('[data-fvx-chrono-photo]');
const index = t < 6 ? 0 : (t < 11.3 ? 1 : 2);
const position=box.querySelector('[data-fvx-chrono-position]');
photos.forEach((f,i)=>{f.hidden=i!==index;});
position.textContent = 'Context photo ' + index;
      };
      range.addEventListener('input', update);
update();})();</script>'''
CSS = '<style>*{box-sizing:border-box}html{background:#181715;color:#faf3e7;font:16px/1.6 system-ui}body{margin:0;padding:1rem}.fvx-chrono-gallery{max-width:1000px;margin:auto}.fvx-chrono-gallery img{width:100%;height:250px;object-fit:contain}figure[hidden]{display:none!important}a{color:#f7d69d}</style>'

def editor(): return '<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1">'+CSS+'<body>'+EXCERPT+OLD+'</body></html>'

class Integration(unittest.TestCase):
 def test_drift(self):
  src=editor(); self.assertRaises(ValueError,build,src.replace(REQUIRED_NASA[1],'https://invalid.test/'))
  self.assertRaises(ValueError,build,src.replace('t < 6 ?','t < 7 ?'))
  ready=build(src)
  self.assertNotIn('t < 11.3 ?',ready)
  self.assertTrue(all(ready.count(u)==1 for u in REQUIRED_NASA))
 def test_real_chromium(self):
  receipt={'mode':'CONTROLLED_EDITOR_EXCERPT','widths':{},'release':'HOLD'}
  with sync_playwright() as p:
   b=p.chromium.launch(executable_path=os.getenv('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
   for width in WIDTHS:
    for enabled in (False,True):
     ctx=b.new_context(viewport={'width':width,'height':800},java_script_enabled=enabled,reduced_motion='reduce')
     ctx.route('**/*',lambda route:route.abort())  # no actual NASA media transport
     page=ctx.new_page();page.set_content(build(editor()),wait_until='load');page.wait_for_timeout(90)
     figs=page.locator('figure[data-fvx-chrono-photo]');self.assertEqual(figs.count(),3)
     self.assertEqual(page.locator('figcaption a[href]').count(),3)
     self.assertTrue(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
     if enabled:
      btn=page.locator('.fvx-archive-choice__button');self.assertEqual(btn.count(),3)
      btn.nth(1).click();self.assertTrue(figs.nth(1).is_visible())
      page.locator('#fire').evaluate('(e)=>{e.value="12";e.dispatchEvent(new Event("input"))}')
      self.assertTrue(figs.nth(1).is_visible())
      self.assertTrue(page.locator('[data-fvx-image-fallback]').count()>=1)
      btn.nth(2).click();btn.nth(2).focus();page.keyboard.press('Home');self.assertTrue(figs.nth(0).is_visible())
     else:self.assertTrue(all(figs.nth(i).is_visible() for i in range(3)))
     if enabled:
      screenshot=page.screenshot(full_page=True,animations='disabled')
      receipt['widths'][str(width)]={'sha256':hashlib.sha256(screenshot).hexdigest()}
     ctx.close()
   b.close()
  (HERE/'artifacts').mkdir(exist_ok=True)
  (HERE/'artifacts'/'integrated_receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True))

if __name__=='__main__':unittest.main()
