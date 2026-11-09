'use strict';
/** Offline, fail-closed archival triage: never infers guest network or publishing authorization. */
const assert=require('node:assert/strict');
const SLOT_IDS=["190:0","190:2","190:3","190:4","190:5","214:0","214:4","211:0","211:1","211:2","211:3","211:4","211:5","434:1","434:2","434:3","434:4","434:5"];
const CENSUS_SHA='92a904c8da1ace1f972b2f00adf1a4847dde2b99';
function validate(a,c){
 assert.equal(a.schema,'fv-media-18-primary-host-risk-v1');
 assert.equal(a.census_blob_sha,CENSUS_SHA);
 assert.equal(a.scope.posts,3); assert.equal(a.scope.slots,18);
 assert.equal(a.scope.visitor_failing_confirmed,0);
 assert.equal(a.scope.catalog_item_verified,a.rows.filter(x=>x.individual_catalog_record_verified).length);
 assert.equal(a.rows.length,SLOT_IDS.length);
 const ids=new Set(),loc=new Set();
 for(const r of a.rows){
  assert.ok(SLOT_IDS.includes(r.slot),'unrecognized slot'); assert.ok(!ids.has(r.slot),'duplicate');ids.add(r.slot);
  const orig=c.rows.find(x=>x.slot===r.slot);assert.ok(orig&&!orig.researched,'slot not previously researched');
  for(const k of ['stored_url','post_url','origin_host'])assert.equal(r[k],orig[k],'source drift '+r.slot+' '+k);
  assert.ok(['cdn.loc.gov','www.nps.gov','images-assets.nasa.gov'].includes(r.origin_host));
  assert.ok(r.canonical_catalog_candidate.startsWith('https://'));
  assert.ok(r.scene_integrity_guard&&r.scene_integrity_guard.length>25);
  assert.ok(r.rights_observation&&r.rights_observation!=='PUBLIC_DOMAIN_CLEARED');
  assert.equal(r.browser_http_status,null);assert.equal(r.browser_natural_px,null);assert.equal(r.browser_transfer_bytes,null);assert.equal(r.browser_failed,null);
  assert.equal(r.archival_native_px,null);assert.equal(r.conditional_960_px,null);
  assert.equal(r.image_binary_identity_verified,false);assert.equal(r.rights_cleared,false);assert.equal(r.visual_approved,false);
  assert.equal(r.sizing_policy,'MAX_960_W_PRESERVE_ASPECT_NO_UPSCALE_IF_NATIVE_UNKNOWN_HOLD');
  assert.deepEqual(r.release,{download:false,cache:false,wordpress_upload:false,block_rewrite:false});
  if(r.origin_host==='cdn.loc.gov'){
   assert.equal(r.authority,'Library of Congress Prints & Photographs');
   assert.ok(r.canonical_catalog_candidate.endsWith(r.archival_locator+'/'));
   assert.ok(/^(npcc\\.|ggbain\\.|pan\\.)/.test(r.archival_locator));
   assert.ok(r.stored_url.includes(r.archival_locator.split('.')[1]));
  }else if(r.origin_host==='images-assets.nasa.gov'){
   assert.equal(r.authority,'NASA');assert.ok(r.stored_url.includes('/'+r.archival_locator+'/'));
   assert.equal(r.canonical_catalog_candidate,'https://images.nasa.gov/details/'+r.archival_locator);
   if(r.archival_locator.startsWith('KSC-2017'))assert.ok(r.scene_integrity_guard.includes('2017'));
  }else{
   assert.equal(r.authority,'National Park Service / Port Chicago');
   assert.ok(r.canonical_catalog_candidate.startsWith('https://www.nps.gov/poch/'));
  }
 }
 assert.equal(ids.size,18);return true;
}
module.exports={validate};
