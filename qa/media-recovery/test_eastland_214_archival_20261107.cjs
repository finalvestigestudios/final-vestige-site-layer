'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {verify}=require('./validate_eastland_214_archival_20261107.cjs');
const src=JSON.parse(fs.readFileSync(path.join(__dirname,'eastland_214_six_sources_20261107.json'),'utf8'));
let checked=0;
function test(label,fn){fn();checked++;console.log('PASS '+label)}
function reject(label,mutate){
 test(label,()=>{const a=JSON.parse(JSON.stringify(src));mutate(a);const r=verify(a);assert.equal(r.pass,false,'should reject '+label);assert.ok(r.errors.length);});
}
test('clean canonical audit',()=>assert.deepEqual(verify(src),{pass:true,errors:[]}));
reject('false 42 failures',a=>a.performance.reported_42_broken_guest_verified=true);
reject('fabricated 76 percent',a=>a.performance.reduced_transfer_76_percent_measured=true);
reject('fabricated wire bytes',a=>a.performance.wire_bytes=1234);
reject('fabricated image status',a=>a.slots[0].actual_browser.http_status=200);
reject('retriever 404 wrongly counted as origin',a=>a.slots[0].retriever.origin_http_status=404);
reject('wrong original URL',a=>a.slots[1].stored_source_url+='?fake=1');
reject('extra image',a=>a.slots.push(a.slots[0]));
reject('missing image',a=>a.slots.pop());
reject('image caching unauthorized',a=>a.slots[2].can_cache=true);
reject('WordPress upload unauthorized',a=>a.slots[3].can_upload_wp=true);
reject('WordPress write claimed',a=>a.production.wordpress_writes=1);
reject('unknown pixels guessed',a=>a.slots[4].authoritative_candidate.derivative_960_px={width:960,height:1317,status:'conditional_by_catalog'});
reject('475px original upscaled',a=>a.slots[2].authoritative_candidate.derivative_960_px.width=960);
reject('960px master stretched',a=>a.slots[1].authoritative_candidate.derivative_960_px.height=540);
reject('LOC chronology caution omitted',a=>a.slots[4].authoritative_candidate.source_note='no concern');
reject('1915 newspaper publication date omitted',a=>a.slots[3].authoritative_candidate.source_note='event date only');
reject('NARA event timing misrepresented',a=>a.slots[5].authoritative_candidate.source_note='taken during active rescue');
reject('source binary identity prematurely certified',a=>a.slots[5].source_binary_verified=true);
reject('catalog URL omitted',a=>a.slots[0].authoritative_candidate.catalog_url='');
console.log(`PASS ${checked}/${checked} cases`);
