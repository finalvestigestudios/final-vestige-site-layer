#!/usr/bin/env python3
"""R392 real Chromium local fixture source-seal regression. Not installed staging."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from semantic_custody import verify_page,verified_records

ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA'; QA.mkdir(exist_ok=True)
# Regenerate first using the inherited R389 PHP contract in a full checkout.
# This committed test never fetches external URLs or changes WordPress.
fixture=QA/'local-php-fixture.html'
if not fixture.exists():
    raise SystemExit('HOLD: generate local-php-fixture.html with inherited R389 qa/contract.php')
source=fixture.read_text(encoding='utf-8')
report={'kind':'LOCAL_CHROMIUM_FIXTURE_NOT_INSTALLED_STAGING','assertions':0,
        'contexts':[],'adversarial':[],'axe_core':'NOT RUN; genuine pinned axe-core required separately',
        'production_changes':False,'release_allowed':False}
def check(value,label):
    report['assertions']+=1
    if not value: raise AssertionError(label)

modes=[('320-mobile',320,780,True,False,'no-preference','none',False),
       ('390-mobile',390,850,True,False,'no-preference','none',False),
       ('768-tablet',768,900,False,False,'no-preference','none',False),
       ('1440-desktop',1440,900,False,False,'no-preference','none',False),
       ('1920-wide',1920,1080,False,False,'no-preference','none',False),
       ('320-nojs',320,800,True,True,'no-preference','none',False),
       ('390-touch',390,850,True,False,'no-preference','none',True),
       ('390-reduced',390,850,True,False,'reduce','none',False),
       ('320-forced',320,850,True,False,'no-preference','active',False),
       ('320-root4x',320,900,True,False,'no-preference','none',False)]
mutations=[
 ('false_ignition_certainty',"""document.querySelector('[data-fv-r384-source-id="05-ignition"] .fv-r384__limit').textContent='Does not establish: The exact ignition wire was found.'""",'record_5_boundary'),
 ('wrong_nasa_pub',"""document.querySelector('[data-fv-r384-publication="B"]').setAttribute('href','https://www.nasa.gov/')""",'publisher_destinations_or_order'),
 ('paid_cta',"""document.querySelector('[data-fv-free-cta]').setAttribute('href','https://checkout.invalid/buy')""",'free_cta_destination'),
 ('falsified_testing_chronology',"""document.querySelectorAll('.fv-r384__phase h3')[2].textContent='January 27 1967 · 102 ignitions'""",'chronology_phase_headings'),
 ('source_role_omitted',"""document.querySelector('[data-fv-r384-record] .fv-r384__drawer p').remove()""",'record_1_source_role'),
 ('invented_archival_image',"""document.querySelector('[data-fv-r384-gallery]').insertAdjacentHTML('beforeend','<img src="data:," alt="unreviewed photo">')""",'unexpected_media'),
 ('dead_index_link',"""document.querySelector('.fv-r384__source-index a[href^="#"]').setAttribute('href','#missing')""",'source_index_targets'),
 ('duplicate_source_id',"""document.querySelectorAll('[data-fv-r384-record]')[1].id=document.querySelector('[data-fv-r384-record]').id""",'duplicate_element_ids'),
 ('tampered_photo_limit',"""document.querySelector('[data-fv-r384-record] .fv-r384__drawer p:nth-of-type(2)').textContent='Photo proves arc location.'""",'record_1_photo_limit'),
 ('source_reordered',"""document.querySelector('.fv-r384__grid').prepend(document.querySelectorAll('[data-fv-r384-record]')[1])""",'record_1_id')]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    try:
        for name,w,h,mobile,nojs,reduced,forced,touch in modes:
            ctx=browser.new_context(viewport={'width':w,'height':h},is_mobile=mobile,
                                    has_touch=mobile or touch,java_script_enabled=not nojs,
                                    reduced_motion=reduced,forced_colors=forced)
            page=ctx.new_page();page.set_content(source)
            if name=='320-root4x':page.add_style_tag(content='html{font-size:400%!important}')
            valid,errors=verify_page(page)
            check(valid,name+': '+str(errors))
            check(page.locator('[data-fv-r384-record]').count()==6,name+' six records')
            check(page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1'),name+' no overflow')
            if name=='390-touch':
                page.locator('summary').first.tap()
                check(page.locator('details').first.evaluate('(n)=>n.open'),name+' touch disclosure')
            if name=='1440-desktop':
                page.locator('summary').first.focus();page.keyboard.press('Enter')
                check(page.locator('details').first.evaluate('(n)=>n.open'),name+' keyboard disclosure')
                page.keyboard.press('Enter')
                check(not page.locator('details').first.evaluate('(n)=>n.open'),name+' keyboard closes')
                ax=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
                check(any(n.get('role',{}).get('value')=='link' and not n.get('ignored') for n in ax),name+' AX links')
            if name=='320-nojs':
                page.locator('summary').first.tap()
                check(page.locator('details').first.evaluate('(n)=>n.open'),name+' no-JS native disclosure')
            if name in ('320-mobile','1440-desktop','320-nojs'):
                page.screenshot(path=str(QA/(name+'.png')),full_page=True,animations='disabled')
            report['contexts'].append({'name':name,'width':w,'result':'PASS'})
            ctx.close()
        ctx=browser.new_context();page=ctx.new_page()
        for name,js,expected in mutations:
            page.set_content(source)
            page.evaluate('() => {'+js+'}')
            valid,errors=verify_page(page)
            check(not valid and expected in errors,name+' MUST fail closed '+str(errors))
            report['adversarial'].append({'name':name,'blocked':True,'code':expected})
        ctx.close()
    finally:browser.close()
check(len(verified_records())==6,'reviewed R377 source corpus remains sealed')
(QA/'semantic-results.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({'contexts':len(modes),'adversarial':len(mutations),
                  'assertions':report['assertions'],'status':report['kind']},indent=2))
