'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {aggregateHistoricalImageWire,AUDIT_BLOB}=require('./aggregate_historical_image_wire_20261112.cjs');
const auditBytes=fs.readFileSync(path.join(__dirname,'live_61post_355image_integrity_consolidated_20261112.json'));
const audit=JSON.parse(auditBytes);
const clone=x=>JSON.parse(JSON.stringify(x));
function makeImage(r,run){
 return {slot:r.slot,post_id:r.post_id,published_original_src:r.source_url,published_alt:r.alt,
  published_source_provenance:'WP_EDIT_SOURCE_MATCHED_FROZEN',
  request_id:run+'-'+r.slot,resource_type:'Image',request_url:r.source_url,
  current_src:r.source_url,final_response_url:r.source_url,response_mime_type:'image/jpeg',
  final_http_status:200,loading_finished:true,
  encoded_data_length:run==='b'?1000:240,network_data_received_bytes:run==='b'?900:200,
  network_data_received_provenance:'CDP_NETWORK_DATA_RECEIVED',
  natural_width:400,natural_height:300,image_identity:'frozen-'+r.slot,
  from_disk_cache:false,from_memory_cache:false,from_service_worker:false,
  decoded_selected_physical_width:400,decoded_selected_physical_height:300,
  decoded_source_provenance:'BROWSER_DECODED_CURRENT_SRC',
  decoded_selected_resource_url:r.source_url,painted_css_width:150,painted_css_height:100,
  image_rendered_visible:true,object_fit:'contain',object_position:'50% 50%'};
}
function makeCapture(rows,run,p){
 return {method:'CHROME_CDP_LOGGED_OUT_COLD',post_id:p,page_url:rows[0].post_url,
  page_http_status:200,full_scroll_complete:true,lazy_images_settled:true,
  network_capture_complete:true,cache_disabled:true,service_workers_bypassed:true,
  run_id:run+'-'+p,prose_fingerprint_sha256:'a'.repeat(64),
  viewport_width:390,viewport_height:844,dpr:2,images:rows.map(r=>makeImage(r,run))};
}
function fixture(){
 const by=new Map();
 for(const r of audit.rows){if(!by.has(r.post_id))by.set(r.post_id,[]);by.get(r.post_id).push(r);}
 return [...by].map(([post_id,rows])=>({
  independent_visual_review:Object.fromEntries(rows.map(r=>[r.slot,{
   method:'SIDE_BY_SIDE_STAGING_SCREENSHOT_REVIEW',
   before_run_id:'b-'+post_id,after_run_id:'a-'+post_id,
   before_current_src:r.source_url,after_current_src:r.source_url,
   before_screenshot_sha256:'b'.repeat(64),after_screenshot_sha256:'c'.repeat(64),
   same_scene_verified:true,same_crop_verified:true,alt_fidelity_verified:true,
   independent_editor_reviewed:true,
   review_evidence_url:'https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1703'}])),
  schema:'fv-cold-transfer-pair-v1',
  source_ledger_blob_sha:'d1a9c7a499510ec37bcdba5858d45165752587e0',
  post_id,expected_slots:rows.map(r=>r.slot),
  before:makeCapture(rows,'b',post_id),after:makeCapture(rows,'a',post_id)
 }));
}
function check(change,pattern){
 const a=clone(audit),pairs=fixture();change(a,pairs);
 const raw=JSON.stringify(a)===JSON.stringify(audit)?auditBytes:Buffer.from(JSON.stringify(a));
 const out=aggregateHistoricalImageWire(raw,pairs,AUDIT_BLOB);
 assert.equal(out.status,'HOLD');assert.match(out.reason,pattern);
 assert.equal(out.historical_cohort_image_wire_reduction_percent,null);
 assert.equal(out.current_sitewide_76_percent_verified,false);
}
test('full 61/355 exact image and cold source quality passes only historical scope',()=>{
 const r=aggregateHistoricalImageWire(auditBytes,fixture(),AUDIT_BLOB);
 assert.equal(r.status,'VERIFIED_HISTORICAL_61_POST_INLINE_IMAGE_COHORT_ONLY');
 assert.equal(r.observed_img_slots,355);assert.equal(r.observed_post_count,61);
 assert.equal(r.historical_cohort_transfer_before_bytes,355000);
 assert.equal(r.historical_cohort_transfer_after_bytes,85200);
 assert.equal(r.historical_cohort_image_wire_reduction_percent,76);
 assert.equal(r.historical_cohort_target_76_met,true);
 assert.equal(r.current_sitewide_76_percent_verified,false);
 assert.equal(r.production_change_allowed,false);
});
test('missing 1 post',()=>check((a,p)=>p.pop(),/INCOMPLETE_61_POST/));
test('duplicate post',()=>check((a,p)=>p[1]=clone(p[0]),/DUPLICATE_OR_UNRELATED_POST/));
test('missing one slot',()=>check((a,p)=>p[5].expected_slots.pop(),/INCOMPLETE_OR_FOREIGN/));
test('extra foreign slot',()=>check((a,p)=>p[5].expected_slots.push('999:1'),/INCOMPLETE_OR_FOREIGN/));
test('duplicate slot',()=>check((a,p)=>p[5].before.images[0]=clone(p[5].before.images[1]),/DUPLICATE_IMAGE_SLOT/));
test('published original URL drift',()=>check((a,p)=>p[5].before.images[0].published_original_src='https://example.com/new.jpg',/UNBOUND_STORED/));
test('published original ALT drift',()=>check((a,p)=>p[5].after.images[0].published_alt='different description',/UNBOUND_STORED/));
test('forged source provenance',()=>check((a,p)=>p[5].after.images[0].published_source_provenance='USER_INPUT',/UNBOUND_STORED/));
test('post URL drift',()=>check((a,p)=>p[5].after.page_url='https://finalvestige.com/other/',/POST_URL_CHANGED/));
test('uncached evidence absent',()=>check((a,p)=>p[5].before.images[0].from_disk_cache=true,/UNVERIFIED_PER_POST/));
test('network bytes absent',()=>check((a,p)=>p[5].after.images[0].encoded_data_length=null,/UNVERIFIED_PER_POST/));
test('visible resolution too small',()=>check((a,p)=>p[5].after.images[0].decoded_selected_physical_width=100,/UNVERIFIED_PER_POST/));
test('changed crop',()=>check((a,p)=>p[5].after.images[0].object_fit='cover',/UNVERIFIED_PER_POST/));
test('stale or forged audit blob',()=>{
 const r=aggregateHistoricalImageWire(auditBytes,fixture(),'0'.repeat(40));
 assert.equal(r.status,'HOLD');assert.match(r.reason,/FROZEN_COHORT_SOURCE_UNVERIFIED/);
});
test('frozen source mutated',()=>check((a,p)=>a.rows[0].source_equal=false,/FROZEN_COHORT_SOURCE_UNVERIFIED/));
test('42 claimed verified spoof',()=>check((a,p)=>a.policy.visitor_browser_confirmed_42_broken=true,/FROZEN_COHORT_SOURCE_UNVERIFIED/));
test('unverified rights override',()=>check((a,p)=>a.rows[0].rights_cleared=true,/FROZEN_COHORT_SOURCE_UNVERIFIED/));

