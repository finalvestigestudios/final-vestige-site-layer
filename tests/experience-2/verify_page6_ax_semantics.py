#!/usr/bin/env python3
"""Chromium CDP accessibility and keyboard check for EX2 scoped WordPress payload.

This is a real browser accessibility-tree test of source-pinned, offline HTML.
It is NOT axe, WCAG 2.2 AA certification, real WordPress/Assembler, Jetpack,
image transfers, native zoom, Safari, Lighthouse, CI/QD or hosted CWV.
Run: python tests/experience-2/verify_page6_ax_semantics.py
"""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
COMPOSER = ROOT / 'tools/experience-2/compose_page6_flagship.py'
SOURCE = ROOT / 'experience2/home-flagship'
WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
CHAPTER_IDS = ('fv-hf-title', 'fv-hf-chronicle', 'fv-hf-evidence',
               'fv-hf-inquiry', 'fv-hf-method-title', 'fv-hf-observer',
               'fv-hf-mind-title')
ROLES_NEED_NAME = {'link', 'button', 'checkbox', 'radio', 'switch', 'textbox',
                   'combobox', 'slider', 'menuitem', 'searchbox'}


def accessible_nodes(page):
    client = page.context.new_cdp_session(page)
    try:
        client.send('Accessibility.enable')
        nodes = client.send('Accessibility.getFullAXTree')['nodes']
    finally:
        client.detach()
    return [{'role': n.get('role', {}).get('value', ''),
             'name': n.get('name', {}).get('value', ''),
             'backend': n.get('backendDOMNodeId')}
            for n in nodes if not n.get('ignored', False)]


def focused_link_ax(page, selector):
    client = page.context.new_cdp_session(page)
    try:
        client.send('DOM.enable')
        client.send('Accessibility.enable')
        root = client.send('DOM.getDocument')['root']['nodeId']
        node = client.send('DOM.querySelector', {'nodeId': root, 'selector': selector})['nodeId']
        if not node:
            return []
        found = client.send('Accessibility.getPartialAXTree',
                            {'nodeId': node, 'fetchRelatives': False})['nodes']
        return [{'role': x.get('role', {}).get('value', ''),
                 'name': x.get('name', {}).get('value', ''),
                 'ignored': x.get('ignored', False)} for x in found]
    finally:
        client.detach()


def inspect(page, javascript):
    nodes = accessible_nodes(page)
    bad = [n for n in nodes if n['role'] in ROLES_NEED_NAME and not n['name'].strip()]
    links = [n for n in nodes if n['role'] == 'link']
    rail = [n for n in focused_link_ax(page, '.fv-hf__focus-rail a')
            if n['role'] == 'link' and not n['ignored'] and n['name'].strip()]
    dom = page.evaluate('''() => {
      const root = document.querySelector('.fv-hf');
      const focus = root?.querySelector('.fv-hf__focus-rail a');
      const chapters = %s;
      const visible = e => {
        const s=getComputedStyle(e), b=e.getBoundingClientRect();
        return !e.closest('[hidden],[inert]') && s.display!=='none' &&
               s.visibility!=='hidden' && b.width>0 && b.height>0;
      };
      return {
        root: !!root,
        chapters: chapters.every(id => !!root.querySelector('#'+id)),
        focusVisible: !!focus && visible(focus),
        focusText: focus?.textContent.trim(),
        focusHref: focus?.getAttribute('href'),
        focusHeight: focus?.getBoundingClientRect().height,
        images: [...root.querySelectorAll('img')].map(i=>({alt:i.getAttribute('alt'),src:i.src})),
        deadButtonsNoJS: [...root.querySelectorAll('button')].filter(visible).length,
        width: innerWidth,
        overflow: Math.max(0, document.documentElement.scrollWidth-innerWidth)
      };
    }''' % json.dumps(CHAPTER_IDS))
    failures=[]
    if bad: failures.append('unnamed accessible controls: '+str(bad[:4]))
    if len(rail)!=1: failures.append('accessible Focus rail link missing/unnamed')
    if not dom['root'] or not dom['chapters']: failures.append('seven-chapter source incomplete')
    if not dom['focusVisible'] or dom['focusHeight'] < 44:
        failures.append('Focus rail invisible or shorter than 44 CSS px')
    if dom['focusHref']!='https://finalvestige.com/focus/':
        failures.append('Focus rail destination changed')
    if len(dom['images'])!=3 or any(not (i['alt'] or '').strip() for i in dom['images']):
        failures.append('three archival images lack alt text')
    if dom['overflow']>0: failures.append('root horizontal overflow')
    if not javascript and dom['deadButtonsNoJS']:
        failures.append('JS-only buttons displayed without scripting')
    return failures, {'axNodes':len(nodes),'namedLinks':len(links),
                      'unnamedControls':len(bad),'focusRailAX':len(rail),**dom}


