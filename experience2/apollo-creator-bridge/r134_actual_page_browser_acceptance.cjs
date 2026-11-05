'use strict';
/**
 * Apollo R134: real-navigation staging acceptance for the exact R133 offline artifact.
 * No document injection, WordPress writes, production deployment, remote dependencies
 * or assertion that lab measurements are production CWV percentiles.
 *
 * Preconditions: complete repo checkout; locally installed Playwright + Chromium,
 * locally installed axe-core. Nothing is installed or downloaded by this script.
 *
 * node experience2/apollo-creator-bridge/r134_actual_page_browser_acceptance.cjs --out /tmp/apollo-r134-qa
 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const crypto=require('node:crypto');
const http=require('node:http');
const {build}=require('./r133_build_research_desk_preview.cjs');
const WIDTHS=[320,360,390,768,1440,1920];
const PAGE_PATH='/apollo/r134-preview.html';
const sha256=x=>crypto.createHash('sha256').update(x).digest('hex');
function receiptBase(){
 return {schema:'fv.apollo.r134.actual-page.v1',release:'STAGING_HOLD',
  browser_acceptance:'NOT_ESTABLISHED',rights:'0_OF_6_CLEARED',
  offer:'NOT_VERIFIED',net_revenue:'NOT_OBSERVABLE',checks:[],errors:[],
  user_agent:null,screenshots:[],metrics:{},axe:{},build:null};
}
function responseServer(html){
 const srv=http.createServer((req,res)=>{
  if(req.method!=='GET'||req.url!==PAGE_PATH){
   res.writeHead(404,{'Content-Type':'text/plain; charset=utf-8','Cache-Control':'no-store'});res.end('Not found');return;
  }
  res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store',
   'Referrer-Policy':'no-referrer','X-Robots-Tag':'noindex, nofollow, noarchive',
   'X-Content-Type-Options':'nosniff'});res.end(html);
 });
 return srv;
}
function observeMetrics(page){
 return page.addInitScript(()=>{
  window.__fvR134={lcp:null,cls:0,errors:[]};
  try{
   new PerformanceObserver(list=>{for(const e of list.getEntries())window.__fvR134.lcp=e.startTime;})
    .observe({type:'largest-contentful-paint',buffered:true});
  }catch(e){window.__fvR134.errors.push('LCP_OBSERVER_UNAVAILABLE');}
  try{
   new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__fvR134.cls+=e.value;})
    .observe({type:'layout-shift',buffered:true});
  }catch(e){window.__fvR134.errors.push('CLS_OBSERVER_UNAVAILABLE');}
 });
}
function assertCheck(receipt,name,condition,detail){
 receipt.checks.push({name,pass:Boolean(condition),detail:detail===undefined?null:detail});
 if(!condition)receipt.errors.push(name+(detail?' :: '+JSON.stringify(detail):''));
}
async function inspectPage(page,receipt,label,html){
 const errors=[];const outbound=[];
 page.on('pageerror',err=>errors.push(err.message));
 page.on('request',req=>{if(!req.url().startsWith('http://127.0.0.1:'))outbound.push(req.url());});
 const response=await page.goto(page.url()==='about:blank'?receipt.url:receipt.url,
   {waitUntil:'load',timeout:15000});
 assertCheck(receipt,label+'_HTTP_200',response&&response.status()===200,response&&response.status());
 assertCheck(receipt,label+'_REAL_NAVIGATION',page.url()===receipt.url,page.url());
 const loaded=await response.text();
 assertCheck(receipt,label+'_EXACT_HTTP_SOURCE',loaded===html,{expected:sha256(html),received:sha256(loaded)});
 await page.waitForTimeout(400); // allow buffered LCP/CLS observers, not a CWV p75 claim
 const state=await page.evaluate(()=>{
  const root=document.querySelector('[data-fvx-ledger]');
  const viewport=document.documentElement.clientWidth;
  return {cards:document.querySelectorAll('[data-fvx-record]').length,
   links:[...document.querySelectorAll('a[href*="nasa.gov/image-detail/"]')].length,
   overflow:document.documentElement.scrollWidth-viewport,
   toolsHidden:root?root.querySelector('[data-fvx-tools]').hidden:null,
   initialized:root?root.dataset.fvxInitialized:null,
   status:root?root.querySelector('[data-fvx-status]').textContent:null,
   metrics:window.__fvR134||null};
 });
 assertCheck(receipt,label+'_SIX_RECORDS',state.cards===6,state.cards);
 assertCheck(receipt,label+'_SIX_NASA_LINKS',state.links===6,state.links);
 assertCheck(receipt,label+'_NO_HORIZONTAL_OVERFLOW',state.overflow<=1,state.overflow);
 assertCheck(receipt,label+'_NO_UNEXPECTED_NETWORK',outbound.length===0,outbound);
 assertCheck(receipt,label+'_NO_PAGE_ERRORS',errors.length===0,errors);
 receipt.metrics[label]=state.metrics;
 return state;
}
async function run({outDir=path.join(os.tmpdir(),'apollo-r134-browser-qa')}={}){
 fs.mkdirSync(outDir,{recursive:true});
 const receipt=receiptBase();
 const built=path.join(outDir,'generated');
 let server=null,browser=null;
 try{
  const result=build({outDir:built});
  const html=fs.readFileSync(result.output,'utf8');
  receipt.build={artifact_sha256:sha256(html),manifest:result.manifest};
  const {chromium}=require('playwright');
  const axePath=require.resolve('axe-core/axe.min.js');
  const executable=process.env.FV_CHROMIUM_EXECUTABLE||undefined;
  browser=await chromium.launch({headless:true,...(executable?{executablePath:executable}:{})});
  receipt.user_agent=browser.version();
  server=responseServer(html);
  await new Promise((resolve,reject)=>{
   server.once('error',reject);server.listen(0,'127.0.0.1',resolve);
  });
  receipt.url='http://127.0.0.1:'+server.address().port+PAGE_PATH;
  // Server health is distinct from browser navigation; test both.
  const raw=await new Promise((resolve,reject)=>{
   http.get(receipt.url,r=>{let b='';r.setEncoding('utf8');r.on('data',s=>b+=s);
    r.on('end',()=>resolve({status:r.statusCode,body:b}));}).on('error',reject);
  });
  assertCheck(receipt,'LOCAL_HTTP_SERVER_200',raw.status===200,raw.status);
  assertCheck(receipt,'LOCAL_HTTP_SOURCE_EQUAL',raw.body===html,sha256(raw.body));
  for(const width of WIDTHS){
   const label='width_'+width;
   const context=await browser.newContext({viewport:{width,height:900},
    ...(width===390?{hasTouch:true,isMobile:true}:{})});
   const page=await context.newPage();
   await observeMetrics(page);
   const state=await inspectPage(page,receipt,label,html);
   assertCheck(receipt,label+'_PROGRESSIVE_SEARCH_INITIALIZED',
    state.initialized==='yes'&&state.toolsHidden===false,
    {initialized:state.initialized,hidden:state.toolsHidden});
   const file=label+'.png';
   await page.screenshot({path:path.join(outDir,file),fullPage:true,animations:'disabled',caret:'hide'});
   receipt.screenshots.push({path:file,sha256:sha256(fs.readFileSync(path.join(outDir,file)))});
   if(width===390||width===1440){
    const input=page.locator('[data-fvx-search]');
    const records=page.locator('[data-fvx-record]:visible');
    await input.fill('nonexistent-r134-test-phrase');
    assertCheck(receipt,label+'_EMPTY_SEARCH',await records.count()===0,
      await page.locator('[data-fvx-empty]').isVisible());
    await input.press('Escape');
    assertCheck(receipt,label+'_ESC_CLEARS_SEARCH',
      await input.inputValue()===''&&(await records.count())===6);
    await input.fill('ignition');
    await page.locator('[data-fvx-clear]').click();
    assertCheck(receipt,label+'_CLEAR_CLICK_RESTORES_SIX',
      await input.inputValue()===''&&(await records.count())===6);
    assertCheck(receipt,label+'_CLEAR_RETURNS_FOCUS',
      await input.evaluate(el=>document.activeElement===el));
   }
   if(state.metrics){
    const m=state.metrics;
    assertCheck(receipt,label+'_LCP_MEASURED',Number.isFinite(m.lcp),m.lcp);
    assertCheck(receipt,label+'_CLS_MEASURED',Number.isFinite(m.cls)&&m.errors.length===0,m);
    if(Number.isFinite(m.lcp))assertCheck(receipt,label+'_LAB_LCP_BUDGET',m.lcp<=2500,m.lcp);
    if(Number.isFinite(m.cls))assertCheck(receipt,label+'_LAB_CLS_BUDGET',m.cls<=0.1,m.cls);
   }else assertCheck(receipt,label+'_METRICS_MISSING',false);
   await context.close();
  }
  // No-JS: content, six cards, chronology and source links must survive.
  const noJs=await browser.newContext({viewport:{width:390,height:844},javaScriptEnabled:false});
  const noJsPage=await noJs.newPage();
  const noJsState=await inspectPage(noJsPage,receipt,'no_js_390',html);
  assertCheck(receipt,'NO_JS_EVIDENCE_AVAILABLE',noJsState.cards===6&&noJsState.links===6&&noJsState.toolsHidden===true);
  await noJs.close();
  // A separate audit context bypasses CSP solely to inject local axe-core.
  // The ordinary real-navigation test above NEVER bypasses production CSP.
  for(const width of [390,1440]){
   const c=await browser.newContext({viewport:{width,height:900},bypassCSP:true,reducedMotion:'reduce'});
   const p=await c.newPage();
   await p.goto(receipt.url,{waitUntil:'load',timeout:15000});
   await p.addScriptTag({path:axePath});
   const axe=await p.evaluate(async()=>window.axe.run(document,{
    runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}}));
   receipt.axe['width_'+width]={violations:axe.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}))};
   assertCheck(receipt,'AXE_'+width+'_ZERO_VIOLATIONS',axe.violations.length===0,receipt.axe['width_'+width]);
   await c.close();
  }
  receipt.browser_acceptance=receipt.errors.length?'FAILED':'TESTED_LOCAL_ONLY';
 }catch(err){receipt.errors.push('RUN_BLOCKER: '+(err&&err.stack||String(err)));}
 finally{
  if(browser)await browser.close().catch(()=>{});
  if(server)await new Promise(r=>server.close(()=>r()));
  delete receipt.url;
  fs.writeFileSync(path.join(outDir,'r134-test-receipt.json'),JSON.stringify(receipt,null,2)+'\n');
 }
 return receipt;
}
if(require.main===module){
 const i=process.argv.indexOf('--out');
 if(i>=0&&!process.argv[i+1])throw Error('--out needs directory');
 run({outDir:i>=0?path.resolve(process.argv[i+1]):undefined})
  .then(r=>{process.stdout.write(JSON.stringify({status:r.browser_acceptance,errors:r.errors,
   checks:r.checks.length,failed:r.checks.filter(x=>!x.pass).length},null,2)+'\n');
   if(r.errors.length||r.browser_acceptance!=='TESTED_LOCAL_ONLY')process.exitCode=2;})
  .catch(e=>{process.stderr.write(String(e.stack||e)+'\n');process.exitCode=2;});
}
module.exports={responseServer,receiptBase,assertCheck,WIDTHS,PAGE_PATH,run};
