#!/usr/bin/env python3
"""Offline exact-source 7-chapter visual QA. NOT WordPress, axe, Lighthouse or media delivery."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
CSS=('flagship.css','chronicle.css','chronicle-lens.css','inquiry.css','observer-lab.css','reading-trail.css')
JS=('flagship.js','observer-lab.js','chronicle-lens.js','reading-trail.js')
CHAPTERS=('fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title')
def load(repo,expected):
    if not re.fullmatch('[0-9a-f]{40}',expected):raise ValueError('40-char SHA required')
    def git(*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
    if git('rev-parse','HEAD')!=expected:raise ValueError('checkout HEAD mismatch')
    files={}
    for n in ('index.html',)+CSS+JS:
        p=repo/'experience2/home-flagship'/n
        if not p.is_file() or p.is_symlink():raise ValueError('missing or symlinked '+n)
        content=p.read_bytes()
        sha=hashlib.sha1(('blob '+str(len(content))+'\0').encode()+content).hexdigest()
        if git('rev-parse','HEAD:experience2/home-flagship/'+n)!=sha:raise ValueError('dirty asset '+n)
        files[n]=content.decode()
    return files
def assemble(files):
    html=files['index.html']
    for n in CSS:
        tag='<link rel="stylesheet" href="./'+n+'">'
        if html.count(tag)!=1:raise ValueError('CSS contract '+n)
        html=html.replace(tag,'<style data-ex2-style="'+n+'">'+files[n]+'</style>')
    tail=''
    for n in JS:
        tag='<script src="./'+n+'" defer></script>'
        if html.count(tag)!=1:raise ValueError('JS contract '+n)
        html=html.replace(tag,'')
        tail+='<script data-ex2-script="'+n+'">'+files[n].replace('</script','<\\/script')+'</script>'
    if html.count('</body>')!=1:raise ValueError('body contract')
    return html.replace('</body>',tail+'</body>')
def inspect(page):
    return page.evaluate("""() => ({
    w:innerWidth,scrollWidth:document.documentElement.scrollWidth,h1:document.querySelectorAll('h1').length,
    chapters:[...document.querySelectorAll('.fv-hf__chapter-nav a')].map(a=>({id:a.hash.slice(1),ok:!!document.getElementById(a.hash.slice(1))})),
    focus:[...document.querySelectorAll('a[href="https://finalvestige.com/focus/"]')].length,
    cases:[...document.querySelectorAll('[data-fv-case]')].filter(e=>!e.hidden&&getComputedStyle(e).display!=='none').length,
    observerHidden:document.querySelector('[data-fv-observer-controls]')?.hidden})""")
def run(html,out,chrome):
    out.mkdir(parents=True,exist_ok=True)
    report={'scope':'Exact committed HTML/CSS/JS rendered via Chromium set_content (about:blank); NOT WordPress',
      'axe':'NOT RUN; fail closed','Lighthouse':'NOT RUN; fail closed','Jetpack':'NOT TESTED',
      'media':'BLOCKED BY TEST ENVIRONMENT; transfer bytes and decoding NOT VERIFIED','tests':[]}
    with sync_playwright() as p:
      b=p.chromium.launch(headless=True,executable_path=chrome,args=['--no-sandbox'])
      for mode in ('js','nojs','reduce'):
        for w in ((320,360,390,768,1024,1440,1920) if mode=='js' else (320,390,768,1440)):
          ctx=b.new_context(viewport={'width':w,'height':900},java_script_enabled=mode!='nojs',reduced_motion='reduce' if mode=='reduce' else 'no-preference')
          pg=ctx.new_page();errors=[];blocked=[]
          pg.on('pageerror',lambda e:errors.append(str(e)))
          pg.route('**/*',lambda route:(blocked.append(route.request.url),route.abort()))
          pg.set_content(html,wait_until='domcontentloaded');pg.wait_for_timeout(120)
          info=inspect(pg)
          passed=(info['scrollWidth']<=w+2 and info['h1']==1
             and tuple(c['id'] for c in info['chapters'])==CHAPTERS
             and all(c['ok'] for c in info['chapters']) and info['focus']>=1 and not errors
             and info['cases']==(3 if mode=='nojs' else 1))
          item={'width':w,'mode':mode,'pass':passed,'dom':info,'errors':errors,'blockedMedia':blocked}
          if mode=='js' and w in (390,1440):
            changes={}
            for c in ('museum','observatory','dossier'):
              btn=pg.locator('[data-fv-direction-choice="'+c+'"]');btn.click()
              changes['direction_'+c]=btn.get_attribute('aria-pressed')=='true' and pg.locator('[data-fv-home-flagship]').get_attribute('data-fv-direction')==c
            for c in ('franklin','malbone','apollo'):
              btn=pg.locator('[data-fv-case-button="'+c+'"]');btn.click()
              changes['case_'+c]=btn.get_attribute('aria-pressed')=='true' and pg.locator('[data-fv-case="'+c+'"]').is_visible()
            for c in ('original','addition','both'):
              btn=pg.locator('[data-fv-chronicle-view="'+c+'"]');btn.click()
              changes['chronicle_'+c]=btn.get_attribute('aria-pressed')=='true'
            for c in ('b','a'):
              btn=pg.locator('[data-fv-observer-switch="'+c+'"]');btn.click()
              changes['observer_'+c]=btn.get_attribute('aria-pressed')=='true'
            item['controls']=changes;item['pass']=item['pass'] and all(changes.values())
          if mode in ('js','nojs') and w in (320,390,1440):
            name=mode+'_'+str(w)+'.png';pg.screenshot(path=str(out/name),animations='disabled')
            item['screenshot']=name
          report['tests'].append(item);ctx.close()
      b.close()
    report['passed']=sum(x['pass'] for x in report['tests'])
    report['total']=len(report['tests'])
    report['fixture_pass']=report['passed']==report['total']
    (out/'receipt.json').write_text(json.dumps(report,indent=2))
    return report
def controls(files):
    checks=[]
    for n in ('flagship.css','reading-trail.js'):
      temp=dict(files);temp.pop(n)
      try:assemble(temp);checks.append(False)
      except KeyError:checks.append(True)
    temp=dict(files);temp['index.html']=temp['index.html'].replace('<script src="./flagship.js" defer></script>','')
    try:assemble(temp);checks.append(False)
    except ValueError:checks.append(True)
    return checks
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--repo',required=True,type=Path);p.add_argument('--expected-head',required=True)
    p.add_argument('--out',required=True,type=Path);p.add_argument('--chromium',default='/usr/bin/chromium')
    a=p.parse_args();files=load(a.repo.resolve(strict=True),a.expected_head)
    report=run(assemble(files),a.out,a.chromium)
    report['negativeControls']=controls(files);report['pass']=report['fixture_pass'] and all(report['negativeControls'])
    (a.out/'receipt.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'pass':report['pass'],'responsiveRuns':report['total'],'passes':report['passed'],'negativeControls':report['negativeControls']}))
    raise SystemExit(0 if report['pass'] else 1)
