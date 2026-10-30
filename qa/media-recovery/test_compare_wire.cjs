'use strict';
const{test}=require('node:test'),assert=require('node:assert/strict');
const{inspectRun,compareWireRuns}=require('./compare_wire_core.cjs');
function fixture(t='2026-10-30T18:00:00.000Z',numbers=[5000,5000]){
 const url='https://finalvestige.com/example/';
 return{schema_version:1,probe_version:2,created:t,mode:'priority',viewport:'390x844',
 probe:'logged-out Chrome CDP, no npm dependencies or WordPress writes',
 browser_product:'Chrome/142.0.1.0',
 run_profile:{cache_disabled:true,service_worker_bypassed:true,scroll_step_px:720,scroll_wait_ms:220,settle_wait_ms:1000},
 requested_pages:1,verified_pages:1,pages:[{post_id:123,url,document_url:url,page_result:'inspected_browser',
 document_network_failures:[],stored_image_count:2,rendered_image_count:2,
 stored_images:numbers.map((n,i)=>({image_key:'123:'+i,result:'loaded_in_probe_browser',
 verified_broken_in_browser:false,natural_width:960,request_url:'https://example.edu/img'+i+'.jpg',http_status:200,transfer_bytes:n})),
 network_images:numbers.map((n,i)=>({url:'https://example.edu/img'+i+'.jpg',status:200,mime_type:'image/jpeg',
 encoded_data_length:n,error:null,from_disk_cache:false,from_service_worker:false,was_cached:false})),
 image_wire_bytes_total:numbers.reduce((a,b)=>a+b,0)}]};
}
const a=()=>fixture(),b=()=>fixture('2026-10-30T19:00:00.000Z',[1200,1200]);
test('SYNTHETIC 10000 to 2400 bytes is 76%, not a live observation',()=>{const r=compareWireRuns(a(),b());assert.equal(r.reduction_percent,76);assert.equal(r.comparable,true)});
test('reject unversioned run',()=>{let r=a();delete r.probe_version;assert.equal(inspectRun(r).ok,false)});
test('reject missing cache policy',()=>{let r=a();delete r.run_profile;assert.equal(inspectRun(r).ok,false)});
test('reject changed viewport',()=>{let r=b();r.viewport='1440x900';assert.equal(compareWireRuns(a(),r).comparable,false)});
test('reject changed post',()=>{let r=b();r.pages[0].url='https://finalvestige.com/other/';assert.equal(compareWireRuns(a(),r).comparable,false)});
test('reject changed image slot',()=>{let r=b();r.pages[0].stored_images[0].image_key='123:99';assert.equal(compareWireRuns(a(),r).comparable,false)});
test('reject lazy incomplete image',()=>{let r=a();r.pages[0].stored_images[0].result='pending_lazy_or_incomplete';assert.equal(inspectRun(r).ok,false)});
test('reject broken baseline',()=>{let r=a();r.pages[0].stored_images[0].result='confirmed_broken_in_probe_browser';assert.equal(compareWireRuns(r,b()).comparable,false)});
test('reject invented total',()=>{let r=a();r.pages[0].image_wire_bytes_total=1;assert.equal(inspectRun(r).ok,false)});
test('reject 404',()=>{let r=b();r.pages[0].network_images[0].status=404;assert.equal(inspectRun(r).ok,false)});
test('reject cache hit',()=>{let r=b();r.pages[0].network_images[0].was_cached=true;assert.equal(inspectRun(r).ok,false)});
test('reject MIME mismatch',()=>{let r=b();r.pages[0].network_images[0].mime_type='text/html';assert.equal(inspectRun(r).ok,false)});
test('reject zero bytes',()=>{let r=b();r.pages[0].network_images[0].encoded_data_length=0;assert.equal(inspectRun(r).ok,false)});
test('reject browser version drift',()=>{let r=b();r.browser_product='Chrome/143.0.0.0';assert.equal(compareWireRuns(a(),r).comparable,false)});
test('reject incomplete page set',()=>{let r=a();r.requested_pages=2;assert.equal(inspectRun(r).ok,false)});
test('reject backward run chronology',()=>{let r=fixture('2026-10-30T17:00:00.000Z',[1200,1200]);assert.equal(compareWireRuns(a(),r).comparable,false)});
test('negative saving means heavier page',()=>{let r=fixture('2026-10-30T19:00:00.000Z',[7500,7500]);assert.equal(compareWireRuns(a(),r).reduction_percent,-50)});

