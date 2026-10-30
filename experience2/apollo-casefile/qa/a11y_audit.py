#!/usr/bin/env python3
"""Offline NON-axe audit of DOM semantics and target geometry in real Chromium.

Not a substitute for axe-core, WCAG conformance, human screen-reader testing,
or field browser metrics. Reproducible without network.
"""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'index.html').read_text(encoding='utf8')
RESULT={'renderer':'headless Chromium set_content (in-memory, no network)','engine':'Playwright','axe':'not present; real axe run is a separate gated test','widths':{},'semantics':{},'keyboard':{}}

def check(ok, message):
    if not ok: raise AssertionError(message)

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in [320,360,390,768,1024,1440,1920]:
        page=browser.new_page(viewport={'width':width,'height':900},device_scale_factor=1,has_touch=True)
        page.set_content(HTML,wait_until='load')
        got=page.evaluate('''() => {
          const all=[...document.querySelectorAll('a,button,input,select,summary')];
          const interactive=all.filter(x=>getComputedStyle(x).display!=='none'&&x.getClientRects().length);
          const small=interactive.map(x=>{const r=x.getBoundingClientRect();return {tag:x.tagName,text:(x.textContent||'').slice(0,50),width:r.width,height:r.height}}).filter(x=>x.width<24||x.height<24);
          const unlabeled=interactive.filter(x=>!((x.getAttribute('aria-label')||'').trim()||(x.textContent||'').trim()||(x.getAttribute('title')||'').trim()||(x.labels&&x.labels.length)||(x.getAttribute('type')==='search')));
          const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);
          const duplicateIds=[...new Set(ids.filter((id,i)=>ids.indexOf(id)!==i))];
          const missingLabelledby=[...document.querySelectorAll('[aria-labelledby]')].filter(x=>x.getAttribute('aria-labelledby').split(/\s+/).some(id=>!document.getElementById(id))).map(x=>x.outerHTML.slice(0,100));
          const unsafeSourceUrls=[...document.querySelectorAll('.ex2-source a,.ex2-gallery__links a')].filter(x=>{try{const u=new URL(x.href);return u.protocol!=='https:'&&u.protocol!=='about:'&&!x.getAttribute('href').startsWith('#')}catch(e){return true}}).map(x=>x.href);
          return {targetCount:interactive.length,small,unlabeled:unlabeled.map(x=>x.outerHTML.slice(0,120)),duplicateIds,missingLabelledby,unsafeSourceUrls,stageCount:document.querySelectorAll('[data-ex2-stage]').length,galleryCount:document.querySelectorAll('[data-ex2-gallery-item]').length,atlasCount:document.querySelectorAll('[data-ex2-atlas-item]').length}
        }''')
        check(not got['small'],f'WCAG target geometry <24px at {width}: {got["small"][:5]}')
        check(not got['unlabeled'],f'Unlabeled control at {width}: {got["unlabeled"][:5]}')
        check(not got['duplicateIds'],f'Duplicate ID at {width}: {got["duplicateIds"]}')
        check(not got['missingLabelledby'],f'Broken aria-labelledby at {width}')
        check(not got['unsafeSourceUrls'],f'Non-HTTPS external source URL at {width}')
        check(got['stageCount']==got['galleryCount']==got['atlasCount']==6,f'Lost records at {width}')
        RESULT['widths'][str(width)]={'visible_interactive_targets':got['targetCount'],'smaller_than_24px':len(got['small']),'unlabeled_controls':len(got['unlabeled']),'duplicate_ids':len(got['duplicateIds']),'broken_aria_labelledby':len(got['missingLabelledby']),'unsafe_source_urls':len(got['unsafeSourceUrls'])}
        page.close()
    page=browser.new_page(viewport={'width':390,'height':900})
    page.set_content(HTML,wait_until='load')
    page.keyboard.press('Tab')
    focus=page.evaluate('''() => ({tag:document.activeElement.tagName,href:document.activeElement.getAttribute('href'),top:Math.round(document.activeElement.getBoundingClientRect().top),outline:getComputedStyle(document.activeElement).outlineStyle})''')
    check(focus['href']=='#main' and focus['top']>=0 and focus['outline']!='none','Keyboard skip link not visibly focusable')
    RESULT['keyboard']['first_tab_skip_link']=focus
    page.locator('.ex2-gallery__item:first-child details summary').focus()
    page.keyboard.press('Enter')
    check(page.locator('.ex2-gallery__item:first-child details').evaluate('(x)=>x.open'),'Gallery details cannot be toggled by Enter')
    RESULT['keyboard']['gallery_native_details_enter']='pass'
    page.close();browser.close()
RESULT['semantics']={'six_stages':True,'six_gallery_items':True,'six_atlas_items':True,'source_links_https_or_anchors':True}
(ROOT/'qa'/'A11Y_LOCAL_AUDIT.json').write_text(json.dumps(RESULT,indent=2,sort_keys=True)+'\n',encoding='utf8')
print('LOCAL NON-AXE AUDIT PASS: ',json.dumps(RESULT['widths'],sort_keys=True))
