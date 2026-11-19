#!/usr/bin/env node
'use strict';
// Offline seven-source custody gate; no network, media download, or CMS mutation.
const fs=require('node:fs');
const names=["USS_Thresher_(SSN-593)_bow.jpg","USS_Thresher_(SSN-593)_launching.jpg","USS_Skylark_(ASR-20).jpg","USS_Thresher_(SSN-593)_watertight_door.jpg","Bathyscaphe_Trieste2_2.jpg","USS_Thresher_(SSN-593)_brass_pipe.jpg","USS_Thresher_(SSN-593)_rudder_sunk.jpg"];
const sources=[
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/USS_Thresher_(SSN-593)_bow.jpg?width=1280",
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/USS_Thresher_(SSN-593)_launching.jpg",
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/USS_Skylark_(ASR-20).jpg",
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/USS_Thresher_(SSN-593)_watertight_door.jpg",
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/Bathyscaphe_Trieste2_2.jpg",
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/USS_Thresher_(SSN-593)_brass_pipe.jpg",
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/USS_Thresher_(SSN-593)_rudder_sunk.jpg"
];
const sizes=[[4918,6136],[740,574],[578,737],[740,532],[1700,1349],[739,574],[740,576]];
const ids=["NH 97545","NH 97552","NH 97310","NH 97567",null,"NH 97570","NH 97557"];
const navy=[
  "https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97545.html",
  "https://www.history.navy.mil/photos/images/h97000/h97552.jpg",
  "https://www.history.navy.mil/photos/images/h97000/h97310c.htm",
  "https://www.history.navy.mil/photos/images/h97000/h97567.jpg",
  null,
  "https://www.history.navy.mil/photos/images/h97000/h97570.jpg",
  "https://www.history.navy.mil/photos/images/h97000/h97557.jpg"
];
function geometry(w,h){const s=Math.min(1,960/Math.max(w,h));return [Math.round(w*s),Math.round(h*s)];}
function validate(x){
 const bad=(msg)=>{throw Error(msg)};
 if(!x||x.schema!=="fv-thresher220-navy-seven-catalog-v1"||x.post_id!==220||x.post_url!=="https://finalvestige.com/2026/08/18/too-deep-for-the-rescue-bell/"||x.historical_modified!=="2026-10-29T18:25:46"||x.source_commit!=="4366489a68620d26592d8438b4402feb453c3166"||x.source_part_git_blob!=="9b16b828342a9ac338f3e65610fd3d8d508355e9"||x.source_part!=="qa/media-recovery/parts/05.json")bad("Source provenance drift");
 if(x.posts_historical!==61||x.authored_images_historical!==355||x.oversized_originals_count!==20||x.oversized_storage_bytes!==64385752)bad("Unsupported census reclassification");
 if(x.browser_captured!==false||x.visitor_broken_count!==null||x.reported_sitewide_42_guest_confirmed!==null||x.sitewide_76_percent_wire_verified!==false||x.current_live_post_rechecked!==false||x.production_writes!==0||x.subscription_spend!==0)bad("False visitor or release assertion");
 if(!Array.isArray(x.slots)||x.slots.length!==7)bad("Seven slots required");
 for(let i=0;i<7;i++){
  const r=x.slots[i];
  if(!r||r.slot!==`220:${i}`||r.authored_source_url!==sources[i]||r.catalog_url!==`https://commons.wikimedia.org/wiki/File:${names[i]}`)bad("Original URL/slot mismatch");
  if(r.original_redirect_tool_result!=="INACCESSIBLE_NO_NUMERIC_HTTP"||r.origin_http_status!==null||r.catalog_html_result!=="RETRIEVED"||r.catalog_http_status!==null||r.guest_current_src!==null||r.guest_status!==null||r.guest_decoded!==null||r.guest_wire_bytes!==null)bad("Invented HTTP/browser status");
  if(r.navy_accession!==ids[i]||r.navy_catalog_or_historical_image_url!==navy[i]||r.navy_url_tool_result!=="INACCESSIBLE_OR_TIMEOUT_NO_NUMERIC_HTTP")bad("Archive record substitution");
  if(!Array.isArray(r.native_catalog_dimensions_px)||r.native_catalog_dimensions_px.length!==2||r.native_catalog_dimensions_px.some((v,j)=>v!==sizes[i][j]))bad("Catalog dimension change");
  const expected=geometry(...sizes[i]);
  if(!Array.isArray(r.conditional_960px_long_edge_no_upscale)||r.conditional_960px_long_edge_no_upscale.length!==2||r.conditional_960px_long_edge_no_upscale.some((v,j)=>v!==expected[j])||Math.max(...expected)>960)bad("Bad sizing or enlargement");
  if(r.catalog_pd_claim!=="US_NAVY_US_GOVERNMENT_WORK_PUBLIC_DOMAIN"||r.item_specific_rights_review_required!==true||r.exact_binary_match_verified!==false||r.media_reuse_approved!==false||r.local_copy_approved!==false||r.cached_wp_media_approved!==false||r.production_wp_write_approved!==false||typeof r.credit!=="string"||!r.credit.startsWith("U.S. Navy"))bad("Unlicensed or unsafe migration");
 }
 return {status:"PASS_SOURCE_CATALOG_ONLY",slots:7,nhhc_accessions:6,visitor_broken_verified:null,replacements_authorized:0};
}
module.exports={validate,geometry};
if(require.main===module){try{if(!process.argv[2])throw Error('Expected manifest path');console.log(JSON.stringify(validate(JSON.parse(fs.readFileSync(process.argv[2],'utf8'))),null,2));}catch(e){console.error('HOLD '+e.message);process.exitCode=1;}}
