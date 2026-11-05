/**
 * Read-only, anonymous, live WordPress/Assembler Focus-funnel acceptance.
 *
 * PROD IS READ-ONLY: opens GET pages; never logs in, posts a form, clicks
 * checkout, activates a plugin, sets a cookie, or touches WordPress REST writes.
 * Unlike the private-Playground exact-source harness, this probes WHAT PUBLIC
 * VISITORS RECEIVE from the already-published site.
 *
 * Run on a trusted checkout:
 *   npm install --no-save playwright axe-core   # only if not already installed
 *   node experience2/home-flagship/qa/release-candidate/live_public_focus_browser_gate.mjs
 * Requires locally installed Chromium (npx playwright install chromium if absent).
 * Exit 1 is a HOLD. Output is only a read-only local screenshot/JSON receipt.
 */
import assert from 'node:assert/strict';
import {mkdir,writeFile,readFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const require=createRequire(import.meta.url);
const ORIGIN='https://finalvestige.com';
const VIEWPORTS=[320,390,768,1279,1280,1440,1920];
const CHAPTERS=['fv-hf-chronicle','fv-hf-evidence','fv-hf-apollo',
  'fv-hf-franklin','fv-hf-malbone','fv-hf-inquiry','fv-hf-observer'];
const OUT=resolve(process.env.FV_EX2_EVIDENCE_DIR||'artifacts/ex2-live-focus-20261104');
const failures=[];
const receipt={kind:'ANONYMOUS_PUBLIC_BROWSER_NOT_PRIVATE_STAGING',
  date:new Date().toISOString(),site:ORIGIN,
  source:'WordPress.com publicly served finalvestige.com, not repository fixture',
  conclusions:'Lab observations only. Not field CWV or WordPress Playground qualification.',
  widths:[],no_js:{},focus:{},failures};

function fail(msg){failures.push(msg);}
function check(ok,msg){if(!ok) fail(msg);}
function pathOnly(raw){try {const u=new URL(raw,ORIGIN);return u.origin===ORIGIN?u.pathname:'external-host';}catch{return 'invalid-url';}}
function safeOrigin(raw){try{return new URL(raw).origin===ORIGIN;}catch{return false;}}
function viewportId(width){return String(width).padStart(4,'0');}
function focusSelectors(){
  return '.fv-site-header .fv-ebook-strip-wrap a[href*="/focus/"], '+
    '.fv-site-header .fv-nav-free-ebook a[href*="/focus/"]';
}
function validateFocusGeometry(rows,width,height){
  const visible=rows.filter(r=>r.visible);
  const onScreen=visible.filter(r=>r.box && r.box.y>=0 &&
    r.box.y+r.box.height<=height && r.box.x>=0 &&
    r.box.x+r.box.width<=width);
  return {visibleCount:visible.length,firstScreenCount:onScreen.length,
    hitCount:onScreen.filter(r=>r.hit && r.box.width>=44 && r.box.height>=44).length,
    modes:[...new Set(visible.map(r=>r.mode))]};
}
export {VIEWPORTS,CHAPTERS,validateFocusGeometry,pathOnly};

async function browserLib(){
  try{return await import('playwright');}
  catch(e){throw new Error('BLOCKER: playwright is unavailable (no PASS): '+e.message);}
}
async function axeFile(){
  try{return require.resolve('axe-core/axe.min.js');}
  catch(e){throw new Error('BLOCKER: axe-core absent; cannot claim WCAG automated check: '+e.message);}
}
async function createPage(browser,width,js=true){
  const context=await browser.newContext({
    viewport:{width,height:900},javaScriptEnabled:js,reducedMotion:'reduce',
    locale:'en-US',colorScheme:'dark',serviceWorkers:'block',acceptDownloads:false,
    ignoreHTTPSErrors:false});
  await context.clearCookies();
  const page=await context.newPage();
  await page.addInitScript(()=>{
    window.__fvLab={start:performance.now(),lcp:0,cls:0};
    if('PerformanceObserver' in window) {
      try{new PerformanceObserver(l=>{for(const e of l.getEntries()){
        window.__fvLab.lcp=e.startTime;
      }}).observe({type:'largest-contentful-paint',buffered:true});}catch{}
      try{new PerformanceObserver(l=>{for(const e of l.getEntries()){
        if(!e.hadRecentInput)window.__fvLab.cls+=e.value;
      }}).observe({type:'layout-shift',buffered:true});}catch{}
    }
  });
  const errors=[],images=[];
  page.on('pageerror',e=>errors.push(String(e).slice(0,200)));
  page.on('response',async r=>{
    if(!r.request().resourceType().includes('image'))return;
    const u=r.url();let bytes=null;
    try{if(r.status()===200)bytes=(await r.body()).length;}catch{}
    images.push({path:pathOnly(u),http:r.status(),bytes,firstParty:safeOrigin(u)});
  });
  return {context,page,errors,images};
}
async function navigatePublic(page,path){
  const response=await page.goto(ORIGIN+path,{waitUntil:'domcontentloaded',timeout:45000});
  assert.ok(response,'No HTTP response for '+path);
  check(response.status()===200,'HTTP '+response.status()+' at '+path);
  check(page.url().startsWith(ORIGIN+'/'),'Cross-origin redirect: '+path);
  // No submission, sign-in, or click instrumentation of any sort.
  return {status:response.status(),urlPath:pathOnly(page.url())};
}
async function chapterState(page,width,mode){
  const state=await page.evaluate(ids=>({
    chapterIds:ids.map(id=>({id,exists:!!document.getElementById(id)})),
    mainCount:document.querySelectorAll('main,[role="main"]').length,
    horizontalOverflow:document.documentElement.scrollWidth>innerWidth+2,
    title:document.title,
    visibleDialogs:[...document.querySelectorAll('[role="dialog"],dialog')].filter(n=>{
      const s=getComputedStyle(n); const r=n.getBoundingClientRect();
      return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0;
    }).length
  }),CHAPTERS);
  for(const id of state.chapterIds) check(id.exists,mode+' '+width+' missing '+id.id);
  check(state.mainCount===1,mode+' '+width+' expected exactly one accessible main');
  check(!state.horizontalOverflow,mode+' '+width+' horizontal overflow');
  check(state.visibleDialogs===0,mode+' '+width+' unexpected visible modal');
  return state;
}
async function focusGeometry(page){
  return page.locator(focusSelectors()).evaluateAll(anchors=>anchors.map(a=>{
    const box=a.getBoundingClientRect(),s=getComputedStyle(a);
    const parent=a.closest('.fv-ebook-strip-wrap,.fv-nav-free-ebook');
    const ps=parent?getComputedStyle(parent):null;
    const visible=s.display!=='none'&&s.visibility!=='hidden'&&
      (!ps||ps.display!=='none')&&box.width>0&&box.height>0;
    const x=box.left+box.width/2,y=box.top+box.height/2;
    const top=document.elementFromPoint(x,y);
    return {mode:parent?.classList.contains('fv-ebook-strip-wrap')?'strip':'nav',
      href:new URL(a.href).pathname,visible,
      box:{x:box.x,y:box.y,width:box.width,height:box.height},
      hit:!!top&&(top===a||a.contains(top))};
  }));
}
async function readImages(page,width){
  const imgs=page.locator('main img');
  const total=await imgs.count(),items=[];
  for(let i=0;i<Math.min(total,20);i++){
    const img=imgs.nth(i);
    try{await img.scrollIntoViewIfNeeded({timeout:7000});await img.evaluate(el=>{
      if(el.complete)return Promise.resolve();
      return new Promise(done=>{el.addEventListener('load',done,{once:true});
        el.addEventListener('error',done,{once:true});setTimeout(done,8000);});
    });}catch{}
    const row=await img.evaluate(el=>({
      alt:el.getAttribute('alt'),srcPath:el.currentSrc?new URL(el.currentSrc).pathname:null,
      complete:el.complete,naturalWidth:el.naturalWidth,naturalHeight:el.naturalHeight
    }));
    items.push(row);
    check(row.complete&&row.naturalWidth>0,'width '+width+' failed image: '+row.srcPath);
  }
  return {total,checked:items};
}
async function runWidth(browser,width,axeSource){
  const {context,page,errors,images}=await createPage(browser,width,true);
  const entry={width,js:true};
  try{
    entry.http=await navigatePublic(page,'/');
    await page.waitForTimeout(500);
    entry.dom=await chapterState(page,width,'JS');
    entry.links=await focusGeometry(page);
    entry.geo=validateFocusGeometry(entry.links,width,900);
    check(entry.geo.visibleCount>=1,'width '+width+' no visible Focus header CTA');
    check(entry.geo.hitCount>=1,'width '+width+' no first-screen >=44px unobstructed Focus CTA');
    if(width<1280){
      check(entry.geo.modes.includes('strip'),'width '+width+' mobile strip not visible');
    }else{
      check(entry.geo.modes.includes('nav'),'width '+width+' desktop nav CTA not visible');
    }
    for(const l of entry.links)check(l.href==='/focus/','Incorrect Focus URL at '+width+':'+l.href);
    entry.images=await readImages(page,width);
    await page.evaluate(()=>scrollTo(0,0));
    await page.screenshot({path:resolve(OUT,'published-'+viewportId(width)+'.png'),
      fullPage:true,animations:'disabled'});
    // Inject into current COMPLETE public document; no 'partial component' axe PASS.
    await page.addScriptTag({path:axeSource});
    entry.axe=await page.evaluate(async()=>{
      const a=await window.axe.run(document,{runOnly:{type:'tag',
        values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
      return {violations:a.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})),
        passes:a.passes.length,incomplete:a.incomplete.length};
    });
    check(entry.axe.violations.length===0,'width '+width+' full-doc axe violations '+JSON.stringify(entry.axe.violations));
    entry.lab=await page.evaluate(()=>({
      navigation:performance.getEntriesByType('navigation').map(n=>({
        responseStart:n.responseStart,domContentLoaded:n.domContentLoadedEventEnd,
        loadEventEnd:n.loadEventEnd})),
      lcp:window.__fvLab?.lcp??null,cls:window.__fvLab?.cls??null,
      note:'Browser lab, NOT Lighthouse or p75 field CWV'}));
    entry.imageHttp=images;
    check(errors.length===0,'width '+width+' page exceptions: '+errors.join('; '));
    entry.pageErrors=errors;
    // Actual CTA GET, never submit a Jetpack form or click paid checkout.
    if(width===390 || width===1440){
      const chosen=page.locator(focusSelectors()).filter({visible:true}).first();
      await chosen.click({timeout:12000});
      await page.waitForURL(u=>u.origin===ORIGIN&&u.pathname==='/focus/',{timeout:25000});
      entry.focusClick={arrived:pathOnly(page.url()),
        jetpackPresent:await page.locator('[class*="jetpack"],form[action*="subscribe"],.wp-block-jetpack-subscriptions').count()>0,
        fieldbookMention:await page.getByText('Seven Day Focus Fieldbook',{exact:false}).count()>0};
      check(entry.focusClick.jetpackPresent,'width '+width+' /focus/ missing Jetpack evidence');
      await page.screenshot({path:resolve(OUT,'focus-'+viewportId(width)+'.png'),
        fullPage:true,animations:'disabled'});
    }
  }catch(e){fail('width '+width+' fatal: '+String(e).slice(0,500));entry.fatal=String(e);}
  finally{await context.close();receipt.widths.push(entry);}
}
async function noJs(browser){
  const width=390,{context,page,errors}=await createPage(browser,width,false);
  try{
    const http=await navigatePublic(page,'/');
    const dom=await chapterState(page,width,'NO-JS');
    const links=await focusGeometry(page),geo=validateFocusGeometry(links,width,900);
    check(geo.hitCount>=1,'NO-JS mobile Focus CTA hidden/blocked');
    receipt.no_js={http,dom,geo,errors};
    await page.screenshot({path:resolve(OUT,'published-nojs-0390.png'),
      fullPage:true,animations:'disabled'});
    check(errors.length===0,'No-JS page exceptions');
  }catch(e){fail('NO-JS fatal: '+String(e));receipt.no_js.fatal=String(e);}
  finally{await context.close();}
}
async function main(){
  await mkdir(OUT,{recursive:true});
  let browser;
  try{
    const pw=await browserLib(),axeSource=await axeFile();
    browser=await pw.chromium.launch({headless:true});
    for(const width of VIEWPORTS)await runWidth(browser,width,axeSource);
    await noJs(browser);
  }catch(e){fail('SETUP/BROWSER BLOCKER '+String(e));}
  finally{
    try{await browser?.close();}catch{}
    receipt.finished=new Date().toISOString();
    receipt.status=failures.length?'HOLD':'BROWSER_GATE_PASSED_NOT_RELEASE_APPROVAL';
    await writeFile(resolve(OUT,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');
    console.log('Final Vestige live anonymous browser gate: '+receipt.status);
    console.log('Evidence: '+OUT+'/receipt.json');
    for(const err of failures)console.error('HOLD: '+err);
    if(failures.length)process.exitCode=1;
  }
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))await main();
