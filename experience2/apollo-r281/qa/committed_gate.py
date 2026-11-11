#!/usr/bin/env python3
"""Reproducible R281 PHP/Chromium gate. Offline fixture, not installed WP/axe/field CWV."""
from pathlib import Path
import hashlib, json, subprocess, sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/fv-r281-committed')
OUT.mkdir(parents=True,exist_ok=True)
php='''define('ABSPATH','/offline-fixture/');
function add_action($a,$b,$c=10){} function add_shortcode($a,$b){}
function plugins_url($a,$b){return '/fake-local-style.css';}
function wp_style_is($a,$b){return true;}
require 'apollo-source-experience.php';
$events=fv_r281_events();
if(!fv_r281_valid_records($events))exit(11);
$bad=$events;$bad[0]['source_url']='https://attacker.invalid/';
if(fv_r281_valid_records($bad))exit(12);
$bad=$events;$bad[1]['date']='1967-01-27';
if(fv_r281_valid_records($bad))exit(13);
$bad=$events;unset($bad[2]['boundary']);
if(fv_r281_valid_records($bad))exit(14);
foreach(['statement','boundary','source_name','source_type','source_dependency'] as $field){
  $bad=$events; $bad[0][$field].=' UNREVIEWED'; if(fv_r281_valid_records($bad))exit(15);
}
$bad=$events; $bad[1]['source_id']='nasa_board'; if(fv_r281_valid_records($bad))exit(16);
echo fv_r281_render(['state'=>'approved','merchant'=>'https://attacker.invalid/']);
echo fv_r281_render(['review'=>'complete']);'''
r=subprocess.run(['php','-r',php],cwd=ROOT,capture_output=True,text=True,timeout=20)
assert r.returncode==0,(r.returncode,r.stderr)
markup=r.stdout
assert markup.count('data-fv-evidence-status="editorial-review-pending"')==2
assert markup.count('https://attacker.invalid')==0
assert markup.count('<details')==6 and markup.count('<time')==6
assert markup.count('fv-r281__source-list')==2
assert 'malicious.invalid' not in markup
NASA=['https://www.nasa.gov/mission/apollo-1/',
      'https://www.nasa.gov/history/Apollo204/proceed.html',
      'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/']
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
assert all(markup.count('href="'+url+'"')==(4 if url in NASA else 2) for url in NASA+[FREE])
css=(ROOT/'assets/apollo-source-experience.css').read_text()
html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0;background:#101418;color:white;font:16px system-ui}</style><style>'+css+'</style></head><body>'+markup+'</body></html>'
contexts=[];screens={}
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    # Negative control: native R282 hash anchors lost focus without a focusable target.
    negative=browser.new_page()
    negative.set_content(html.replace(' tabindex="-1"',''))
    negative.locator('.fv-r281__rail a').first.focus()
    negative.locator('.fv-r281__rail a').first.press('Enter')
    assert negative.evaluate('document.activeElement.id') != 'fv-r281-1-event-1'
    negative.close()
    for width in [320,390,768,1440,1920]:
        for js in [False,True]:
            ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                    reduced_motion='reduce',has_touch=width<=390,forced_colors='active' if width==320 else 'none')
            pg=ctx.new_page();requests=[];errors=[]
            pg.on('request',lambda request:requests.append(request.url))
            pg.on('pageerror',lambda error:errors.append(str(error)))
            pg.set_content(html)
            assert not requests and not errors,(width,js,requests,errors)
            assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,js,'overflow')
            assert pg.get_by_role('navigation',name='Apollo chronology').count()==2
            assert pg.get_by_role('list',name='Historical evidence plates').count()==2
            assert pg.get_by_role('complementary',name='Source gallery').count()==2
            assert pg.locator('.fv-r281__source-list').first.locator('li').count()==3
            assert all(pg.locator('.fv-r281__source-list').first.locator('a[href="'+url+'"]').count()==1 for url in NASA)
            ax=ctx.new_cdp_session(pg).send('Accessibility.getFullAXTree')['nodes']
            assert any('Inspect NASA Apollo 204 Review Board report' in n.get('name',{}).get('value','') for n in ax)
            ids=pg.locator('[id]').evaluate_all('nodes=>nodes.map(x=>x.id)')
            assert len(ids)==len(set(ids))==20
            assert pg.locator('.fv-r281__plate[tabindex="-1"]').count()==6
            assert pg.locator('.fv-r281__source-list>li[tabindex="-1"]').count()==6
            assert pg.locator('.fv-r281__source-jump a').count()==6
            assert pg.locator('.fv-r281__source-return a').count()==6
            for index in range(6):
                anchor=pg.locator('.fv-r281__rail a').nth(index)
                target=anchor.get_attribute('href')[1:]
                anchor.focus();anchor.press('Enter')
                assert pg.evaluate('document.activeElement.id')==target,(width,js,index,'native focus lost')
                assert pg.locator('#'+target).evaluate('el=>getComputedStyle(el).outlineStyle')!='none'
            # R284: claim → custodian catalogue → same claim, native hash/focus.
            for index in range(6):
                plate=pg.locator('.fv-r281__plate').nth(index)
                jump=plate.locator('.fv-r281__source-jump a')
                source_id=jump.get_attribute('href')[1:]
                jump.focus();jump.press('Enter')
                assert pg.evaluate('document.activeElement.id')==source_id,(width,js,index,'source target focus lost')
                record=pg.locator('#'+source_id)
                assert record.evaluate('e=>getComputedStyle(e).outlineStyle')!='none'
                assert record.locator('a[href^="https://"]').count()==1
                back=record.locator('.fv-r281__source-return a')
                assert back.get_attribute('href')=='#'+plate.get_attribute('id')
                back.focus();back.press('Enter')
                assert pg.evaluate('document.activeElement.id')==plate.get_attribute('id'),(width,js,index,'claim return focus lost')
            assert pg.locator('.fv-r281__plate[tabindex="0"]').count()==0
            for root_px in (32,64):
                pg.evaluate('px=>document.documentElement.style.fontSize=px+"px"',root_px)
                assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,js,root_px,'text overflow')
            pg.evaluate('document.documentElement.style.fontSize=""')
            assert pg.get_by_role('link',name='Read the free Apollo 1 investigation').count()==2
            assert all(pg.locator('a[href="'+url+'"]').count()==4 for url in NASA)
            d=pg.locator('details').first;d.locator('summary').focus();pg.keyboard.press('Enter')
            assert d.get_attribute('open') is not None
            pg.keyboard.press('Enter');assert d.get_attribute('open') is None
            pg.locator('.fv-r281__rail a').first.click()
            assert pg.evaluate('location.hash')=='#fv-r281-1-event-1'
            pg.emulate_media(media='print')
            a=pg.locator('.fv-r281__drawer-body a').first
            assert a.is_visible()
            assert NASA[0] in a.evaluate("e=>getComputedStyle(e,'::after').content")
            g=pg.locator('.fv-r281__source-list').first.locator('a').first
            assert NASA[0] in g.evaluate("e=>getComputedStyle(e,'::after').content")
            assert pg.locator('.fv-r281__source-jump').first.is_hidden()
            assert pg.locator('.fv-r281__source-return').first.is_hidden()
            free_link=pg.get_by_role('link',name='Read the free Apollo 1 investigation').first
            assert FREE in free_link.evaluate("e=>getComputedStyle(e,'::after').content")
            pg.emulate_media(media='screen')
            if width in (390,1440) and not js:
                path=OUT/f'r281-{width}-nojs.png';pg.screenshot(path=str(path),full_page=True,animations='disabled')
                screens[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
            contexts.append({'width':width,'js':js,'result':'PASS'})
            ctx.close()
    browser.close()
receipt={'suite':'R281 actual PHP plus Chromium offline accessibility/print source gate',
         'php_sha256':hashlib.sha256((ROOT/'apollo-source-experience.php').read_bytes()).hexdigest(),
         'css_sha256':hashlib.sha256(css.encode()).hexdigest(),
         'contexts':contexts,'native_fragment_focus_checks':60,'native_source_roundtrip_checks':60,'R282_negative_control':'rejected','root_text_stress_px':[32,64], 'screenshot_sha256':screens,'release':'HARD_HOLD',
         'unverified':['installed WordPress','genuine axe-core','screen reader','browser HTTP/CSP','field LCP/CLS','paid sales']}
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(f'PHP PASS | Chromium {len(contexts)}/{len(contexts)} PASS | Receipt SHA256 '+hashlib.sha256((OUT/'receipt.json').read_bytes()).hexdigest())
