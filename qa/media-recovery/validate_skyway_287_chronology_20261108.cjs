"use strict";
const fs=require("node:fs"),path=require("node:path");
const ids={
 RC09236:[32082,"1980-05-09","/fpc/reference/rc09236.jpg"],
 DGM0236:[267897,"1982-02","/fpc/dgmarks/DGM0236.jpg"],
 PR01070:[1042,"1986","/fpc/prints/pr01070.jpg"],
 K894127:[131903,"circa 1987","/fpc/commerce/K894127.jpg"],
 K894293:[132066,"1989","/fpc/commerce/K894293.jpg"]
};
function audit(d){
 const err=[],fail=x=>err.push(x),s=d.source_custody||{},b=d.baselines||{},h=d.holds||{};
 if(d.schema!=="fv-skyway-287-official-archive-timeline-v1")fail("schema");
 if(s.frozen_live_wp_ledger_blob!=="c7bd43334ecd993195956448c12e4e7ed441b191"||s.image_key!=="287:5"||s.post_id!==287)fail("source_join");
 if(s.original_src!=="https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg"||s.alt!=="The old Sunshine Skyway wreckage and the later bridge replacement in Tampa Bay.")fail("original_drift");
 if(s.visitor_http!==null||s.independent_retriever_wrapper!=="404_not_origin_or_visitor")fail("invented_browser_failure");
 if(d.existing_relocation?.photo_identity_unverified!==true||d.existing_relocation?.permission!=="HOLD")fail("publisher_permission");
 if(d.rights_policy?.item_specific_release_approved!==false||!d.rights_policy?.announcement?.startsWith("https://dos.fl.gov/")||!d.rights_policy?.selection?.startsWith("https://www.floridamemory.com/"))fail("rights_policy");
 if(b.historic_posts!==61||b.historic_images!==355||b.expanded_posts!==66||b.expanded_images!==361||b.guest_confirmed_broken_total!==null||b.reported_42_verified!==false||b.percent_76_measured!==false||b.oversize_decimal_count!==15||b.oversize_stored_bytes!==47096779)fail("baseline");
 for(const [k,v] of Object.entries({source_failure_browser_confirmed:false,image_downloads:0,cache_or_mirrors:0,wordpress_writes:0,homepage_changes:0,cost_usd:0,automatic_replacements:0})){if(h[k]!==v)fail("writes_"+k);}
 if(!Array.isArray(d.entries)||d.entries.length!==5){fail("count");return err;}
 const seen=new Set();
 for(const r of d.entries){
  const spec=ids[r.catalog_id];if(!spec||seen.has(r.catalog_id)){fail("id_duplicate_or_unknown");continue;}seen.add(r.catalog_id);
  if(r.catalog_url!=="https://www.floridamemory.com/items/show/"+spec[0]||r.catalog_date!==spec[1]||r.original_catalog_image_path!==spec[2]||r.derived_official_image_url!=="https://www.floridamemory.com"+spec[2])fail("catalog_identity_"+r.catalog_id);
  if(r.catalog_method!=="WEB_INDEX_OFFICIAL_CATALOG_TEXT_AVAILABLE"||!r.scene_description||!r.collection||!r.credit)fail("catalog_provenance");
  for(const x of ["catalog_http_status","image_origin_http_status","visitor_http_status","visitor_current_src","native_px","conditional_960_px","wire_bytes","binary_hash_sha256"])if(r[x]!==null)fail("invented_"+x);
  if(r.same_photo_as_published!==false||r.rehosting_rights_verified!==false||r.rights_status!=="ITEM_REVIEW_HOLD"||r.max_width_px!==960||r.no_upscale!==true||r.decision!=="DIFFERENT_PHOTO_EDITORIAL_ALTERNATIVE_ONLY"||r.asset_binary_downloaded!==false||r.wp_upload_authorized!==false||r.post_rewrite_authorized!==false)fail("release_guard");
 }
 if(seen.size!==5)fail("missing_catalog");
 return err;
}
module.exports={audit};
if(require.main===module){const d=JSON.parse(fs.readFileSync(path.join(__dirname,"skyway_287_florida_memory_chronology_20261108.json"),"utf8"));const errors=audit(d);console.log(JSON.stringify({status:errors.length?"FAIL":"PASS",items:d.entries?.length,errors}));process.exitCode=errors.length?1:0;}
