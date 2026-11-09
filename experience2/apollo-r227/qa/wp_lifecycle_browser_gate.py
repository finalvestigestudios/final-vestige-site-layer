#!/usr/bin/env python3
"""R227 exact-input Apollo / WordPress lifecycle and browser acceptance.

Staging only: no network requests, WP/database writes, analytics or paid services.
Tests a small WP-function shim, NOT an installed WordPress site.
Requires Python Playwright and a local Chromium executable.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from playwright.sync_api import sync_playwright

PINNED_R225_MANIFEST_SHA256 = '4efaf0a57d38af349d44302905fbfdc8b8936ac8bbc04a2d7a61fb805ba93628'
FREE_URL = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
WIDTHS = (320, 390, 768, 1440, 1920)
SCENARIOS = ('direct','reusable','nested','cycle','missing-ref','ordinary','late','printed','double')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def canonical(data):
    return (json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')


def pinned(dist):
    check(sha((dist/'manifest.json').read_bytes())==PINNED_R225_MANIFEST_SHA256,'R225 manifest SHA mismatch')
    manifest=json.loads((dist/'manifest.json').read_text())
    for name, expected in manifest['files'].items():
        path=dist/name
        check(path.is_file() and sha(path.read_bytes())==expected,'R225 generated asset drift: '+name)
    return manifest


def php_scenario(shim,dist,scenario):
    proc=subprocess.run(['php',str(shim),str(dist/'fv-ex2-apollo-r224.php'),scenario],
                        capture_output=True,text=True,timeout=9,check=False)
    check(proc.returncode==0,'PHP scenario '+scenario+' failed: '+proc.stderr[:400])
    try:
        data=json.loads(proc.stdout)
    except ValueError as exc:
        raise AssertionError('invalid PHP JSON scenario '+scenario+': '+proc.stdout[:200]) from exc
    check(data['mode']==scenario,'wrong PHP mode')
    return data


def run_php(shim,dist):
    summary={}
    for mode in SCENARIOS:
        row=php_scenario(shim,dist,mode)
        present=bool(row['html'])
        should_show=mode in ('direct','reusable','nested','printed','double')
        check(present== (should_show or mode=='late'), mode+' presence mismatch')
        if mode in ('direct','reusable','nested','double'):
            check(row['css']=='enqueued',mode+' failed CSS preflight')
        if mode=='printed':check(row['css']=='done','CSS not printed by head')
        if mode in ('ordinary','cycle','missing-ref','late'):
            check(row['css']=='absent',mode+' unexpected CSS')
        if should_show:
            check(not row['fallback'] and '<article' in row['html'],mode+' expected full content')
            check(row['html'].count(FREE_URL)==1,mode+' incorrect editorial destination count')
        if mode=='late':
            check(row['fallback'] and FREE_URL in row['html'],'late render did not fail open')
        if mode=='double':check(row['second_fallback'],'second shortcode created duplicate IDs')
        if mode=='nested':check(row['parse_calls']==2,'synced nested block not walked')
        if mode=='cycle':check(row['parse_calls']<=4,'recursive block cycle not bounded')
        summary[mode]={'css':row['css'],'fallback':row['fallback'],
                       'second_fallback':row['second_fallback'], 'parse_calls':row['parse_calls'],
                       'content_sha256':row['content_sha256']}
    full=php_scenario(shim,dist,'direct')['html']
    # Only staging copies can be mutated, never the pinned input directory.
    mutations=(('atlas-html','templates/atlas-fragment.html',lambda b:b+b'<!-- R227 unreviewed edit -->'),
               ('css-bytes','assets/atlas-scoped.css',lambda b:b+b'/* R227 mutation */'),
               ('crosswalk','source-url-crosswalk.json',lambda b:b+b' '),
               ('chronology','chronology-period-custody.json',lambda b:b+b' '))
    for label,name,change in mutations:
        with tempfile.TemporaryDirectory(prefix='fv-r227-mut-') as tmp:
            copy=Path(tmp)/'dist'
            shutil.copytree(dist,copy)
            target=copy/name
            target.write_bytes(change(target.read_bytes()))
            damaged=php_scenario(shim,copy,'tamper')
            check(damaged['fallback'] and damaged['css']=='absent',label+' tamper bypassed fail-open')
        summary['mutation_'+label]={'detected':True}
    with tempfile.TemporaryDirectory(prefix='fv-r227-missing-') as tmp:
        copy=Path(tmp)/'dist';shutil.copytree(dist,copy)
        (copy/'templates/atlas-fragment.html').unlink()
        lost=php_scenario(shim,copy,'missing-file')
        check(lost['fallback'] and lost['css']=='absent','missing template bypassed fail-open')
        summary['mutation_missing_template']={'detected':True}
    return full,summary


def test_browser(html,css,out):
    records=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for width in WIDTHS:
                for js in (False,True):
                    mode='js' if js else 'nojs'
                    ctx=browser.new_context(viewport={'width':width,'height':850},
                        device_scale_factor=1,java_script_enabled=js,
                        has_touch=width<=390,is_mobile=width<=390,
                        reduced_motion='reduce' if width==320 else 'no-preference')
                    page=ctx.new_page()
                    requests=[]
                    page.on('request',lambda req:requests.append(req.url))
                    doc=('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                         '<meta name="viewport" content="width=device-width, initial-scale=1">'
                         '<title>Apollo 1 / Staging Acceptance</title><style>'+css+'</style></head><body>'
                         +html+'</body></html>')
                    page.set_content(doc,wait_until='load')
                    check(page.locator('h1').count()==1,'h1 count '+mode)
                    check(page.locator('.fv-apollo-atlas').count()==1,'Apollo Atlas missing')
                    cta=page.locator(f'a[href="{FREE_URL}"]')
                    check(cta.count()==1,'free editorial CTA missing/duplicated')
                    check(cta.is_visible(),'editorial CTA hidden')
                    box=cta.bounding_box()
                    check(box is not None and box['height']>=44,'CTA touch target under 44px')
                    overflow=page.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
                    check(overflow<=1,f'horizontal overflow {width} {mode}: {overflow}')
                    refs=page.evaluate('''() => {
                      const all=[...document.querySelectorAll('[id]')].map(el=>el.id);
                      const bad=[];
                      for(const el of document.querySelectorAll('[aria-labelledby],[aria-describedby],[href^="#"]')){
                        for(const attr of ['aria-labelledby','aria-describedby','href']){
                          if(!el.hasAttribute(attr))continue;
                          if(attr==='href' && !el.getAttribute('href').startsWith('#'))continue;
                          const ids=attr==='href'?[el.getAttribute(attr).slice(1)]:el.getAttribute(attr).split(/\\s+/);
                          for(const id of ids)if(id&&!document.getElementById(id))bad.push(attr+':'+id);
                        }
                      }
                      return {duplicated:all.length-new Set(all).size,bad};
                    }''')
                    check(refs['duplicated']==0 and not refs['bad'],'IDs/ARIA bad '+str(refs))
                    check(not requests,'unexpected external browser requests '+str(requests[:2]))
                    img=out/f'{width}-{mode}.png'
                    page.screenshot(path=str(img),full_page=True,animations='disabled')
                    sums=page.locator('details > summary')
                    check(sums.count()>=4,'source disclosures missing')
                    if js:
                        sums.first.focus()
                        page.keyboard.press('Enter')
                    else:
                        if width<=390:
                            sums.first.tap()  # Real Playwright touch input in mobile contexts.
                        else:
                            sums.first.click()
                    check(sums.first.evaluate('(e)=>e.parentElement.open'),'native disclosure failed '+mode)
                    access='not_tested'
                    if js and width==390:
                        snap=cta.aria_snapshot()
                        check('link' in snap.lower(),'CTA lost native link semantics')
                        access=sha(snap.encode())
                    records.append({'width':width,'javascript':js,'overflow':overflow,
                        'screenshot_sha256':sha(img.read_bytes()),'disclosure':'pass',
                        'native_cta_ax':access,'remote_requests':len(requests)})
                    ctx.close()
        finally:
            browser.close()
    return records


def main():
    args=argparse.ArgumentParser()
    args.add_argument('--dist',required=True,type=Path)
    args.add_argument('--out',required=True,type=Path)
    parsed=args.parse_args()
    dist=parsed.dist.resolve();out=parsed.out.resolve();out.mkdir(parents=True,exist_ok=True)
    shim=Path(__file__).with_name('wp_lifecycle_shim.php')
    pinned(dist)
    fragment,php=run_php(shim,dist)
    browser=test_browser(fragment,(dist/'assets/atlas-scoped.css').read_text(),out)
    receipt={'status':'PASS','input_manifest_sha256':PINNED_R225_MANIFEST_SHA256,
        'php':php,'browser':browser,
        'limits':['PHP function shim only: not installed WordPress or Assembler',
                  'page.set_content: not HTTP navigation',
                  'native Chromium semantics: axe-core and screen reader not executed',
                  'no production field LCP/CLS or merchant conversion evidence',
                  'no page or affiliate activation']}
    (out/'receipt.json').write_bytes(canonical(receipt))
    print('PASS: 9 PHP lifecycle scenarios, 5 integrity mutations, 10 Chromium contexts')
    print('receipt_sha256='+sha((out/'receipt.json').read_bytes()))

if __name__=='__main__':main()
