#!/usr/bin/env python3
"""Review-only exact-source Chromium first-screen gate. Never publishes or writes CMS.

--checkout + --expected-head enforces a clean exact Git HEAD and 11 blob identities.
--source-dir is an explicitly labelled reconstructed-blob mode for offline QA.
Neither mode certifies WordPress, Jetpack, axe/WCAG or CWV/Lighthouse.
"""
import argparse, asyncio, hashlib, json, subprocess
from pathlib import Path
from playwright.async_api import async_playwright

NAMES = ['index.html','flagship.css','chronicle.css','chronicle-lens.css',
         'inquiry.css','observer-lab.css','reading-trail.css',
         'flagship.js','observer-lab.js','chronicle-lens.js','reading-trail.js']
WIDTHS = [320,360,390,768,920,921,1440,1920]
CHAPTERS = ['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry',
            'fv-hf-method-title','fv-hf-observer','fv-hf-mind-title']

def git(repo, *args):
    return subprocess.check_output(['git', *args], cwd=repo, text=True).strip()

def verify_and_assemble(source, checkout=None, expected_head=None):
    files = {}
    if checkout:
        head = git(checkout, 'rev-parse', 'HEAD')
        if head != expected_head or len(head) != 40:
            raise ValueError('FAIL CLOSED: exact Git HEAD mismatch')
    else:
        head = None
    for name in NAMES:
        path = source / name
        if not path.is_file() or path.is_symlink():
            raise ValueError('missing or symlinked required source: ' + name)
        data = path.read_bytes()
        sha = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if checkout:
            git_path = 'experience2/home-flagship/' + name
            committed = git(checkout, 'rev-parse', 'HEAD:' + git_path)
            if committed != sha:
                raise ValueError('FAIL CLOSED: modified source blob: ' + name)
        files[name] = data.decode('utf-8')
    html = files['index.html']
    for name in NAMES[1:7]:
        link = f'<link rel="stylesheet" href="./{name}">'
        if html.count(link) != 1: raise ValueError('missing CSS link ' + name)
        html = html.replace(link, '<style>\n' + files[name] + '\n</style>')
    for name in NAMES[7:]:
        tag = f'<script src="./{name}" defer></script>'
        if html.count(tag) != 1: raise ValueError('missing JS script ' + name)
        html = html.replace(tag, '')
    scripts = '\n'.join('<script>\n' + files[name] + '\n</script>' for name in NAMES[7:])
    if html.count('</body>') != 1: raise ValueError('invalid body delimiter')
    return html.replace('</body>', scripts + '\n</body>'), head

