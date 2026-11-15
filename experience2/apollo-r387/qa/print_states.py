#!/usr/bin/env python3
"""R387 local Chromium proof: custody print is invariant to open disclosure state.
This is not hosted staging, a WordPress integration test or field Core Web Vitals.
"""
import json
from pathlib import Path
import subprocess
import fitz
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent
QA = ROOT / 'QA'
QA.mkdir(exist_ok=True)
subprocess.run(['php',str(BASE/'apollo-r386/qa/contract.php')],check=True,stdout=subprocess.PIPE)
html = (BASE/'apollo-r386/QA/local-php-fixture.html').read_text(encoding='utf-8')
records = json.loads((BASE/'apollo-r377/custody.json').read_text(encoding='utf-8'))['records']
assert len(records) == 6
states = [0,1,3,6]
report = {'result':'LOCAL_CHROMIUM_PASS_NOT_INSTALLED_STAGING', 'checks':0, 'print_states':[],
          'widths':[320,390,768,1440,1920], 'axe':'NOT RUN: package not installed',
          'hosted_cwv':'NOT MEASURED', 'wordpress':'NOT TESTED','http_csp':'NOT TESTED'}

def check(test,why):
    report['checks'] += 1
    if not test:
        raise AssertionError(why)

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for width in report['widths']:
        context = browser.new_context(viewport={'width':width,'height':850},
            is_mobile=width <= 390,has_touch=width <= 390)
        page = context.new_page()
        page.set_content(html,wait_until='load')
        check(page.locator('details').count() == 6,f'{width} native disclosure count')
        check(page.locator('[data-fv-free-cta]').count() == 1,f'{width} exactly one free CTA')
        check(page.locator('[data-fv-r384-nasa]').count() == 6,f'{width} six original citations')
        check(page.locator('.fv-r384__phase').count() == 3,f'{width} chronological sequence')
        check(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),f'{width} overflow')
        check(not page.locator('.fv-r384__print-custody').first.is_visible(),f'{width} print mirror hidden on screen')
        page.screenshot(path=str(QA/f'{width}-screen.png'),full_page=True,animations='disabled')
        if width == 1440:
            page.locator('summary').first.focus()
            page.keyboard.press('Enter')
            check(page.locator('details').first.evaluate('(e)=>e.open'),'keyboard enter opens')
            page.keyboard.press('Enter')
            check(not page.locator('details').first.evaluate('(e)=>e.open'),'keyboard enter closes')
        if width == 390:
            page.locator('summary').first.tap()
            check(page.locator('details').first.evaluate('(e)=>e.open'),'touch toggles')
        context.close()

    # Print the exact same evidence at zero, one, three, and six open drawers.
    # Browser default prints open <details> contents, so R386 duplicated custody.
    printed_texts = []
    for opened in states:
        context = browser.new_context(viewport={'width':1440,'height':900})
        page = context.new_page()
        page.set_content(html,wait_until='load')
        page.eval_on_selector_all('details','(all,n)=>all.forEach((e,i)=>e.open=i<n)',opened)
        check(page.locator('details[open]').count()==opened,f'{opened} open state actually set')
        check(page.locator('.fv-r384__drawer').first.is_visible(),f'{opened} native details screen visible')
        page.emulate_media(media='print')
        check(page.locator('.fv-r384__drawer:visible').count()==0,f'{opened} print native duplicates suppressed')
        check(page.locator('.fv-r384__print-custody:visible').count()==6,f'{opened} print mirror visible')
        page.screenshot(path=str(QA/f'print-{opened}-open.png'),full_page=True,animations='disabled')
        pdf_path = QA/f'Apollo_R387_{opened}_open_print.pdf'
        page.pdf(path=str(pdf_path),format='A4',print_background=True)
        doc = fitz.open(str(pdf_path))
        txt = '\n'.join(p.get_text() for p in doc)
        norm = ' '.join(txt.split())
        check(txt.count('Source role:')==6,f'{opened} source roles exactly once')
        check(txt.count('What a photograph cannot prove:')==6,f'{opened} photo limits exactly once')
        check(txt.count('https://www.nasa.gov/missions/apollo/apollo-1/')>=5,f'{opened} NASA board printable URLs')
        check('https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/' in txt.replace('\n',''),f'{opened} later tests printable URL')
        check('Read the complete free Apollo 1 investigation' in txt,f'{opened} one relevant action')
        for record in records:
            for fld in ('evidence_role','catalog_note'):
                check(' '.join(record[fld].split()) in norm,f'{opened} exact {record["id"]} {fld}')
        check(len(doc)>=1,f'{opened} print output generated')
        printed_texts.append((opened,len(doc),norm))
        report['print_states'].append({'drawers_open':opened,'pages':len(doc),'source_roles':6,
            'photo_limitations':6,'verdict':'PASS'})
        context.close()

    # 100% source custody even if JavaScript is disabled and every drawer was opened by touch.
    context=browser.new_context(viewport={'width':320,'height':780},java_script_enabled=False,
        has_touch=True,is_mobile=True)
    page=context.new_page()
    page.set_content(html)
    page.locator('summary').first.tap()
    check(page.locator('details').first.evaluate('(e)=>e.open'),'no-JS native disclosure functional')
    check(page.locator('[data-fv-free-cta]').count()==1,'no-JS single CTA')
    check(page.locator('[data-fv-r384-nasa]').count()==6,'no-JS original links')
    page.screenshot(path=str(QA/'320-nojs.png'),full_page=True,animations='disabled')
    context.close()
    browser.close()

check(len({pages for _,pages,_ in printed_texts})==1,'pagination invariant across disclosure states')
check(all(text==printed_texts[0][2] for _,_,text in printed_texts),'print wording invariant across disclosure states')
(QA/'print-state-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':report['result'],'checks':report['checks'],
                  'print_scenarios':len(report['print_states']),'invariant_pages':printed_texts[0][1]},indent=2))
