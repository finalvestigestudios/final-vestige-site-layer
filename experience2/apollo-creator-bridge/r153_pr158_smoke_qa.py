#!/usr/bin/env python3
"""R153 PR158-markup-shape smoke test. Offline fixture, never live WordPress.
Run: python r153_pr158_smoke_qa.py [output_directory]
"""
import hashlib, json, os, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
JS=ROOT/'r153_source_ledger_compat.js'
PR158_TOOL='<div data-fvx-tools hidden><label for="ledger-search">SEARCH SOURCE RECORDS</label><input id="ledger-search" type="search" data-fvx-search aria-controls="ledger-grid"><span role="status" aria-live="polite" data-fvx-status></span></div>'
IDS=[f'fv-ex2-ledger-apollo1-record-{n:02}' for n in range(1,7)]

def html():
    cards=''.join(f'<article id="{id}" data-fvx-record data-fvx-search="NASA S67-{19000+n} evidence record"><h2>Evidence record {n}</h2><a href="https://www.nasa.gov/">NASA source</a></article>' for n,id in enumerate(IDS))
    nav=''.join(f'<a href="#{id}">Jump {n}</a>' for n,id in enumerate(IDS))
    return '<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font:16px system-ui;margin:0;padding:12px}*,*:before,*:after{box-sizing:border-box}article{padding:16px;border:1px solid #999;margin:8px} [hidden]{display:none!important}a:focus-visible,input:focus-visible,button:focus-visible{outline:3px solid} nav{display:flex;flex-wrap:wrap;gap:8px}</style><nav>'+nav+'</nav><section data-fvx-ledger>'+PR158_TOOL+'<div id="ledger-grid">'+cards+'</div><p data-fvx-empty hidden>No results</p></section></html>'

def run(output):
    output=Path(output)
    if output.exists():raise ValueError('Refusing to overwrite evidence')
    output.mkdir(parents=True)
    code=JS.read_text()
    data={'status':'STAGING_HOLD','fixture':'PR158_MARKUP_SHAPE_NOT_EXACT_TEMPLATE','source_sha256':hashlib.sha256(code.encode()).hexdigest(),'checks':[],'screenshots':[],'axe':'NOT_EXECUTED','real_wordpress_lcp_cls':'NOT_MEASURED','commercial_conversion':'NOT_VERIFIED'}
    def ck(w,label,good):data['checks'].append({'width':w,'check':label,'pass':bool(good)})
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path=os.getenv('FV_CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
        data['chromium_version']=b.version
        for w in [320,360,390,768,1440,1920]:
            c=b.new_context(viewport={'width':w,'height':800},reduced_motion='reduce',has_touch=w==390)
            c.route('**/*',lambda r:r.abort())
            page=c.new_page();page.set_content(html());page.add_style_tag(path=str(ROOT/'r153_source_ledger_compat.css'));page.add_script_tag(content=code)
            search=page.locator('input[data-fvx-search]');clear=page.locator('button[data-fvx-clear]')
            ck(w,'activates_without_clear_in_template',page.locator('[data-fvx-tools]').is_visible() and clear.count()==1)
            search.fill('S67-19001');ck(w,'filters_to_one',page.locator('[data-fvx-record]:visible').count()==1)
            page.evaluate(f'location.hash="#{IDS[4]}"');page.wait_for_function('(id)=>document.activeElement.id===id',arg=IDS[4])
            ck(w,'hash_restores_hidden',search.input_value()=='' and page.locator('[data-fvx-record]:visible').count()==6)
            ck(w,'no_horizontal_overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'))
            file=f'r153-smoke-{w}.png';page.screenshot(path=str(output/file),animations='disabled',full_page=True)
            data['screenshots'].append({'file':file,'sha256':hashlib.sha256((output/file).read_bytes()).hexdigest()});c.close()
            c=b.new_context(viewport={'width':w,'height':800},java_script_enabled=False);c.route('**/*',lambda r:r.abort())
            page=c.new_page();page.set_content(html());ck(w,'nojs_all_records_visible',page.locator('[data-fvx-record]:visible').count()==6 and page.locator('[data-fvx-tools]').is_hidden());c.close()
        b.close()
    data['passed']=sum(v['pass'] for v in data['checks']);data['failed']=len(data['checks'])-data['passed']
    (output/'receipt.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    return data
if __name__=='__main__':
    report=run(sys.argv[1] if len(sys.argv)>1 else 'r153-smoke-output')
    print(json.dumps({'passed':report['passed'],'failed':report['failed']}))
    sys.exit(1 if report['failed'] else 0)
