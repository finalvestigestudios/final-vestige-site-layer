#!/usr/bin/env python3
"""R340: actual PHP-rendered no-network Chromium QA for isolated WP shortcode adapter.
Runs two independent no-JS experiences; no WordPress install, live HTTP, axe or production CWV.
"""
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parents[1]
PHP = HERE / 'apollo-accession-gallery.php'
CSS = HERE / 'assets/accession-gallery.css'
OLD_CSS = HERE.parent / 'apollo-r339/assets/chronology-rail.css'
OUT = Path(os.environ.get('FV_R340_OUT', '/tmp/fv-apollo-r340'))
OUT.mkdir(parents=True, exist_ok=True)
LINKS = (
    'https://www.nasa.gov/image-detail/amf-s67-15717/',
    'https://www.nasa.gov/image-detail/amf-s66-58038/',
    'https://www.nasa.gov/image-detail/amf-s67-21294/',
    'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/',
)
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'


def gitblob(path):
    data = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\x00' + data).hexdigest()


def php_run(code):
    p = subprocess.run(['php'], input=code, text=True, capture_output=True, check=True)
    assert not p.stderr, p.stderr
    return p.stdout


def php_fixture():
    stub = '''<?php
    define('ABSPATH', __DIR__);
    $styles=[];
    function add_shortcode($name,$callback){}
    function add_action($name,$callback,$priority=10){}
    function is_singular(){return true;}
    function get_post(){return (object)['post_content'=>'[fv_apollo_experience_r340]'];}
    function has_shortcode($content,$tag){return strpos($content,'['.$tag) !== false;}
    function plugins_url($relative,$file){return '/wp-content/plugins/apollo-r340/'.$relative;}
    function wp_enqueue_style($name,$url,$depends,$version){global $styles;$styles[]=['handle'=>$name,'url'=>$url];}
    require %s;
    fv_apollo_r340_enqueue();
    echo 'STYLES:'.json_encode($styles).'\n';
    echo fv_apollo_r340_experience_shortcode();
    echo fv_apollo_r340_experience_shortcode();
    ''' % json.dumps(str(PHP))
    rendered = php_run(stub)
    style_line, body = rendered.split('\n', 1)
    assert style_line.startswith('STYLES:')
    styles = json.loads(style_line[7:])
    assert len(styles) == 2 and {x['handle'] for x in styles} == {'fv-apollo-r339-chronology','fv-apollo-r340-gallery'}, styles
    assert styles[0]['url'].endswith('/apollo-r339/assets/chronology-rail.css')
    assert styles[1]['url'].endswith('apollo-r340/assets/accession-gallery.css')
    page = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>' + OLD_CSS.read_text() + '\n' + CSS.read_text() + '</style></head><body style="margin:0">' + body + '</body></html>'
    return body, page, styles


def contract(body):
    soup = BeautifulSoup(body, 'html.parser')
    issues=[]
    galleries=soup.select('section[data-fv-r340-gallery]')
    if len(galleries) != 2: issues.append('2 independently rendered galleries required')
    ids=[n['id'] for n in soup.select('[id]')]
    if len(ids)!=len(set(ids)): issues.append('duplicate IDs')
    for g in galleries:
        cards=g.select('li[data-fv-r340-role]')
        if len(cards)!=4: issues.append('catalogue must contain four reviewed accession records');continue
        if [a.get('href') for a in g.select('a[data-fv-r340-source]')] != list(LINKS): issues.append('NASA exact archive links drifted')
        if any(c.get('data-fv-r340-role')!='contextual-photo-only' or c.get('data-fv-r340-rights')!='review-required' for c in cards): issues.append('rights/proof boundary missing')
        if len(g.select('details > summary')) != 4: issues.append('missing native disclosure')
        if len(g.select('[data-fv-r339-cta],a[href*="payhip"],img,iframe,script')): issues.append('commercial CTA/media inserted in source gallery')
        if 'not a Review Board conclusion' not in g.get_text(' ',strip=True): issues.append('photo vs Board distinction missing')
    if len(soup.select('[data-fv-r339-cta="editorial"]')) != 2: issues.append('exactly one editorial CTA per composed experience')
    if any(a['href'] != FREE for a in soup.select('[data-fv-r339-cta="editorial"]')): issues.append('editorial destination drifted')
    if any(urlsplit(a.get('href','')).hostname not in ('www.nasa.gov','finalvestige.com') for a in soup.select('a[href^="http"]')): issues.append('unapproved outbound host')
    if re.search(r'data-geo-pin|data-map-edge|utm_campaign|data-affiliate|data-merchant',body,re.I):issues.append('invented geo/commerce/attribution')
    return issues


