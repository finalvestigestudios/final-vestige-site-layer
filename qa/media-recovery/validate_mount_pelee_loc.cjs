"use strict";
const ORIGINAL={
  "413:1": {
    "stored_src": "https://tile.loc.gov/storage-services/service/pnp/stereo/1s40000/1s41000/1s41500/1s41590v.jpg",
    "loc_reproduction": "LC-DIG-stereo-1s41590",
    "loc_lccn": "98504788"
  },
  "413:3": {
    "stored_src": "https://tile.loc.gov/storage-services/service/pnp/stereo/1s40000/1s41000/1s41500/1s41518v.jpg",
    "loc_reproduction": "LC-DIG-stereo-1s41518",
    "loc_lccn": null
  },
  "413:4": {
    "stored_src": "https://tile.loc.gov/storage-services/service/pnp/stereo/1s40000/1s41000/1s41400/1s41424v.jpg",
    "loc_reproduction": "LC-DIG-stereo-1s41424",
    "loc_lccn": "2006688499"
  },
  "413:5": {
    "stored_src": "https://tile.loc.gov/storage-services/service/pnp/stereo/1s40000/1s41000/1s41500/1s41568v.jpg",
    "loc_reproduction": "LC-DIG-stereo-1s41568",
    "loc_lccn": "2004680426"
  }
};
function validate(j){
 const errors=[];
 if(!j || !Array.isArray(j.rows)) return ["rows missing"];
 if(j.post_id!==413 || j.stored_total_images!==6 || j.first_party_images!==2 || j.offsite_loc_images!==4 ||
 j.verified_loc_catalogs!==3 || j.unmatched_loc_catalogs!==1 || j.verified_visitor_requests!==0 ||
 j.wordpress_production_changes!==0 || j.rows.length!==4) errors.push("summary mismatch");
 const seen=new Set();
 for(const r of j.rows){
  if(!r || !ORIGINAL[r.key] || seen.has(r.key)){errors.push("duplicate or unknown slot");continue;}
  seen.add(r.key);
  const b=ORIGINAL[r.key];
  if(r.post_id!==413 || r.slot!==Number(r.key.split(":")[1])) errors.push("slot mismatch");
  for(const k of ["stored_src","loc_reproduction","loc_lccn"]) if(r[k]!==b[k]) errors.push("source mismatch "+k);
  if(r.source_host!=="tile.loc.gov") errors.push("host mismatch");
  if(r.loc_item_url!==(b.loc_lccn?"https://www.loc.gov/item/"+b.loc_lccn+"/":null) ||
     r.identification!==(b.loc_lccn?"exact_catalog_reproduction_number":"item_not_confirmed")) errors.push("unproven provenance");
  if(r.viewer_decode!==(r.key==="413:4"?"image_visible_in_web_viewer":"not_observed")) errors.push("viewer evidence invented");
  for(const k of ["actual_browser_http_status","actual_transfer_bytes","actual_natural_width_px","broken_in_browser",
   "original_dimensions_px","proposed_derivative_dimensions_px","original_sha256","wordpress_media_id","measured_weight_reduction_pct"])
   if(r[k]!==null) errors.push("unverified observation "+k);
  if(r.max_width_px!==960 || r.never_upscale!==true || r.rights_cleared!==false ||
     r.production_upload_approved!==false || r.production_post_edit_approved!==false) errors.push("unsafe production or sizing");
  if(typeof r.archive_note!=="string" || r.archive_note.length<40 ||
    typeof r.rights_note!=="string" || r.rights_note.length<40) errors.push("missing rights/archival note");
 }
 if(seen.size!==4) errors.push("missing source keys");
 return errors;
}
module.exports={validate};
