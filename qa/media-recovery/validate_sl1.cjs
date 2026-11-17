"use strict";
const fs = require("node:fs");
const path = require("node:path");
const expectedNames = [
  "SL1nuclearpowerplant.JPG",
  "SL-1_-_Cutaway_of_reactor_and_control_building.png",
  "SL-1_-_Reactor_schematic.png",
  "US_AEC_SL-1.JPG",
  "Sl-1-ineel81-3966.jpg",
  "Sl-1-ineel61-9.jpg",
  "SL-1_-_Dismantling_of_the_foundation_piers.jpg"
];
const expectedSizes = [[704,346],[729,589],[1454,1753],[346,253],[1406,1881],[1436,1113],[1402,1050]];
function validate(input) {
 const errors = [];
 const fail=(msg)=>errors.push(msg);
 const j=typeof input==="string"?JSON.parse(input):input;
 if(j.schema_version!==1 || j.wordpress_read_only_snapshot?.post_id!==221 || j.wordpress_read_only_snapshot?.matching_stored_image_count!==7) fail("snapshot/schema");
 const s=j.site_wide_context||{};
 if(s.published_posts!==61||s.source_img_refs!==355||s.stored_offsite_refs!==288||s.media_originals_over_1_5_MiB!==13||s.claimed_broken_image_count_unverified!==42||s.claimed_reduction_percent_unverified!==76) fail("site wide context");
 const v=j.verification_scope||{};
 if(v.visitor_browser_requests_measured!==false||v.exact_http_status_known!==false||v.original_binary_downloaded!==false) fail("unearned browser/binary claim");
 if(!Array.isArray(j.rows)||j.rows.length!==7) {fail("seven rows required"); return errors;}
 const seen=new Set();
 for(const r of j.rows) {
  const slot=r.slot; if(!Number.isInteger(slot)||slot<0||slot>6){fail("bad slot");continue;}
  if(seen.has(slot)) fail("duplicate slot "+slot); seen.add(slot);
  const file=expectedNames[slot], size=expectedSizes[slot];
  if(r.image_key!==`221:${slot}`||r.post_id!==221) fail("slot identity "+slot);
  if(r.original_filename!==file||r.exact_stored_url!==`https://commons.wikimedia.org/wiki/Special:Redirect/file/${file}`||r.commons_file_record_url!==`https://commons.wikimedia.org/wiki/File:${file}`) fail("source provenance "+slot);
  if(r.recorded_original_dimensions_px?.width!==size[0]||r.recorded_original_dimensions_px?.height!==size[1]) fail("recorded dimensions "+slot);
  const width=Math.min(960,size[0]), height=Math.round(width*size[1]/size[0]);
  if(r.candidate_dimensions_px?.width!==width||r.candidate_dimensions_px?.height!==height) fail("no-upscale 960px target "+slot);
  if(!r.source_credit_claim||!r.primary_archive_context_but_not_binary_proof||!r.editorial_date_caution||!r.proposed_action||!r.rights_claim_on_commons) fail("provenance/caution "+slot);
  if(r.rights_review_complete!==false||r.wp_upload_authorized!==false||r.wp_post_rewrite_authorized!==false||r.wp_cached_media_id!==null) fail("unapproved production action "+slot);
  for(const field of ["original_binary_sha256","original_asset_http_status","visitor_browser_http_status","visitor_natural_width_px","visitor_transfer_bytes","confirmed_browser_broken","measured_reduction_percent"]) if(r[field]!==null) fail("fabricated evidence "+slot+":"+field);
  if(slot===6&&!r.primary_archive_context_but_not_binary_proof.includes("67-2587")) fail("unresolved foundation photo ID");
  if(slot===3&&!r.proposed_action.includes("346px")) fail("low-res no-upscale");
 }
 if(seen.size!==7) fail("missing slot");
 return errors;
}
if(require.main===module){const target=process.argv[2]||path.join(__dirname,"sl1_primary_source_20261030.json");const bad=validate(fs.readFileSync(target,"utf8"));if(bad.length){console.error(bad.join("\\n"));process.exitCode=1}else console.log("SL-1 source-custody gate PASS: 7/7 no-upload/no-unverified-status records");}
module.exports={validate};
