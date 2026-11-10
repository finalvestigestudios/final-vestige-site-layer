#!/usr/bin/env python3
"""R255 original-PHP Apollo Atlas touch-path browser gate. Offline staging; no WP/HTTP/axe assertions."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

SEALED_MANIFEST_SHA256 = 'f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
INVESTIGATION = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
PATHS = ('#fv-apollo-finding-oxygen', '#fv-apollo-finding-fire', '#fv-apollo-photo-aftermath')
ALL = '.fv-apollo-atlas a, .fv-apollo-atlas summary'
TARGET = '.fv-apollo-atlas .fv-apollo-confidence-answer a[href^="#fv-apollo-"]'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(atlas, r253, r254, r255):
    raw = (atlas/'manifest.json').read_bytes()
    assert sha(raw)==SEALED_MANIFEST_SHA256, 'sealed NASA R238 manifest drift'
    for rel, checksum in json.loads(raw)['files'].items():
        assert sha((atlas/rel).read_bytes()) == checksum, 'sealed file drift: '+rel
    php = subprocess.run(['php', str(atlas/'wp-render-shim-r224.php'),
        str((atlas/'fv-ex2-apollo-r224.php').resolve()), 'normal'], capture_output=True,
        text=True, check=True)
    html = json.loads(php.stdout)['html']
    assert html == (atlas/'templates/atlas-fragment.html').read_text(), 'source PHP/HTML drift'
    css = '\n'.join(p.read_text() for p in (atlas/'assets/atlas-scoped.css',r253,r254))
    add = r255.read_text()
    assert '.fv-apollo-confidence-answer' in add and 'min-height: 44px' in add
    assert '@media print' in add and 'forced-colors' in add
    return html,css,add


def doc(html, css):
    return ('<!doctype html><html lang="en"><head><meta name="viewport" '
        'content="width=device-width, initial-scale=1"><style>'+css+
        '</style></head><body>'+html+'</body></html>')


def interactives(page, selector=ALL):
    return page.locator(selector).evaluate_all('''es=>es.filter(e=>{
      const r=e.getBoundingClientRect(),s=getComputedStyle(e);
      return r.width>0 && r.height>0 && s.visibility!=='hidden' && s.display!=='none'
    }).map(e=>({tag:e.tagName,href:e.getAttribute('href'),
      text:e.textContent.trim().slice(0,80),height:+e.getBoundingClientRect().height.toFixed(2),
      width:+e.getBoundingClientRect().width.toFixed(2)}))''')


def main():
    ap=argparse.ArgumentParser()
    for name in ('atlas','r253','r254','r255','out'):
        ap.add_argument('--'+name, type=Path, required=True)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    html,base,overlay=load(a.atlas,a.r253,a.r254,a.r255)
    results=[];screens=[]
    with sync_playwright() as pw:
        b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in (320,390,768,1440,1920):
            for js in (True,False):
                c=b.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                    is_mobile=width<=390,has_touch=width<=390,
                    reduced_motion='reduce' if not js else 'no-preference')
                page=c.new_page();requests=[];page.on('request',lambda req:requests.append(req.url))
                page.set_content(doc(html,base))
                page.locator('details').evaluate_all('es=>es.forEach(e=>e.open=true)')
                prior=[x for x in interactives(page,TARGET) if x['height']<43.99]
                assert len(prior)==3, f'unexpected pre-fix size at {width}: {prior}'
                page.set_content(doc(html,base+'\n'+overlay))
                page.locator('details').evaluate_all('es=>es.forEach(e=>e.open=true)')
                actions=interactives(page)
                failed=[x for x in actions if x['height']<43.99 or x['width']<=0]
                assert not failed, f'{width} js={js} undersized actions: {failed}'
                anchors=interactives(page,TARGET)
                assert len(anchors)==3 and {x['href'] for x in anchors}==set(PATHS)
                assert page.locator('.fv-apollo-atlas a.cta').count()==1
                assert page.locator('.fv-apollo-atlas a.cta').get_attribute('href')==INVESTIGATION
                assert page.locator('a[href*="payhip.com"],a[href*="awin1.com"]').count()==0
                assert page.locator('.fv-apollo-atlas a[href^="https://www.nasa.gov/"]').count()>=47
                assert page.evaluate('document.documentElement.scrollWidth-innerWidth')<=1
                first=page.locator(TARGET).first
                first.focus(); assert first.evaluate('e=>document.activeElement===e')
                if width<=390: first.tap()
                else: first.press('Enter')
                assert page.evaluate('location.hash')==PATHS[0], 'internal evidence anchor did not navigate'
                assert page.locator(PATHS[0]).count()==1
                # All three targets remain addressable; even no-JS native anchors work.
                summary=page.locator('#fv-apollo-source-drawer summary')
                summary.focus();summary.press('Enter')
                assert not page.locator('#fv-apollo-source-drawer').evaluate('e=>e.open')
                summary.press('Space')
                assert page.locator('#fv-apollo-source-drawer').evaluate('e=>e.open')
                assert not requests, f'unexpected external network dependency: {requests}'
                if width in (390,1440):
                    shot_page=c.new_page()
                    shot_page.set_content(doc(html,base+'\n'+overlay))
                    shot_page.locator('details').evaluate_all('es=>es.forEach(e=>e.open=true)')
                    file=a.out/f'{width}-{"js" if js else "nojs"}.png'
                    shot_page.screenshot(path=str(file),full_page=True,animations='disabled')
                    shot_page.close()
                    screens.append({'file':file.name,'sha256':sha(file.read_bytes())})
                results.append({'width_css_px':width,'javascript':js,
                    'prior_small_evidence_paths':len(prior),'evidence_path_links':len(anchors),
                    'all_visible_actions':len(actions),
                    'minimum_action_height_px':min(x['height'] for x in actions),
                    'overflow_px':max(0,page.evaluate('document.documentElement.scrollWidth-innerWidth'))})
                c.close()
        # Narrow CSS viewport simulates 200% zoom's reflow stress; not browser UI zoom.
        c=b.new_context(viewport={'width':160,'height':900},java_script_enabled=False)
        p=c.new_page();p.set_content(doc(html,base+'\n'+overlay))
        p.locator('details').evaluate_all('es=>es.forEach(e=>e.open=true)')
        assert p.evaluate('document.documentElement.scrollWidth-innerWidth')<=1
        assert all(x['height']>=43.99 for x in interactives(p))
        c.close()
        # Demonstrate a real regression is detected if R255 source overlay is removed.
        c=b.new_context(viewport={'width':390,'height':900});p=c.new_page()
        p.set_content(doc(html,base))
        p.locator('details').evaluate_all('es=>es.forEach(e=>e.open=true)')
        assert len([x for x in interactives(p) if x['height']<43.99])==3
        c.close()
        # Print CSS does not introduce touch affordances into the archival print reading flow.
        c=b.new_context(viewport={'width':390,'height':900});p=c.new_page()
        p.set_content(doc(html,base+'\n'+overlay));p.emulate_media(media='print')
        styles=p.locator(TARGET).first.evaluate('e=>({display:getComputedStyle(e).display,minHeight:getComputedStyle(e).minHeight})')
        assert styles['display']=='inline' and styles['minHeight']=='0px',styles
        c.close();b.close()
    receipt={'release':'STAGING_HOLD','status':'PASS','source_manifest_sha256':SEALED_MANIFEST_SHA256,
        'r253_sha256':sha(a.r253.read_bytes()),'r254_sha256':sha(a.r254.read_bytes()),
        'r255_sha256':sha(a.r255.read_bytes()),'php_original_source_match':True,
        'contexts':len(results),'rows':results,'screenshots':screens,
        'negative_control':'PASS','narrow_160px_reflow':'PASS','print_reset':'PASS',
        'genuine_axe':'NOT_RUN','installed_wordpress':'NOT_RUN','http_csp':'NOT_RUN',
        'field_lcp_cls':'NOT_RUN','browser_ui_zoom':'NOT_RUN',
        'paid_transactions_and_net_revenue':'NOT_OBSERVABLE'}
    (a.out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'result':'PASS','contexts':len(results),'baseline_short_targets':3,
        'remaining_short_targets':0,'min_height':min(r['minimum_action_height_px'] for r in results),
        'screenshots':len(screens),'sha256':sha((a.out/'receipt.json').read_bytes())},sort_keys=True))

if __name__=='__main__': main()
