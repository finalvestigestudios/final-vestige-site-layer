#!/usr/bin/env python3
"""R241: NASA source-role and commercial-rights custody for the staged Apollo Atlas.
Offline only: exact R238 manifest + actual PHP shim + Chromium. Not axe, WP, or legal clearance.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

MANIFEST = 'f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
NASA = 'https://www.nasa.gov/'
BOARD = NASA+'missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
RIGHTS = NASA+'nasa-brand-center/advertising-guidelines/'
ORIGINAL = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
RECORDS = {
    'Apollo 204 Review Board': {'url':BOARD, 'kind':'report'},
    'S66-58038': {'url':NASA+'image-detail/amf-s66-58038/', 'kind':'pre-fire'},
    'S67-15717': {'url':NASA+'image-detail/amf-s67-15717/', 'kind':'pre-fire'},
    'S67-21294': {'url':NASA+'image-detail/amf-s67-21294/', 'kind':'aftermath'},
}
WIDTHS = (320,390,768,1440,1920)


def sha(b): return hashlib.sha256(b).hexdigest()


def load(root):
    assert sha((root/'manifest.json').read_bytes()) == MANIFEST, 'manifest drift'
    manifest=json.loads((root/'manifest.json').read_text())
    assert manifest['status']=='STAGING_HOLD' and manifest['not_live'] is True
    for p,d in manifest['files'].items(): assert sha((root/p).read_bytes())==d, 'drift '+p
    p=subprocess.run(['php',str(root/'wp-render-shim-r224.php'),str((root/'fv-ex2-apollo-r224.php').resolve()),'normal'],capture_output=True,text=True,timeout=20,check=True)
    obj=json.loads(p.stdout)
    assert obj['css']=='enqueued' and not obj['fallback'] and not obj['js']
    assert obj['html']==(root/'templates/atlas-fragment.html').read_text(), 'not actual PHP rendered HTML'
    return obj['html'],(root/'assets/atlas-scoped.css').read_text()


def policy(fragment):
    s=BeautifulSoup(fragment,'html.parser'); text=s.get_text(' ',strip=True)
    hrefs=[a.get('href','') for a in s.select('a')]
    assert len(s.select('a.cta'))==1 and s.select_one('a.cta')['href']==ORIGINAL, 'CTA mismatch'
    assert sum(h==ORIGINAL for h in hrefs)==1, 'more than one investigation link'
    assert hrefs.count(BOARD)>=6 and hrefs.count(RIGHTS)>=1
    assert 'No single ignition source was conclusively identified' in text
    assert 'not' in text.lower() and 'commercial' in text.lower()
    assert len(s.select('[data-fv-plate-source]'))==4
    assert len(s.select('img,svg,video,iframe,script,canvas'))==0, 'uncleared media or scripts'
    assert not re.search(r'(?i)utm_|affiliate|payhip|awin1|example\.invalid|data-paid-order|\bcheckout\b|\bcommission\b',fragment), 'unauthorized sales/attribution copy'
    assert not re.search(r'(?i)data-(?:latitude|longitude)|\bgoogle\.maps\b',fragment), 'invented geo mapping'
    for name,rec in RECORDS.items():
        assert rec['url'] in hrefs, 'missing NASA record: '+name
        plates=[x for x in s.select('[data-fv-plate-source]') if name in x.get_text(' ',strip=True)]
        assert len(plates)==1, 'source EvidencePlate misassociation: '+name
        ptext=plates[0].get_text(' ',strip=True).lower()
        assert any(w in ptext for w in ('cannot','not a','does not','no single','uncertain')), 'no evidence limitation: '+name
        if rec['kind']=='pre-fire':
            assert 'before' in ptext or 'pre-accident' in ptext or 'pre-fire' in ptext
        if rec['kind']=='aftermath': assert 'aftermath' in ptext or 'damage' in ptext
    assert 'NASA' in text and not re.search(r'(?i)nasa (approved|endorsed|certified) (?:the )?(?:product|offer|dossier)',text)
    return {'record_count':len(RECORDS),'nasa_board_links':hrefs.count(BOARD),'rights_links':hrefs.count(RIGHTS),'source_action_count':len(s.select('[data-fv-plate-source]')),'single_free_cta':True}


def mutations(fragment):
    base=policy(fragment)
    tests={
        'tampered_report':fragment.replace(BOARD, 'https://example.invalid/report/',1),
        'tampered_photo':fragment.replace(RECORDS['S67-15717']['url'],'https://example.invalid/photo/',1),
        'invented_paid_order':fragment.replace('class="fv-apollo-atlas"','class="fv-apollo-atlas" data-paid-order="true"'),
        'invented_geo':fragment.replace('class="fv-apollo-atlas"','class="fv-apollo-atlas" data-latitude="28"'),
        'unauthorized_tracking':fragment.replace('</article>','<script src="https://tracker.invalid/a.js"></script></article>'),
        'extra_paid_cta':fragment.replace('</article>','<a class="cta" href="https://payhip.com/">Buy now</a></article>'),
        'false_ignition_certainty':fragment.replace('No single ignition source was conclusively identified.','The single ignition source was conclusively identified.'),
    }
    # One URL alteration might leave duplicate citations: require exact URL set and minimum counts.
    failed=[]
    for name,bad in tests.items():
        try: policy(bad)
        except AssertionError: failed.append(name)
    assert len(failed)==len(tests), 'mutation escaped: '+str(set(tests)-set(failed))
    return {'rejected':failed,'count':len(failed),'baseline':base}


def browse(fragment, css, out):
    doc='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body style="margin:0">'+fragment+'</body></html>'
    receipts=[]
    with sync_playwright() as pw:
        b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for w in WIDTHS:
            for js in (False,True):
                ctx=b.new_context(viewport={'width':w,'height':900},java_script_enabled=js,has_touch=w<=390,is_mobile=w<=390,reduced_motion='reduce')
                page=ctx.new_page();requests=[];page.on('request',lambda request:requests.append(request.url));page.set_content(doc)
                assert not requests, 'unexpected request'
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), 'overflow'
                assert page.locator('a.cta').count()==1 and page.locator('a.cta').is_visible()
                assert page.locator('[data-fv-plate-source]').count()==4
                assert page.locator('details.fv-apollo-source-drawer').count()==1
                d=page.locator('details.fv-apollo-source-drawer');d.locator('summary').click()
                assert d.evaluate('(e)=>e.open')
                names=page.context.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
                links=[x.get('name',{}).get('value','') for x in names if x.get('role',{}).get('value')=='link' and not x.get('ignored')]
                assert all(any(name in n for n in links) for name in RECORDS), 'unreadable NASA accessible link'
                assert not [n for n in links if not n.strip()]
                # Source and temporal order must be visible without scripts or extra navigation.
                assert page.locator('#fv-apollo-chronology time[datetime]').count()>=5
                shot=ctx.new_page();shot.set_content(doc);shot.mouse.move(0,0);shot.wait_for_timeout(80)
                f=f'{w}-{"js" if js else "nojs"}.png';shot.screenshot(path=str(out/f),full_page=True,animations='disabled')
                receipts.append({'width':w,'javascript':js,'screenshot_sha256':sha((out/f).read_bytes()),'accessible_links':len(links)})
                ctx.close()
        version=b.version;b.close()
    return version,receipts


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--atlas',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    assert not a.out.exists(),'no overwriting evidence'
    frag,css=load(a.atlas);change=mutations(frag);a.out.mkdir(parents=True)
    version,checks=browse(frag,css,a.out)
    receipt={'run':'Apollo R241 NASA source/rights custody','protected_manifest':MANIFEST,'browser':version,'cases':checks,
    'negative_tests':change,'source_truth':'NASA Review Board and Apollo 1 gallery reviewed 2026-11-09',
    'rights':'NASA public source access does NOT clear commercial reproduction, likenesses or endorsement',
    'code':'offline actual PHP adapter source; NOT WordPress installed',
    'axe':'NOT_EXECUTED','screen_reader':'NOT_TESTED','field_CWV':'NOT_MEASURED','qualified_sessions':'UNKNOWN',
    'orders':'UNKNOWN','revenue_per_1000_qualified_sessions':'NOT_COMPUTABLE','release':'STAGING_HOLD'}
    (a.out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'contexts':len(checks),'rejected':change['count'],'sha256_receipt':sha((a.out/'receipt.json').read_bytes()),'status':'STAGING_HOLD'}))
if __name__=='__main__':main()
