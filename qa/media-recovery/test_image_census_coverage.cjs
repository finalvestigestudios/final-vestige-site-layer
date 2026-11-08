'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {proofKind,assessPage,assessRun}=require('./image_census_coverage_core.cjs');
function slot(i,kind='loaded'){
 const s={image_key:'268:'+i,stored_url:'https://example.org/'+i+'.jpg',current_src:'https://example.org/'+i+'.jpg',
  current_src_identity_verified:true,network_final_identity_verified:true,
  loaded_network_proof_verified:true,transfer_bytes:800,
  complete:true,request_url:'https://example.org/'+i+'.jpg',
  result:'loaded_in_probe_browser',verified_broken_in_browser:false,natural_width:960,http_status:200,
  network_failure:null,visual_failure_kind:null,response_mime_type:'image/jpeg'};
 if(kind==='broken'){s.result='confirmed_broken_in_probe_browser';s.verified_broken_in_browser=true;
  s.natural_width=0;s.http_status=404;s.visual_failure_kind='http_error';}
 if(kind==='error-html'){s.result='confirmed_broken_in_probe_browser';s.verified_broken_in_browser=true;
  s.natural_width=0;s.http_status=200;s.visual_failure_kind='non_image_error_payload';s.response_mime_type='text/html';}
 if(kind==='pending'){s.result='pending_lazy_or_incomplete';s.verified_broken_in_browser=null;s.complete=false;s.natural_width=0;}
 return s;
}
function page(id=268,items=[slot(0)]){return {post_id:id,page_result:'inspected_browser',
 scroll_coverage:{complete:true,state:'full_height_scanned'},stored_image_count:items.length,stored_images:items};}
test('complete successful image count does not imply broken images',()=>{const p=assessPage(page());assert.equal(p.complete,true);assert.equal(p.confirmed_broken_count,0)});
test('confirmed HTTP 404 with zero decode can be counted',()=>{const p=assessPage(page(268,[slot(0,'broken')]));assert.equal(p.complete,true);assert.equal(p.confirmed_broken_count,1)});
test('200 HTML error plus zero decode has a verifiable failure kind',()=>{assert.equal(proofKind(slot(0,'error-html')),'broken')});
test('pending lazy image invalidates zero-broken report',()=>{const p=assessPage(page(268,[slot(0),slot(1,'pending')]));assert.equal(p.confirmed_broken_count,null);assert.equal(p.known_loaded_count,1)});
test('alt-only matching is not proof',()=>{const s=slot(0);s.result='alt_only_identity_unverified';s.current_src_identity_verified=false;assert.equal(assessPage(page(268,[s])).complete,false)});
test('wrong currentSrc identity does not count as loaded',()=>{const s=slot(0);s.current_src_identity_verified=false;assert.equal(proofKind(s),'unresolved')});
test('duplicate image slot key fails closed',()=>{const p=assessPage(page(268,[slot(0),slot(0)]));assert.equal(p.complete,false);assert.ok(p.errors.includes('invalid_or_duplicate_slot_key'))});
test('missing stored slot fails closed',()=>{const p=page();p.stored_image_count=2;assert.equal(assessPage(p).complete,false)});
test('partial page or scroll does not claim a census',()=>{const p=page();p.page_result='inspected_browser_partial_scroll';assert.equal(assessPage(p).confirmed_broken_count,null);p.page_result='inspected_browser';p.scroll_coverage.complete=false;assert.equal(assessPage(p).complete,false)});
test('empty image article can have a complete zero census',()=>{assert.equal(assessPage(page(268,[])).confirmed_broken_count,0)});
test('network error cannot be asserted without explicit failure kind and request',()=>{const s=slot(0,'broken');s.http_status=null;s.network_failure='net::ERR_CONNECTION_RESET';s.visual_failure_kind='network_error';assert.equal(proofKind(s),'broken');s.request_url=null;assert.equal(proofKind(s),'unresolved')});
test('contradictory status 404 on a decoded loaded image is unresolved',()=>{const s=slot(0);s.http_status=404;assert.equal(proofKind(s),'unresolved')});
test('reported HTTP 200 without MIME error is not sufficient broken proof',()=>{const s=slot(0,'error-html');s.response_mime_type='image/jpeg';assert.equal(proofKind(s),'unresolved')});
test('fully complete run reports number of real broken slots',()=>{const a=page(268,[slot(0,'broken')]),b=page(432,[{...slot(1,'error-html'),image_key:'432:1'}]);const r=assessRun([a,b],2);assert.equal(r.complete,true);assert.equal(r.confirmed_broken_count,2)});
test('a partially covered second post invalidates run aggregate',()=>{const a=page(268,[slot(0,'broken')]),b=page(432,[slot(1,'pending')]);const r=assessRun([a,b],2);assert.equal(r.complete,false);assert.equal(r.known_broken_count,1);assert.equal(r.confirmed_broken_count,null)});
test('missing and duplicate posts reject aggregate even if individual counts pass',()=>{const a=page();assert.equal(assessRun([a],2).complete,false);assert.equal(assessRun([a,a],2).complete,false)});
test('invalid scalar and negative count reject aggregate',()=>{assert.equal(assessRun([],0).complete,false);assert.equal(assessPage({...page(),stored_image_count:-1}).complete,false)});
test('loaded pixels without a matching HTTP status must remain unresolved',()=>{const s=slot(0);s.http_status=null;assert.equal(proofKind(s),'unresolved');s.http_status=200;s.request_url=null;assert.equal(proofKind(s),'unresolved')});
