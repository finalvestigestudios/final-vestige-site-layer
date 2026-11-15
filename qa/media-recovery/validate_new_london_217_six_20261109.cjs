'use strict';
// Offline audit release guard. NO network access, image reads, WP writes, or published-post edits.
const EXPECTED = {
  "217:0": {
    "url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/New_London_School_explosion.jpg?width=1280",
    "alt": "The shattered New London School after the March 18, 1937 gas explosion, with rescuers gathered around the ruins.",
    "catalog": "https://commons.wikimedia.org/wiki/File:New_London_School_explosion.jpg",
    "source": "https://newsroom.ap.org/editorial-photos-videos/detail?itemid=6663ae6645e5da11af9f0014c2589dfb&mediatype=photo",
    "native": [
      760,
      609
    ],
    "license": "COMMONS_PD_US_NOT_RENEWED_ASSERTION_NOT_INDEPENDENTLY_ADJUDICATED",
    "credit": "Associated Press; photographer unidentified"
  },
  "217:1": {
    "url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/New_London_School_before_explosion.webp?width=1280",
    "alt": "London School in East Texas before the March 1937 explosion, showing the large modern school building intact.",
    "catalog": "https://commons.wikimedia.org/wiki/File:New_London_School_before_explosion.webp",
    "source": "https://www.mysanantonio.com/entertainment/visual_arts/article/Books-chronicle-37-school-explosion-3410834.php",
    "native": [
      960,
      685
    ],
    "license": "COMMONS_PD_US_NOT_RENEWED_ASSERTION_NOT_INDEPENDENTLY_ADJUDICATED",
    "credit": "Photographer unknown; Commons cites mySanAntonio and historical newspapers"
  },
  "217:2": {
    "url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/INP_Photos_of_New_London_School_explosion.jpg?width=1280",
    "alt": "Rescuers and debris at New London School after the 1937 explosion, photographed for International News Photos.",
    "catalog": "https://commons.wikimedia.org/wiki/File:INP_Photos_of_New_London_School_explosion.jpg",
    "source": "https://www.newspapers.com/newspage/1260112112/",
    "native": [
      2861,
      2244
    ],
    "license": "COMMONS_PD_SCAN_AND_US_NOT_RENEWED_ASSERTION_REVIEW_REQUIRED",
    "credit": "International News Photos / San Antonio Light, March 19, 1937"
  },
  "217:3": {
    "url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/INP_Photos_of_New_London_School_explosion_(1).jpg?width=1280",
    "alt": "Emergency workers at the New London School ruins after the March 1937 explosion.",
    "catalog": "https://commons.wikimedia.org/wiki/File:INP_Photos_of_New_London_School_explosion_(1).jpg",
    "source": "https://www.newspapers.com/newspage/1260112112/",
    "native": [
      2457,
      1950
    ],
    "license": "COMMONS_PD_SCAN_AND_US_NOT_RENEWED_ASSERTION_REVIEW_REQUIRED",
    "credit": "International News Photos / San Antonio Light, extracted photograph 1"
  },
  "217:4": {
    "url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/INP_Photos_of_New_London_School_explosion_(2).jpg?width=1280",
    "alt": "Rescue and recovery activity among the wreckage of New London School after the gas explosion.",
    "catalog": "https://commons.wikimedia.org/wiki/File:INP_Photos_of_New_London_School_explosion_(2).jpg",
    "source": "https://www.newspapers.com/newspage/1260112112/",
    "native": [
      2457,
      1862
    ],
    "license": "COMMONS_PD_SCAN_AND_US_NOT_RENEWED_ASSERTION_REVIEW_REQUIRED",
    "credit": "International News Photos / San Antonio Light, extracted photograph 2"
  },
  "217:5": {
    "url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/New_London_School_Explosion_Memorial_-_46699056584.jpg?width=1280",
    "alt": "New London School Explosion Memorial in Texas, photographed in 2016.",
    "catalog": "https://commons.wikimedia.org/wiki/File:New_London_School_Explosion_Memorial_-_46699056584.jpg",
    "source": "https://www.flickr.com/photos/52855156@N00/46699056584/",
    "native": [
      3840,
      2160
    ],
    "license": "CC_BY_SA_2_0_GENERIC_CREDIT_LICENSE_LINK_AND_ADAPTATION_NOTICE",
    "credit": "QuesterMark"
  }
};
const EXPECTED_PART_SHA = "0f3dfe398a76838049cebba7cb773d5c5a0c8c69";
function insist(condition, why) { if(!condition) throw new Error(why); }
function validate(data) {
 insist(data && data.schema === "fv-media-new-london-217-six-source-custody-v1", "schema");
 insist(data.source_cohort.posts===61 && data.source_cohort.inline_positions===355 &&
  data.source_cohort.external_origin_positions===288, "frozen_cohort");
 insist(data.source_cohort.source_part_sha===EXPECTED_PART_SHA, "source_part_sha");
 insist(data.source_cohort.post_id===217 && data.source_cohort.as_of==="2026-10-30", "source_post");
 insist(data.evidence.redirects_tested===6 && data.evidence.external_web_retriever_not_accessible===6 &&
  data.evidence.commons_catalog_html_verified===6, "catalog_or_retrieval_counts");
 insist(data.evidence.guest_observation_performed===false && data.evidence.verified_guest_broken===0, "guest_failure_fabrication");
 insist(data.evidence.proposed_76pct_wire_reduction_measured===false &&
  data.evidence.oversize_stored_bytes_not_wire_bytes===47096779 &&
  data.evidence.wordpress_originals_over_1500000_bytes===15, "weight_claim");
 insist(data.site_qa_p0_owner.includes("#154") && data.site_qa_p0_queue.join(",")==="285:5,285:2,287:5,418:1,418:2,407:1", "existing_p0_queue");
 insist(data.editorial_alternative_not_equivalent.image_identity_verified_same_as_any_stored_slot===false &&
  data.editorial_alternative_not_equivalent.rights_for_fv_republication_cleared===false &&
  data.editorial_alternative_not_equivalent.do_not_auto_substitute===true, "substitution");
 insist(Array.isArray(data.rows)&&data.rows.length===6, "row_count");
 const slots=new Set();
 for(const row of data.rows) {
  const p=EXPECTED[row.slot]; insist(p && !slots.has(row.slot), "slot_or_duplicate");
  slots.add(row.slot);
  insist(row.post_id===217 && row.post_url===data.source_cohort.post_url, "post_identity");
  insist(row.stored_url===p.url && row.original_alt===p.alt, "original_source_alt");
  insist(row.inventory_source?.blob_sha===EXPECTED_PART_SHA, "frozen_source_sha");
  insist(row.external_retrieval?.checked_utc_date==="2026-11-09" &&
   row.external_retrieval.method==="WEB_OPEN_STORED_COMMONS_REDIRECT" &&
   row.external_retrieval.observation==="NOT_ACCESSIBLE_VIA_THIS_TOOL" &&
   row.external_retrieval.wrapper_status===null &&
   row.external_retrieval.origin_http_status===null, "wrapper_not_origin_http");
  const c=row.catalog; insist(c?.url===p.catalog && c?.underlying_source_url===p.source &&
   c?.html_readable===true && c?.catalog_metadata_not_binary_decode===true &&
   c?.credit===p.credit && c?.license_observation===p.license, "catalog_provenance_rights");
  insist(JSON.stringify(c.original_catalog_dimensions_px)===JSON.stringify(p.native), "native_catalog_geometry");
  const s=row.conditional_960px, w=Math.min(p.native[0],960), h=Math.round(p.native[1]*w/p.native[0]);
  insist(s?.max_width_px===960 && s.no_upscaling===true && s.not_a_created_derivative===true &&
   JSON.stringify(s.dimensions_px)===JSON.stringify([w,h]), "960_no_upscale_geometry");
  const visitor=row.visitor;
  for(const key of ["actual_http_status","final_current_src","image_mime","natural_width_px",
   "natural_height_px","uncached_encoded_wire_bytes","confirmed_broken"])
   insist(visitor && visitor[key]===null, "no_fabricated_guest_measurement:"+key);
  const release=row.release;
  for(const key of ["item_rights_cleared","exact_binary_identity_verified","visual_editor_approved",
   "download_authorized","cache_authorized","wordpress_media_upload_authorized","post_block_rewrite_authorized"])
   insist(release && release[key]===false,"unapproved_release:"+key);
  insist(typeof row.historical_integrity_note==="string" && row.historical_integrity_note.length>=35, "historical_integrity");
  if(row.slot==="217:0") insist(row.historical_integrity_note.includes("1937-03-17") &&
    row.historical_integrity_note.includes("1937-03-18"),"event_date_conflict");
  if(row.slot==="217:1") insist(row.historical_integrity_note.toLowerCase().includes("prior"),"before_vs_after");
  if(["217:2","217:3","217:4"].includes(row.slot))
   insist(row.historical_integrity_note.includes("crop") || row.historical_integrity_note.includes("collage"),"newspaper_crop_identity");
  if(row.slot==="217:5") insist(c.license_observation.includes("CC_BY_SA_2_0") &&
   row.historical_integrity_note.includes("2016"),"modern_creator_credits");
 }
 return {rows:6,catalog_html:6,guest_broken_confirmed:0,released:0};
}
module.exports={validate,EXPECTED};
if(require.main===module) {
 const fs=require('node:fs'); const path=require('node:path');
 const data=JSON.parse(fs.readFileSync(path.join(__dirname,'new_london_217_six_source_20261109.json'),'utf8'));
 console.log(JSON.stringify(validate(data)));
}
