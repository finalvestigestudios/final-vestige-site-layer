'use strict';
const expected={
"432:0":["PR04493","/fpc/prints/pr04493.jpg","https://floridamemory.com/items/show/4144","1928"],
"432:1":["RC17068","/fpc/reference/rc17068.jpg","https://www.floridamemory.com/items/show/38362","1928-09"],
"432:2":["RC10673","/fpc/reference/rc10673.jpg","https://floridamemory.com/items/show/33289","1928"],
"432:4":["RC04344","/fpc/reference/rc04344.jpg","https://floridamemory.com/items/show/27848","1928"],
"432:5":["RC07668","/fpc/reference/rc07668.jpg","https://floridamemory.com/items/show/30741","1928"]
};
function validate(a){
 const errors=[];
 const fail=(x)=>errors.push(x);
 if(a?.schema!=="fv-florida-five-catalog-redirect-v1")fail("schema");
 if(a?.pinned_prior_blob_sha!=="c6f34b00e4173d7ce2247b351695ed1ff39688f5")fail("source_pin");
 if(a?.scope?.post_id!==432||a?.scope?.new_exact_catalog_records!==5||a?.scope?.known_catalog_records_total!==7)fail("cohort");
 if(a?.scope?.historical_posts!==61||a?.scope?.historical_inline_images!==355)fail("historical_denominator");
 if(a?.guest_42_failures_verified!==false||a?.visitor_76_percent_savings_measured!==false)fail("unsupported_claim");
 if(a?.oversize?.originals_over_1500000!==20||a?.oversize?.stored_bytes!==64385752||a?.oversize?.guest_transfer_bytes!==null)fail("stored_not_wire");
 if(a?.site_qa_owner!=="PR154 existing guest-browser collector"||a?.decision!=="HOLD")fail("handoff");
 if(a?.downloads!==0||a?.wordpress_writes!==0||a?.homepage_design_changes!==0||a?.spend!==0)fail("unauthorized_action");
 if(a?.rights_faq!=="https://floridamemory.com/share/order-info/faq.php")fail("rights_policy");
 if(!Array.isArray(a?.rows)||a.rows.length!==5)fail("row_count");
 const seen=new Set();
 for(const r of a?.rows||[]){
  const e=expected[r.slot];
  if(!e||seen.has(r.slot)){fail("invalid_or_duplicate_slot");continue}
  seen.add(r.slot);
  const [id,path,catalogURL,date]=e;
  if(r.post_id!==432||r.accession!==id||r.catalog_image_path!==path||r.catalog_url!==catalogURL||r.catalog_date!==date)fail(r.slot+":catalog");
  if(r.catalog_evidence_method!=="INDEXED_OFFICIAL_CATALOG_SEARCH_EXTRACT"||r.catalog_access!=="DIRECT_GET_TOOL_BLOCKED")fail(r.slot+":catalog_method");
  if(r.edit_url!=="https://www.floridamemory.com"+path||!r.jetpack_view_url.startsWith("https://i0.wp.com/www.floridamemory.com"+path))fail(r.slot+":source");
  if(r.canonical_image_url!=="https://floridamemory.com"+path)fail(r.slot+":canonical");
  const t=r.retriever||{};
  if(t.requested_url!==r.edit_url||t.tool_error_code!==500||t.tool_error_reason!=="REDIRECT_DESTINATION_INACCESSIBLE_TO_RETRIEVER"||t.redirect_target!==r.canonical_image_url||t.origin_http_status!==null)fail(r.slot+":tool_not_browser");
  if(r.jetpack_reader!=="INACCESSIBLE_UNKNOWN_STATUS")fail(r.slot+":jetpack_unknown");
  for(const k of ["guest_current_src","guest_http_status","guest_decode","guest_transfer_bytes","guest_screenshot","decoded_native_dimensions","proposed_review_dimensions","binary_sha256"]){if(r[k]!==null)fail(r.slot+":"+k)}
  if(r.cap_width_no_upscale_px!==960||r.source_rights_mark!=="PDM_1_0_NO_KNOWN_COPYRIGHT_RESTRICTIONS"||r.source_credit!=="State Archives of Florida, Florida Memory"||r.item_rights_review!=="HOLD")fail(r.slot+":rights_geometry");
  if(r.pixel_and_crop_identical!==false||r.cache_authorized!==false||r.staging_authorized!==false||r.post_rewrite_authorized!==false)fail(r.slot+":release");
  if(typeof r.existing_alt!=="string"||!r.existing_alt.trim()||typeof r.editorial_caveat!=="string"||!r.editorial_caveat.trim()||!/^2026-/.test(r.wp_modified))fail(r.slot+":metadata");
 }
 if(seen.size!==5)fail("coverage");
 return {ok:errors.length===0,errors,decision:"HOLD"};
}
module.exports={validate};
if(require.main===module){
 const fs=require("node:fs");
 const file=process.argv[2]||"qa/media-recovery/florida432_five_catalog_redirect_custody_20261116_1326pt.json";
 const result=validate(JSON.parse(fs.readFileSync(file,"utf8")));
 console.log(JSON.stringify(result));
 process.exitCode=result.ok?0:1;
}