def main():
    assert subprocess.run(['php','-l',str(PHP)],capture_output=True).returncode==0
    body, full, wp_styles=php_fixture()
    assert not contract(body), contract(body)
    mutants=[
        body.replace(LINKS[0], 'https://payhip.com/b/unknown',1),
        body.replace('contextual-photo-only','ignition-proof',1),
        body.replace('review-required','commercial-cleared',1),
        body.replace('not a Review Board conclusion','is a Review Board conclusion',1),
        body.replace('data-fv-r339-cta="editorial"','data-fv-r339-cta="purchase"',1),
        body.replace('data-fv-r340-gallery','data-geo-pin="invented" data-fv-r340-gallery',1),
        body.replace('id="fv-apollo-r340-gallery-2"','id="fv-apollo-r340-gallery-1"',1),
    ]
    assert all(contract(mutant) for mutant in mutants), 'a dangerous mutation escaped the custody gate'
    cases=[]; screenshots=[]
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
        try:
            caseset=([(w,True,16,False,False) for w in (320,360,390,768,1024,1440,1920)] +
                [(w,False,16,False,False) for w in (320,390,1440)] +
                [(320,True,32,False,False),(320,True,64,False,True),
                 (390,True,16,True,True),(1440,True,16,True,True)])
            for width,js,px,contrast,motion in caseset:
                page=b.new_page(viewport={'width':width,'height':950},java_script_enabled=js,has_touch=(width<=390),
                    forced_colors='active' if contrast else 'none',reduced_motion='reduce' if motion else 'no-preference')
                try:
                    page.set_content(full,wait_until='load')
                    if px!=16:page.add_style_tag(content=f'html{{font-size:{px}px!important}}')
                    data=page.evaluate('''() => {
                        const galleries=[...document.querySelectorAll('[data-fv-r340-gallery]')], links=[...document.querySelectorAll('.fv-apollo-r340 a')], summaries=[...document.querySelectorAll('.fv-apollo-r340 summary')];
                        const boxes=links.concat(summaries).map(a=>{const r=a.getBoundingClientRect();return {w:r.width,h:r.height,left:r.left,right:r.right}});
                        return {galleryCount:galleries.length,cards:galleries.map(g=>g.querySelectorAll('li[data-fv-r340-role]').length),
                          links:links.length,summaries:summaries.length,idsUnique:document.querySelectorAll('[id]').length === new Set([...document.querySelectorAll('[id]')].map(n=>n.id)).size,
                          overflow:document.documentElement.scrollWidth-innerWidth,boxes};}''')
                    assert data['galleryCount']==2 and data['cards']==[4,4] and data['links']==8 and data['summaries']==8 and data['idsUnique'], data
                    assert data['overflow']<=1, (width,px,data['overflow'])
                    assert all(r['w']>5 and r['h']>=43.5 and r['left']>=-1 and r['right']<=width+1 for r in data['boxes']), (width,px,data['boxes'])
                    d=page.locator('[data-fv-r340-gallery]').first.locator('details').first
                    d.locator('summary').focus();page.keyboard.press('Enter')
                    assert d.evaluate('(x)=>x.open'), 'native keyboard gallery drawer failed'
                    assert page.locator('[data-fv-r340-gallery]').first.locator('a[data-fv-r340-source]').first.get_attribute('href')==LINKS[0]
                    assert page.locator('[data-fv-r339-cta="editorial"]').count()==2
                    if width in (320,390,1440) and px==16 and not contrast:
                        name=f'r340-{width}-'+('js' if js else 'nojs')+'.png';page.screenshot(path=str(OUT/name),full_page=True);screenshots.append(name)
                    cases.append({'width':width,'js':js,'fontPx':px,'forcedColors':contrast,'reducedMotion':motion,'overflowPx':data['overflow'],'result':'PASS'})
                finally:page.close()
        finally:b.close()
    receipt={'classification':'Actual local PHP+Chromium fixture; not WordPress install, axe, HTTP, Firefox/WebKit, or production CWV',
      'parentR339GitBlob':gitblob(HERE.parent/'apollo-r339/chronology-rail.php'),
      'gitBlobs':{'php':gitblob(PHP),'css':gitblob(CSS),'qa':gitblob(Path(__file__))},
      'enqueuedWordPressStylesInStub':wp_styles,'unsafeMutationsRejected':len(mutants),'cases':cases,'screenshots':screenshots,'release':'HARD HOLD'}
    (OUT/'r340-acceptance.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS',len(cases),'local real Chromium contexts,',len(mutants),'unsafe mutations rejected,',len(wp_styles),'WP-style enqueue handles')

if __name__ == '__main__': main()
