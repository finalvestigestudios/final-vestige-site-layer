'use strict';
// All fixture URLs and bytes here are SYNTHETIC. Never cite them as live measurements.
const test = require('node:test');
const assert = require('node:assert/strict');
const { assess, validateCapture, SCHEMA, SOURCE } = require('./assess_cold_wire_savings_20261115.cjs');
const h = 'a'.repeat(64), h2 = 'b'.repeat(64);
const protocol = {
  collector:'siteqa-154-export', user_agent:'synthetic QA UA', browser_version:'synthetic 100',
  viewport_width_px:390, viewport_height_px:844, device_scale_factor:2,
  network_profile:'synthetic fixed', scroll_protocol:'full-page-settle-all-lazy-images',
  cache_mode:'cold-disabled', service_worker_mode:'bypassed', session_mode:'logged-out'
};
function req(bytes, id='req-1') { return {
  request_id:id, url:'https://example.invalid/image-'+id+'.jpg', resource_type:'Image',
  byte_source:SOURCE, http_status:200, mime_type:'image/jpeg', encoded_data_length:bytes,
  response_finished:true, redirect_chain_complete:true,
  from_disk_cache:false, from_memory_cache:false, from_service_worker:false
}; }
function cap(phase, bytes=1000) { return { schema:SCHEMA, phase, cohort:'frozen-61', protocol:structuredClone(protocol),
  pages:[1,2].map(i=>({post_id:i,url:'https://example.invalid/posts/'+i+'/',
    content_sha256:h,image_slot_manifest_sha256:h2,all_lazy_images_requested:true,
    load_completion_confirmed:true,dom_image_slots:1,decoded_image_slots:1,broken_image_slots:0,
    screenshot_review_passed:true,rights_review_passed:true,review_evidence:'synthetic test signoff',
    requests:[req(bytes,'req-'+i)] }))
  }; }
function run(b,a){return assess(b,a,{expectedCount:2,allowSyntheticTests:true});}
function rejectMutation(name,fn){ test(name,()=>{
  const b=cap('before'),a=cap('after'); fn(b,a);
  assert.throws(()=>run(b,a),/HOLD:/);
});}

test('SYNTHETIC only: 76% threshold uses sum of actual CDP wire bytes',()=>{
  let r=run(cap('before',1000),cap('after',240));
  assert.equal(r.measured_reduction_percent,76); assert.equal(r.meets_76_percent_threshold,true);
  assert.equal(r.before_image_wire_bytes,2000);assert.equal(r.after_image_wire_bytes,480);
});
test('SYNTHETIC only: 75.9% is not 76%',()=>{
  const r=run(cap('before',1000),cap('after',241));
  assert.equal(r.measured_reduction_percent,75.9);assert.equal(r.meets_76_percent_threshold,false);
});
test('SYNTHETIC only: request totals sum over all pages and do not average page percentages',()=>{
  const b=cap('before'); b.pages[0].requests=[req(9000,'req-a')];
  const a=cap('after'); a.pages[0].requests=[req(9000,'req-a')]; a.pages[1].requests=[req(100,'req-b')];
  const r=run(b,a);assert.equal(r.before_image_wire_bytes,10000);assert.equal(r.after_image_wire_bytes,9100);
  assert.equal(r.measured_reduction_percent,9);
});
test('SYNTHETIC only: real CLI never accepts 2-page partial cohort',()=>{
  assert.throws(()=>assess(cap('before'),cap('after')),/HOLD:/);
});
rejectMutation('reject mismatched published article identity',(_b,a)=>a.pages[0].post_id=19);
rejectMutation('reject different content fingerprint',(_b,a)=>a.pages[0].content_sha256='c'.repeat(64));
rejectMutation('reject different source-slot manifest',(_b,a)=>a.pages[0].image_slot_manifest_sha256='c'.repeat(64));
rejectMutation('reject viewport mismatch',(_b,a)=>a.protocol.viewport_width_px=500);
rejectMutation('reject non-guest authenticated capture',(_b,a)=>a.protocol.session_mode='authenticated');
rejectMutation('reject warm/cached image experiment',(_b,a)=>a.protocol.cache_mode='warm');
rejectMutation('reject active service workers',(_b,a)=>a.protocol.service_worker_mode='active');
rejectMutation('reject incomplete lazy-image traversal',(_b,a)=>a.pages[0].all_lazy_images_requested=false);
rejectMutation('reject decoded image slot missing',(_b,a)=>a.pages[0].decoded_image_slots=0);
rejectMutation('reject broken image remaining',(_b,a)=>a.pages[0].broken_image_slots=1);
rejectMutation('reject absent screenshot signoff',(_b,a)=>a.pages[0].screenshot_review_passed=false);
rejectMutation('reject absent image rights signoff',(_b,a)=>a.pages[0].rights_review_passed=false);
rejectMutation('reject missing evidence note',(_b,a)=>a.pages[0].review_evidence='');
rejectMutation('reject invented HTTP status',(_b,a)=>a.pages[0].requests[0].http_status=599);
rejectMutation('reject opaque/malformed image MIME',(_b,a)=>a.pages[0].requests[0].mime_type='text/html');
rejectMutation('reject Resource Timing estimated bytes',(_b,a)=>a.pages[0].requests[0].byte_source='estimatedTransferredBytes');
rejectMutation('reject missing encoded CDP wire bytes',(_b,a)=>a.pages[0].requests[0].encoded_data_length=null);
rejectMutation('reject cached image',(_b,a)=>a.pages[0].requests[0].from_disk_cache=true);
rejectMutation('reject uncollected redirect chain',(_b,a)=>a.pages[0].requests[0].redirect_chain_complete=false);
rejectMutation('reject duplicate request IDs',(_b,a)=>a.pages[0].requests.push({...a.pages[0].requests[0]}));
rejectMutation('reject repeat post ID',(_b,a)=>a.pages[1].post_id=a.pages[0].post_id);
rejectMutation('reject wrong page URL',(_b,a)=>a.pages[0].url='https://example.invalid/other/');
rejectMutation('reject changed DOM image slot count',(_b,a)=>{a.pages[0].dom_image_slots=2;a.pages[0].decoded_image_slots=2});
rejectMutation('reject invalid original content SHA',(_b,a)=>a.pages[0].content_sha256='fake');
rejectMutation('reject a synthetic/no-status original URL',(_b,a)=>a.pages[0].requests[0].url='not-a-url');
rejectMutation('reject unsupported 304 cached result',(_b,a)=>a.pages[0].requests[0].http_status=304);
rejectMutation('reject non-finished image request',(_b,a)=>a.pages[0].requests[0].response_finished=false);
rejectMutation('reject 0-byte image response',(_b,a)=>a.pages[0].requests[0].encoded_data_length=0);
rejectMutation('reject unsupported gzip/body size estimate',(_b,a)=>a.pages[0].requests[0].byte_source='compression-estimate');
