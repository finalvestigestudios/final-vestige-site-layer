"""Local Chrome accessibility-tree and synthetic paint smoke; NOT axe/WCAG or field CWV."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'index.html').read_text(encoding='utf-8')
results=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for w in (320,390,768,1440,1920):
  ctx=browser.new_context(viewport={'width':w,'height':900},reduced_motion='reduce')
  page=ctx.new_page()
  page.evaluate('''()=>{window.__fvVitals={lcp:0,cls:0};
    try{new PerformanceObserver(l=>{for(const x of l.getEntries())window.__fvVitals.lcp=Math.max(window.__fvVitals.lcp,x.startTime)}).observe({type:'largest-contentful-paint',buffered:true})}catch(_){}
    try{new PerformanceObserver(l=>{for(const x of l.getEntries()){if(!x.hadRecentInput)window.__fvVitals.cls+=x.value}}).observe({type:'layout-shift',buffered:true})}catch(_){}
  }''')
  page.set_content(HTML,wait_until='load');page.wait_for_timeout(180)
  session=ctx.new_cdp_session(page)
  tree=session.send('Accessibility.getFullAXTree')['nodes']
  roles=[];unnamed=[]
  for n in tree:
   if n.get('ignored'):continue
   role=n.get('role',{}).get('value','');name=n.get('name',{}).get('value','')
   if role in ('button','combobox','link','summary','heading'):roles.append((role,name))
   if role in ('button','combobox','link') and not name.strip():unnamed.append(role)
  assert not unnamed,(w,unnamed)
  assert sum(x[0]=='combobox' for x in roles)>=1
  assert sum('Follow the remedy' in x[1] for x in roles)>=1
  found=page.locator('.ex2-trail__card').count()
  assert found==6
  # WCAG-ish geometry smoke, deliberately not passing it off as axe certification.
  dims=page.locator('.ex2-trail__controls button').bounding_box()
  assert dims and dims['height']>=44
  metrics=page.evaluate('window.__fvVitals')
  results.append(dict(width=w,named_interactives=len([r for r in roles if r[0] in ('button','combobox','link')]),unnamed_controls=len(unnamed),lcp_ms=round(metrics['lcp'],2),cls=round(metrics['cls'],4),select_height=round(dims['height'])))
  ctx.close()
 browser.close()
(ROOT/'qa'/'TRAIL_AX_PERF_RESULTS.json').write_text(json.dumps({'run_scope':'local Chromium in-memory full-page fixture, no actual WP staging or network assets','axe':'NOT RUN — no verified local axe-core bundle','metrics_class':'synthetic browser, NOT field p75 Core Web Vitals','results':results},indent=2)+'\n',encoding='utf-8')
print('TRAIL_AX_PERF_SMOKE_PASS',json.dumps(results))
