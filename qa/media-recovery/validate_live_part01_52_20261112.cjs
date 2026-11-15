"use strict";
// Offline source-only integrity gate. Do not interpret this as a browser/network test.
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
function isHttps(s){return typeof s==="string" && /^https:\/\/[^\/\s?#]+(?:\/|$)/i.test(s)}
function validate(d){
 assert.equal(d.schema,"fv-media-live-part01-source-geometry-v1");
 assert.equal(d.method,"READ_ONLY_AUTHENTICATED_WORDPRESS_POST_EDIT_SOURCE");
 assert.equal(d.provenance.frozen_blob,"948bc1b65b42799aa40cfdb810ddf6ffd80886b6");
 assert.equal(d.provenance.candidate_register_blob,"4965a862f7de7de46c1f4a1e26f3ca70a8c38805");
 assert.equal(d.provenance.siteqa_pr,154);
 const c=d.counts,p=d.posts,r=d.rows;
 assert.equal(c.posts,8);assert.equal(c.images,52);assert.equal(c.frozen_images,52);
 assert.equal(p.length,8);assert.equal(r.length,52);assert.deepEqual(d.drift,[]);
 assert.equal(d.cohort.historic_posts,61);assert.equal(d.cohort.historic_images,355);assert.equal(d.cohort.historic_external,288);
 assert.equal(d.cohort.reported_broken_unconfirmed,42);
 assert.equal(d.cohort.stored_oversized_originals,15);
 assert.equal(d.cohort.stored_oversized_bytes,47096779);
 assert.equal(d.cohort.wire_savings_76pct_measured,false);
 for(const k of ["catalog_candidates_not_rights_authorizations","conditional_960px_requires_native_pixel_and_DPR_validation","source_http_not_measured","guest_http_not_measured","no_wordpress_writes","no_caching","no_binary_downloads","siteqa_browser_owner"])assert.equal(d.policy[k],true,k);
 assert.equal(d.policy.measured_cls,null);
 const unique=new Set(),postIds=new Set(p.map(x=>x.post_id));assert.equal(postIds.size,8);
 for(const row of r){
  assert(!unique.has(row.slot),"duplicate image slot");unique.add(row.slot);
  assert(postIds.has(row.post_id),"unknown post");
  assert(row.slot.startsWith(row.post_id+":"),"slot/post mismatch");
  assert.equal(row.source_equal,true,"source drift");
  assert.equal(row.alt_equal,true,"ALT drift");
  assert(isHttps(row.live_src)&&row.live_src===row.frozen_src,"wrong source identity");
  assert.equal(row.live_alt,row.frozen_alt,"wrong ALT identity");
  assert((row.html_width===null&&row.html_height===null)||(Number.isSafeInteger(row.html_width)&&row.html_width>0&&Number.isSafeInteger(row.html_height)&&row.html_height>0),"invalid/partial dimensions");
  assert.equal(row.literal_srcset_present,false,"unreviewed srcset");
  for(const k of ["origin_http_status","guest_http_status","guest_natural_px","guest_encoded_wire_bytes","guest_failure_confirmed"])assert.equal(row[k],null,"fabricated browser/wire evidence "+k);
  for(const k of ["rehost_or_cache_approved","wordpress_write_approved"])assert.equal(row[k],false,"unauthorized media operation "+k);
  assert(Array.isArray(row.candidate_catalogs),"candidate records missing");
  for(const cand of row.candidate_catalogs){
    assert(isHttps(cand.catalog_url),"invalid catalog link");
    assert.equal(cand.exact_visual_match_verified,false);
    assert.equal(cand.item_rights_cleared,false);
    if(cand.conditional_960px!=null){
     assert(Array.isArray(cand.conditional_960px)&&cand.conditional_960px.length===2);
     const [w,h]=cand.conditional_960px;
     assert(Number.isSafeInteger(w)&&w>0&&w<=960&&Number.isSafeInteger(h)&&h>0,"invalid 960px plan");
    }
  }
 }
 for(const post of p){
  assert.equal(post.status,"publish");
  assert(isHttps(post.post_url));
  assert.equal(r.filter(x=>x.post_id===post.post_id).length,post.live_images);
  assert.equal(post.live_images,post.frozen_images);
 }
 const tally={posts:p.length,images:r.length,source_equal:r.filter(x=>x.source_equal).length,source_drift:r.filter(x=>x.source_equal===false).length,alt_equal:r.filter(x=>x.alt_equal).length,alt_drift:r.filter(x=>x.alt_equal===false).length,missing_dimensions:r.filter(x=>x.html_width===null).length,both_dimensions:r.filter(x=>x.html_width!==null).length,partial_dimensions:r.filter(x=>(x.html_width===null)!==(x.html_height===null)).length,candidate_slots:r.filter(x=>x.candidate_catalogs.length>0).length,literal_srcset:r.filter(x=>x.literal_srcset_present).length};
 for(const [key,value] of Object.entries(tally))assert.equal(c[key],value,"incorrect aggregate: "+key);
 return tally;
}
if(require.main===module){
 const input=process.argv[2]||path.join(__dirname,"live_part01_8posts_52_images_20261112.json");
 console.log(JSON.stringify(validate(JSON.parse(fs.readFileSync(input,"utf8")))));
}
module.exports={validate};
