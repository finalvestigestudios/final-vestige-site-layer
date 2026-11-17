"""Real Chromium on offline PHP-rendered markup; this is NOT an HTTP/staging LCP or axe run."""
from pathlib import Path
import json
import os
import subprocess
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT/'QA'
SHOTS=QA/'screenshots'

def html(mode='staging'):
    return subprocess.run(['php',str(ROOT/'qa/render_fixture.php')],capture_output=True,text=True,
        check=True,env=dict(os.environ,FV_TEST_MODE=mode)).stdout

def metrics(page):
    return page.evaluate('''() => ({
        scroll:document.documentElement.scrollWidth,
        client:document.documentElement.clientWidth,
        stages:document.querySelectorAll('.fv-r418__stage').length,
        sources:document.querySelectorAll('.fv-r418__stage a[href^="https://www.nasa.gov/"]').length,
        details:document.querySelectorAll('.fv-r418__stage details').length,
        ctas:document.querySelectorAll('a[href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"]').length
    })''')

def run():
    SHOTS.mkdir(parents=True, exist_ok=True)
    observations=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.getenv('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        for width in [320,360,390,768,1024,1440,1920]:
            page=browser.new_page(viewport={'width':width,'height':900},device_scale_factor=1)
            page.set_content(html())
            record=metrics(page)
            assert record['stages']==3 and record['sources']==3 and record['details']==3 and record['ctas']==1,record
            assert record['scroll'] <= record['client'],(width,record)
            page.screenshot(path=str(SHOTS/f'{width}.png'),full_page=True,animations='disabled')
            observations.append({'scenario':f'responsive-{width}', 'status':'PASS', 'geometry':record})
            page.close()
        page=browser.new_page(viewport={'width':390,'height':844},java_script_enabled=False)
        page.set_content(html());page.locator('summary').first.click()
        assert page.locator('details').first.get_attribute('open') is not None
        assert page.locator('a[href^="https://www.nasa.gov/"]').count()==4
        page.screenshot(path=str(SHOTS/'390-nojs.png'),full_page=True)
        observations.append({'scenario':'native no-JS disclosure','status':'PASS'})
        page.close()
        page=browser.new_page(viewport={'width':390,'height':844})
        page.set_content(html());page.locator('summary').first.focus();page.keyboard.press('Enter')
        assert page.locator('details').first.get_attribute('open') is not None
        page.screenshot(path=str(SHOTS/'390-keyboard.png'),full_page=True)
        observations.append({'scenario':'keyboard disclosure','status':'PASS'})
        page.close()
        page=browser.new_page(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
        page.set_content(html());page.locator('summary').nth(1).tap()
        assert page.locator('details').nth(1).get_attribute('open') is not None
        page.screenshot(path=str(SHOTS/'390-touch.png'),full_page=True)
        observations.append({'scenario':'touch disclosure','status':'PASS'})
        page.close()
        page=browser.new_page(viewport={'width':320,'height':880},forced_colors='active',reduced_motion='reduce')
        page.set_content(html());page.evaluate('document.documentElement.style.fontSize="64px"')
        record=metrics(page)
        assert record['scroll'] <= record['client'],record
        page.screenshot(path=str(SHOTS/'320-400pct-forced-colors.png'),full_page=True)
        observations.append({'scenario':'400% enlarged text, forced-colors, reduced motion','status':'PASS','geometry':record})
        page.close()
        page=browser.new_page(viewport={'width':390,'height':844})
        page.set_content(html('double'))
        ids=page.locator('[id]').evaluate_all('(nodes)=>nodes.map(n=>n.id)')
        assert len(ids)==len(set(ids))
        assert page.locator('[data-fv-r418-chronology]').count()==2
        observations.append({'scenario':'two instances IDs unique','status':'PASS'})
        page.close()
        page=browser.new_page(viewport={'width':390,'height':844})
        page.set_content(html('production'))
        assert page.locator('[data-fv-r418-chronology]').count()==0
        assert page.locator('a[href^="https://finalvestige.com/"]').count()==1
        observations.append({'scenario':'production context fail-open free article','status':'PASS'})
        page.close()
        page=browser.new_page(viewport={'width':390,'height':844})
        page.set_content(html())
        ax=page.context.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
        disclosure=[n for n in ax if (n.get('role') or {}).get('value') == 'DisclosureTriangle']
        assert len(disclosure)==3,(len(disclosure),[(n.get('name') or {}).get('value') for n in disclosure])
        observations.append({'scenario':'Chromium CDP accessibility tree','status':'PASS','disclosures':len(disclosure),'not_axe_core':True})
        page.close()
        page=browser.new_page(viewport={'width':1440,'height':880})
        page.set_content(html());page.emulate_media(media='print')
        page.screenshot(path=str(SHOTS/'1440-print.png'),full_page=True)
        observations.append({'scenario':'print media legible','status':'PASS'})
        page.close()
        # This runtime's Chromium navigation is blocked by administrator. Don't fake real CWV.
        observations.append({'scenario':'installed WordPress + navigated LCP/CLS + genuine axe-core','status':'NOT_TESTED','reason':'No installed staging, administrator blocks page.goto; no local axe-core bundle'})
        browser.close()
    (QA/'browser_results.json').write_text(json.dumps(observations,sort_keys=True,indent=2)+'\n')
    print('R418 offline Chromium:',sum(x['status']=='PASS' for x in observations),'PASS;',sum(x['status']=='NOT_TESTED' for x in observations),'NOT_TESTED')

if __name__=='__main__':run()
