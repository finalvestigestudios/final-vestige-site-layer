"use strict";
const EXPECTED=Object.freeze({
"418:0":"https://www.history.uscg.mil/Portals/6/2_%20new%20and%20old%20lighthouses%2019849609_web1_1_-Scotch-Cap-lighthouse-1200x984.jpg",
"418:3":"https://www.history.uscg.mil/Portals/6/6_%20Scotch%20Cap%20remains.jpg",
"418:4":"https://www.hawaiimagazine.com/wp-content/uploads/2020/12/Tsunami1946NOAA2.jpg",
"418:5":"https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/styles/full_width/public/media/images/19460401_UNKNOWN_37-012_copy.jpg?itok=ASMRCahz"
});
function validate(data) {
 const errors=[];
 const fail=(e)=>errors.push(e);
 if(data?.schema!=="fv-scotch-cap-noaa-four-v1"||data?.post_id!==418||data?.rows?.length!==4) fail("invalid exact four-slot cohort");
 if(data?.article_url!=="https://finalvestige.com/2026/08/20/the-lighthouse-was-gone-at-dawn-1946-tsunami/") fail("wrong article URL");
 const b=data?.baseline||{};
 if(b.historical_posts!==61||b.historical_stored_inline_images!==355||b.current_posts!==66||b.current_stored_inline_images!==361||b.reported_broken_images!==42||b.confirmed_broken_images!==null||b.claimed_weight_reduction_pct!==76||b.measured_weight_reduction_pct!==null||b.originals_over_1_5_mib!==13||b.oversized_original_storage_bytes!==43522829)fail("unsupported cohort or savings assertion");
 const seen=new Set();
 for(const r of data?.rows||[]){
  if(seen.has(r.key)||!Object.hasOwn(EXPECTED,r.key)||r.published_src!==EXPECTED[r.key])fail("URL or slot identity mismatch"); seen.add(r.key);
  if(!r.alt||!r.subject||!r.source_catalog_url||!r.candidate_url||!r.catalog_evidence||!r.credit||!r.item_rights)fail("missing provenance");
  for(const k of ["guest_browser_http","guest_natural_width","guest_natural_height","guest_current_src","guest_encoded_bytes","guest_broken","origin_http"])if(r[k]!==null)fail("invented visitor/origin evidence: "+k);
  for(const k of ["rights_republication_cleared","third_party_caching_authorized","wordpress_write_authorized","same_binary_verified"])if(r[k]!==false)fail("rights or binary prematurely approved: "+k);
  if(r.max_preview_width_px!==960||r.no_upscale!==true||r.preserve_aspect_ratio!==true)fail("sizing policy weakened");
  if(r.native_master_pixels!==null||r.wordpress_stored_width_px!==null||r.wordpress_stored_height_px!==null)fail("native or WordPress dimensions fabricated");
  if(!["rendered","retriever_not_accessible"].includes(r.published_viewer)||!["rendered","catalog_text_indexed_binary_unverified"].includes(r.candidate_viewer))fail("invalid viewer observation");
  if(r.candidate_preview_pixels!==null){
    const [w,h]=r.candidate_preview_pixels;
    if(!Number.isInteger(w)||!Number.isInteger(h)||w<1||h<1||w>960||JSON.stringify(r.proposed_if_rights_cleared_pixels)!==JSON.stringify(r.candidate_preview_pixels))fail("unsafe preview geometry");
  }else if(r.proposed_if_rights_cleared_pixels!==null)fail("fabricated derivative geometry");
  if(r.key==="418:0"&&!r.subject.includes("Pre-disaster"))fail("pre-disaster photo conflated");
  if(r.key==="418:3"&&!r.subject.includes("Aerial"))fail("aerial after-photo conflated");
  if(r.key==="418:4"&&(!r.source_catalog_url.includes("pl23theb2705jpg")||!r.subject.includes("in progress")))fail("NOAA subject/catalog mismatch");
  if(r.key==="418:5"&&(!r.source_catalog_url.includes("usgs.gov/media/images")||!r.subject.includes("Aftermath")))fail("USGS aftermath mismatch");
 }
 if(seen.size!==4)fail("missing source slot");
 const s=data?.release||{};
 if(s.site_qa_collector_duplicated!==false||s.wordpress_production_writes!==0||s.third_party_caches!==0||s.image_downloads!==0||s.production_repairs!==0||s.additional_spend_usd!==0||s.homepage_design_changes!==0)fail("unauthorized production action");
 return {ok:errors.length===0,errors};
}
module.exports={validate,EXPECTED};
if(require.main===module){
 const fs=require("node:fs"),file=process.argv[2]||"qa/media-recovery/scotch_cap_noaa_four_20261106.json";
 const r=validate(JSON.parse(fs.readFileSync(file,"utf8")));console.log(JSON.stringify(r));if(!r.ok)process.exitCode=1;
}
