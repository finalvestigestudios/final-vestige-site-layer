"use strict";
// Exact-catalog item-level visual fidelity and 960px no-upscale gate. Read-only.
const fs = require("node:fs");
const path = require("node:path");
function audit(data,parent){
 const e=[]; const fail=(x)=>e.push(x);
 if(data.schema!=="fv-commons-fine-detail-item-catalog-v1")fail("schema");
 if(data.source_ledger?.git_blob_sha!=="4c45bf5b2216bf5f0a09dbf8cd5b64136a160107")fail("source_sha");
 if(data.rows?.length!==8)fail("count");
 if(data.reported_42_broken_guest_verified!==false||data.reported_76_percent_cold_image_reduction_measured!==false)fail("unproved_claim");
 if(data.wordPress_production_writes!==0||data.image_binaries_downloaded!==0)fail("modification");
 const keys=new Set();
 const sourceMap=new Map(parent.rows.map(r=>[r.image_key,r]));
 let small=0,cc=0;
 for(const row of (data.rows||[])){
   if(keys.has(row.image_key))fail("duplicate_key");keys.add(row.image_key);
   const origin=sourceMap.get(row.image_key);
   if(!origin||origin.priority!=="CONDITIONAL_JPEG_960_QUERY_CANDIDATE")fail("candidate_missing");
   if(row.original_stored_url!==origin?.exact_stored_source_url||row.original_stored_alt!==origin?.stored_alt||row.catalog_url!==origin?.commons_file_catalog_url||row.proposed_960_url!==origin?.conditional_960_url||row.post_url!==origin?.post_url)fail("provenance_drift");
   const w=row.reported_native_px?.width,h=row.reported_native_px?.height;
   if(!Number.isInteger(w)||!Number.isInteger(h)||w<=0||h<=0) {fail("invalid_catalog_geometry");continue;}
   const max=Math.min(w,960),height=Math.round(h*max/w);
   if(row.proportional_target_px?.width!==max||row.proportional_target_px?.height!==height||row.conditional_max_width_px!==960||row.source_is_narrower_than_960!==(w<960)||row.resize_to_960_appropriate_without_upscale!==(w>=960))fail("upscale_or_aspect_violation");
   if(w<960)small++;
   if(typeof row.reported_catalog_license!=="string"||!["CC_BY_2_0","CC_BY_3_0_CATALOG_ASSERTION","CC_BY_SA_2_5","CC_BY_SA_4_0","PD_US_GOV_CATALOG_ASSERTION","PD_NASA_CATALOG_ASSERTION","PUBLIC_DOMAIN_CATALOG_ASSERTION"].includes(row.reported_catalog_license))fail("unverified_license_category");
   if(row.reported_catalog_license.startsWith("CC_"))cc++;
   if(!row.detail_risk||!row.catalog_credit_note||row.visual_detail_hold!==true||row.rights_attribution_and_publisher_review_required!==true||row.license_release_approved!==false||row.source_identity_pixel_match_verified!==false||row.cache_or_upload_authorized!==false||row.wordpress_write_authorized!==false||row.original_downloaded!==false||row.derivative_generated!==false)fail("release_gate");
   for(const field of ["guest_http_status","guest_current_src","guest_decoded_px","guest_cold_transfer_bytes","measured_transfer_savings_bytes","binary_sha256"]){if(row[field]!==null)fail("invented_"+field)}
 }
 if(small!==4||cc!==4||data.totals?.catalog_native_under_960!==small||data.totals?.cc_license_items!==cc||data.totals?.audited_exact_source_items!==8||data.totals?.detail_hold_items!==8||data.totals?.suggested_automatic_rewrites!==0||data.totals?.confirmed_guest_broken!==0)fail("totals");
 return e;
}
module.exports={audit};
if (require.main===module){const d=JSON.parse(fs.readFileSync(path.join(__dirname,"commons_8_fine_detail_catalog_20261108.json"),"utf8")); const p=JSON.parse(fs.readFileSync(path.join(__dirname,"wikimedia_118_width_960_census_20261108.json"),"utf8"));const errors=audit(d,p); console.log(JSON.stringify({status:errors.length?"FAIL":"PASS",errors,count:d.rows.length}));process.exitCode=errors.length?1:0;}
