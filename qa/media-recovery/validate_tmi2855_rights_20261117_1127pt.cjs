'use strict';
const assert=require('node:assert/strict');
const ORIGINAL='https://images.saymedia-content.com/.image/ar_16%3A9%2Cc_fill%2Ccs_srgb%2Cfl_progressive%2Cq_auto%3Aeco%2Cw_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg';
function validate(x){
 assert.equal(x.schema,'fv-media-tmi2855-alternate-rights-v1');
 assert.equal(x.post_id,285);assert.equal(x.slot,'285:5');
 assert.equal(x.wp_revision,'2026-11-02T21:39:59');
 assert.equal(x.wp_snapshot_blob,'9c3fdb065c57faf69e14b269ee3622e4e44c1462');
 assert.equal(x.published_url,'https://i0.wp.com/'+ORIGINAL.slice(8)+'?ssl=1');
 assert.equal(x.published_alt,'Aerial view of the Three Mile Island nuclear generating station on the Susquehanna River.');
 assert.equal(x.origin_reader.url,ORIGINAL);
 assert.equal(x.origin_reader.kind,'independent_public_retriever');
 assert.equal(x.origin_reader.http_status,404);
 assert.equal(x.jetpack_reader.http_status,null);
 for(const [k,v] of Object.entries(x.visitor))assert.equal(v,null,'invented visitor fact: '+k);
 assert.equal(x.guest_42_failures_confirmed,null);
 assert.equal(x.wire_savings_76_percent_verified,false);
 assert.deepEqual(x.oversized_originals,{count:20,stored_bytes:64385752,visitor_transfer_bytes:null});
 assert.equal(x.release,'HOLD_GUEST_RIGHTS_BINARY_EDITORIAL_STAGING');
 for(const [k,v] of Object.entries(x.actions))assert.equal(v,false,'unsafe action: '+k);
 assert.equal(x.candidates.length,3);
 assert.deepEqual(x.candidates.map(v=>v.id),['DOE_COMMONS_PD','NRC_MARCH_1979','NRC_TITLED_1979_TAKEN_2008']);
 const d=x.candidates[0];
 assert.equal(d.catalog,'https://commons.wikimedia.org/wiki/File:Three_Mile_Island_(color).jpg');
 assert.equal(d.license,'PD_US_GOV_REPORTED');
 assert.equal(d.native_width,2592);assert.equal(d.native_height,2488);
 assert.equal(d.review_width,960);assert.equal(d.review_height,Math.round(2488*960/2592));
 assert.ok(d.scene.includes('different aerial photo'));
 for(const c of x.candidates){
  assert.equal(c.same_binary,false);assert.equal(c.cache_allowed,false);
  assert.equal(c.wp_upload_allowed,false);assert.equal(c.binary_sha256,null);
  if(c.review_width!==null){assert.ok(c.review_width<=960 && c.review_width<=c.native_width);assert.ok(c.review_height<=c.native_height);}
  else assert.equal(c.review_height,null);
 }
 for(const c of x.candidates.slice(1)){
  assert.equal(c.license,'CC-BY-NC-ND-2.0');
  assert.equal(c.native_width,null);assert.equal(c.native_height,null);assert.equal(c.review_width,null);
 }
 assert.ok(x.candidates[1].scene.includes('March 1979'));
 assert.ok(x.candidates[2].scene.includes('August 12 2008'));
 assert.equal(x.license_link,'https://creativecommons.org/licenses/by-nc-nd/2.0/deed.en');
 return {decision:'HOLD',guest_failure_confirmed:false,commercial_candidates_approved:0};
}
module.exports={validate};
