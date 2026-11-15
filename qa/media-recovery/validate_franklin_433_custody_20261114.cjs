'use strict';
/** Offline source-custody and release gate. No HTTP requests, image copies or CMS writes. */
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const SLOTS=['433:1','433:2','433:3','433:4','433:5','433:6'];
const NATIVE=[[1576,2506],[750,523],[399,600],[1477,2357],[3284,3966],[726,1119]];
const HOSTS=['finalvestige.com','upload.wikimedia.org','d3d0lqu00lnqvz.cloudfront.net'];
function httpsURL(value){try{const u=new URL(value);return u.protocol==='https:'&&!u.username&&!u.password&&!u.hash?u:null;}catch{return null;}}
function validate(a){
 assert.equal(a.schema,'fv-franklin-433-archival-media-custody-v1');
 assert.equal(a.published_post.id,433);
 assert.equal(a.published_post.status,'publish');
 assert.equal(a.published_post.stored_img_count,6);
 assert.equal(a.published_post.external_src_count,5);
 assert.equal(a.historical_baseline.confirmed_guest_broken,null);
 assert.equal(a.historical_baseline.actual_wire_reduction_percent,null);
 for(const k of ['allow_wordpress_production_writes','allow_asset_downloads_or_caches','allow_auto_replacement'])assert.equal(a.release[k],false);
 for(const k of ['homepage_excluded','require_exact_scene_approval','require_item_rights_and_credit','require_actual_css_dpr','require_reversible_stage'])assert.equal(a.release[k],true);
 assert.equal(a.release.site_qa_cold_browser_owner,154);
 assert.ok(Array.isArray(a.images));
 assert.deepEqual(a.images.map(x=>x.slot),SLOTS);
 for(let i=0;i<a.images.length;i++){
  const r=a.images[i],src=httpsURL(r.stored_url),catalog=httpsURL(r.source_record_url);
  assert.ok(src&&catalog,'HTTPS URL at '+r.slot);
  assert.ok(HOSTS.includes(src.hostname),'wrong source host at '+r.slot);
  assert.equal(catalog.hostname,'commons.wikimedia.org');
  assert.ok(catalog.pathname.startsWith('/wiki/File:'),'item catalog required');
  assert.ok(typeof r.alt==='string'&&r.alt.length>=30);
  assert.ok(typeof r.published_caption==='string'&&r.published_caption.length>=35);
  assert.ok(typeof r.source_rights==='string'&&r.source_rights.length>=50);
  assert.deepEqual(r.native_px,NATIVE[i]);
  const [w,h]=r.native_px,[dw,dh]=r.conditional_960_no_upscale_px;
  assert.equal(dw,Math.min(w,960),'must not upscale');
  assert.ok(Math.abs(dh-dw*h/w)<=1&&dh<=h,'aspect ratio and height');
  for(const field of ['origin_http_status','logged_out_browser_http_status','rendered_current_src','actual_transfer_bytes','confirmed_guest_broken'])assert.equal(r[field],null,'no invented visitor measurements');
  for(const field of ['candidate_binary_identity_verified','rights_cleared_for_rehost','production_replacement_approved'])assert.equal(r[field],false,'no premature approval');
  assert.equal(r.review_hold,true);
  assert.equal(r.caption_license_mismatch,i===4,'preserve original rights discrepancy');
 }
 const photo=a.images[4],poster=a.images[5];
 assert.equal(photo.license_class,'CC-BY-SA-4.0');
 assert.match(photo.published_caption,/public domain/i);
 assert.match(photo.source_rights,/FabTet.*2023.*CC BY-SA 4\.0/);
 assert.equal(poster.license_class,'pd_underlying_host_reproduction_unverified');
 assert.match(poster.source_rights,/not binary matched/);
 assert.deepEqual(a.images[2].conditional_960_no_upscale_px,[399,600]);
 return {result:'HOLD',checked:6,editorial_rights_conflict:['433:5'],guest_browser_evidence_available:false,production_change_authorized:false};
}
function load(file){if(fs.statSync(file).size>65536)throw Error('input too large');return JSON.parse(fs.readFileSync(file,'utf8'));}
if(require.main===module){try{const file=process.argv[2]||path.join(__dirname,'franklin_433_custody_20261114.json');console.log(JSON.stringify(validate(load(file)),null,2));}catch(e){console.error('FRANKLIN_MEDIA_HOLD: '+e.message);process.exitCode=2;}}
module.exports={httpsURL,validate,load};
