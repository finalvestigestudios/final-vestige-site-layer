#!/usr/bin/env python3
"""R17 actual Chromium proof of source-vs-photo separation and container reflow.

Uses original pinned Apollo 12 source files, generated protected PHP, in-memory
Chromium. Never claims installed WP, browser HTTP headers, hosted CWV or axe.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_exact import get_fixture

HERE=Path(__file__).resolve().parent
OUT=HERE/'r17-screenshots'
WIDTHS=(320,360,390,768,1024,1440,1920)


def run():
    html,plugin_sha=get_fixture()
    OUT.mkdir(exist_ok=True,parents=True)
    report={'source':'exact hash-checked PHP built from Apollo PR215',
            'php_sha256':plugin_sha,'browser':'Chromium 144 Playwright via page.set_content',
            'not_a_hosted_wordpress_or_axe_test':True,'measurements':[],'screenshots':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            ctx=browser.new_context(viewport={'width':width,'height':900},
                                    reduced_motion='reduce' if width==320 else 'no-preference')
            page=ctx.new_page(); page.set_content(html,wait_until='load')
            cards=page.locator('#source-concordance [data-concordance-record]')
            assert cards.count()==6
            assert page.locator('#source-concordance .fv-ex2-concordance__witness').count()==12
            assert page.locator('#source-concordance a[href^="#source-"]').count()==6
            assert page.locator('#source-concordance a[href^="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/"]').count()==6
            for card in cards.all():
                text=card.inner_text()
                assert 'INTERPRETATION / BOARD RECORD' in text
                assert 'WHAT THE NASA PHOTOGRAPH DEPICTS' in text
                assert 'What photograph ' in text
                assert 'Open original source drawer' in text
                assert card.locator('img,script,iframe').count()==0
                assert card.locator('a').count()==4
                assert card.locator('details > summary').count()==1
            columns=cards.first.locator('.fv-ex2-concordance__proof').evaluate('e=>getComputedStyle(e).gridTemplateColumns.split(" ").filter(Boolean).length')
            cardw=cards.first.evaluate('e=>Math.round(e.getBoundingClientRect().width)')
            assert (cardw<=520 and columns==1) or (cardw>520 and columns==2), (width,cardw,columns)
            docw=page.evaluate('document.documentElement.scrollWidth')
            assert docw<=width+1,(width,docw)
            for era,num in (('1966',1),('1967',3),('2017',2),('all',6)):
                page.locator(f'#fv-ex2-lens-{era}').check()
                assert page.locator('#source-concordance [data-concordance-record]:visible').count()==num,(width,era)
            first=cards.first
            first.locator('summary').click()
            assert first.locator('details').evaluate('e=>e.open')
            if width in (390,1440):
                shot=OUT/f'r17-dual-witness-{width}.png'
                page.locator('#source-concordance').screenshot(path=str(shot),animations='disabled')
                report['screenshots'].append({'name':shot.name,'sha256':sha256(shot.read_bytes()).hexdigest()})
            report['measurements'].append({'width':width,'first_card_width':cardw,
                'first_proof_columns':columns,'document_width':docw,
                'board_links':6,'photo_links':6,'source_drawer_links':6,
                'no_external_media_embedded':True})
            ctx.close()
        ctx=browser.new_context(viewport={'width':1920,'height':900},java_script_enabled=False)
        page=ctx.new_page();page.set_content(html,wait_until='load')
        page.locator('#source-concordance').evaluate('(n)=>{n.style.width="420px";n.style.maxWidth="420px"}')
        page.locator('#source-concordance .fv-ex2-concordance__inner').evaluate('(n)=>n.style.width="100%"')
        # An embed narrower than the browser viewport must not create two tiny proof columns.
        card=page.locator('#source-concordance [data-concordance-record]').first
        size=card.locator('.fv-ex2-concordance__proof').evaluate('e=>getComputedStyle(e).gridTemplateColumns.split(" ").filter(Boolean).length')
        assert size==1,('narrow CMS block must collapse the proof columns',size)
        page.locator('#fv-ex2-lens-1966').check()
        assert page.locator('#source-concordance [data-concordance-record]:visible').count()==1
        page.locator('#fv-ex2-lens-all').check()
        assert page.locator('#source-concordance [data-concordance-record]:visible').count()==6
        report['narrow_wordpress_block_no_js']={'viewport':1920,'parent_width':420,'proof_columns':size,'filters_work':True}
        ctx.close()
        browser.close()
    path=HERE/'R17_DUAL_WITNESS_BROWSER_RESULTS.json'
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('R17_DUAL_WITNESS_PASS',len(report['measurements']),'widths; no-JS narrow WP block; snapshots',len(report['screenshots']))
    return report

if __name__=='__main__':run()
