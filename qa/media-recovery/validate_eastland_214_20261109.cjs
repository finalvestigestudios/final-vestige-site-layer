'use strict';
/** Read-only immutable source/rights/geometry gate for Eastland post 214. No network and no CMS integration. */
const EXPECTED = [
  {
    "slot": "214:0",
    "post_id": 214,
    "source": "https://cdn.loc.gov/service/pnp/ggbain/19600/19622v.jpg",
    "alt": "SS Eastland lying on its side beside the Chicago River wharf after capsizing on July 24, 1915.",
    "catalog": "https://www.loc.gov/pictures/item/2014699553/"
  },
  {
    "slot": "214:1",
    "post_id": 214,
    "source": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Wreck_of_the_Eastland,_Chicago,_1915.jpg",
    "alt": "Panoramic view of the overturned Eastland and rescue activity along the Chicago River in 1915.",
    "catalog": "https://www.loc.gov/item/2007661460/"
  },
  {
    "slot": "214:2",
    "post_id": 214,
    "source": "https://commons.wikimedia.org/wiki/Special:Redirect/file/EastlandKenosha.jpg",
    "alt": "The tug Kenosha alongside the overturned Eastland, rescuing survivors from the exposed hull in the Chicago River.",
    "catalog": "https://commons.wikimedia.org/wiki/File:EastlandKenosha.jpg"
  },
  {
    "slot": "214:3",
    "post_id": 214,
    "source": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Helen_Repa_Eastland_Disaster_photo.png?width=1280",
    "alt": "Western Electric nurse Helen Repa assisting a victim after the Eastland disaster in Chicago.",
    "catalog": "https://commons.wikimedia.org/wiki/File:Helen_Repa_Eastland_Disaster_photo.png"
  },
  {
    "slot": "214:4",
    "post_id": 214,
    "source": "https://cdn.loc.gov/service/pnp/ggbain/19600/19623v.jpg",
    "alt": "Rescuers attempting to revive a victim of the Eastland disaster in Chicago in July 1915.",
    "catalog": "https://www.loc.gov/pictures/item/2014699554/"
  },
  {
    "slot": "214:5",
    "post_id": 214,
    "source": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Photograph_of_The_Eastland_(upside_down)_on_Chicago_River,_Chicago._-_NARA_-_281841.jpg?width=1280",
    "alt": "National Archives photograph of the overturned Eastland in the Chicago River after the 1915 disaster.",
    "catalog": "https://www.archives.gov/chicago/highlights/eastland"
  }
];
const validateData = function validateData(d,exp){
 const errs=[];
 if(d.schema!=="fv-media-eastland-214-archival-primary-custody-v1")errs.push("schema");
 if(d.source_fixture_sha!=="0f3dfe398a76838049cebba7cb773d5c5a0c8c69")errs.push("fixture_sha");
 if(d.post_id!==214||d.rows?.length!==6)errs.push("row_count_or_post");
 if(d.site_baseline?.historic_posts!==61||d.site_baseline?.historic_image_positions!==355||d.site_baseline?.historic_upstream_external_positions!==288)errs.push("historical_baseline");
 if(d.site_baseline?.historic_broken_report_unverified!==42||d.site_baseline?.guest_confirmed_broken!==0||d.site_baseline?.claimed_76_percent_cold_wire_savings_verified!==false||d.site_baseline?.wp_originals_over_1500000_bytes!==15||d.site_baseline?.wp_oversized_original_stored_bytes!==47096779)errs.push("claims_or_storage");
 if(d.measurement_policy?.guest_http_available!==false||d.measurement_policy?.actual_transferred_bytes_available!==false||d.measurement_policy?.conditional_960_dimensions_are_catalog_derived_not_browser!==true)errs.push("measurement_policy");
 const seen=new Set();
 for(const x of d.rows||[]){
  const e=exp.find(y=>y.slot===x.slot);
  if(!e||seen.has(x.slot)){errs.push("unknown_or_duplicate_slot:"+x.slot);continue}seen.add(x.slot);
  if(x.post_id!==214||x.stored_original_url!==e.source||x.stored_alt!==e.alt||x.candidate?.catalog_url!==e.catalog)errs.push("source_identity:"+x.slot);
  if(x.frozen_source_fixture?.blob_sha!==d.source_fixture_sha||x.frozen_source_fixture?.path!=="qa/media-recovery/parts/06.json")errs.push("source_custody:"+x.slot);
  const s=x.source_observation||{};
  if(s.method!=="WEB_OPEN_INDEPENDENT_RETRIEVER"||s.result!=="TOOL_INACCESSIBLE"||s.origin_http_status!==null||s.guest_http_status!==null||s.guest_current_src!==null||s.guest_natural_dimensions!==null||s.guest_encoded_transfer_bytes!==null||s.confirmed_broken!==null)errs.push("fake_browser_status:"+x.slot);
  const c=x.candidate||{}, n=c.catalog_native_dimensions_px, t=c.conditional_960px_no_upscale_dimensions_px;
  if(c.item_rights_cleared!==false||c.exact_binary_crop_proven!==false||c.visual_editor_approved!==false||!c.rights_summary||!c.historical_visual_integrity||!c.source_evidence_url||!c.accession)errs.push("copyright_or_context:"+x.slot);
  if(n===null){if(t!==null)errs.push("invented_pixels:"+x.slot)}
  else if(!Array.isArray(n)||n.length!==2||!n.every(v=>Number.isSafeInteger(v)&&v>0)||!Array.isArray(t)||t.length!==2||!t.every(v=>Number.isSafeInteger(v)&&v>0)||t[0]!==Math.min(960,n[0])||t[1]!==Math.round(n[1]*t[0]/n[0])||t[0]>n[0]||t[1]>n[1])errs.push("invalid_max_960:"+x.slot);
  const z=x.release||{};
  if(Object.values(z).some(v=>v!==false)||Object.keys(z).sort().join(",")!==["binary_download","cache_rehost","homepage_design_change","post_block_rewrite","wordpress_media_upload"].sort().join(","))errs.push("unauthorized_action:"+x.slot);
 }
 return errs;
};
module.exports = { validateData, EXPECTED };
