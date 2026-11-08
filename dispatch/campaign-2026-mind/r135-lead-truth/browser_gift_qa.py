"""Offline Chromium test of WP Focus inline v2 versus candidate v3.
No production requests, subscriber interaction, cookies or sending.
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
# Reproduces the inline logic observed in WP pages_get /focus/ page #1579.
ORIGINAL = r'''(function(){var g=document.getElementById('fvf-gift');if(!g){return;}
var bad=['invalid_email','error','blocked_email','opted_out','blocked'];
function show(){g.hidden=false;}
var q=null;try{q=new URLSearchParams(window.location.search).get('subscribe');}catch(e){}
if(q){if(bad.indexOf(q)<0){show();}}
var c=document.querySelector('.wp-block-jetpack-subscriptions__container');
function check(){if(c){if(/\bis-subscriber\b/.test(c.className)){show();}}}
check();if(c){if(window.MutationObserver){new MutationObserver(check).observe(c,{attributes:true,attributeFilter:['class']});}}})();'''
PROPOSED = (ROOT / 'focus-gift-v3-PROPOSAL.js').read_text()

def run():
    cases = ['', 'success','pending','false','unsubscribed','invalid_email','garbage']
    outcomes = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':390,'height':844})
        for version in ['old','new']:
            for state in cases + ['pending+native_UI_marker']:
                marker = state == 'pending+native_UI_marker'
                token = 'pending' if marker else state
                page.set_content('<!doctype html><html><body><div class="wp-block-jetpack-subscriptions__container'+(' is-subscriber' if marker else '')+'"></div><div id="fvf-gift" hidden>Your fieldbook is ready.</div></body></html>')
                url = 'https://example.invalid/focus/'+(('?subscribe='+token) if token else '')
                script = ORIGINAL if version == 'old' else PROPOSED
                # In-memory fake URL; real Chromium DOM executes the target JS.
                shown = page.evaluate("({source, url}) => { const u=new URL(url); const w={location:{search:u.search,href:u.href},MutationObserver:window.MutationObserver}; new Function('window',source)(w); return !document.getElementById('fvf-gift').hidden; }",{'source':script,'url':url})
                outcomes.append({'fixture':version,'subscribe_token':state or 'ABSENT','gift_visible':shown})
        browser.close()
    assert next(x for x in outcomes if x['fixture']=='old' and x['subscribe_token']=='pending')['gift_visible']
    assert not next(x for x in outcomes if x['fixture']=='new' and x['subscribe_token']=='pending')['gift_visible']
    assert next(x for x in outcomes if x['fixture']=='new' and x['subscribe_token']=='success')['gift_visible']
    output = {'mode':'LOCAL_SYNTHETIC_NOT_LIVE','cases':len(outcomes),'results':outcomes}
    (ROOT/'chromium-gift-evidence.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))

if __name__=='__main__': run()
