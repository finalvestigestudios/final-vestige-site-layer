'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const http=require('node:http');
const {responseServer,receiptBase,assertCheck,WIDTHS,PAGE_PATH}=require('./r134_actual_page_browser_acceptance.cjs');
async function fixture(html,callback){
 const server=responseServer(html);
 await new Promise((resolve,reject)=>{
  server.once('error',reject);server.listen(0,'127.0.0.1',resolve);
 });
 const base='http://127.0.0.1:'+server.address().port;
 const get=(route)=>new Promise((resolve,reject)=>{
  http.get(base+route,r=>{let body='';r.setEncoding('utf8');r.on('data',x=>body+=x);
   r.on('end',()=>resolve({status:r.statusCode,body,headers:r.headers}));}).on('error',reject);
 });
 try{return await callback(get);}finally{await new Promise(r=>server.close(()=>r()));}
}
test('viewport matrix includes constrained mobile and large desktop widths',()=>{
 assert.deepEqual(WIDTHS,[320,360,390,768,1440,1920]);
});
test('staging receipt fails closed and never asserts revenue or image clearance',()=>{
 const r=receiptBase();
 assert.equal(r.release,'STAGING_HOLD');
 assert.equal(r.browser_acceptance,'NOT_ESTABLISHED');
 assert.equal(r.rights,'0_OF_6_CLEARED');
 assert.equal(r.offer,'NOT_VERIFIED');
 assert.equal(r.net_revenue,'NOT_OBSERVABLE');
});
test('named failures become visible and prevent release success',()=>{
 const r=receiptBase();
 assertCheck(r,'SIX_RECORDS',false,{actual:5});
 assert.equal(r.checks[0].pass,false);
 assert.match(r.errors[0],/SIX_RECORDS/);
 assertCheck(r,'HTTP_200',true,200);
 assert.equal(r.checks.length,2);
 assert.equal(r.errors.length,1);
});
test('actual HTTP server returns the exact provided HTML, never injected DOM',async()=>{
 const html='<!doctype html><h1>Research Desk test</h1>\n';
 await fixture(html,async get=>{
  const r=await get(PAGE_PATH);
  assert.equal(r.status,200);assert.equal(r.body,html);
  assert.match(r.headers['content-type'],/text\/html/);
  assert.equal(r.headers['x-robots-tag'],'noindex, nofollow, noarchive');
  assert.equal(r.headers['referrer-policy'],'no-referrer');
  assert.equal(r.headers['cache-control'],'no-store');
 });
});
test('server refuses unrelated and production-like routes',async()=>{
 await fixture('<h1>Staging</h1>',async get=>{
  for(const route of ['/','/wp-admin','/apollo/other.html']){
   const r=await get(route);
   assert.equal(r.status,404);assert.equal(r.body,'Not found');
  }
 });
});
test('plain HTTP server adds explicit nosniff header',async()=>{
 await fixture('ok',async get=>{
  const r=await get(PAGE_PATH);
  assert.equal(r.headers['x-content-type-options'],'nosniff');
 });
});
test('canonical staging path is not a public WP route',()=>{
 assert.equal(PAGE_PATH,'/apollo/r134-preview.html');
 assert.equal(PAGE_PATH.startsWith('/wp-'),false);
});
test('no tests activate merchant, signup, analytics or content posting',()=>{
 const r=receiptBase();
 assert.equal(r.checks.length,0);
 assert.equal(r.screenshots.length,0);
 assert.equal(r.metrics&&Object.keys(r.metrics).length,0);
});
