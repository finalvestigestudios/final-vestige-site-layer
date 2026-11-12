#!/usr/bin/env python3
"""R319: real Chromium CDP accessibility-tree audit; offline, NOT axe/WP acceptance."""
import hashlib, json, subprocess
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
PHP = ROOT/'apollo-r281/apollo-source-experience.php'
JS = ROOT/'apollo-r281/assets/apollo-cache-continuation.js'
CSS = ROOT/'apollo-r281/assets/apollo-source-experience.css'
FIXTURE = ROOT/'apollo-r301/qa/local_http_fixture.php'
OUT = ROOT/'apollo-r319/QA'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
UTM = 'utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo1_yt_longform001'
BLOBS = {'php':'9ff32d45b7e957e1d25724ab5fc55c467aaa55e2',
         'js':'a3c858b51005495ebebb326086badc155c1b7e5a'}


def git_blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def render(query):
    return subprocess.check_output(['php','-r','parse_str($argv[2],$_GET);include $argv[1];',
        str(FIXTURE),'instances=2&queue=0&'+query],text=True)


def tree_audit(cdp):
    roles = [(n.get('role',{}).get('value'),n.get('name',{}).get('value','').strip())
             for n in cdp.send('Accessibility.getFullAXTree')['nodes'] if not n.get('ignored')]
    controls = [(r,n) for r,n in roles if r in ('link','DisclosureTriangle','button')]
    regions = [n for r,n in roles if r=='region']
    return {'controls':len(controls),'unnamed':[r for r,n in controls if not n],
            'disclosures':sum(r=='DisclosureTriangle' for r,n in controls),
            'regions':regions}


def main():
    assert git_blob(PHP.read_bytes())==BLOBS['php']
    assert git_blob(JS.read_bytes())==BLOBS['js']
    subprocess.run(['php','-l',str(PHP)],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['node','--check',str(JS)],check=True,stdout=subprocess.DEVNULL)
    raw=render(UTM)
    assert raw==render('')==render('utm_campaign=invalid'), 'Cache variant changed'
    html=raw.replace('</head>','<style>'+CSS.read_text()+'</style></head>')
    receipts=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in (320,390,768,1440,1920):
            for mode in ('js','nojs','forced'):
                enabled=mode!='nojs'
                ctx=browser.new_context(viewport={'width':width,'height':900},
                    java_script_enabled=enabled,has_touch=width<=390,reduced_motion='reduce',
                    forced_colors='active' if mode=='forced' else 'none',service_workers='block')
                pg=ctx.new_page()
                pg.goto('about:blank?'+UTM)
                pg.set_content(html)
                if enabled: pg.add_script_tag(content=JS.read_text())
                assert pg.locator('section.fv-r281').count()==2
                assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                cdp=ctx.new_cdp_session(pg)
                cdp.send('Accessibility.enable')
                closed=tree_audit(cdp)
                assert not closed['unnamed'] and closed['disclosures']==14,closed
                assert len(closed['regions'])==2 and len(set(closed['regions']))==2
                pg.locator('section.fv-r281 details').evaluate_all('(a)=>a.forEach(d=>d.open=true)')
                opened=tree_audit(cdp)
                assert not opened['unnamed'] and opened['controls']>closed['controls'],opened
                cta=pg.locator('section.fv-r281 a[data-fv-cta]').first
                cta.focus();pg.keyboard.press('Shift+F10')
                got=cta.get_attribute('href')
                assert (dict(parse_qsl(urlsplit(got).query))==dict(parse_qsl(UTM))) if enabled else got==FREE
                assert pg.locator('section.fv-r281 a[data-fv-cta]').nth(1).get_attribute('href')==FREE
                route=pg.locator('section.fv-r281 .fv-r281__authority-jump a').first
                route.click()
                target=pg.locator(pg.evaluate('location.hash'))
                assert target.count()==1 and target.is_visible()
                assert target.evaluate('(n)=>n===document.activeElement')
                if width==390 and mode=='js':
                    cta.evaluate('(n)=>{n.textContent="";n.removeAttribute("aria-label")}')
                    assert tree_audit(cdp)['unnamed'], 'Mutated empty link was not detected'
                    cta.evaluate('(n)=>{n.textContent="Read the free Apollo 1 investigation"}')
                if width in (390,1440) and mode in ('js','nojs'):
                    OUT.mkdir(parents=True,exist_ok=True)
                    pg.screenshot(path=str(OUT/f'r319-{width}-{mode}-ax.png'),full_page=True,animations='disabled')
                receipts.append({'width':width,'mode':mode,'closed':closed,'opened':opened,'pass':True})
                ctx.close()
        browser.close()
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'r319-cdp-receipt.json').write_text(json.dumps({
        'contexts':receipts,'count':len(receipts),'negative_control':'PASS: unnamed link detected',
        'accessibility_source':'Chromium CDP Accessibility.getFullAXTree',
        'axe_core':'NOT RUN','browser_http_csp':'BLOCKED BY ADMINISTRATOR',
        'wordpress_installed':'NOT TESTED','production_cwv':'NOT MEASURED'},indent=2)+'\n')
    print('R319 PASS: 15/15 offline Chromium CDP accessibility contexts, mutated link rejected')

if __name__=='__main__':main()
