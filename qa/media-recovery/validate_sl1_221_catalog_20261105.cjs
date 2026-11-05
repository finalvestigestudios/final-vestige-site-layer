'use strict';
// Frozen seven-slot SL-1 catalog audit; offline, fail-closed, NO downloads or WordPress writes.
const PIN={
  "221:0": {
    "src": "https://commons.wikimedia.org/wiki/Special:Redirect/file/SL1nuclearpowerplant.JPG",
    "alt": "SL-1 nuclear reactor building at the National Reactor Testing Station in Idaho.",
    "w": 704,
    "h": 346,
    "file": "SL1nuclearpowerplant.JPG"
  },
  "221:1": {
    "src": "https://commons.wikimedia.org/wiki/Special:Redirect/file/SL-1_-_Cutaway_of_reactor_and_control_building.png",
    "alt": "Cutaway diagram of the SL-1 reactor and control building showing the reactor vessel and operating floor.",
    "w": 729,
    "h": 589,
    "file": "SL-1_-_Cutaway_of_reactor_and_control_building.png"
  },
  "221:2": {
    "src": "https://commons.wikimedia.org/wiki/Special:Redirect/file/SL-1_-_Reactor_schematic.png",
    "alt": "SL-1 reactor schematic showing the core, pressure vessel and control-rod arrangement.",
    "w": 1454,
    "h": 1753,
    "file": "SL-1_-_Reactor_schematic.png"
  },
  "221:3": {
    "src": "https://commons.wikimedia.org/wiki/Special:Redirect/file/US_AEC_SL-1.JPG",
    "alt": "Atomic Energy Commission crews removing the damaged SL-1 reactor core from the Idaho facility after the 1961 accident.",
    "w": 346,
    "h": 253,
    "file": "US_AEC_SL-1.JPG"
  },
  "221:4": {
    "src": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Sl-1-ineel81-3966.jpg",
    "alt": "Retrospective photograph showing severe damage inside the SL-1 reactor core after the 1961 prompt-critical excursion.",
    "w": 1406,
    "h": 1881,
    "file": "Sl-1-ineel81-3966.jpg"
  },
  "221:5": {
    "src": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Sl-1-ineel61-9.jpg",
    "alt": "Health physicists checking U.S. Highway 20 for radioactive contamination on the morning after the SL-1 accident.",
    "w": 1436,
    "h": 1113,
    "file": "Sl-1-ineel61-9.jpg"
  },
  "221:6": {
    "src": "https://commons.wikimedia.org/wiki/Special:Redirect/file/SL-1_-_Dismantling_of_the_foundation_piers.jpg",
    "alt": "Workers dismantling the SL-1 reactor foundation piers during later cleanup of the Idaho site.",
    "w": 1402,
    "h": 1050,
    "file": "SL-1_-_Dismantling_of_the_foundation_piers.jpg"
  }
};
const PIN_BLOB="9b16b828342a9ac338f3e65610fd3d8d508355e9";
function validate(x){
 const e=[];
 if(!x||x.schema!=="fv-sl1-221-archival-catalog-no-release-v1")e.push("schema");
 if(x?.frozen_source_git_blob_sha!==PIN_BLOB)e.push("frozen_blob");
 if(x?.article_post_id!==221||x?.source_slot_count!==7||x?.catalog_pages_reviewed!==7)e.push("count");
 const s=x?.sitewide_context;if(s?.frozen_posts!==61||s?.source_image_slots!==355||s?.external_source_refs!==288||s?.reported_broken_42!=="UNVERIFIED"||s?.claimed_transfer_reduction_76_percent!=="UNMEASURED"||s?.oversized_originals!==13||s?.oversized_original_storage_bytes!==43522829)e.push("false_sitewide_claim");
 if(x?.source_browser_verified_broken_count!==null||x?.guest_browser_census_complete!==false||x?.rights_or_cache_cleared!==false||x?.production_writes_authorized!==false)e.push("unsafe_global_release");
 if(!Array.isArray(x?.rows)||x.rows.length!==7)return [...e,"seven_rows_required"];
 const seen=new Set();
 for(const r of x.rows){
  if(!r||!Object.hasOwn(PIN,r.image_key)||seen.has(r.image_key)){e.push("slot_duplicate_or_unknown");continue}
  seen.add(r.image_key);const p=PIN[r.image_key],w=Math.min(960,p.w),h=Math.round(p.h*w/p.w);
  if(r.post_id!==221||r.exact_published_src!==p.src||r.published_alt!==p.alt||r.catalog_title!==p.file||r.catalog_url!=="https://commons.wikimedia.org/wiki/File:"+encodeURIComponent(p.file))e.push("source_drift:"+r.image_key);
  if(r.catalog_original_px?.width!==p.w||r.catalog_original_px?.height!==p.h||r.proposed_uncropped_px?.width!==w||r.proposed_uncropped_px?.height!==h||r.delivery_max_width_px!==960||r.no_upscale!==true||r.below_960px_master!==(p.w<960))e.push("geometry_drift:"+r.image_key);
  if(r.catalog_html_retrievable!==true||r.original_binary_downloaded!==false||r.source_binary_hash_sha256!==null||r.chrome_image_http_status!==null||r.chrome_decoded_dimensions!==null||r.chrome_transfer_bytes!==null||r.observed_broken_in_guest_browser!==null)e.push("false_browser_or_binary_proof:"+r.image_key);
  if(r.item_specific_rights_review!=="HOLD"||r.reuse_or_wp_upload_authorized!==false||typeof r.commons_license_claim!=="string"||!r.commons_license_claim.startsWith("PD-"))e.push("rights_unverified:"+r.image_key);
  if(r.conflicting_catalog_chronology!==(r.image_key==="221:6")||(r.image_key==="221:6"&&r.year_of_depicted_work_or_photo!==null))e.push("chronology_drift:"+r.image_key);
 }
 if(seen.size!==7)e.push("missing_slot");
 return [...new Set(e)];
}
if(require.main===module){const fs=require('node:fs'),path=require('node:path');try{const a=JSON.parse(fs.readFileSync(path.join(__dirname,'sl1_221_seven_catalog_20261105.json'),'utf8'));const errors=validate(a);console.log(JSON.stringify({valid:errors.length===0,errors,slots:a.rows.length,release:'HOLD'},null,2));if(errors.length)process.exitCode=1}catch(e){console.error(e);process.exitCode=1}}
module.exports={validate,PIN,PIN_BLOB};
