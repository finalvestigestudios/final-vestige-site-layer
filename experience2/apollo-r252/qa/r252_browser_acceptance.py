#!/usr/bin/env python3
"""R252: original NASA Atlas accessibility journey, archival print and custody acceptance.

Runs pinned R238 PHP-rendered content inside isolated Playwright Chromium; no
WordPress, external calls, merchant destinations or live release. Real axe-core
can be supplied as --axe-js; absence is reported, never silently treated as pass.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz

MANIFEST_SHA256 = 'f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
CTA = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
WIDTHS = (320, 390, 768, 1440, 1920)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def source(atlas):
    blob = (atlas/'manifest.json').read_bytes()
    assert digest(blob) == MANIFEST_SHA256, 'protected manifest changed'
    manifest = json.loads(blob)
    assert manifest['not_live'] is True and manifest['status'] == 'STAGING_HOLD'
    for name, expected in manifest['files'].items():
        assert digest((atlas/name).read_bytes()) == expected, 'asset drift: ' + name
    cmd = ['php', str(atlas/'wp-render-shim-r224.php'),
           str((atlas/'fv-ex2-apollo-r224.php').resolve()), 'normal']
    data = json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=25).stdout)
    html = data['html']
    assert html == (atlas/'templates/atlas-fragment.html').read_text(), 'PHP render drift'
    css = (atlas/'assets/atlas-scoped.css').read_text()
    return html, css

def assert_page(page, width):
    page.locator('.fv-apollo-atlas').wait_for(state='visible')
    assert page.get_by_role('heading', name='A fire. A record. Unanswered questions.').count() == 1
    assert page.locator('[data-fv-plate-source]').count() == 4
    assert page.locator('#fv-apollo-chronology ol time[datetime]').count() >= 5
    assert page.locator('.fv-apollo-print-custody a[href^="https://www.nasa.gov/"]').count() >= 8
    assert page.locator('a.cta').count() == 1
    assert page.locator('a.cta').get_attribute('href') == CTA
    assert page.locator('a[href^="https://payhip.com"], a[href*="awin1.com"]').count() == 0
    metrics = page.evaluate("""() => {
        const root=document.querySelector('.fv-apollo-atlas');
        const ids=Array.from(root.querySelectorAll('[id]')).map(n=>n.id);
        const anchors=Array.from(root.querySelectorAll('a[href]'));
        const bad=anchors.filter(a=>{const u=a.getAttribute('href');
            if(u.startsWith('#')) return !root.querySelector('[id="'+CSS.escape(u.slice(1))+'"]');
            try {const x=new URL(u);return x.protocol!=='https:' ||
               !['www.nasa.gov','finalvestige.com'].includes(x.hostname)} catch {return true}
        });
        const overflow=Math.max(document.documentElement.scrollWidth,document.body.scrollWidth)-innerWidth;
        const times=Array.from(document.querySelectorAll('#fv-apollo-chronology ol time[datetime]')).map(n=>n.dateTime);
        return {ids:ids.length,dupe_ids:ids.length-new Set(ids).size,links:anchors.length,
          bad_links:bad.length,overflow_px:overflow,chronology_sorted:JSON.stringify(times)===JSON.stringify([...times].sort()),
          document_lang:document.documentElement.lang,body_text:root.innerText.length}
    }""")
    assert metrics['dupe_ids'] == 0 and metrics['bad_links'] == 0, metrics
    assert metrics['overflow_px'] <= 1 and metrics['chronology_sorted'], metrics
    assert metrics['body_text'] > 4000 and metrics['document_lang'] == 'en', metrics
    skip=page.locator('a.skip')
    skip.focus()
    assert skip.evaluate('(n)=>document.activeElement===n')
    skip.press('Enter')
    assert page.evaluate('location.hash') == '#fv-apollo-main'
    cta=page.locator('a.cta')
    cta.focus()
    assert cta.evaluate('(n)=>document.activeElement===n')
    summary=page.locator('#fv-apollo-source-drawer summary')
    summary.focus()
    summary.press('Enter')
    assert page.locator('#fv-apollo-source-drawer').evaluate('(n)=>n.open')
    summary.press('Space')
    assert not page.locator('#fv-apollo-source-drawer').evaluate('(n)=>n.open')
    if width <= 390:
        summary.tap()
        assert page.locator('#fv-apollo-source-drawer').evaluate('(n)=>n.open')
    if not page.locator('#fv-apollo-source-drawer').evaluate('(n)=>n.open'):
        summary.press('Enter')
    # Real Chromium CDP accessibility tree, NOT an axe-core or human screen-reader test.
    ax=page.context.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
    names=[n.get('name',{}).get('value','') for n in ax]
    assert any('Verify at NASA' in n for n in names), 'NASA AX names missing'
    assert any('Read investigation' in n or 'Read the investigation' in n for n in names)
    return {**metrics, 'ax_nodes':len(ax),
            'nasa_ax_named':sum('Verify at NASA' in n for n in names)}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--atlas', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--axe-js', type=Path, help='Independent official axe-core bundle, not downloaded at runtime')
    args=parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    html,css=source(args.atlas)
    doc=('<!doctype html><html lang="en"><head><meta charset="UTF-8">'
         '<meta name="viewport" content="width=device-width, initial-scale=1">'
         '<title>Apollo 1 Evidence Atlas staging test</title><style>'
         +css+'</style></head><body>'+html+'</body></html>')
    entries=[];screens=[];print_receipts=[];axe=[];violations=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        for width in WIDTHS:
            for js in (True, False):
                context=browser.new_context(viewport={'width':width,'height':800},
                    device_scale_factor=1,java_script_enabled=js,
                    reduced_motion='reduce' if not js else 'no-preference',
                    is_mobile=width<=390,has_touch=width<=390)
                page=context.new_page()
                requests=[]
                page.on('request',lambda request:requests.append(request.url))
                page.set_content(doc,wait_until='load')
                row=assert_page(page,width)
                assert requests==[], 'unexpected network: '+repr(requests)
                row.update({'width':width,'js':js,'requests':0,
                    'navigation_mode':'set_content; HTTP navigation blocked by administrator'})
                if args.axe_js and js:
                    assert args.axe_js.exists(), 'axe-core bundle missing'
                    page.add_script_tag(path=str(args.axe_js))
                    result=page.evaluate("""async () => {
                      if (!window.axe || !window.axe.version) throw Error('axe-core unavailable');
                      const r=await axe.run(document.querySelector('.fv-apollo-atlas'),
                         {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
                      return {version:axe.version,violations:r.violations.map(x=>({
                        id:x.id,impact:x.impact,affected:x.nodes.length}))};
                    }""")
                    axe.append({'width':width,'js':js,**result})
                    violations.extend(result['violations'])
                if width in (390,1440):
                    shot=args.out/f'{width}-{"js" if js else "nojs"}.png'
                    page.screenshot(path=str(shot),full_page=True,animations='disabled')
                    screens.append({'file':shot.name,'sha256':digest(shot.read_bytes())})
                if (width,js) in ((390,True),(1440,False)):
                    page.emulate_media(media='print')
                    outfile=args.out/f'{width}-{"js" if js else "nojs"}-source-custody.pdf'
                    raw=page.pdf(print_background=True,prefer_css_page_size=True)
                    pdf=fitz.open(stream=raw,filetype='pdf')
                    metadata=pdf.metadata
                    metadata.update({'creationDate':"D:20000101000000+00'00'",
                                     'modDate':"D:20000101000000+00'00'"})
                    pdf.set_metadata(metadata)
                    pdf.save(outfile,garbage=4,deflate=True,no_new_id=1)
                    pdf.close()
                    printed=fitz.open(outfile)
                    words='\n'.join(pg.get_text() for pg in printed)
                    assert words.count('nasa.gov')>=8, 'print lost source URLs'
                    assert 'Archival source and rights index' in words, 'print lost rights index'
                    print_receipts.append({'file':outfile.name,'sha256':digest(outfile.read_bytes()),
                         'pages':len(printed),'visible_nasa_urls':words.count('nasa.gov')})
                    page.emulate_media(media='screen')
                entries.append(row)
                context.close()
        browser.close()
    assert not violations, 'genuine axe-core violations: '+repr(violations)
    receipt={'status':'PASS','scope':'EXACT_R238_PHP_RENDERED_ATLAS_OFFLINE',
      'manifest_sha256':MANIFEST_SHA256,'not_live':True,'contexts':len(entries),
      'widths':list(WIDTHS),'entries':entries,'screenshots':screens,'print_pdf':print_receipts,
      'axe':axe if args.axe_js else 'NOT_EXECUTED_MISSING_OFFICIAL_BUNDLE',
      'http_csp':'NOT_TESTED_ADMIN_POLICY','wordpress':'NOT_TESTED','field_cwv':'NOT_TESTED',
      'checkout_sales':'NOT_TESTED_NO_APPROVED_PAID_OFFER'}
    out=args.out/'receipt.json'
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'PASS','contexts':len(entries),'screenshots':len(screens),
      'print_pdf':len(print_receipts),'receipt_sha256':digest(out.read_bytes()),
      'axe':'EXECUTED' if args.axe_js else receipt['axe']},sort_keys=True))

if __name__=='__main__':
    main()
