#!/usr/bin/env python3
"""R253 offline exact PHP Atlas action-size gate; not WordPress/axe/field CWV."""
import argparse, hashlib, json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz

MANIFEST='f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
CTA='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
SEL=', '.join('.fv-apollo-atlas '+x+' a[href^="https://www.nasa.gov/"]' for x in
  ('.plate details','.source-card details','.fv-apollo-custody-list','#fv-apollo-source-drawer'))
def sha(x):return hashlib.sha256(x).hexdigest()
def measure(page):
    for selector in ('#fv-apollo-source-drawer','.plate details','.source-card details'):
        page.locator(selector).evaluate_all('(xs)=>xs.forEach(x=>x.open=true)')
    return page.locator(SEL).evaluate_all('''es=>es.map(e=>({h:e.getBoundingClientRect().height,
      w:e.getBoundingClientRect().width,href:e.getAttribute('href')}))''')
def main():
    p=argparse.ArgumentParser();p.add_argument('--atlas',type=Path,required=True)
    p.add_argument('--css',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    m=(a.atlas/'manifest.json').read_bytes();assert sha(m)==MANIFEST
    for path,digest in json.loads(m)['files'].items():
        assert sha((a.atlas/path).read_bytes())==digest, 'R238 drift: '+path
    adapter=subprocess.run(['php',str(a.atlas/'wp-render-shim-r224.php'),
      str((a.atlas/'fv-ex2-apollo-r224.php').resolve()),'normal'],check=True,capture_output=True,text=True)
    html=json.loads(adapter.stdout)['html'];assert html==(a.atlas/'templates/atlas-fragment.html').read_text()
    css=(a.atlas/'assets/atlas-scoped.css').read_text();patch=a.css.read_text()
    assert 'min-height: 44px' in patch and '@media print' in patch
    def doc(add):return ('<!doctype html><html lang="en"><head><meta name="viewport" '
      'content="width=device-width,initial-scale=1"><style>'+css+'\n'+(patch if add else '')+
      '</style></head><body>'+html+'</body></html>')
    rows=[];shots=[];print_sources=[]
    with sync_playwright() as pw:
        b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in (320,390,768,1440,1920):
            for js in (True,False):
                c=b.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                  is_mobile=width<=390,has_touch=width<=390,reduced_motion='reduce' if not js else 'no-preference')
                pg=c.new_page();requests=[];pg.on('request',lambda r:requests.append(r.url))
                pg.set_content(doc(False));old=measure(pg);assert len(old)==20 and min(x['h'] for x in old)<24
                pg.set_content(doc(True));new=measure(pg)
                assert len(new)==20 and all(x['h']>=43.9 and x['w']>0 for x in new)
                assert all(x['href'].startswith('https://www.nasa.gov/') for x in new)
                assert pg.locator('a.cta').count()==1 and pg.locator('a.cta').get_attribute('href')==CTA
                assert pg.locator('a[href*="payhip.com"],a[href*="awin1.com"]').count()==0
                metrics=pg.evaluate('''()=>({overflow:document.documentElement.scrollWidth-innerWidth,
                  ids:[...document.querySelectorAll('.fv-apollo-atlas [id]')].map(n=>n.id),
                  times:[...document.querySelectorAll('#fv-apollo-chronology ol time[datetime]')].map(n=>n.dateTime)})''')
                assert metrics['overflow']<=1 and len(metrics['ids'])==len(set(metrics['ids']))
                assert metrics['times']==sorted(metrics['times'])
                s=pg.locator('#fv-apollo-source-drawer summary');s.focus();s.press('Enter')
                assert not pg.locator('#fv-apollo-source-drawer').evaluate('(x)=>x.open')
                s.press('Space');assert pg.locator('#fv-apollo-source-drawer').evaluate('(x)=>x.open')
                link=pg.locator('.fv-apollo-custody-list a[href^="https://www.nasa.gov/"]').first
                link.focus();assert link.evaluate('(e)=>document.activeElement===e')
                if js:
                    pg.evaluate('''()=>{window._clicked=0;for(const a of document.querySelectorAll('.fv-apollo-atlas a'))
                      a.addEventListener('click',e=>{if(a.href.startsWith('https://www.nasa.gov/'))
                        {e.preventDefault();window._clicked++}})}''')
                    if width<=390:link.tap()
                    else:link.press('Enter')
                    assert pg.evaluate('window._clicked')==1
                assert requests==[], 'unexpected HTTP request'
                if width in (390,1440):
                    pg.evaluate('''() => {if(document.activeElement?.blur)document.activeElement.blur();
                      document.scrollingElement.style.scrollBehavior='auto';window.scrollTo(0,0)}''')
                    pg.wait_for_timeout(100)
                    f=a.out/f'{width}-{"js" if js else "nojs"}.png';pg.screenshot(path=str(f),full_page=True,animations='disabled')
                    shots.append({'name':f.name,'sha256':sha(f.read_bytes())})
                if (width,js) in ((390,True),(1440,False)):
                    pg.emulate_media(media='print');pdf=fitz.open(stream=pg.pdf(print_background=True),filetype='pdf')
                    txt='\n'.join(x.get_text() for x in pdf)
                    assert 'Archival source and rights index' in txt and txt.count('nasa.gov')>=8
                    print_sources.append({'width':width,'visible_nasa_urls':txt.count('nasa.gov')})
                rows.append({'width':width,'js':js,'baseline_min_px':round(min(x['h'] for x in old),2),
                  'fixed_min_px':round(min(x['h'] for x in new),2),'source_actions':len(new),'overflow_px':max(0,metrics['overflow'])})
                c.close()
        for color,w in [('active',390),('none',320),('none',640)]:
            c=b.new_context(viewport={'width':w,'height':900},forced_colors=color);pg=c.new_page();pg.set_content(doc(True))
            assert pg.evaluate('document.documentElement.scrollWidth-innerWidth')<=1;c.close()
        c=b.new_context();pg=c.new_page();pg.set_content(doc(True).replace('min-height: 44px','min-height: 0'))
        assert min(x['h'] for x in measure(pg))<44,'mutation did not regress';c.close();b.close()
    result={'status':'PASS','not_live':True,'source_manifest_sha256':MANIFEST,
      'overlay_sha256':sha(a.css.read_bytes()),'contexts':len(rows),'rows':rows,
      'screenshots':shots,'print_source_checks':print_sources,'negative_control':'PASS',
      'extra_contexts':'forced-colors and narrow 320/640 reflow proxies',
      'axe':'NOT_RUN','browser_zoom':'NOT_RUN','wordpress':'NOT_RUN','field_lcp_cls':'NOT_RUN',
      'paid_sales':'NOT_OBSERVABLE','release':'STAGING_HOLD'}
    f=a.out/'receipt.json';f.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'PASS','contexts':len(rows),'min_before_px':min(x['baseline_min_px'] for x in rows),
      'min_after_px':min(x['fixed_min_px'] for x in rows),'receipt_sha256':sha(f.read_bytes())}))
if __name__=='__main__':main()
