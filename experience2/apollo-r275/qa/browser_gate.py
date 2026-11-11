#!/usr/bin/env python3
"""R275 offline Chromium source-custody regression; not axe, WordPress or real HTTP."""
import argparse, hashlib, json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
arg=argparse.ArgumentParser();arg.add_argument('output'); opts=arg.parse_args()
out=Path(opts.output);out.mkdir(parents=True,exist_ok=True)
html=subprocess.check_output(['php',str(ROOT/'../../apollo-r274/qa/multi-render.php')]).decode('utf-8')
expected=['fv-r273-title','fv-r273-title-2','fv-r273-title-3']
results=[];screens={}; perf=[]; source_labels=['Read NASA primary source: Apollo 204 Review Board report','Read NASA primary source: Four recorded chronology markers']
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in [320,390,768,1440,1920]:
        for js in (True,False):
            context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,device_scale_factor=1,has_touch=width<=390,reduced_motion='reduce')
            page=context.new_page(); requests=[];page.on('request',lambda q:requests.append(q.url))
            page.set_content(html,wait_until='load')
            panels=page.locator('aside.fv-r273');assert panels.count()==3
            assert page.locator('.fv-r273__shared-source').count()==3
            assert all('not two independent source confirmations' in q for q in page.locator('.fv-r273__shared-source').all_text_contents())
            assert 'Unverified review metadata present' in panels.nth(2).inner_text()
            ids=page.locator('[id]').evaluate_all('(nodes)=>nodes.map(n=>n.id)')
            assert len(ids)==len(set(ids)),('duplicate identifiers',ids)
            for idx,title in enumerate(expected):
                panel=panels.nth(idx)
                assert panel.get_attribute('aria-labelledby')==title
                assert panel.locator('h2').get_attribute('id')==title
                assert panel.get_attribute('data-fv-review-ready')=='false'
                assert panel.locator('a[href^="https://www.nasa.gov/"]').count()==2
                assert panel.locator('a[href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"]').count()==1
                panel.locator('summary').click()  # native interaction works with JS off
                assert panel.locator('details[open]').count()==1
                for label in source_labels:assert panel.get_by_role('link',name=label,exact=False).count()==1
            assert panels.nth(0).locator('.fv-r273__status').all_text_contents()==['Editorial review pending']*2
            assert 'independent acceptance required' in panels.nth(2).inner_text()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),(width,js,'overflow')
            assert requests==[],requests
            if js:
                session=context.new_cdp_session(page);session.send('Accessibility.enable');tree=session.send('Accessibility.getFullAXTree')['nodes']; names=[n.get('name',{}).get('value','') for n in tree];session.detach()
                for label in source_labels:assert any(label in str(s) for s in names),('missing accessible link name',label)
            if width in (390,1440):
                page.locator('summary').evaluate_all('(nodes)=>nodes.forEach(n=>n.parentElement.open=false)')
                target=out/(f'{width}-'+('js' if js else 'nojs')+'.png')
                page.screenshot(path=str(target),full_page=True,animations='disabled')
                screens[target.name]=hashlib.sha256(target.read_bytes()).hexdigest()
            results.append({'viewport':width,'javascript':js,'status':'PASS'})
            context.close()
    for width in (320,390,768,1440,1920):
        context=browser.new_context(viewport={'width':width,'height':900},has_touch=True,reduced_motion='reduce',forced_colors='active')
        page=context.new_page();page.set_content(html)
        page.evaluate('document.documentElement.style.fontSize="64px"')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),(width,'400%-font-overflow')
        page.locator('aside.fv-r273').first.locator('summary').tap()
        assert page.locator('aside.fv-r273').first.locator('details[open]').count()==1
        page.locator('aside.fv-r273').first.locator('summary').focus()
        assert page.evaluate('document.activeElement.tagName')=='SUMMARY'
        perf.append({'viewport':width,'400pct_root_font':'PASS','touch':'PASS','forced_colors':'PASS','reduced_motion':'PASS'})
        context.close()
    browser.close()
receipt={'suite':'R275','chromium_version':'system Chromium','contexts':results,'stress':perf,'screenshots_sha256':screens,'genuine_axe':'UNAVAILABLE_NOT_EXECUTED','installed_wordpress':'NOT_TESTED','browser_ui_zoom':'NOT_TESTED','field_lcp_cls':'NOT_TESTED','public_release':'HARD_HOLD'}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(f'R275 {len(results)}/{len(results)} Chromium contexts; {len(perf)}/{len(perf)} touch/text stress PASS; receipt '+hashlib.sha256((out/'receipt.json').read_bytes()).hexdigest())
