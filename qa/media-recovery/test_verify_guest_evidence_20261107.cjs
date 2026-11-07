'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {inspectManifest,inspectGuestEvidence}=require('./verify_guest_evidence_20261107.cjs');
const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'p0_guest_evidence_manifest_20261107.json'),'utf8'));
const clone=x=>JSON.parse(JSON.stringify(x));
const check=(name,transform,valid=false)=>test(name,()=>{const x=clone(manifest);transform(x);assert.equal(inspectManifest(x).ok,valid);});
test('six read-only WordPress source slots pass',()=>assert.equal(inspectManifest(manifest).ok,true));
check('missing slot fails',x=>x.rows.pop());
check('faked HTTP status fails',x=>x.rows[0].browser_http_status=404);
check('faked broken claim fails',x=>x.rows[0].visitor_broken=true);
check('faked 76 percent fails',x=>x.claimed_76pct_wire_savings='MEASURED');
check('permission claim fails',x=>x.rows[0].candidates[0].rehosting_authorized=true);
check('unsafe image upscaling fails',x=>x.rows[0].candidates[0].conditional_preview_px=[960,720]);
check('distorted preview fails',x=>x.rows[0].candidates[0].conditional_preview_px=[819,400]);
check('oversize preview fails',x=>x.rows[0].candidates[1].conditional_preview_px=[1000,960]);
check('invented visitor network bytes fail',x=>x.rows[0].visitor_transfer_bytes=100);
check('duplicate source slot fails',x=>x.rows[1].slot=x.rows[0].slot);
test('without guest capture reports explicit unresolved state',()=>{const r=inspectGuestEvidence(manifest);assert.equal(r.ok,true);assert.equal(r.sitewide_weight_reduction_pct,null);assert.equal(r.confirmed_broken_count,null);});
const s=(phase,id,encoded,http,nat)=>({
 id,phase,page_url:manifest.rows[0].page_url, user_agent:'synthetic-test-UA',browser_version:'test-Chromium',
 network_profile:'test-4G',viewport:{width:390,height:844,dpr:2},cache_disabled:true,full_scroll:true,lazy_settled:true,requests_complete:true,
 dom_image_count:1,dom_images:[{slot:'285:5',current_src:manifest.rows[0].published_src,natural_width:nat,natural_height:nat?300:0,complete:true,visible:true,screenshot_ref:'synthetic-not-real.png',request_id:'r1'}],
 image_requests:[{id:'r1',url:manifest.rows[0].published_src,resource_type:'image',http_status:http,mime:http===404?'text/html':'image/jpeg',encoded_bytes:encoded,from_cache:false}]
});
const fixture=()=>({schema:'fv-guest-cdp-image-capture-v1',capture_method:'chromium-cdp',real_capture:true,runs:[s('before','b',1000,404,0),s('after','a',240,200,400)]});
test('test-only fabricated pair computes 76% SAMPLE but never site-wide',()=>{
 const r=inspectGuestEvidence(manifest,fixture());
 assert.equal(r.ok,true);assert.equal(r.page_pairs.length,1);assert.equal(r.page_pairs[0].sample_reduction_pct,76);
 assert.equal(r.sitewide_weight_reduction_pct,null);assert.equal(r.confirmed_broken_count,null);assert.equal(r.production_release_authorized,false);
});
test('failed image remains candidate pending screenshot review',()=>assert.equal(inspectGuestEvidence(manifest,fixture()).review_candidate_count,1));
const badCapture=(label,mutate)=>test(label,()=>{const c=fixture();mutate(c);assert.equal(inspectGuestEvidence(manifest,c).ok,false);});
badCapture('web wrapper is not CDP',c=>c.capture_method='web.run.open');
badCapture('warm cache fails gate',c=>c.runs[0].cache_disabled=false);
badCapture('cached image fails gate',c=>c.runs[0].image_requests[0].from_cache=true);
badCapture('incomplete lazy scroll fails gate',c=>c.runs[0].lazy_settled=false);
badCapture('missing DOM image coverage fails gate',c=>c.runs[0].dom_image_count=8);
badCapture('unmatched currentSrc fails gate',c=>c.runs[0].dom_images[0].current_src='https://example.org/mismatch.png');
badCapture('unmatched CDP request fails gate',c=>c.runs[0].dom_images[0].request_id='unknown');
badCapture('duplicate CDP image request IDs fail gate',c=>c.runs[0].image_requests.push(clone(c.runs[0].image_requests[0])));
badCapture('zero HTTP status without network error fails',c=>c.runs[0].image_requests[0].http_status=0);
badCapture('duplicate capture run ids fail',c=>c.runs[1].id='b');
badCapture('foreign page fails',c=>c.runs[1].page_url='https://example.org/unknown');
test('different DPR makes incompatible pair, not a 76% claim',()=>{
 const c=fixture();c.runs[1].viewport.dpr=3;const r=inspectGuestEvidence(manifest,c);assert.equal(r.ok,true);assert.equal(r.page_pairs.length,0);
});
test('missing screenshot reference cannot be promoted as a break candidate',()=>{
 const c=fixture();c.runs[0].dom_images[0].screenshot_ref=null;
 const r=inspectGuestEvidence(manifest,c);assert.equal(r.ok,true);assert.equal(r.review_candidate_count,0);
});
test('HTML instead of an image never counts as decoded',()=>{
 const c=fixture();c.runs[1].image_requests[0].mime='text/html';
 const r=inspectGuestEvidence(manifest,c);assert.equal(r.ok,true);assert.equal(r.observations.find(x=>x.phase==='after').status,'INCONCLUSIVE');
});
