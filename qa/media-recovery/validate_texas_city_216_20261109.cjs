"use strict";
const PINNED_SLOTS = ["216:0","216:1","216:2","216:3","216:4","216:5"];
const PINNED_SOURCES = {"216:0":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Txcitydisasterparkinglot.jpg?width=1280","216:1":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Texas_City_Disaster_Firemen_Memorial.jpg?width=960","216:2":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Txcitydisaster5storybuilding.jpg","216:3":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Texas_-_Texas_City_-_NARA_-_68149862.jpg?width=1280","216:4":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Txcitydisasterboat.jpg","216:5":"https://commons.wikimedia.org/wiki/Special:Redirect/file/Grandcampanchor.jpg"};
const PINNED_ALTS = {"216:0":"Wrecked automobiles in a parking lot about one quarter mile from the Texas City explosion, photographed April 18, 1947.","216:1":"Memorial to the Texas City firefighters killed in the 1947 disaster.","216:2":"A damaged five-story building in Texas City two days after the 1947 explosions.","216:3":"Aerial view of the Texas City industrial waterfront from a U.S. government photographic series dating to the 1940s.","216:4":"A wrecked ship in the Texas City harbor after the 1947 explosions, associated with the High Flyer and Wilson B. Keene disaster area.","216:5":"One of the Grandcamp anchors displayed in Texas City Memorial Park after the 1947 disaster."};
const REQUIRED_FALSE = ["rights_cleared","byte_identity_verified","full_resolution_visual_check_passed","download_authorized","cache_authorized","wordpress_upload_authorized","post_block_rewrite_authorized"];
function validate(d) {
 const errors=[];
 const bad=(e)=>errors.push(e);
 if(!d||d.schema!=="fv-media-texas-city-primary-conflict-v1"||!Array.isArray(d.rows)||d.rows.length!==6)return ["invalid_schema_or_count"];
 if(d.source_inventory?.blob_sha!=="0f3dfe398a76838049cebba7cb773d5c5a0c8c69"||d.source_census?.blob_sha!=="92a904c8da1ace1f972b2f00adf1a4847dde2b99")bad("unpinned_frozen_inventory");
 if(d.reported_42_browser_confirmed!==false||d.proposed_76pct_wire_savings_measured!==false||d.rights_release_or_caching_authorized!==false)bad("unproven_release_claim");
 const seen=new Set();
 for(const r of d.rows) {
  const k=r.slot;
  if(!PINNED_SLOTS.includes(k)||seen.has(k))bad("duplicate_or_unknown_slot:"+k);
  seen.add(k);
  if(r.post_id!==216||r.stored_url!==PINNED_SOURCES[k]||r.original_alt!==PINNED_ALTS[k])bad("source_or_alt_mismatch:"+k);
  if(r.source_corpus_blob_sha!=="0f3dfe398a76838049cebba7cb773d5c5a0c8c69")bad("source_custody:"+k);
  if(r.retriever?.observation!=="TOOL_URL_NOT_ACCESSIBLE"||r.retriever?.actual_origin_http_status!==null)bad("fabricated_source_http:"+k);
  const v=r.visitor||{};
  for(const f of ["guest_browser_http_status","guest_broken","decoded_width_px","decoded_height_px","transfer_bytes","was_cached"])if(v[f]!==null)bad("fabricated_guest_field:"+k+":"+f);
  const c=r.candidate||{},dims=c.native_catalog_px,target=c.conditional_max960_px;
  if(!Array.isArray(dims)||dims.length!==2||!dims.every(n=>Number.isInteger(n)&&n>0)||!Array.isArray(target)||target.length!==2)bad("missing_geometry:"+k);
  else if(target[0]!==Math.min(960,dims[0])||target[1]!==Math.round(dims[1]*Math.min(960,dims[0])/dims[0]))bad("invalid_960_no_upscale:"+k);
  if(c.catalog_geometry_not_binary_verified!==true||c.exact_binary_or_crop_verified!==false)bad("fabricated_asset_verification:"+k);
  if(!/^https:\/\//.test(c.catalog_url||"")||!/^https:\/\//.test(c.primary_authority_url||""))bad("missing_primary_catalog:"+k);
  if(["216:0","216:2","216:4"].includes(k)&&c.source_rights_conflict!==true)bad("uh_rights_conflict_lost:"+k);
  if(k==="216:1"&&!String(c.rights_observation).includes("CC BY-SA 4.0"))bad("modern_license_lost:"+k);
  if(k==="216:5"&&(!target||target[0]!==480||target[1]!==320))bad("memorial_upscale:"+k);
  if(!r.release||REQUIRED_FALSE.some(f=>r.release[f]!==false))bad("unsafe_release_flag:"+k);
  if(r.recovery_plan?.stage!=="HOLD")bad("unsafe_recovery_status:"+k);
 }
 return errors;
}
module.exports={validate,PINNED_SLOTS,PINNED_SOURCES,PINNED_ALTS};
if(require.main===module){
 const fs=require("node:fs"),path=require("node:path");
 const p=process.argv[2]||path.join(__dirname,"texas_city_216_six_primary_rights_20261109.json");
 const errors=validate(JSON.parse(fs.readFileSync(p,"utf8")));
 if(errors.length){console.error(errors.join("\n"));process.exitCode=1}else console.log("PASS: six exact-source, guest-status-null, rights-hold records");
}