async def exercise(browser, markup, width, js, reduced, out):
    ctx = await browser.new_context(viewport={'width':width,'height':820},
            java_script_enabled=js,reduced_motion='reduce' if reduced else 'no-preference')
    await ctx.route('https://**/*', lambda route: route.abort())
    page = await ctx.new_page(); errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    await page.set_content(markup, wait_until='load')
    await page.wait_for_timeout(100)
    details = await page.evaluate('''() => {
      const q=s=>document.querySelector(s);
      const b=s=>q(s).getBoundingClientRect();
      const cases=[...document.querySelectorAll('[data-fv-case]')];
      const ch=['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'];
      return {overflow:document.documentElement.scrollWidth-innerWidth,
        chapterCount:ch.filter(id=>!!document.getElementById(id)).length,
        chapterLinks:q('.fv-hf__chapter-nav').querySelectorAll('a').length,
        focusHref:q('.fv-hf__mast-cta').href, focusHeight:b('.fv-hf__mast-cta').height,
        heroActionTop:b('.fv-hf__button--gold').top,
        devButtonsVisible:[...document.querySelectorAll('[data-fv-direction-choice]')].filter(e=>e.getBoundingClientRect().width>0).length,
        mobileNav:getComputedStyle(q('.fv-hf__mobile-menu')).display,
        desktopNav:getComputedStyle(q('.fv-hf__nav')).display,
        casesVisible:cases.filter(e=>getComputedStyle(e).display!=='none').length,
        sourceImages:document.querySelectorAll('img[data-fv-archive-img]').length,
        bodyMainFocus:q('#fv-hf-main').getAttribute('tabindex')};
    }''')
    faults=[]
    def ck(condition, message):
        if not condition: faults.append(message)
    ck(details['overflow']<=1,'horizontal overflow')
    ck(details['chapterCount']==7 and details['chapterLinks']==7,'seven chapters absent')
    ck(details['focusHref']=='https://finalvestige.com/focus/' and details['focusHeight']>=44,'Focus CTA regression')
    ck(details['sourceImages']==3,'source images not preserved')
    ck(details['bodyMainFocus']=='-1','main skip destination not focusable')
    ck(details['devButtonsVisible']==0,'review toolbar starts expanded')
    ck(details['desktopNav']=='none' if width<=920 else details['desktopNav']!='none','duplicate or missing desktop nav')
    ck(details['mobileNav']!='none' if width<=920 else details['mobileNav']=='none','mobile nav breakpoint')
    ck(details['casesVisible']==(1 if js else 3),'no-JS/readable archive or enhanced case regression')
    ck(not errors,'page JS exception: '+' | '.join(errors))
    await page.keyboard.press('Tab')
    first = await page.evaluate('document.activeElement.getAttribute("href")')
    ck(first=='#fv-hf-main','first Tab must bypass developer controls')
    await page.keyboard.press('Enter')
    hashval = await page.evaluate('location.hash')
    ck(hashval=='#fv-hf-main','no-JS native main skip navigation')
    if js and width==390 and not reduced:
        dev=page.locator('.fv-hf__studio-controls')
        await dev.locator('summary').click()
        ck(await dev.get_attribute('open') is not None,'dev selector did not open')
        await dev.locator('[data-fv-direction-choice="museum"]').click()
        ck(await page.locator('[data-fv-home-flagship]').get_attribute('data-fv-direction')=='museum','art directions not preserved')
        await page.locator('[data-fv-case-button="franklin"]').click()
        ck(await page.locator('[data-fv-case="franklin"]').is_visible(),'case switch failed')
        await page.locator('[data-fv-chronicle-view="original"]').click()
        ck(await page.locator('.fv-hf__chronicle').get_attribute('data-fv-chronicle-mode')=='original','chronicle lens failed')
        await page.locator('[data-fv-observer-switch="b"]').click()
        ck(await page.locator('[data-fv-observer-frame="b"]').is_visible(),'observer interaction failed')
    if width in (320,390,768,1440,1920) and js and not reduced:
        await page.screenshot(path=str(out/f'firstscreen_{width}.png'),animations='disabled')
    await ctx.close()
    return {'width':width,'javascript':js,'reducedMotion':reduced,'pass':not faults,
            'errors':faults,'firstTabHref':first,**details}

async def run(args):
    source=args.source_dir if args.source_dir else args.checkout/'experience2/home-flagship'
    if args.checkout and not args.expected_head: raise ValueError('--expected-head is mandatory for a checkout')
    markup, head = verify_and_assemble(source,args.checkout,args.expected_head)
    args.out.mkdir(parents=True,exist_ok=True)
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path=args.chromium,args=['--no-sandbox'])
        rows=[]
        for width in WIDTHS:
            for js in (False,True):
                for reduced in (False,True):
                    rows.append(await exercise(browser,markup,width,js,reduced,args.out))
        await browser.close()
    result={'mode':'exact_checkout' if args.checkout else 'reconstructed_verified_source_blobs',
            'head':head,'external_images':'blocked offline','wordpress':False,'axe':False,
            'lighthouse':False,'cases':len(rows),'passed':sum(r['pass'] for r in rows),
            'rows':rows}
    (args.out/'report.json').write_text(json.dumps(result,indent=2))
    print(f"Integrated first-screen Chromium {result['passed']}/{len(rows)} PASS")
    for r in rows:
        if not r['pass']:print(r['width'],r['javascript'],r['reducedMotion'],r['errors'])
    if result['passed']!=len(rows):raise SystemExit(1)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--checkout',type=Path)
    group.add_argument('--source-dir',type=Path)
    ap.add_argument('--expected-head')
    ap.add_argument('--chromium',default='/usr/bin/chromium')
    ap.add_argument('--out',type=Path,default=Path('ex2-firstscreen-qa'))
    asyncio.run(run(ap.parse_args()))
