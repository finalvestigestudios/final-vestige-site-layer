'use strict';
const EXPECTED={
  "432:0": {
    "identifier": "PR04493",
    "source": "https://www.floridamemory.com/fpc/prints/pr04493.jpg",
    "catalog": "https://floridamemory.com/items/show/4144",
    "path": "/fpc/prints/pr04493.jpg",
    "canonical": "https://floridamemory.com/fpc/prints/pr04493.jpg"
  },
  "432:1": {
    "identifier": "RC17068",
    "source": "https://www.floridamemory.com/fpc/reference/rc17068.jpg",
    "catalog": "https://floridamemory.com/items/show/38362",
    "path": "/fpc/reference/rc17068.jpg",
    "canonical": "https://floridamemory.com/fpc/reference/rc17068.jpg"
  },
  "432:2": {
    "identifier": "RC10673",
    "source": "https://www.floridamemory.com/fpc/reference/rc10673.jpg",
    "catalog": "https://floridamemory.com/items/show/33289",
    "path": "/fpc/reference/rc10673.jpg",
    "canonical": "https://floridamemory.com/fpc/reference/rc10673.jpg"
  },
  "432:3": {
    "identifier": "N031889",
    "source": "https://www.floridamemory.com/fpc/general/n031889.jpg",
    "catalog": "https://floridamemory.com/items/show/141398",
    "path": "/fpc/general/n031889.jpg",
    "canonical": "https://floridamemory.com/fpc/general/n031889.jpg"
  },
  "432:4": {
    "identifier": "RC04344",
    "source": "https://www.floridamemory.com/fpc/reference/rc04344.jpg",
    "catalog": "https://floridamemory.com/items/show/27848",
    "path": "/fpc/reference/rc04344.jpg",
    "canonical": "https://floridamemory.com/fpc/reference/rc04344.jpg"
  },
  "432:5": {
    "identifier": "RC07668",
    "source": "https://www.floridamemory.com/fpc/reference/rc07668.jpg",
    "catalog": "https://floridamemory.com/items/show/30741",
    "path": "/fpc/reference/rc07668.jpg",
    "canonical": "https://floridamemory.com/fpc/reference/rc07668.jpg"
  },
  "432:6": {
    "identifier": "MSF-PB11548-001",
    "source": "https://www.floridamemory.com/fpc/msf/MSF-PB11548-001.jpg",
    "catalog": "https://floridamemory.com/items/show/340182",
    "path": "/fpc/msf/MSF-PB11548-001.jpg",
    "canonical": "https://floridamemory.com/fpc/msf/MSF-PB11548-001.jpg"
  }
};
function validate(a){
 const errors=[];const fail=(s)=>errors.push(s);
 if(!a||typeof a!=="object"||Array.isArray(a))return ["not_an_object"];
 if(a.schema!=="fv-florida-432-www-apex-web-wrapper-v1"||a.observed_date_utc!=="2026-11-09"||a.post_id!==432||a.post_status!=="publish"||a.post_url!=="https://finalvestige.com/2026/08/20/they-buried-the-dead-apart-okeechobee-1928/"||a.post_modified!=="2026-08-28T03:07:30")fail("wp_provenance");
 const s=a.scope||{},rights=a.rights||{},p=a.performance||{},rel=a.release||{};
 if(s.source_slots!==7||s.unique_origin_hosts!==1||s.wrapper_redirect_unavailable_count!==7||s.visitor_confirmed_broken!==null||s.not_seven_independent_outages!==true)fail("cluster_scope");
 if(rights.status!=="item-level reuse/copyright and attribution review pending"||rights.blank_catalog_rights_field_is_permission!==false||rights.cache_or_republish_approved!==false)fail("rights_hold");
 if(p.native_dimensions_verified!==false||p.verified_wire_bytes!==null||p.conditional_max_width_px!==960||p.no_upscale!==true||p.actual_960_derivatives!==null)fail("geometry_transfer_hold");
 if(rel.wordpress_writes!==0||rel.binary_downloads!==0||rel.cache_writes!==0||rel.homepage_changes!==0||rel.spend_usd!==0||rel.all_images_hold!==true)fail("release_hold");
 if(!Array.isArray(a.rows)||a.rows.length!==7)return [...new Set([...errors,"seven_slots_required"])];
 let seen=new Set();
 for (const r of a.rows){
   const e=EXPECTED[r.slot];
   if(!e||seen.has(r.slot)){fail("duplicate_or_unknown_slot");continue;} seen.add(r.slot);
   if(r.identifier!==e.identifier||r.wp_published_src!==e.source||r.official_catalog!==e.catalog||r.official_catalog_image_path!==e.path||r.conditional_canonical_origin_url!==e.canonical||r.catalog_path_matches_wp_source!==true||r.scene?.length<5)fail("exact_catalog_source_integrity");
   if(r.source_href_catalog_verified!==(r.identifier!=="RC17068"&&r.identifier!=="RC04344"&&r.identifier!=="RC07668"))fail("original_link_target_overclaim");
   const w=r.web_open||{},c=r.candidate||{};
   if(w.observed_url!==e.source||w.wrapper_status!==500||w.wrapper_label!=="REDIRECT_TARGET_INACCESSIBLE"||w.reported_redirect_to!==e.canonical||["origin_status","guest_chrome_status","guest_natural_width","guest_natural_height","guest_encoded_bytes","guest_broken"].some(k=>w[k]!==null))fail("web_wrapper_not_browser");
   if(c.is_same_archive_record!==true||c.downloaded!==false||c.byte_identical_to_published_source!==null||c.native_dimensions!==null||c.conditional_960px_dimensions!==null||c.rights_cleared!==false||c.editor_approved!==false||c.publish!==false)fail("candidate_not_cleared");
 }
 if(seen.size!==7)fail("missing_slot");
 return [...new Set(errors)];
}
module.exports={validate};
if(require.main===module){const fs=require('node:fs');const a=JSON.parse(fs.readFileSync(process.argv[2]||'qa/media-recovery/florida_432_seven_web_redirect_20261109.json','utf8'));const err=validate(a);if(err.length){console.error('HOLD '+err.join(','));process.exitCode=1}else console.log('PASS 7 Florida source URLs; 1 clustered wrapper redirect issue; guest status UNKNOWN')}