def main():
    spec = importlib.util.spec_from_file_location('fv_page6_composer',COMPOSER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    # Composer fails closed unless all 11 flagship source Git blob hashes match.
    payload = module.stage_payload(SOURCE)
    shell = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
             '<meta name="viewport" content="width=device-width,initial-scale=1">'
             '</head><body><header style="height:75px;background:#172323;color:#fff">'
             'SIMULATED WP HEADER — NOT ASSEMBLER</header>')
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXECUTABLE','/usr/bin/chromium'),
                                  headless=True,args=['--no-sandbox'])
        try:
            for width in WIDTHS:
                for javascript in (False,True):
                    page=browser.new_page(viewport={'width':width,'height':900},
                                          java_script_enabled=javascript,reduced_motion='reduce')
                    page.route('**/*',lambda route:route.abort())
                    errors=[]
                    page.on('pageerror',lambda err:errors.append(str(err)))
                    page.set_content(shell+payload+'</body></html>')
                    failures,facts=inspect(page,javascript)
                    assert not errors,(width,javascript,errors)
                    assert not failures,(width,javascript,failures)
                    page.keyboard.press('Tab')
                    path=[]
                    for _ in range(15):
                        control=page.evaluate('''() => {
                          const e=document.activeElement;
                          return {label:e.textContent.trim().slice(0,80),
                                  css:typeof e.className==='string'?e.className:''};
                        }''')
                        path.append(control)
                        if 'fv-hf__mast-cta' in control['css']:
                            break
                        page.keyboard.press('Tab')
                    assert 'fv-hf__mast-cta' in path[-1]['css'], (width,javascript,'Focus not reachable in 15 Tabs')
                    facts.update(width=width,javascript=javascript,focusTabIndex=len(path),
                                 pageErrors=errors)
                    results.append(facts)
                    if width in (390,1440) and javascript:
                        page.screenshot(path=str(ROOT/f'ax-semantic-{width}.png'),full_page=False)
                    if width==390 and javascript:
                        for case, mutation in (
                            ('focus_label_erased', "document.querySelector('.fv-hf__focus-rail a').textContent='';"),
                            ('focus_display_hidden', "document.querySelector('.fv-hf__focus-rail a').style.display='none';"),
                            ('investigation_link_label_erased', "document.querySelector('.fv-hf__opening-actions a.fv-hf__text-link').textContent='';"),
                        ):
                            negative=browser.new_page(viewport={'width':390,'height':900},java_script_enabled=True)
                            negative.route('**/*',lambda route:route.abort())
                            negative.set_content(shell+payload+'</body></html>')
                            negative.evaluate(mutation)
                            findings,_=inspect(negative,True)
                            assert findings,'negative control escaped: '+case
                            results.append({'negative':case,'rejected':True,'failures':findings})
                            negative.close()
                    page.close()
        finally:
            browser.close()
    report={'scope':'Source-pinned Chromium CDP AX + keyboard; simulated WordPress shell only',
            'passedPositive':14,'passedNegative':3,
            'notTested':['real WordPress','Assembler','axe','WCAG 2.2 AA','Jetpack confirmation',
                         'real image bytes','native zoom','Lighthouse','field CWV','Safari'],
            'results':results}
    (ROOT/'page6-ax-semantic-results.json').write_text(json.dumps(report,indent=2))
    print('PASS 14/14 AX + keyboard; 3/3 negative controls; NOT WordPress/axe/WCAG')


if __name__=='__main__':
    main()
