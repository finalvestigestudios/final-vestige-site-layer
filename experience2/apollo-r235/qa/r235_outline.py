#!/usr/bin/env python3
"""Apollo R235: pin-verified section-outline correction and exact-fragment Chromium gate.

Offline local fixture only; intentionally does not install WordPress or claim axe/field CWV.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

PARENT_MANIFEST = 'bde3b3595c88f230ec0ffdeb978080c6d3c9f7ab638dbabe481b470ff540ff9f'
PARENT_INDEX = 'f996183d3e36191c045348b61b0e70573974c58ce38a1f2e0c5fb52e499545d1'
OLD_HEADING = '<h3 id="fv-apollo-trace-title">Trace each finding to what the source actually supports.</h3>'
NEW_HEADING = OLD_HEADING.replace('<h3 ', '<h2 ').replace('</h3>', '</h2>')
OLD_STYLE = '.fv-apollo-atlas .fv-apollo-trace h3{'
NEW_STYLE = '.fv-apollo-atlas .fv-apollo-trace > h2{'

def sha(data): return hashlib.sha256(data).hexdigest()
def read(path): return path.read_bytes()
def changed_once(content, old, new):
    assert content.count(old) == 1, f'expected exactly one match: {old[:64]!r}'
    return content.replace(old, new)

def build(parent, out):
    manifest_bytes = read(parent / 'manifest.json')
    assert sha(manifest_bytes) == PARENT_MANIFEST, 'unverified R234 manifest'
    original = json.loads(manifest_bytes)
    for name, digest in original['files'].items():
        assert sha(read(parent / name)) == digest, f'parent file modified: {name}'
    assert sha(read(parent / 'index.html')) == PARENT_INDEX, 'parent HTML fixture modified'
    assert not out.exists(), 'do not overwrite a prior build'
    shutil.copytree(parent, out)
    old_html = (out / 'templates/atlas-fragment.html').read_text()
    old_css = (out / 'assets/atlas-scoped.css').read_text()
    old_php = (out / 'fv-ex2-apollo-r224.php').read_text()
    old_index = (out / 'index.html').read_text()
    assert sha(old_html.encode()) == original['files']['templates/atlas-fragment.html']
    new_html = changed_once(old_html, OLD_HEADING, NEW_HEADING)
    new_css = changed_once(old_css, OLD_STYLE, NEW_STYLE)
    new_index = changed_once(old_index, OLD_HEADING, NEW_HEADING)
    fragment_digest = sha(new_html.encode())
    css_digest = sha(new_css.encode())
    assert old_php.count(original['files']['templates/atlas-fragment.html']) == 2
    assert old_php.count(original['files']['assets/atlas-scoped.css']) == 1
    new_php = old_php.replace(original['files']['templates/atlas-fragment.html'], fragment_digest)
    new_php = new_php.replace(original['files']['assets/atlas-scoped.css'], css_digest)
    # CSS cache version tracks changed stylesheet.
    old_cache = original['files']['assets/atlas-scoped.css'][:12]
    assert new_php.count("array(),'"+old_cache+"');") == 1, 'CSS cache token unexpected'
    new_php = new_php.replace("array(),'"+old_cache+"');", "array(),'"+css_digest[:12]+"');")
    for name, value in [('templates/atlas-fragment.html',new_html), ('assets/atlas-scoped.css',new_css),
                        ('index.html',new_index), ('fv-ex2-apollo-r224.php',new_php)]:
        (out / name).write_text(value)
    orig_links = [(a.get('href'),a.get_text(' ',strip=True),a.get('aria-describedby')) for a in BeautifulSoup(old_html,'html.parser').find_all('a')]
    new_links = [(a.get('href'),a.get_text(' ',strip=True),a.get('aria-describedby')) for a in BeautifulSoup(new_html,'html.parser').find_all('a')]
    assert orig_links == new_links, 'NASA sources/CTA changed'
    assert len(new_links) >= 75, 'incomplete source fixture'
    original['files']['templates/atlas-fragment.html'] = fragment_digest
    original['files']['assets/atlas-scoped.css'] = css_digest
    original['files']['fv-ex2-apollo-r224.php'] = sha(new_php.encode())
    original['r235_change'] = 'Promote source-trace section title from h3 to h2; preserve its CSS and asset pins'
    original['release'] = 'R235_STAGING_HOLD'
    original['status'] = 'STAGING_HOLD'
    (out / 'manifest.json').write_text(json.dumps(original,sort_keys=True,indent=2)+'\n')
    assert all(sha(read(out/name)) == digest for name,digest in original['files'].items())
    php = subprocess.run(['php','-l',str(out/'fv-ex2-apollo-r224.php')],text=True,capture_output=True)
    assert php.returncode == 0, php.stderr
    shim = out / 'wp-render-shim-r224.php'
    for mode, expected in [('normal',False),('printed',False),('late',True)]:
        p = subprocess.run(['php',str(shim),str(out/'fv-ex2-apollo-r224.php'),mode],capture_output=True,text=True)
        assert p.returncode == 0, p.stderr
        result=json.loads(p.stdout)
        assert result['fallback'] is expected, f'{mode}: {result}'
    return {'parent_manifest_sha256':PARENT_MANIFEST,'manifest_sha256':sha(read(out/'manifest.json')),
            'template_sha256':fragment_digest,'css_sha256':css_digest,'php_sha256':sha(new_php.encode()),
            'source_links_preserved':len(new_links),'php_modes':['normal','printed','late']}

def browser(out, qa):
    qa.mkdir(parents=True,exist_ok=False)
    html=(out/'templates/atlas-fragment.html').read_text()
    css=(out/'assets/atlas-scoped.css').read_text()
    root='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>'
    receipt={}; widths=[320,390,768,1440,1920]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in widths:
          for js in (False,True):
            context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                         reduced_motion='reduce',is_mobile=width<=390,has_touch=width<=390,
                         device_scale_factor=1)
            page=context.new_page()
            requests=[]
            page.on('request', lambda r: requests.append(r.url))
            page.set_content(root,wait_until='load')
            before=page.evaluate('''() => {
              const root=document.querySelector('.fv-apollo-atlas');
              const section=root.querySelector('section.fv-apollo-trace');
              const h=section.querySelector('#fv-apollo-trace-title');
              const title=section.getAttribute('aria-labelledby');
              const links=[...root.querySelectorAll('a[href^="#"]')];
              const ids=[...root.querySelectorAll('[id]')].map(x=>x.id);
              return {h2:h?.tagName==='H2',section_name:title===h?.id,heading_levels:[...root.querySelectorAll('h1,h2,h3')].map(x=>Number(x.tagName[1])),
                horiz:document.documentElement.scrollWidth<=innerWidth,ids_unique:new Set(ids).size===ids.length,
                anchors:links.length,broken:links.filter(x=>!document.getElementById(x.getAttribute('href').slice(1))).length,
                source_links:root.querySelectorAll('a[href*="nasa.gov/"]').length,
                cta:root.querySelectorAll('a.cta[href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"]').length,
                disclosures:root.querySelectorAll('details').length,
                geo:root.querySelectorAll('[data-lat],[data-lon],[data-lng],[data-coordinates]').length,
                js:root.querySelectorAll('script,iframe,canvas').length};}''')
            assert before['h2'] and before['section_name'] and before['horiz'] and before['ids_unique']
            assert before['anchors'] >= 25 and before['broken'] == 0
            assert before['source_links'] >= 25 and before['cta'] == 1
            assert before['disclosures'] >= 10 and before['geo'] == 0 and before['js'] == 0 and not requests
            # Real browser accessibility tree exposes the named heading as level 2.
            session=context.new_cdp_session(page)
            ax=session.send('Accessibility.getFullAXTree')['nodes']
            titles=[n for n in ax if n.get('role',{}).get('value')=='heading' and
                    n.get('name',{}).get('value')=='Trace each finding to what the source actually supports.']
            assert len(titles)==1 and any(prop.get('name')=='level' and prop.get('value',{}).get('value')==2
                      for prop in titles[0].get('properties',[])), 'Chrome AX heading level wrong'
            # Screenshot before focus/tap avoids nondeterministic mobile activation highlight.
            page.screenshot(path=str(qa/(f'{width}-'+('js' if js else 'nojs')+'.png')),full_page=True,animations='disabled')
            # Verify native keyboard and touch disclosures without injecting JS.
            details=page.locator('#fv-apollo-source-drawer')
            assert not details.evaluate('(x)=>x.open')
            if width<=390:
                page.locator('#fv-apollo-source-drawer summary').tap()
            else:
                page.locator('#fv-apollo-source-drawer summary').focus()
                page.keyboard.press('Enter')
            assert details.evaluate('(x)=>x.open')
            receipt[f'{width}-'+('js' if js else 'nojs')]={
                'width':width,'ax_heading_level':2,'anchors':before['anchors'], 'nasa_links':before['source_links'],
                'cta':before['cta'],'disclosures':before['disclosures'],'overflow':False,
                'screenshot_sha256':sha(read(qa/(f'{width}-'+('js' if js else 'nojs')+'.png')))}
            context.close()
        browser.close()
    (qa/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return sha(read(qa/'receipt.json'))

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--parent',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--qa',type=Path,required=True)
    a=parser.parse_args(); meta=build(a.parent,a.out);meta['qa_sha256']=browser(a.out,a.qa)
    print(json.dumps(meta,sort_keys=True,indent=2))
