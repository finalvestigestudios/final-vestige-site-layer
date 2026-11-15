#!/usr/bin/env python3
"""R376 local WordPress API stub and Chromium QA. NOT installed WordPress/staging."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
from urllib.parse import urlparse
from pypdf import PdfReader
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
SOURCES={
'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
'https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/',
'https://www.nasa.gov/history/55-years-ago-tragedy-on-the-launch-pad/',
}
CASES=[('mobile-320',320,False,False,False,False,False),
 ('mobile-390',390,False,False,False,False,False),
 ('tablet-768',768,False,False,False,False,False),
 ('desktop-1440',1440,False,False,False,False,False),
 ('wide-1920',1920,False,False,False,False,False),
 ('nojs-320',320,True,False,False,False,False),
 ('root4x-320',320,False,True,False,False,False),
 ('reduced-390',390,False,False,True,False,False),
 ('forced-320',320,False,False,False,True,False),
 ('touch-390',390,False,False,False,False,True)]
PERF="""(() => {window.__fvR376={lcp:null,cls:0};
try {new PerformanceObserver(l=>{for(const e of l.getEntries())window.__fvR376.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(_){}
try {new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__fvR376.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(_){}
})();"""

def digest(obj):return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def snapshot(page):
    # This is the same event-to-NASA citation DOM contract verified in R374,
    # evaluated against NEW R376 WordPress lifecycle stub output, not a reused PNG.
    return page.evaluate("""() => {
      const norm=x=>(x||'').replace(/\\s+/g,' ').trim();
      const roots=[...document.querySelectorAll('[data-fv-apollo-path]')];
      if(roots.length!==1)return {root_count:roots.length};
      const r=roots[0],txt=(n,s)=>norm(n?.querySelector(s)?.textContent);
      const stages=[...r.querySelectorAll('[data-fv-evidence-stage]')].map(s=>{
        const d=s.querySelector('details[data-fv-source-drawer]');
        return {when:txt(s,'.fv-apollo-r372__when'),heading:txt(s,'h3'),
          claim:txt(s,'.fv-apollo-r372__claim'),limit:txt(s,'.fv-apollo-r372__limit'),
          source:txt(s,'.fv-apollo-r372__source'),summary:txt(s,'details summary'),
          href:d?.querySelector('a[data-fv-nasa-source]')?.href||null,
          print:s.querySelector('a[data-fv-print-source]')?.href||null,
          native:!!d?.querySelector(':scope > summary')};
      });
      const context=r.querySelector('[data-fv-context]');
      return {root_count:1,stages,context:txt(r,'[data-fv-context]'),
        context_href:context?.querySelector('a[data-fv-nasa-context]')?.href||null,
        context_print:r.querySelector('.fv-apollo-r372__context a[data-fv-print-source]')?.href||null,
        native_context:!!context?.querySelector(':scope > summary'),
        cta:[...r.querySelectorAll('[data-fv-free-cta]')].map(a=>[a.href,norm(a.textContent)]),
        note:txt(r,'.fv-apollo-r372__note'),method:txt(r,'.fv-apollo-r372__method')};
    }""")

# Reviewed R374 full chronology fingerprint and exact 4 source assignments.
CUSTODY='9ce651c80e7d6d5dc91a5ad3b7a8bac7eb9a6341c18d41ac2877298697ff117f'
ASSIGNMENTS=[
'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
'https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/']

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    php=[]
    for scenario in ('enabled','disabled','production','wronghost','preowned','functioncollision','mutation'):
        proc=subprocess.run(['php',str(HERE/'scenario.php'),scenario],capture_output=True,text=True)
        try: row=json.loads(proc.stdout)
        except Exception:raise RuntimeError(f'PHP {scenario} did not return JSON: {proc.stdout} {proc.stderr}')
        row['process_rc']=proc.returncode;row['stderr']=proc.stderr
        php.append(row)
    fixture=subprocess.run(['php',str(HERE/'scenario.php'),'enabled','--html'],capture_output=True,text=True,check=True).stdout
    out=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for name,width,nojs,root4x,reduced,forced,touch in CASES:
            ctx=browser.new_context(viewport={'width':width,'height':860},java_script_enabled=not nojs,
              reduced_motion='reduce' if reduced else 'no-preference',
              forced_colors='active' if forced else 'none',has_touch=touch)
            page=ctx.new_page(); requests=[]
            page.on('request',lambda r:requests.append(r.url))
            if not nojs:page.evaluate(PERF)  # local fixture observer; set_content is not real navigation
            page.set_content(fixture,wait_until='load')
            if root4x:page.add_style_tag(content='html{font-size:64px!important}')
            page.wait_for_timeout(180)
            snap=snapshot(page)
            dom=page.evaluate("""() => {const r=document.querySelector('[data-fv-apollo-path]');
             return {count:document.querySelectorAll('[data-fv-apollo-path]').length,
              css:getComputedStyle(r).getPropertyValue('--ar-bg').trim(),
              overflow:document.documentElement.scrollWidth>innerWidth+1,
              sources:[...r.querySelectorAll('[data-fv-nasa-source], [data-fv-nasa-context]')].map(a=>a.href),
              cta:[...r.querySelectorAll('[data-fv-free-cta]')].map(a=>a.href),
              ids:[...document.querySelectorAll('[id]')].map(a=>a.id),
              perf:window.__fvR376||null};}""")
            checks={'one_component':dom['count']==1,'four_stages':len(snap['stages'])==4,
               'stage_custody_digest_unchanged':digest(snap)==CUSTODY,
               'correct_stage_to_NASA_join':[x.get('href') for x in snap['stages']]==ASSIGNMENTS,
               'matching_print_citations':[x.get('print') for x in snap['stages']]==ASSIGNMENTS,
               'four_unique_NASA_destinations':set(dom['sources'])==SOURCES,
               'single_free_only_CTA':dom['cta']==[FREE],
               'CSS_applied':dom['css']=='#0d1011','no_horizontal_overflow':not dom['overflow'],
               'unique_anchor_ids':len(dom['ids'])==len(set(dom['ids'])),
               'no_remote_resources_requested':len(requests)==0}
            s=page.locator('[data-fv-source-drawer] summary').first
            if s.count():
                s.focus();page.keyboard.press('Enter')
                checks['keyboard_open']=page.locator('[data-fv-source-drawer]').first.evaluate('(e)=>e.open')
                page.keyboard.press('Enter')
                checks['keyboard_close']=not page.locator('[data-fv-source-drawer]').first.evaluate('(e)=>e.open')
                s.click();checks['pointer_touch_open']=page.locator('[data-fv-source-drawer]').first.evaluate('(e)=>e.open')
                s.click()
            else:checks['native_drawers']=False
            page.screenshot(path=str(args.out/(name+'.png')),full_page=True,animations='disabled')
            if name=='desktop-1440':
                page.emulate_media(media='print')
                page.pdf(path=str(args.out/'r376-print.pdf'),format='A4',print_background=True)
            out.append({'case':name,'checks':checks,'fixture_perf_not_field':dom['perf'],
               'requests':requests,'mode':'WORDPRESS_API_STUB_FIXTURE_NOT_STAGING'})
            ctx.close()
        browser.close()
    links=[]
    for p in PdfReader(str(args.out/'r376-print.pdf')).pages:
        for a in p.get('/Annots',[]):
            d=a.get_object().get('/A');
            if d and d.get('/URI'):links.append(str(d['/URI']))
    print_gate=SOURCES.issubset(set(links)) and FREE in links
    success=(all(x['process_rc']==0 and x['failed']==0 for x in php)
        and all(all(x['checks'].values()) for x in out) and print_gate)
    result={'status':'LOCAL_PHP_CHROMIUM_PASS_NOT_INSTALLED_WORDPRESS' if success else 'FAIL',
      'php':php,'browser':out,'print_links_verified':print_gate,'print_link_destinations':sorted(set(links)),
      'genuine_axe_core':'NOT_EXECUTED','installed_WordPress_Assembler':'NOT_EXECUTED',
      'HTTP_CSP_stylesheet_waterfall':'NOT_VERIFIED','hosted_CI':'NOT_VERIFIED',
      'production_LCP_CLS_INP':'NOT_MEASURED','reviewed_stage_document_custody_sha256':CUSTODY}
    (args.out/'results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],len(php),'WP API-stub scenarios',len(out),'browser contexts',sum(len(x['checks']) for x in out),'browser assertions', 'print',print_gate)
    sys.exit(0 if success else 1)
if __name__=='__main__': main()
