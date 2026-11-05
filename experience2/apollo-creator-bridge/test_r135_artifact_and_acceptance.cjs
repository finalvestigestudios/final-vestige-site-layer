'use strict';
/**
 * R135 read-only source and deterministic artifact regression tests.
 * These do NOT substitute for the R134 genuine-navigation Playwright/axe run.
 * Execute from a complete checkout: node --test experience2/apollo-creator-bridge/test_r135_artifact_and_acceptance.cjs
 */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const crypto=require('node:crypto');
const vm=require('node:vm');
const http=require('node:http');
const {build}=require('./r133_build_research_desk_preview.cjs');
const {responseServer,receiptBase,WIDTHS,PAGE_PATH}=require('./r134_actual_page_browser_acceptance.cjs');
const {auditRoute}=require('./r129_creator_route_gate.cjs');
const SHA=x=>crypto.createHash('sha256').update(x).digest('hex');
const RUNNER=path.join(__dirname,'r134_actual_page_browser_acceptance.cjs');
const LANDING=path.join(__dirname,'landing-preview.html');
function buildPair(){
 const home=fs.mkdtempSync(path.join(os.tmpdir(),'fv-r135-double-build-'));
 try{
  const first=build({outDir:path.join(home,'first')});
  const second=build({outDir:path.join(home,'replay')});
  const a=fs.readFileSync(first.output,'utf8'),b=fs.readFileSync(second.output,'utf8');
  return {a,b,manifestA:first.manifest,manifestB:second.manifest};
 }finally{fs.rmSync(home,{recursive:true,force:true});}
}
test('R135 runner parses in native Node and remains explicitly staging-only',()=>{
 const src=fs.readFileSync(RUNNER,'utf8');
 assert.doesNotThrow(()=>new vm.Script(src,{filename:RUNNER}));
 assert.equal(receiptBase().release,'STAGING_HOLD');
 assert.equal(receiptBase().offer,'NOT_VERIFIED');
 assert.equal(receiptBase().net_revenue,'NOT_OBSERVABLE');
});
test('full source-controlled Research Desk builds produce identical artifacts',()=>{
 const p=buildPair();
 assert.equal(p.a,p.b);
 assert.deepEqual(p.manifestA,p.manifestB);
 assert.equal(p.manifestA.artifact_sha256,SHA(p.a));
 assert.equal(p.manifestB.artifact_sha256,SHA(p.b));
});
test('artifact retains 6 source-only NASA photo links and a single H1',()=>{
 const p=buildPair(),html=p.a;
 assert.equal((html.match(/<a\s[^>]*href="https:\/\/www\.nasa\.gov\/image-detail\//g)||[]).length,6);
 assert.equal((html.match(/<h1\b/g)||[]).length,1);
 assert.match(html,/Source custody:/);
 assert.match(html,/All six photographs require individual reuse review/);
 assert.doesNotMatch(html,/<(?:img|picture|iframe|form|video)\b/i);
});
test('no-JS native markup has six evidence records and search controls hidden',()=>{
 const html=buildPair().a;
 assert.equal((html.match(/<article\b[^>]*data-fvx-record\b/g)||[]).length,6);
 assert.match(html,/data-fvx-tools hidden/);
 assert.match(html,/data-fvx-clear hidden/);
 assert.equal((html.match(/<details\b/g)||[]).length,6);
});
test('original Apollo page has exactly one free classroom CTA; no assumed sale',()=>{
 const a=auditRoute(fs.readFileSync(LANDING,'utf8'));
 assert.equal(a.status,'PASS',a.errors.join('; '));
 assert.equal(a.primary_cta_count,1);
 assert.equal(a.commerce_status,'NO_VERIFIED_PAID_OFFER_OR_MERCHANT');
 assert.equal(a.attribution_status,'UNOBSERVABLE_NOT_A_SALE');
});
test('acceptance suite covers authentic keyboard, touch, print, privacy and metrics',()=>{
 const s=fs.readFileSync(RUNNER,'utf8');
 for(const x of ['TWO_INDEPENDENT_BUILDS_IDENTICAL','MANIFEST_MATCHES_EXACT_ARTIFACT',
  "page.keyboard.press('Tab')",'.tap()','noJsPage.pdf(',
  'PRINT_NO_JS_SIX_SOURCE_RECORDS','_NO_UNEXPECTED_CLIENT_STORAGE',
  '_SOURCE_LINK_PRIVACY','PerformanceObserver','axe.run(document']){
  assert.ok(s.includes(x),'missing acceptance contract '+x);
 }
 assert.deepEqual(WIDTHS,[320,360,390,768,1440,1920]);
});
test('R135 never treats local browser metrics as production traffic or revenue',()=>{
 const r=receiptBase();
 assert.equal(r.browser_acceptance,'NOT_ESTABLISHED');
 assert.equal(r.rights,'0_OF_6_CLEARED');
 assert.deepEqual(r.metrics,{});
 assert.deepEqual(r.axe,{});
});
test('HTTP staging service is only served on exact isolated path',async()=>{
 const server=responseServer('<!doctype html><title>R135 fixture</title>');
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
 const base='http://127.0.0.1:'+server.address().port;
 const get=route=>new Promise((resolve,reject)=>http.get(base+route,res=>{
  let data='';res.setEncoding('utf8');res.on('data',x=>data+=x);
  res.on('end',()=>resolve({status:res.statusCode,data,headers:res.headers}));
 }).on('error',reject));
 try{
  const ok=await get(PAGE_PATH),denied=await get('/wp-admin');
  assert.equal(ok.status,200);assert.equal(ok.headers['cache-control'],'no-store');
  assert.equal(ok.headers['x-robots-tag'],'noindex, nofollow, noarchive');
  assert.equal(denied.status,404);
 }finally{await new Promise(r=>server.close(r));}
});
