#!/usr/bin/env python3
"""R464 local PHP→Chromium PDF source-custody smoke; NOT hosted WordPress/axe/CWV."""
import hashlib, json, os, re, subprocess
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA'/'r464-smoke';OUT.mkdir(parents=True,exist_ok=True)
PHP=ROOT/'apollo_rights_gallery.php'
def php(cmd):
    return subprocess.check_output(['php','-r',f'require {json.dumps(str(PHP))}; {cmd}'],text=True)
HTML=php('echo fv457_render();')
A=json.loads(php('echo json_encode(fv457_records());'))
C=json.loads(php('echo json_encode(fv457_chronology());'))
S={x['source_url'] for x in A}|{x['source'] for x in C}
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
assert len(A)==6 and len(C)==3 and len(S)==9
assert [c['machine_date'] for c in C]==['1967-01','1967-01-27','2017-01-27']
assert HTML.count('<time datetime=')==3 and HTML.count(FREE)==1
PASSED=[];SHOTS=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
    for width in (320,360,390,768,1024,1440,1920):
        for enabled in (True,False):
            ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled)
            pg=ctx.new_page();pg.set_content(HTML,wait_until='load')
            label=f'{width}-js{int(enabled)}'
            assert pg.locator('.fv457__moment:visible').count()==3
            assert pg.locator('.fv457__card:visible').count()==6
            assert pg.locator('.fv457__chronology-print:visible').count()==0
            assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            details=pg.locator('.fv457__moment details').nth(1)
            details.locator('summary').focus();pg.keyboard.press('Enter')
            assert details.evaluate('(e)=>e.open')
            pg.keyboard.press('Enter');assert not details.evaluate('(e)=>e.open')
            if enabled:
                pg.get_by_role('button',name='Confirmed homepage (1)').click()
                assert pg.locator('.fv457__card:visible').count()==1
            doc=fitz.open(stream=pg.pdf(format='A4',print_background=True,tagged=True),filetype='pdf')
            links={x['uri'] for page in doc for x in page.get_links() if x.get('uri')}
            txt=' '.join((' '.join(page.get_text() for page in doc)).split())
            assert links==S|{FREE},(label,links^(S|{FREE}))
            assert txt.count('Printable chronology source:')==3
            assert txt.count('Printable NASA source:')==6
            assert 'Source acceptance HOLD' in txt and 'not commercial media clearance' in txt
            doc.close()
            if enabled and width in (320,390,768,1440,1920):
                pg.emulate_media(media='print')
                assert pg.locator('.fv457__chronology-print:visible').count()==3
                assert pg.locator('.fv457__card:visible').count()==6
                name=f'{width}-print.png';pg.screenshot(path=str(OUT/name),full_page=True,animations='disabled')
                SHOTS.append(name)
                pg.emulate_media(media='screen')
                assert pg.locator('.fv457__card:visible').count()==1
            PASSED.append(label);ctx.close()
    browser.close()
report={'sprint':'R464','pass_count':len(PASSED),'failed':[],'cases':PASSED,
 'screenshots':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.png')},
 'unique_pdf_links':10,'nasa_links':9,'free_cta_links':1,
 'hosted_wordpress':'HOLD_NOT_RUN','axe_core':'HOLD_NOT_RUN',
 'navigated_lcp_cls':'HOLD_NOT_RUN - ERR_BLOCKED_BY_ADMINISTRATOR',
 'manual_screen_reader':'HOLD_NOT_RUN','release':'HARD_HOLD'}
(OUT/'REPORT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({'passed':len(PASSED),'screenshots':len(SHOTS),'unique_links':10}))
