"""Offline Chromium smoke for R163. Run python test_smoke.py.
Source: R162 exact 3-photo fragment; mocked image transport, never installed WP.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from stage_patch import patch
import json, hashlib
D=Path(__file__).parent
old=D.parent/'apollo-r162'/'live_gallery_fragment.html'
fragment=(old if old.exists() else D/'live_gallery_fragment.html').read_text()
assert hashlib.sha256(fragment.encode()).hexdigest() == 'c814d0ce743a6f49caf16c66218702d9272d8b370ba965dc36b61a3b56df56df'
oldcode="""<script>
const box = document.querySelector('[data-fvx-chronology]');
const range = box.querySelector('input');
const update = () => {
 const t = +range.value;
        /* Historical context views: these photos are NOT time-stamped fire evidence. */
        const photos = box.querySelectorAll('[data-fvx-chrono-photo]');
        if (photos.length === 3) {
          const index = t < 6 ? 0 : (t < 11.3 ? 1 : 2);
          photos.forEach((photo, i) => { photo.hidden = i !== index; });
          const position = box.querySelector('[data-fvx-chrono-position]');
          if (position) {
            position.hidden = false;
            position.textContent = 'Context photo ' + (index + 1) + ' of 3 · These photographs do not depict the marked seconds.';
          }
        }
      };
      range.addEventListener('input', update);
      update();
</script>"""
head="""<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><style>
body{margin:0;background:#090a0a;color:#eee;font:16px system-ui}.fv-ex2-page{max-width:1100px;margin:auto;padding:16px;box-sizing:border-box}
.fvx-chrono-gallery{border:1px solid #776;padding:12px;box-sizing:border-box}.fvx-chrono-gallery__figure[hidden]{display:none!important}
.fvx-chrono-gallery__figure{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.fvx-chrono-gallery__image{width:100%;max-width:100%;height:160px;object-fit:contain}
.fvx-chrono-gallery__caption{min-width:0;overflow-wrap:anywhere}
.fvx-chrono-gallery__caption strong{display:block}.fvx-chrono-gallery__caption small{display:block}
@media(max-width:760px){.fvx-chrono-gallery__figure{grid-template-columns:minmax(0,1fr)}}
</style><body><main class=fv-ex2-page><section data-fvx-chronology><input aria-label='Seconds' type=range min=0 max=14.7 step=.1 value=0>"""
source=head+fragment.replace('Moving the slider changes the archival view for exploration only.','Moving the slider changes the archival view for exploration only.')+'</section></main>'+oldcode
preview=patch(source,(D/'gallery-independent.js').read_text(),(D/'gallery-independent.css').read_text())
tests=0
def ok(v):
 global tests
 assert v
 tests+=1
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width in (320,360,390,768,1440,1920):
  ctx=browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce')
  page=ctx.new_page();page.set_content(preview,wait_until='domcontentloaded')
  g=page.locator('[data-fvx-chrono-gallery]');b=g.locator('button')
  ok(b.count()==3);ok(g.locator('figure:visible').count()==1)
  b.nth(1).click();ok(g.locator('figure:visible').first.get_attribute('data-fvx-chrono-photo')=='1')
  page.locator('input[type=range]').fill('14')
  ok(g.locator('figure:visible').first.get_attribute('data-fvx-chrono-photo')=='1')
  b.nth(1).focus();page.keyboard.press('ArrowRight')
  ok(b.nth(2).get_attribute('aria-pressed')=='true')
  ok(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
  ctx.close()
 for width in (320,390,1920):
  ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=False)
  page=ctx.new_page();page.set_content(preview,wait_until='domcontentloaded')
  ok(page.locator('figure:visible').count()==3)
  ok(page.locator('figcaption a').count()==3)
  ctx.close()
 browser.close()
print(json.dumps({'status':'PASS','assertions':tests,'scope':'offline HTML fixture; not WordPress staging or axe-core'}))
