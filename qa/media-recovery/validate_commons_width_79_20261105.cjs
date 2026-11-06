"use strict";
const TERMS=["map","chart","diagram","graph","document","letter","manuscript","newspaper","inscription","engraving","text","legend","label","schematic","figure","planisphere","scan","technical","table","script","blueprint","timeline","instrument","illustration"];
const TRUSTED=["05b01ce3876a62233b1bb497cdc4b1e842d487ee","fe4a33b8a0ca0d2c19d8a577d92281af0ce1e9e7","ccda35904b62ed1f2dbda09ab5001c39888b6faa","a4e0ad40652446761fdcc5f879127038255d8838","c3278c73bd6498debb541e9a52dc3df9b4fd3e61","aab2002740fcd59bb0a192d80a86a3b2e1514e26"];
function detailSensitive(alt){const tokens=(alt||"").toLowerCase().split(/[^a-z]+/);return TERMS.some(k=>tokens.some(t=>t===k||t===k+"s"));}
function validate(d){
 const e=[],bad=x=>e.push(x);
 if(!d||d.schema!=="fv-commons-1280-to-960-proposal-20261105-v1")return ["schema"];
 const b=d.underlying_census||{};
 if(b.published_posts!==66||b.inline_images!==361||b.external_origin_refs!==294||b.wikimedia_redirect_refs!==124||b.original_size_1280_requests!==79||b.affected_posts!==18)bad("source census");
 if(!Array.isArray(d.sources)||d.sources.length!==6||d.sources.some((x,i)=>x.part!==i+1||x.git_blob_sha!==TRUSTED[i]||x.source_pr!==1138))bad("source blob");
 if(!Array.isArray(d.rows)||d.rows.length!==79)return e.concat("row count");
 const keys=new Set(),originals=new Set(),posts=new Set();let sensitive=0;
 const prefix="https://commons.wikimedia.org/wiki/Special:Redirect/file/";
 for(const [i,x]of d.rows.entries()){
  const p="row "+i+":",old=x.original_url||"",rem=old.slice(prefix.length);
  if(typeof x.key!=="string"||!x.key.includes(":")||x.key.split(":")[0]!==String(x.post_id)||keys.has(x.key))bad(p+"key");
  keys.add(x.key);posts.add(x.post_id);
  if(typeof x.post_title!=="string"||!x.post_title.trim()||typeof x.post_url!=="string"||!x.post_url.startsWith("https://finalvestige.com/"))bad(p+"post");
  if(typeof x.original_alt!=="string"||!x.original_alt.trim())bad(p+"alt");
  const detail=detailSensitive(x.original_alt);if(detail)sensitive++;
  if(x.detail_sensitive!==detail||x.review_queue!==(detail?"DETAIL_FIRST":"VISUAL_PARITY")||x.quality_review_required!==true)bad(p+"quality");
  if(!old.startsWith(prefix)||!rem.endsWith("?width=1280")||rem.split("?").length!==2||rem.length<12)bad(p+"original");
  if(x.proposed_same_file_url_960!==old.slice(0,-11)+"?width=960")bad(p+"same-file URL");
  if(x.commons_file_description_page!=="https://commons.wikimedia.org/wiki/File:"+rem.slice(0,-11))bad(p+"file provenance");
  if(x.original_width_request_px!==1280||x.proposed_width_request_px!==960)bad(p+"width request");
  originals.add(old);
  for(const k of ["source_intrinsic_dimensions_px","browser_current_src","guest_browser_http_status","guest_image_decoded_dimensions","measured_cold_transfer_before_bytes","measured_cold_transfer_after_bytes","alternative_http_status","rights_license"])if(x[k]!==null)bad(p+k);
  if(x.rights_review!=="HOLD_ITEM_LEVEL")bad(p+"rights");
  for(const k of ["request_only_candidate","actual_byte_savings_unmeasured"])if(x[k]!==true)bad(p+k);
  for(const k of ["no_upscale_proven","copyright_reuse_reviewed","local_cache_approved","derivative_processing_approved","wordpress_change_approved","publication_approved"])if(x[k]!==false)bad(p+k);
 }
 if(keys.size!==79||originals.size!==79||posts.size!==18||sensitive!==b.detail_sensitive_slots)bad("aggregate cohort");
 const a=d.interpretation||{};
 for(const k of ["visitor_failure_count","measured_76_percent_wire_reduction","actual_visitor_byte_savings"])if(a[k]!==null)bad("aggregate:"+k);
 if(a.reported_42_broken!=="UNVERIFIED"||a.no_image_binary_downloaded!==true||a.production_changes!==0||a.max_proposed_request_width_px!==960||a.original_and_proposed_are_same_commons_file_path!==true||a.query_width_is_a_requested_rendition_not_verified_natural_dimensions!==true||a.candidate_960_is_neither_a_cached_binary_nor_a_license_grant!==true||a.browser_and_rights_and_visual_review_required!==true||a.no_upscale_must_be_proved_from_file_catalog_and_downloaded_lawful_binary_before_changes!==true||a.type_of_http_status!=="NULL_UNMEASURED_GUEST_ORIGIN")bad("release gate");
 return e;
}
if(typeof module!=="undefined"&&module.exports)module.exports={validate,detailSensitive};
if(typeof require!=="undefined"&&typeof module!=="undefined"&&require.main===module){
 const fs=require("node:fs");if(!process.argv[2]){console.error("usage: node validate_commons_width_79_20261105.cjs <audit.json>");process.exit(2);}
 const issues=validate(JSON.parse(fs.readFileSync(process.argv[2],"utf8")));console.log(JSON.stringify({valid:issues.length===0,issues}));if(issues.length)process.exit(1);
}
