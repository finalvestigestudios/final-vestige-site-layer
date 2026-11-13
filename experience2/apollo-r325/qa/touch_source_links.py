#!/usr/bin/env python3
"""Apollo R325: actual Chromium tap-target/accessibility regression; never visits live WordPress."""
import hashlib, json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
PHP=ROOT/'apollo-r281/apollo-source-experience.php'
CSS=ROOT/'apollo-r281/assets/apollo-source-experience.css'
JS=ROOT/'apollo-r281/assets/apollo-cache-continuation.js'
STUB=ROOT/'apollo-r320/qa/wp_late_shortcodes.php'
OUT=ROOT/'apollo-r325/QA'
PIN={'php':'91745c286b2f23fb8a93058afb58905a2756714e',
     'css':'550e1dc6ac869ebbda1b371343a6cdd91f8608f4',
     'js':'f85617e5f12ba747908ac507261f69c377369de7'}
MARKER='/* R325 — primary NASA evidence links'
BASE_CSS_BLOB='7c0e58782a8ec7b23f28da784a84c827f117914a'
WIDTHS=(320,360,390,768,1024,1440,1920)

def git_blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def assert_pins():
    for k,p in [('php',PHP),('css',CSS),('js',JS)]:
        assert git_blob(p.read_bytes())==PIN[k], f'unreviewed {k} source drift'
    subprocess.run(['php','-l',str(PHP)],check=True,capture_output=True)
    subprocess.run(['node','--check',str(JS)],check=True,capture_output=True)

def render_html():
    raw=subprocess.check_output(['php',str(STUB),'late-dynamic','1'],text=True)
    head,trail=raw.split('<!--R320_QUEUE:',1)
    assert json.loads(trail.split('-->')[0])['calls']==1
    return head

def source_links(page):
    return page.locator('section.fv-r281 a[data-fv-link-purpose]')

def measured_targets(page):
    page.locator('section.fv-r281 details').evaluate_all('(els)=>els.forEach(e=>e.open=true)')
    return source_links(page).evaluate_all('''els=>els.map(el=>{
      const r=el.getBoundingClientRect();return {href:el.href,text:el.innerText.trim().slice(0,55),
      width:+r.width.toFixed(2),height:+r.height.toFixed(2),display:getComputedStyle(el).display};
    })''')

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    assert_pins()
    css=CSS.read_text();baseline,marker_tail=css.split(MARKER,1)
    assert marker_tail and git_blob(baseline[:-1].encode())==BASE_CSS_BLOB, 'negative-control original CSS changed'
    assert 'r325-'+hashlib.sha256(CSS.read_bytes()).hexdigest()[:12] in PHP.read_text()
    html=render_html()
    results=[]
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            # Exact R324 CSS controls show real sub-24px NASA source-link targets.
            baseline_page=b.new_page(viewport={'width':1440,'height':900})
            baseline_page.goto('about:blank');baseline_page.set_content(html.replace('</head>','<style>'+baseline+'</style></head>'))
            old=measured_targets(baseline_page)
            small=[e for e in old if e['height']<24]
            assert len(small)>=3, f'R324 regression witness missing: {small}'
            baseline_page.close()
            for width in WIDTHS:
                for enabled in (True,False):
                    ctx=b.new_context(viewport={'width':width,'height':900},
                       java_script_enabled=enabled,has_touch=width<=390,reduced_motion='reduce')
                    page=ctx.new_page();page.goto('about:blank')
                    page.set_content(html.replace('</head>','<style>'+css+'</style></head>'))
                    if enabled:page.add_script_tag(content=JS.read_text())
                    targets=measured_targets(page)
                    assert len(targets)>=15, ('missing cited targets',len(targets))
                    short=[e for e in targets if e['height']<43.5 or e['width']<24]
                    assert not short, (width,enabled,short[:4])
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'), (width,'horizontal overflow')
                    assert page.locator('section.fv-r281 a[data-fv-cta]').count()==1
                    assert page.locator('[data-fv-image-rights="not-cleared-for-reuse"]').count()==4
                    assert page.locator('[data-lat],[data-lng],[data-geo-edge],img,video').count()==0
                    assert all(e['href'].startswith('https://www.nasa.gov/') or e['href'].startswith('https://sma.nasa.gov/') for e in targets)
                    # Real pointer hit test: center of an official source link must hit the link itself.
                    first=source_links(page).first
                    first.scroll_into_view_if_needed(timeout=3000)
                    hit=first.evaluate('''e=>{
                      const r=e.getBoundingClientRect(), x=r.x+r.width/2,y=r.y+r.height/2;
                      return document.elementFromPoint(x,y)?.closest('a')===e;}''')
                    assert hit, (width,enabled,'hit target is obscured')
                    first.focus()
                    assert first.evaluate('e=>document.activeElement===e')
                    focus=first.evaluate('e=>getComputedStyle(e).outlineStyle')
                    assert focus!='none', (width,enabled,'missing keyboard focus outline')
                    if width in (390,1440) and enabled:
                        page.screenshot(path=str(OUT/f'r325-{width}-source-tap.png'),full_page=False)
                    results.append({'width':width,'js':enabled,'sourceLinks':len(targets),
                        'minHeight':min(e['height'] for e in targets),
                        'minWidth':min(e['width'] for e in targets),'keyboardOutline':focus,'centerHit':hit})
                    ctx.close()
            # Forced-colors and 200% text: same source navigation remains reachable.
            for style in ('forced-colors','200-percent-type'):
                ctx=b.new_context(viewport={'width':390,'height':800},reduced_motion='reduce')
                pg=ctx.new_page();pg.goto('about:blank');pg.set_content(html.replace('</head>','<style>'+css+'</style></head>'))
                if style=='forced-colors':pg.emulate_media(forced_colors='active')
                else:pg.add_style_tag(content='html{font-size:200%!important}')
                dims=measured_targets(pg)
                assert len(dims)>=15 and all(t['height']>=43.5 for t in dims)
                assert pg.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),style
                ctx.close()
        finally:b.close()
    receipt={'version':'R325','scope':'STAGING local Chromium, not WordPress/CDN',
      'browserContexts':results,'baselineNegativeCount':len(small),'baselineExamples':small[:4],
      'sourceBlobs':PIN,'axe':'BLOCKED: genuine axe-core not executed',
      'nativeHttp':'UNVERIFIED','screenReader':'NOT EXECUTED','productionCoreWebVitals':'NOT MEASURED',
      'purchase':'UNVERIFIED; no authenticated SKU or settled order'}
    (OUT/'r325-touch-qa-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(f'R325 PASS {len(results)}/{len(results)} Chromium width/JS contexts, {len(small)} genuine baseline short targets, two accessibility profiles')

if __name__=='__main__':main()
