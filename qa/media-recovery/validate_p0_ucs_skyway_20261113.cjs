'use strict';
/** Offline fail-closed source/rights gate: no network access or WordPress writes. */
const fs=require('node:fs');
const E={
  "285:2": {
    "post": 285,
    "page": "https://finalvestige.com/2026/08/19/the-light-said-closed-three-mile-island/",
    "src": "https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg",
    "candidate": "https://blog.ucs.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg",
    "catalog": "https://blog.ucs.org/dlochbaum/nuclear-plant-accidents-three-mile-island/",
    "wrapper": 500,
    "credit": "Nuclear Regulatory Commission"
  },
  "287:5": {
    "post": 287,
    "page": "https://finalvestige.com/2026/08/19/the-warning-was-a-man-waving-sunshine-skyway/",
    "src": "https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg",
    "candidate": "https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg",
    "catalog": "https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/",
    "wrapper": 404,
    "credit": "University Press of Florida"
  }
};
const fm={
  "catalog": "https://www.floridamemory.com/items/show/32083",
  "id": "RC09237",
  "image_catalog_path": "/fpc/reference/rc09237.jpg",
  "date": "1980-05-09",
  "scene": "Black-and-white photograph of car near collapsed roadway; NOT publisher ship-and-pier photograph",
  "rights_policy": "https://floridamemory.com/share/order-info/faq.php",
  "site_mark": "PDM_1_0",
  "credit": "State Archives of Florida, Florida Memory, RC09237",
  "native_px": null,
  "http_status": null,
  "exact_scene_match": false,
  "download_or_cache_allowed": false
};
function validate(a){
 const bad=[],check=(ok,k)=>{if(!ok)bad.push(k);};
 check(a?.schema==="fv-p0-ucs-skyway-archive-bridge-v1"&&a.observed_date==="2026-11-13","schema");
 check(typeof a?.methodology==="string"&&a.methodology.includes("not real origin HTTP"),"wrapper");
 check(a?.historical?.posts===61&&a.historical.inline_images===355&&a.historical.reported_broken===42&&
   a.historical.guest_confirmed_broken===null&&a.historical.measured_transfer_reduction_pct===null,"historical_unverified");
 check(a?.expanded_prior?.posts===66&&a.expanded_prior.inline_images===361&&
   a.expanded_prior.wordpress_originals_above_1500000_bytes===16&&a.expanded_prior.stored_original_bytes===49107665,"stored_not_wire");
 check(Array.isArray(a?.rows)&&a.rows.length===2&&new Set(a.rows.map(r=>r.slot)).size===2,"two_rows");
 for(const r of Array.isArray(a?.rows)?a.rows:[]){
   const e=E[r.slot];check(!!e,"known_slot");if(!e)continue;
   check(r.post_id===e.post&&r.post_url===e.page&&r.original_src===e.src&&r.wp_last_readback==="2026-11-08","original_"+r.slot);
   const o=r.observation||{};
   check(o.url===e.src&&o.retriever_wrapper_status===e.wrapper&&
     o.kind===(r.slot==="285:2"?"REDIRECT_TARGET_INACCESSIBLE":"NOT_FOUND")&&
     o.redirect_target===(r.slot==="285:2"?e.candidate:null)&&o.origin_http===null&&
     o.visitor_http===null&&o.visitor_currentSrc===null&&o.visitor_pixels===null&&o.visitor_wire_bytes===null,"no_fake_http_"+r.slot);
   const c=r.candidate||{};
   check(c.url===e.candidate&&c.catalog===e.catalog&&c.published_caption_source===e.credit&&
     c.original_file_or_crop_proven===false&&c.native_px===null&&
     c.rights_to_rehost_verified===false&&c.cache_allowed===false,"rights_source_"+r.slot);
   check(c.visual_type===(r.slot==="285:2"?"FIGURE_4_NOT_POWER_PLANT_AERIAL":"SHIP_PIER_AFTER_COLLISION"),"visual_type_"+r.slot);
   if(r.slot==="287:5"){
     const f=r.alternate_florida_archive||{};
     for(const [k,v] of Object.entries(fm))check(JSON.stringify(f[k])===JSON.stringify(v),"florida_"+k);
   }else check(!Object.hasOwn(r,"alternate_florida_archive"),"no_wrong_archive_alternative");
 }
 const rights=a?.rights||{};
 check(rights.florida_memory_policy_url===fm.rights_policy&&rights.sitewide_pdm_mark===true&&
    rights.state_archives_credit_required===true&&rights.item_donor_review_pending===true&&
    rights.applies_to_UCS_figure===false&&rights.applies_to_publisher_skyway_photo===false,"sitewide_not_transitive");
 check(a?.siteqa?.pr===154&&a.siteqa.sole_owner_of_browser_collector===true&&
   a.siteqa.required?.includes("CSS_width_and_DPR")&&a.siteqa.required?.includes("request_ID_and_redirect_chain"),"siteqa_handoff");
 const release=a?.release||{};
 check(Object.keys(release).length===8&&release.conditional_width_cap_px===960&&release.no_upscale===true&&
   release.dimensions_unverified===true&&release.downloaded_images===0&&release.rights_approved===false&&
   release.staging_or_wordpress_writes===false&&release.deploy_or_merge===false&&release.paid_spend_usd===0,"release_hold");
 return {ok:bad.length===0,reasons:[...new Set(bad)]};
}
if(require.main===module){const p=process.argv[2];if(!p){console.error('Usage: node validate_p0_ucs_skyway_20261113.cjs audit.json');process.exit(2);}const result=validate(JSON.parse(fs.readFileSync(p,'utf8')));console.log(JSON.stringify(result));if(!result.ok)process.exitCode=1;}
module.exports={validate};
