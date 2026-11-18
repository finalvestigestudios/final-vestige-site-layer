#!/usr/bin/env python3
"""Offline Chromium structural QA. Not axe-core and NOT navigated WordPress staging."""
import json,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
Q=ROOT/'QA'; IMG=Q/'screenshots';IMG.mkdir(parents=True,exist_ok=True)
fixture=subprocess.run(['php',str(ROOT/'qa/fixture.php')],capture_output=True,text=True,check=True).stdout
rows=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for js in (True,False):
        for w in (320,360,390,768,1024,1440,1920):
            ctx=browser.new_context(viewport={'width':w,'height':820},java_script_enabled=js,has_touch=True,is_mobile=(w<=390),reduced_motion='reduce')
            page=ctx.new_page()
            page.set_content(fixture,wait_until='load')
            page.locator('[data-r444-root]').wait_for()
            records=page.locator('[data-r444-record]').count()
            links=page.locator('.fv-r444__next a').count()
            url=page.locator('.fv-r444__next a').get_attribute('href')
            nasa=page.locator('a[href^="https://www.nasa.gov/"]').count()
            valid=records==5 and links==1 and nasa==5 and 'utm_' not in url
            # Native details must work without JavaScript; JS filter is supplemental.
            summary=page.locator('[data-r444-record] details summary').first
            if w<=390:
                summary.tap()
                interaction='touch'
            else:
                summary.focus()
                page.keyboard.press('Enter')
                interaction='keyboard'
            details_open=page.locator('[data-r444-record] details').first.get_attribute('open') is not None
            valid=valid and details_open
            if js:
                c=page.locator('[data-r444-controls]')
                valid=valid and c.count()==1 and not c.is_hidden()
                target=page.get_by_role('button',name='Later account')
                if w<=390: target.tap()
                else:
                    target.focus()
                    page.keyboard.press('Enter')
                visible=sum(page.locator('[data-r444-record]').nth(i).is_visible() for i in range(5))
                valid=valid and visible==1
                target=page.get_by_role('button',name='All five')
                if w<=390: target.tap()
                else:
                    target.focus()
                    page.keyboard.press('Enter')
            else:
                valid=valid and all(page.locator('[data-r444-record]').nth(i).is_visible() for i in range(5))
            overflow=page.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth + 1')
            valid=valid and not overflow
            # Return to fully expanded initial gallery for a visually comparable screenshot.
            if w<=390: summary.tap()
            else:
                summary.focus()
                page.keyboard.press('Enter')
            path=IMG/f'{w}-{("js" if js else "nojs")}.png'
            page.screenshot(path=str(path),full_page=True,animations='disabled')
            row={'width':w,'javascript':js,'records':records,'nasa_links':nasa,'cta_count':links,'cta_untagged':'utm_' not in url,'details_opens':details_open,'interaction':interaction,'overflow':overflow,'pass':valid,'screenshot':path.name}
            rows.append(row)
            ctx.close()
    # Extra local interaction evidence, not standalone accessibility certification.
    ctx=browser.new_context(viewport={'width':390,'height':844},forced_colors='active',reduced_motion='reduce')
    page=ctx.new_page(); page.set_content(fixture);page.screenshot(path=str(IMG/'390-forced-colors.png'),full_page=True)
    ctx.close()
    ctx=browser.new_context(viewport={'width':900,'height':760})
    page=ctx.new_page();page.set_content(fixture);page.emulate_media(media='print');page.screenshot(path=str(IMG/'900-print.png'),full_page=True)
    ctx.close()
    browser.close()
Q.mkdir(exist_ok=True)
(Q/'browser_results.json').write_text(json.dumps({'mode':'actual PHP-rendered HTML using Playwright set_content; NOT navigated staging','axe_core':'NOT RUN','LCP_CLS':'NOT RUN: page navigation blocked','cases':rows},indent=2)+'\n')
print(f'{sum(r["pass"] for r in rows)}/{len(rows)} chromium checks PASS; captures={len(list(IMG.glob("*.png")))}')
if not all(r['pass'] for r in rows):print([r for r in rows if not r['pass']]);raise SystemExit(2)