'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const original=require('./p0_primary_rights_scene_readiness_20261112.json');
const {validate,triage,slots}=require('./validate_p0_primary_rights_scene_20261112.cjs');
const copy=()=>JSON.parse(JSON.stringify(original));
const ready=slot=>({slot,site_qa_result:'BROWSER_CONFIRMED_BROKEN',
 site_qa_evidence_blob_sha:'b'.repeat(40),exact_same_scene_verified:true,
 photo_fingerprint_reviewed:true,item_rights_checked:true,source_attribution_recorded:true,
 no_upscale_at_max_960_verified:true,dpr_visual_quality_approved:true,editor_staging_approved:true});
test('pinned 6 audit and historical 61/355/288 baseline',()=>{
 assert.equal(validate(),true);assert.equal(original.records.length,6);
 assert.equal(original.historical.reported_broken_unconfirmed,42);
 assert.equal(original.historical.wire_reduction_76_percent_measured,false);
});
test('every record retains unknown guest/origin responses and no permission',()=>{
 for(const x of original.records){
  assert.equal(x.guest_http_status,null);assert.equal(x.origin_http_status,null);
  assert.equal(x.wordpress_upload_approved,false);assert.equal(x.item_reuse_approved,false);
 }});
test('historical source URL mutation invalidates audit',()=>{
 const x=copy();x.records[0].exact_stored_src='https://example.org/other.jpg';
 assert.equal(validate(x),false);
});
test('wrong wrapper code invalidates audit',()=>{
 const x=copy();x.records[1].retriever_observation.code=404;
 assert.equal(validate(x),false);
});
test('cannot claim fabricated guest 404',()=>{
 const x=copy();x.records[2].guest_http_status=404;assert.equal(validate(x),false);
});
test('cannot claim rights approved without item review',()=>{
 const x=copy();x.records[3].item_reuse_approved=true;assert.equal(validate(x),false);
});
test('cannot turn on caching globally',()=>{
 const x=copy();x.policy.no_cache=false;assert.equal(validate(x),false);
});
test('cannot approve upscaled 1200 image',()=>{
 const x=copy();x.records[0].conditional_960_no_upscale_px=[1200,800];assert.equal(validate(x),false);
});
test('duplicate slot fails 6-row coverage',()=>{
 const x=copy();x.records[1].slot=x.records[0].slot;assert.equal(validate(x),false);
});
test('unverified browser slot held by Site QA',()=>{
 assert.equal(triage({slot:'418:1'}).reason,'AWAIT_SITE_QA_154_GUEST_CDP_EVIDENCE');
});
test('loaded image is not a replacement target',()=>{
 assert.equal(triage({slot:'287:5',site_qa_result:'BROWSER_VERIFIED_LOADED'}).reason,'ORIGINAL_VISITOR_IMAGE_LOADED_KEEP_IT');
});
test('invented failure missing evidence hash held',()=>{
 assert.equal(triage({slot:'418:1',site_qa_result:'BROWSER_CONFIRMED_BROKEN'}).reason,'AWAIT_SITE_QA_154_GUEST_CDP_EVIDENCE');
});
test('same event is not proof of same historical photograph',()=>{
 const x=ready('418:2');x.photo_fingerprint_reviewed=false;
 assert.equal(triage(x).reason,'SOURCE_SCENE_CROP_OR_PIXEL_MATCH_UNVERIFIED');
});
test('USGS public domain still needs item credit review',()=>{
 const x=ready('407:1');x.item_rights_checked=false;
 assert.equal(triage(x).reason,'ITEM_RIGHTS_AND_CREDIT_HOLD');
});
test('960px derivative without 2x clarity is held',()=>{
 const x=ready('285:5');x.dpr_visual_quality_approved=false;
 assert.equal(triage(x).reason,'RESPONSIVE_VISUAL_HOLD');
});
test('editor staging signoff is separate from rights',()=>{
 const x=ready('287:5');x.editor_staging_approved=false;
 assert.equal(triage(x).reason,'STAGING_EDITOR_HOLD');
});
test('even hypothetical fully signed evidence NEVER authorizes production',()=>{
 for(const slot of slots){const x=triage(ready(slot));
  assert.equal(x.status,'STAGING_REVIEW_ONLY');
  assert.equal(x.production_write_approved,false);
  assert.equal(x.cache_approved,false);
 }});
test('all 6 official/publisher URLs are explicit',()=>{
 for(const r of original.records)assert.ok(r.candidate_catalog.startsWith('https://'));
});
