#!/usr/bin/env node
/** EX2 isolated real Assembler frontend gate. Only call after verified Gutenberg
 * editor Save inside disposable loopback WordPress Playground. RELEASE HOLD.
 * Not WordPress.com hosting, real Jetpack, live page6, field CWV or manual WCAG.
 */
import assert from 'node:assert/strict';
import {correctIsolatedNavigation} from './assembler_nav_native_fixture.mjs';
import {createHash} from 'node:crypto';
import {readFile, readdir, mkdir} from 'node:fs/promises';
import {join, relative, resolve, sep} from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const sha=b=>createHash('sha256').update(b).digest('hex');
const loopback=(raw)=>{
  try {const u=new URL(raw);return u.protocol==='http:'&&['localhost','127.0.0.1','[::1]'].includes(u.hostname)&&Boolean(u.port)&&!u.username&&!u.password;}catch{return false;}
};
const mediaHost=(raw)=>{
  try {const u=new URL(raw);return u.protocol==='https:'&&['finalvestige.com','i0.wp.com'].includes(u.hostname)&&!u.username&&!u.password&&/\.(webp|png|jpe?g|svg)$/i.test(u.pathname);}catch{return false;}
};
const widths=[320,390,768,1440,1920];
async function walk(base,dir=base){
  const out=[];
  for(const d of await readdir(dir,{withFileTypes:true})){
    if(d.isSymbolicLink())throw new Error('Theme symlink denied');
    const f=join(dir,d.name);
    if(d.isDirectory())out.push(...await walk(base,f));
    else if(d.isFile())out.push(f);
    else throw new Error('Nonregular theme entry denied');
  }
  return out;
}
function themeVersion(css){
  const name=css.match(/^Theme Name:\s*(.+)$/mi)?.[1]?.trim();
  const version=css.match(/^Version:\s*(.+)$/mi)?.[1]?.trim();
  if(name!=='Assembler'||!version||!/^\d+\.\d+\.\d+$/.test(version))throw new Error('Invalid Assembler metadata');
  return version;
}
async function activateTheme(server,themeDirectory){
  const base=resolve(themeDirectory);
  const version=themeVersion(await readFile(join(base,'style.css'),'utf8'));
  const files=await walk(base);
  assert.ok(files.length>5&&files.length<900,'Unexpected theme file inventory');
  const root='/wordpress/wp-content/themes/assembler',dirs=new Set([root]);
  let bytes=0;
  for(const f of files){
    const parts=relative(base,f).split(sep);
    if(parts.some(x=>x==='..'||x==='.'||!x))throw new Error('Theme traversal denied');
    for(let i=1;i<parts.length;i++)dirs.add(root+'/'+parts.slice(0,i).join('/'));
    bytes+=(await readFile(f)).length;
  }
  assert.ok(bytes>1000&&bytes<30_000_000,'Unexpected theme bytes');
  for(const dir of [...dirs].sort((a,b)=>a.length-b.length))await server.playground.mkdir(dir);
  for(const f of files)await server.playground.writeFile(root+'/'+relative(base,f).split(sep).join('/'),await readFile(f));
  const php=`<?php require '/wordpress/wp-load.php'; switch_theme('assembler'); $t=wp_get_theme(); echo wp_json_encode(array('stylesheet'=>get_stylesheet(),'template'=>get_template(),'version'=>$t->get('Version'),'home'=>home_url('/')));`;
  const result=await server.playground.run({code:php});
  let obj;
  try {obj=JSON.parse(result.text);}catch{throw new Error('WordPress theme activation receipt invalid');}
  assert.equal(obj.stylesheet,'assembler');
  assert.equal(obj.template,'assembler');
  assert.equal(obj.version,version);
  assert.ok(loopback(obj.home));
  return {version,files:files.length,bytes,provenance:'WordPress.com free official Assembler download (not version-pinned)'};
}
function restrictNetwork(page,blocked){
  return page.route('**/*',route=>{
    const u=route.request().url();
    if(loopback(u)||mediaHost(u))return route.continue();
    try {blocked.add(new URL(u).hostname);}catch{blocked.add('[invalid]');}
    return route.abort();
  });
}
async function imageBodies(page){
  // HTTP bytes alone cannot establish that Chromium decoded the real image.
  // Force only archival img elements to load; do not change layout styles.
  const decoded=await page.locator('img').evaluateAll(async els=>Promise.all(
    els.map(async el=>{
      const initial=el.currentSrc||el.src;
      if(!/^https:\/\/(finalvestige\.com|i0\.wp\.com)\//.test(initial))return null;
      el.loading='eager';
      let decodeError=null,timer;
      try{
        await Promise.race([
          el.decode(),
          new Promise((_,reject)=>{timer=setTimeout(
            ()=>reject(new Error('image decode timeout')),20000);})
        ]);
      }catch(e){decodeError=String(e).slice(0,160);}
      finally{clearTimeout(timer);}
      return {url:el.currentSrc||el.src,complete:el.complete,
        width:el.naturalWidth,height:el.naturalHeight,decode_error:decodeError};
    })
  ));
  const entries=decoded.filter(x=>x&&mediaHost(x.url));
  if(entries.length<2)throw new Error('Missing two archival browser image candidates');
  const cache=new Map(),rows=[];
  for(const entry of entries){
    let http=cache.get(entry.url);
    if(!http){
      const response=await page.request.get(entry.url,{
        maxRedirects:2,timeout:30000,failOnStatusCode:false
      });
      const body=await response.body();
      http={status:response.status(),
        mime:(response.headers()['content-type']||'').split(';')[0],
        bytes:body.byteLength,sha256:sha(body)};
      cache.set(entry.url,http);
    }
    const pass=entry.complete&&entry.width>0&&entry.height>0&&
      !entry.decode_error&&http.status===200&&
      http.mime.startsWith('image/')&&http.bytes>100;
    rows.push({host:new URL(entry.url).hostname,
      source_file:new URL(entry.url).pathname.split('/').pop(),
      ...http,decoded:entry.complete&&entry.width>0&&entry.height>0&&
      !entry.decode_error,natural_width:entry.width,natural_height:entry.height,
      decode_error:entry.decode_error,pass});
  }
  if(new Set(rows.map(x=>x.source_file)).size<2)
    throw new Error('Missing distinct Apollo and Franklin media sources');
  if(rows.some(x=>!x.pass))
    throw new Error('Archival image byte or browser decode failure: '+
      JSON.stringify(rows.filter(x=>!x.pass)));
  return rows;
}
// The builder appends all four executable sources AFTER the closed flagship
// root. They are Gutenberg custom HTML block siblings, not descendants of
// [data-fv-home-flagship]. Never mistake a root-scoped count of zero for
// evidence that WordPress stripped source JS. Still fail closed if any are
// truly absent, duplicated, reordered, or replaced in the rendered document.
const EXPECTED_RENDERED_SCRIPTS=Object.freeze([
  'flagship.js','observer-lab.js','chronicle-lens.js','reading-trail.js'
]);
export function renderedScriptNames(documentScope=globalThis.document){
  return [...documentScope.querySelectorAll('script[data-fv-source]')]
    .map(s=>s.getAttribute('data-fv-source'));
}
export function assertRenderedScriptNames(names){
  assert.deepEqual(names,EXPECTED_RENDERED_SCRIPTS,
    'Missing, duplicated, reordered or unauthorized rendered flagship JS');
}
async function checkView(page,width,axePath,outputDirectory){
  await page.setViewportSize({width,height:900});
  await page.goto(page.stageUrl,{waitUntil:'domcontentloaded',timeout:90000});
  await page.locator('[data-fv-home-flagship]').waitFor({timeout:30000});
  await page.evaluate(()=>document.fonts?.ready);
  const state=await page.evaluate(()=>{
    const root=document.querySelector('[data-fv-home-flagship]');
    const links=[...root.querySelectorAll('.fv-hf__chapter-nav a[href^="#"]')];
    return {chapter_links:links.length,chapter_targets:links.filter(a=>document.getElementById(a.getAttribute('href').slice(1))).length,
      margins:document.querySelectorAll('.fv-margin-strip__item').length,
      focus:(document.body.innerText.match(/Focus Fieldbook/g)||[]).length,
      overflow:document.documentElement.scrollWidth>innerWidth+1,
      main:!!root.querySelector('main'),h1:!!root.querySelector('h1'),
      // Executable sources are Gutenberg siblings AFTER the flagship root.
      // Inspect them independently at DOCUMENT scope below.
      // The styling must exist in the SAVED Gutenberg source; page.addStyleTag
      // (except axe-core JS below) must never be used as a fake release pass.
      saved_layout_styles:document.querySelectorAll('style[data-fv-stage-only="assembler-saved-layout"]').length,
      root_width:Math.round(root.getBoundingClientRect().width),
      viewport_width:innerWidth,
      margins_region:(()=>{
        const region=document.querySelector('.fv-margin-strip__window');
        if(!region)return {present:false};
        const first=region.querySelector('.fv-margin-strip__item');
        return {present:true,role:region.getAttribute('role'),
          label:region.getAttribute('aria-label'),tabindex:region.getAttribute('tabindex'),
          item_count:region.querySelectorAll('.fv-margin-strip__item').length,
          overflow_y:getComputedStyle(region).overflowY,
          first_position:first?getComputedStyle(first).position:'missing'};
      })()};
  });
  const sourceScripts=await page.evaluate(renderedScriptNames);
  state.inline_scripts=sourceScripts.length;
  state.inline_script_names=sourceScripts;
  // The receipt is safe metadata only: file basenames, no source, credentials,
  // subscriber data, or DOM content. It survives later accessibility failure.
  console.log(JSON.stringify({event:'EX2_RENDERED_SCRIPT_CUSTODY',width,
    names:sourceScripts}));
  // Capture SAVED WordPress layout before any assertion or axe failure.
  // These are not browser-overlay corrected screenshots.
  await mkdir(outputDirectory,{recursive:true});
  await page.screenshot({path:join(outputDirectory,`assembler-${width}.png`),
    animations:'disabled',fullPage:false,timeout:30000});
  if(width===1440)await page.screenshot({
    path:join(outputDirectory,'assembler-1440-fullpage.png'),
    animations:'disabled',fullPage:true,timeout:60000
  });
  assert.equal(state.chapter_links,7);
  assert.equal(state.chapter_targets,7);
  assert.equal(state.margins,72);
  assert.ok(state.focus>=1);
  assert.equal(state.overflow,false,`Horizontal overflow at ${width}`);
  assert.equal(state.main,true);assert.equal(state.h1,true);
  assertRenderedScriptNames(sourceScripts);
  assert.equal(state.saved_layout_styles,1,'Assembler styles must be persisted in Gutenberg');
  assert.ok(state.root_width>=width-2 && state.root_width<=width+2,
    `SAVED Assembler full-bleed canvas failed at ${width}: ${state.root_width}px (620px theme baseline)`);
  assert.deepEqual(state.margins_region,{
    present:true,role:'region',label:'72 synthetic historical fragments',
    tabindex:'0',item_count:72,overflow_y:'auto',first_position:'static'
  },'Synthetic Margins must remain readable and keyboard scrollable without JS');
  // Preserve HTTP-body AND actual browser decode receipts if axe fails.
  // Media re-fetched only at desktop to avoid 5x redundant transfers.
  const media=width===1440?await imageBodies(page):[];
  if(media.length)console.log(JSON.stringify({event:'EX2_MEDIA_BODY_AND_BROWSER_DECODE',width,media}));
  await page.addScriptTag({path:axePath});
  const scans=await page.evaluate(async()=>{
    if(!window.axe)throw new Error('axe unavailable: fail closed');
    const opts={runOnly:{type:'tag',
      values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}};
    const runBounded=async (scope)=>{
      let timer;
      try {
        const r=await Promise.race([
          window.axe.run(scope,opts),
          new Promise((_,reject)=>{timer=setTimeout(
            ()=>reject(new Error('axe scan exceeded 40s')),40000);})
        ]);
        return r.violations.map(v=>({id:v.id,impact:v.impact,
          nodes:v.nodes.length,selectors:v.nodes.slice(0,3).map(n=>n.target)}));
      } finally {clearTimeout(timer);}
    };
    // A component-only axe pass can MISS the 72 synthetic Margins fragments,
    // Jetpack stub and Assembler navigation. Require BOTH scoped and full DOM.
    const flagship=await runBounded(document.querySelector('[data-fv-home-flagship]'));
    const whole_document=await runBounded(document);
    return {flagship,whole_document};
  });
  if(scans.flagship.length || scans.whole_document.length)
    throw new Error(`Automated axe findings at ${width}: ${JSON.stringify(scans)}`);
  return {width,state,axe_violations:0,media};
}
// Continue independent viewports after a real defect so visual evidence is
// collected for the whole page. Return failures explicitly; callers MUST
// throw after the matrix and must not translate a partial pass into a pass.
export async function collectViewportEvidence(viewports,check){
  const completed=[],failures=[];
  for(const width of viewports){
    try{completed.push(await check(width));}
    catch(e){failures.push({width,reason:String(e?.message||e).slice(0,1500)});}
  }
  return {completed,failures};
}
export async function runAssemblerPreview({server,browser,context,draftId,themeDirectory,outputDirectory}){
  assert.ok(Number.isInteger(draftId)&&draftId>0);
  assert.ok(loopback(server.serverUrl));
  const theme=await activateTheme(server,themeDirectory);
  await mkdir(outputDirectory,{recursive:true});
  const blocked=new Set(),page=await context.newPage();
  page.stageUrl=new URL(`/?page_id=${draftId}&preview=true`,server.serverUrl).href;
  if(!loopback(page.stageUrl))throw new Error('Unsafe preview URL');
  await restrictNetwork(page,blocked);
  const axePath=require.resolve('axe-core/axe.min.js');
  // The real unmodified vendor theme has a serious list-semantic defect in
  // its default fallback navigation. Measure and preserve that baseline first.
  // Configure a real native WP navigation + template-part override ONLY in this
  // disposable loopback Playground, never by rewriting browser DOM or source.
  // Full-document axe remains enabled for the entire five-width matrix.
  const navigationFixture=await correctIsolatedNavigation({server,page,axePath,outputDirectory});
  const {completed:responsive,failures:viewportFailures}=await collectViewportEvidence(
    widths,width=>checkView(page,width,axePath,outputDirectory));
  // A serious Assembler theme issue at one breakpoint must not erase screenshots
  // or the media decode results from every later breakpoint. All failures are
  // kept as explicit HOLDs; there is no suppression of failed axe rules.
  console.log(JSON.stringify({event:'EX2_VIEWPORT_EVIDENCE_MATRIX',
    requested:widths,completed:responsive.map(x=>x.width),failures:viewportFailures}));
  await page.setViewportSize({width:720,height:450});
  await page.goto(page.stageUrl,{waitUntil:'domcontentloaded',timeout:90000});
  const reflow=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,
    chapters:document.querySelectorAll('.fv-hf__chapter-nav a').length}));
  assert.equal(reflow.overflow,false,'200% desktop CSS viewport equivalent overflow');
  assert.equal(reflow.chapters,7);
  await page.close();
  const noContext=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
  await noContext.addCookies(await context.cookies());
  const noPage=await noContext.newPage();
  await restrictNetwork(noPage,blocked);
  await noPage.goto(new URL(`/?page_id=${draftId}&preview=true`,server.serverUrl).href,
    {waitUntil:'domcontentloaded',timeout:90000});
  const noJS=await noPage.evaluate(()=>{
    const root=document.querySelector('[data-fv-home-flagship]');
    const region=document.querySelector('.fv-margin-strip__window');
    return {chapters:document.querySelectorAll('.fv-hf__chapter-nav a').length,
      margins:document.querySelectorAll('.fv-margin-strip__item').length,
      h1:document.querySelectorAll('[data-fv-home-flagship] h1').length,
      saved_layout_styles:document.querySelectorAll('style[data-fv-stage-only="assembler-saved-layout"]').length,
      canvas_width:Math.round(root?.getBoundingClientRect().width || 0),
      region_tabindex:region?.getAttribute('tabindex'),
      region_role:region?.getAttribute('role')};
  });
  // No-JS photo and computed readability are from SAVED CSS, not an overlay.
  await noPage.screenshot({path:join(outputDirectory,'assembler-390-nojs.png'),
    animations:'disabled',fullPage:false,timeout:30000});
  const noJSCSS=await noPage.evaluate(()=>{
    const item=document.querySelector('.fv-margin-strip__item');
    const windowEl=document.querySelector('.fv-margin-strip__window');
    return {item_position:item?getComputedStyle(item).position:null,
      item_opacity:item?getComputedStyle(item).opacity:null,
      window_overflow:windowEl?getComputedStyle(windowEl).overflowY:null,
      horizontal_overflow:document.documentElement.scrollWidth>innerWidth+1};
  });
  assert.deepEqual(noJSCSS,{item_position:'static',item_opacity:'1',
    window_overflow:'auto',horizontal_overflow:false},
    'CSS must keep all 72 synthetic records readable without JavaScript');
  assert.deepEqual(noJS,{chapters:7,margins:72,h1:1,
    saved_layout_styles:1,canvas_width:390,region_tabindex:'0',region_role:'region'});
  await noContext.close();
  if(viewportFailures.length)
    throw new Error('ISOLATED_ASSEMBLER_VIEWPORT_ADMISSION_HOLD '+
      JSON.stringify(viewportFailures));
  return {type:'ISOLATED_WP_ASSEMBLER_RENDER_SYNTHETIC_ONLY',release:'HOLD',theme,
    responsive,navigation_fixture:navigationFixture,zoom_200_percent_equivalent:reflow,no_js:noJS,blocked_hosts:[...blocked].sort(),
    limits:['synthetic Margins are not production historical records','stage CSS is not proposed production CSS',
      'not WP.com Atomic parity','the local Assembler header is intentionally overridden via native WP template part; unmodified-vendor axe remains FAIL','not real Jetpack','not real hosted page6 content','not physical browser zoom','not manual WCAG 2.2 AA','not field Core Web Vitals']};
}
// Export a strictly read-only browser-media routine for mock adversarial tests.
export {imageBodies};
function selfTest(){
  for(const u of ['http://localhost:3211/','http://127.0.0.1:9473/'])assert.ok(loopback(u));
  for(const u of ['https://finalvestige.com/','http://localhost/','http://localhost:3211@evil.com/'])assert.ok(!loopback(u));
  assert.ok(mediaHost('https://finalvestige.com/wp-content/uploads/f.jpg'));
  assert.ok(mediaHost('https://i0.wp.com/finalvestige.com/test.webp?fit=300'));
  for(const u of ['http://finalvestige.com/foo.jpg','https://evil.example/test.png','https://finalvestige.com/wp-admin/'])assert.ok(!mediaHost(u));
  assert.equal(themeVersion('Theme Name: Assembler\nVersion: 0.0.126\n'),'0.0.126');
  assert.throws(()=>themeVersion('Theme Name: Other\nVersion: 1.0.0\n'));
  console.log(JSON.stringify({self_test:'PASS',checks:12,network_used:false,release:'HOLD'}));
}
if(process.argv.includes('--self-test'))selfTest();
