#!/usr/bin/env python3
"""Exact-Blueprint seven-chapter *static* visual QA. NEVER a WordPress/axe/Lighthouse pass.

Usage: python verify_flagship_fullpage_review.py --blueprint FILE --out DIR
Python Playwright + local Chromium required; no network calls are made.
"""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

CHAPTERS = ('fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry',
            'fv-hf-method-title','fv-hf-observer','fv-hf-mind-title')
SIZES = ((320,568),(360,640),(390,667),(768,900),(1440,900),(1920,1080))

def load(path):
    original = path.read_bytes(); bp=json.loads(original)
    steps=[s for s in bp['steps'] if s.get('step')=='writeFile']
    assert len(steps)==1 and 'FVPG_CSS_END' in steps[0]['data'], 'Not the exact flagship MU-plugin'
    source=steps[0]['data']
    def nowdoc(kind):
        opener="<<<'FVPG_"+kind+"_END'\n"
        tail='\nFVPG_'+kind+'_END'
        assert source.count(opener)==1 and source.count(tail)==1
        return source.split(opener,1)[1].split(tail,1)[0]
    css,js,html = (nowdoc(k) for k in ('CSS','JS','HTML'))
    assert html.count('class="fv-margin-strip__item"')==72
    assert html.count('https://finalvestige.com/focus/')==5
    assert html.count('data-fv-archive-img')==2
    assert all('id="'+i+'"' in html for i in CHAPTERS)
    return {'sha256':hashlib.sha256(original).hexdigest(),
            'blob_sha':hashlib.sha1(b'blob '+str(len(original)).encode()+b'\0'+original).hexdigest(),
            'css':css,'js':js,'html':html}

def run(bp, out, negative=False):
    out.mkdir(parents=True,exist_ok=True)
    rows=[]; blocked=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width,height in SIZES:
            for mode in ('js','nojs','reduced','zoom200') if width==390 else ('js','nojs','zoom200') if width==1440 else ('js','nojs'):
                page=browser.new_page(viewport={'width':width,'height':height},java_script_enabled=mode!='nojs',
                                      reduced_motion='reduce' if mode=='reduced' else 'no-preference')
                # Explicitly DISABLE network; image transfers CANNOT be certified in this fixture.
                page.route('**/*', lambda route: route.abort())
                page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+bp['css']+'</style></head><body>'+bp['html']+'</body></html>',wait_until='domcontentloaded')
                if mode!='nojs': page.add_script_tag(content=bp['js'])
                if mode=='zoom200': page.evaluate("document.documentElement.style.zoom='2'")
                page.wait_for_timeout(300)
                sizes=page.evaluate('''() => ({viewport:innerWidth, documentWidth:document.documentElement.scrollWidth,
                    height:document.documentElement.scrollHeight,
                    margins:document.querySelectorAll('.fv-margin-strip__item').length,
                    chapters:document.querySelectorAll('.fv-hf__chapter-nav a[href^="#"]').length,
                    focusLinks:[...document.querySelectorAll('a')].filter(a=>a.href==='https://finalvestige.com/focus/').length,
                    images:[...document.querySelectorAll('img[data-fv-archive-img]')].map(i=>({src:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth>0})) })''')
                assert sizes['viewport']==width and sizes['documentWidth'] <= width + 1, sizes
                assert (sizes['margins'],sizes['chapters'],sizes['focusLinks'],len(sizes['images']))==(72,7,5,2)
                assert all(not im['loaded'] for im in sizes['images']), 'Unexpected external fetch in isolated fixture'
                if mode=='nojs':
                    assert page.locator('.fv-hf__case-choice-group').is_hidden()
                    assert page.locator('[data-fv-observer-controls]').is_hidden()
                    assert page.locator('[data-fv-chronicle-lens]').is_hidden()
                    assert page.locator('.fv-hf__inquiry-record').count()==3
                if width==390 and mode!='zoom200':
                    focus=page.locator('.fv-hf__text-link--focus').first.bounding_box()
                    assert focus and focus['height'] >= 44 and focus['y']+focus['height'] <= height+1,focus
                if mode=='reduced':
                    assert page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches')
                clearance=[]
                for anchor in CHAPTERS:
                    page.evaluate('window.scrollTo(0,document.documentElement.scrollHeight/2)')
                    page.evaluate('''id => document.querySelector('.fv-hf__chapter-nav a[href="#'+id+'"]').click()''', anchor)
                    data=page.evaluate('''id => {let e=document.getElementById(id), h=e.matches('h1,h2,h3')?e:e.querySelector('h1,h2,h3'),n=document.querySelector('.fv-hf__chapter-nav'); return {gap:h.getBoundingClientRect().top-n.getBoundingClientRect().bottom,hash:location.hash}}''',anchor)
                    clearance.append(round(data['gap'],1))
                    assert data['hash']=='#'+anchor and data['gap']>=12,{'width':width,'mode':mode,'anchor':anchor,**data}
                page.evaluate('window.scrollTo(0,0)')
                if mode=='js' and width in (320,390,768,1440,1920):
                    page.screenshot(path=str(out/f'fullpage_{width}_exact_static.png'),full_page=True,animations='disabled')
                    page.screenshot(path=str(out/f'firstscreen_{width}_exact_static.png'),animations='disabled')
                rows.append({'width':width,'height':height,'mode':mode,'checks':len(CHAPTERS)+4,
                             'min_chapter_clearance_px':min(clearance),'scroll_height':sizes['height'],
                             'focus_390_firstscreen':bool(width!=390 or mode=='zoom200' or focus['y']+focus['height']<=height+1),
                             'network_image_transfer':'NOT TESTED: network deliberately blocked'})
                page.close()
        browser.close()
    result={'source_sha256':bp['sha256'],'source_git_blob':bp['blob_sha'],
            'class':'EXACT SOURCE / STATIC CHROMIUM — NOT WORDPRESS',
            'total_chapter_clicks':len(rows)*7,'result':'PASS','modes':rows,
            'hard_blockers':['real WordPress/Assembler','real media response bytes','axe WCAG','Lighthouse/CWV','Safari','Jetpack','independent QD/CI'],
            'negative_control': 'run with --mutate-scrolling and EXPECT failure' }
    (out/'report.json').write_text(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--blueprint',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--mutate-scrolling',action='store_true',help='Adversarial expected failure: delete scoped chapter heading clearance')
    args=parser.parse_args();bp=load(args.blueprint)
    if args.mutate_scrolling:
        # Exact original regression: remove recently committed high-specificity clearance fix.
        import re
        bp['css'],n=re.subn(r'\.fv-hf\s+#fv-hf-title\s*,\s*\.fv-hf\s+#fv-hf-method-title\s*,\s*\.fv-hf\s+#fv-hf-mind-title\s*\{[^{}]*scroll-margin-top[^{}]*\}', '', bp['css'],flags=re.S)
        assert n==1, f'Negative control unable to find expected selector: {n}'
    r=run(bp,args.out);print(json.dumps({'result':r['result'],'modes':len(r['modes']),'chapter_clicks':r['total_chapter_clicks'],'blob':r['source_git_blob']},indent=2))
