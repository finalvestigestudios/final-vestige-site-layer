#!/usr/bin/env python3
"""Independent, real-Chromium accessibility-tree QA for the R16 Apollo staging review.

NOT axe-core, not WCAG certification and not an actual WordPress/HTTP run.
Uses Chromium CDP Accessibility.getFullAXTree against exact, digest-checked
PHP-generated HTML, with interactive controls exercised before reinspection.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_exact import get_fixture

HERE = Path(__file__).resolve().parent
OUT = HERE / 'r16-screenshots'
RESULT = HERE / 'R16_ACCESSIBILITY_TREE_RESULTS.json'
WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
INTERACTIVE = {'button', 'link', 'radio', 'searchbox', 'combobox', 'DisclosureTriangle'}


def audit_ax(cdp):
    nodes=cdp.send('Accessibility.getFullAXTree')['nodes']
    inspect=[]
    for n in nodes:
        if n.get('ignored'):
            continue
        role=n.get('role',{}).get('value','')
        if role in INTERACTIVE:
            label=n.get('name',{}).get('value','').strip()
            inspect.append({'role':role, 'named':bool(label),
                            'dom_node':n.get('backendDOMNodeId')})
    unnamed=[x for x in inspect if not x['named']]
    if unnamed:
        raise AssertionError('Unnamed actionable elements in Chromium accessibility tree: '+repr(unnamed[:20]))
    return {'actionables':len(inspect),'roles':dict(Counter(x['role'] for x in inspect)),
            'unnamed':len(unnamed)}


def run():
    html,plugin_sha=get_fixture()
    OUT.mkdir(exist_ok=True,parents=True)
    report={'status':'PASS', 'mode':'in-memory exact PHP-rendered Chromium CDP Accessibility.getFullAXTree',
            'sha256_php_plugin':plugin_sha,'axe_status':'NOT_RUN_NO_VERIFIED_BUNDLE',
            'wcag_certified':False,'wordpress_integrated':False,
            'source_commit':'74375657f2cdaac0710f94c6de6c24534ee06858',
            'widths':[], 'screenshots':[]}
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        for width in WIDTHS:
            ctx=b.new_context(viewport={'width':width,'height':900},
                  reduced_motion='reduce' if width==320 else 'no-preference')
            page=ctx.new_page()
            page.set_content(html,wait_until='load')
            cdp=ctx.new_cdp_session(page)
            baseline=audit_ax(cdp)
            assert baseline['actionables'] >= 120,(width,baseline)
            assert page.get_by_role('group',name='View records by source year').count()==1
            assert page.get_by_role('radio').count()==4
            assert page.get_by_role('main',name='Apollo 1 evidence investigation').count()==1
            assert page.get_by_role('searchbox').count()>=1
            duplicates=page.evaluate('''()=>{
              const ids=[...document.querySelectorAll('[id]')].map(n=>n.id);
              return ids.filter((id,i)=>ids.indexOf(id)<i);
            }''')
            assert not duplicates,(width,duplicates)
            broken_fragments=page.evaluate('''()=>[...document.querySelectorAll('a[href^="#"]')]
              .filter(a=>!document.getElementById(a.getAttribute('href').slice(1)))
              .map(a=>a.getAttribute('href'))''')
            assert not broken_fragments,(width,broken_fragments)
            card=page.locator('#source-concordance')
            card.get_by_role('radio',name='1966 rehearsal — 1').check()
            assert card.locator('[data-concordance-record]:visible').count()==1
            assert card.get_by_role('radio',name='1966 rehearsal — 1').is_checked()
            year=audit_ax(cdp)
            # When filtering to 1966, the other five cards are CSS-hidden and
            # their four distinct source links per record MUST be absent from the focus order.
            hidden=card.locator('[data-concordance-record]:not(:visible) a').count()
            assert hidden==20,(width,hidden)
            assert year['actionables']<=baseline['actionables']-20,(width,year,baseline)
            card.get_by_role('radio',name='All six source records').check()
            assert card.locator('[data-concordance-record]:visible').count()==6
            restored=audit_ax(cdp)
            assert restored['actionables']==baseline['actionables'],(width,restored,baseline)
            card.locator('details summary').first.focus()
            page.keyboard.press('Enter')
            assert card.locator('details').first.evaluate('(n)=>n.open')
            disclosure=audit_ax(cdp)
            # R18 native cross-lane custody disclosure exposes six NASA links, six casefile
            # links and one pinned source link only when expanded.
            assert disclosure['actionables']==baseline['actionables']+14,(width,disclosure,baseline)  # +1 R23 nested identity disclosure
            card.locator('details summary').first.focus();page.keyboard.press('Enter')
            assert not card.locator('details').first.evaluate('(n)=>n.open')
            assert audit_ax(cdp)['actionables']==baseline['actionables'],(width,'disclosure focus restoration')
            if width in (390,1440):
                card.get_by_role('radio',name='1966 rehearsal — 1').check()
                target=OUT/f'r16-ax-year-1966-{width}.png'
                card.screenshot(path=str(target),animations='disabled')
                report['screenshots'].append({'name':target.name,
                    'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
            report['widths'].append({'width':width, 'baseline':baseline,
                'filtered_1966':year, 'all_restored':restored,
                'disclosure_open':disclosure, 'broken_fragment_links':0,
                'duplicate_dom_ids':0, 'concealed_card_links_absent':hidden,
                'landmark_and_radiogroup_named':True})
            ctx.close()
        b.close()
    RESULT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('R16_CDP_AX_PASS',len(report['widths']),'viewports',
          'actionable elements:',[w['baseline']['actionables'] for w in report['widths']])
    return report

if __name__=='__main__':run()
