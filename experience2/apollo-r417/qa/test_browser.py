"""R417 offline Chromium acceptance on PHP-rendered source; navigation + axe + LCP/CLS are NOT claimed."""
from pathlib import Path
import json, os, subprocess
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA'
SHOTS=OUT/'screenshots'

def markup(mode='staging'):
    return subprocess.run(['php',str(ROOT/'qa/render_fixture.php')],
        env=dict(os.environ,FV_TEST_MODE=mode),capture_output=True,text=True,check=True).stdout

def geometry(page):
    return page.evaluate('''() => ({
      width:document.documentElement.scrollWidth, viewport:innerWidth,
      cards:document.querySelectorAll('.fv-r417__item').length,
      disclosures:document.querySelectorAll('details').length,
      cta:document.querySelectorAll('a[href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"]').length
    })''')

def main():
    SHOTS.mkdir(parents=True,exist_ok=True)
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.getenv('CHROMIUM_PATH','/usr/bin/chromium'),
            headless=True,args=['--no-sandbox'])
        for width in (320,360,390,768,1024,1440,1920):
            page=browser.new_page(viewport={'width':width,'height':880})
            page.set_content(markup())
            stats=geometry(page)
            assert stats['cards']==6 and stats['disclosures']==6 and stats['cta']==1
            assert stats['width']<=stats['viewport'],str(stats)
            page.screenshot(path=str(SHOTS/f'{width}.png'),full_page=True,animations='disabled')
            results.append({'scenario':f'{width}px','pass':True,'geometry':stats})
            page.close()
        page=browser.new_page(viewport={'width':390,'height':880},java_script_enabled=False)
        page.set_content(markup());page.locator('summary').first.click()
        assert page.locator('details').first.get_attribute('open') is not None
        page.screenshot(path=str(SHOTS/'390-nojs-open.png'),full_page=True)
        results.append({'scenario':'no JavaScript native disclosure','pass':True});page.close()
        page=browser.new_page(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
        page.set_content(markup());page.locator('summary').nth(3).tap()
        assert page.locator('details').nth(3).get_attribute('open') is not None
        page.screenshot(path=str(SHOTS/'390-touch.png'),full_page=True)
        results.append({'scenario':'mobile touch disclosure','pass':True});page.close()
        page=browser.new_page(viewport={'width':320,'height':850},reduced_motion='reduce',forced_colors='active')
        page.set_content(markup());page.evaluate('document.documentElement.style.fontSize="64px"')
        stats=geometry(page);assert stats['width']<=stats['viewport']
        page.screenshot(path=str(SHOTS/'320-400pct-forced-colors.png'),full_page=True)
        results.append({'scenario':'400pct text forced-colors reduced-motion','pass':True,'geometry':stats});page.close()
        page=browser.new_page(viewport={'width':390,'height':844})
        page.set_content(markup());page.locator('summary').first.focus();page.keyboard.press('Enter')
        assert page.locator('details').first.get_attribute('open') is not None
        page.screenshot(path=str(SHOTS/'390-keyboard.png'),full_page=True)
        results.append({'scenario':'keyboard native disclosure','pass':True});page.close()
        page=browser.new_page(viewport={'width':390,'height':844});page.set_content(markup('double'))
        ids=page.locator('[id]').evaluate_all('(ns)=>ns.map(n=>n.id)')
        assert len(ids)==len(set(ids))
        results.append({'scenario':'multi instance unique ids','pass':True});page.close()
        page=browser.new_page(viewport={'width':390,'height':844});page.set_content(markup('production'))
        assert page.locator('[data-fv-r417-provenance]').count()==0 and page.locator('a').count()==1
        results.append({'scenario':'production fallback','pass':True});page.close()
        page=browser.new_page(viewport={'width':1440,'height':880});page.set_content(markup());page.emulate_media(media='print')
        assert page.evaluate("getComputedStyle(document.querySelector('.fv-r417 details')).display")=='none'
        page.screenshot(path=str(SHOTS/'1440-print.png'),full_page=True)
        results.append({'scenario':'print layout','pass':True});page.close()
        page=browser.new_page(viewport={'width':390,'height':844});page.set_content(markup())
        ax=page.context.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
        names=[(n.get('name') or {}).get('value','') for n in ax if (n.get('role') or {}).get('value')=='DisclosureTriangle']
        assert names.count('Photo date and limits')==6
        results.append({'scenario':'Chrome accessibility tree six disclosures','pass':True});page.close()
        page=browser.new_page(viewport={'width':1440,'height':880})
        try:
            page.goto((ROOT/'qa/render_fixture.php').as_uri(),timeout=5000)
            nav='unexpected navigation success; run server-based performance acceptance'
        except Exception as e:
            nav=str(e).split('\n')[0]
        results.append({'scenario':'real browser navigation','status':'BLOCKED','reason':nav})
        page.close();browser.close()
    assert len(results)==16
    (OUT/'browser_results.json').write_text(json.dumps(results,indent=2)+'\n')
    print('15 offline Chromium scenarios PASS; navigation status:',results[-1])

if __name__=='__main__':main()