test('caller passing a parsed object rather than frozen raw Git bytes is rejected',()=>{
 const out=aggregateHistoricalImageWire(audit,fixture(),AUDIT_BLOB);
 assert.equal(out.status,'HOLD');assert.match(out.reason,/RAW_GIT_BLOB_SHA_MISMATCH/);
});
test('same-length original image URL substitution is rejected despite claimed frozen SHA',()=>{
 const needle=Buffer.from('https://');
 const mutated=Buffer.from(auditBytes);
 const index=mutated.indexOf(needle);
 assert.ok(index>=0);
 mutated[index+8]^=1;
 assert.equal(mutated.length,auditBytes.length);
 const out=aggregateHistoricalImageWire(mutated,fixture(),AUDIT_BLOB);
 assert.equal(out.status,'HOLD');assert.match(out.reason,/RAW_GIT_BLOB_SHA_MISMATCH/);
 assert.equal(out.historical_cohort_image_wire_reduction_percent,null);
});
test('reformatting otherwise identical audit invalidates exact freeze',()=>{
 const out=aggregateHistoricalImageWire(Buffer.from(JSON.stringify(audit)),fixture(),AUDIT_BLOB);
 assert.equal(out.status,'HOLD');assert.match(out.reason,/RAW_GIT_BLOB_SHA_MISMATCH/);
});
