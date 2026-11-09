'use strict';
// Offline audit integrity gate. No network or CMS writes.
const EXPECTED=[
  {
    "slot": "268:0",
    "source_url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Archimedes%20Palimpsest.jpg?width=1280",
    "source_alt": "Open page of the Archimedes Palimpsest showing the later prayer-book text written across older erased Greek mathematics and diagrams.",
    "catalog_url": "https://commons.wikimedia.org/wiki/File:Archimedes_Palimpsest.jpg",
    "rights_status": "COMMONS_PD_US_CLAIM",
    "size": [
      665,
      448
    ],
    "conditional": [
      665,
      448
    ],
    "tool": "TOOL_INACCESSIBLE"
  },
  {
    "slot": "268:1",
    "source_url": "https://archimedespalimpsest.org/assets/img/imaging_x8.jpg",
    "source_alt": "A forged painted page in the Archimedes Palimpsest covering older erased writing beneath the medieval prayer text.",
    "catalog_url": "https://www.archimedespalimpsest.org/about/imaging/capture.php",
    "rights_status": "PROJECT_SITE_STATIC_RIGHTS_UNVERIFIED",
    "size": null,
    "conditional": null,
    "tool": "WRAPPER_403"
  },
  {
    "slot": "268:2",
    "source_url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/002r-001v%20Arch13r%20Sinar%20uvblue%20norm8%20Euchologion%20up%20%289737603804%29.jpg?width=960",
    "source_alt": "Ultraviolet image of a folio from the Archimedes Palimpsest showing the medieval prayer text and faint erased undertext.",
    "catalog_url": "https://commons.wikimedia.org/wiki/File:002r-001v_Arch13r_Sinar_uvblue_norm8_Euchologion_up_(9737603804).jpg",
    "rights_status": "COMMONS_CC_BY_2_0_PROJECT_CC_BY_3_0_CONFLICT",
    "size": [
      10880,
      8160
    ],
    "conditional": [
      960,
      720
    ],
    "tool": "TOOL_INACCESSIBLE"
  },
  {
    "slot": "268:3",
    "source_url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/017r-016v%20Heiberg-UV-blue%20%289737623542%29.jpg?width=960",
    "source_alt": "Image of an Archimedes Palimpsest folio associated with Heiberg's early twentieth-century study and modern ultraviolet imaging.",
    "catalog_url": "https://commons.wikimedia.org/wiki/File:017r-016v_Heiberg-UV-blue_(9737623542).jpg",
    "rights_status": "COMMONS_CC_BY_2_0_PROJECT_CC_BY_3_0_CONFLICT",
    "size": [
      2040,
      2720
    ],
    "conditional": [
      960,
      1280
    ],
    "tool": "TOOL_INACCESSIBLE"
  },
  {
    "slot": "268:4",
    "source_url": "https://www.archimedespalimpsest.org/assets/img/imagecapture-capture2b.jpg",
    "source_alt": "A conservator handling a separated Archimedes Palimpsest leaf during preparation for imaging.",
    "catalog_url": "https://www.archimedespalimpsest.org/about/imaging/capture.php",
    "rights_status": "PROJECT_SITE_STATIC_RIGHTS_UNVERIFIED",
    "size": null,
    "conditional": null,
    "tool": "WRAPPER_403"
  },
  {
    "slot": "268:5",
    "source_url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/017r-016v%20Arch07r%20Sinar%20pseudo%20no-veil%20%289734386225%29.jpg?width=960",
    "source_alt": "Processed multispectral image of an Archimedes Palimpsest folio making the erased undertext more legible beneath the prayer book.",
    "catalog_url": "https://commons.wikimedia.org/wiki/File:017r-016v_Arch07r_Sinar_pseudo_no-veil_(9734386225).jpg",
    "rights_status": "COMMONS_CC_BY_2_0_PROJECT_CC_BY_3_0_CONFLICT",
    "size": [
      8160,
      10880
    ],
    "conditional": [
      960,
      1280
    ],
    "tool": "TOOL_INACCESSIBLE"
  },
  {
    "slot": "268:6",
    "source_url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/028v-021r%20Arch08r%20XRF%20FeFront%20registered%20%289734104759%29.jpg?width=1280",
    "source_alt": "X-ray fluorescence iron map of an Archimedes Palimpsest folio revealing erased writing through elemental imaging.",
    "catalog_url": "https://commons.wikimedia.org/wiki/File:028v-021r_Arch08r_XRF_FeFront_registered_(9734104759).jpg",
    "rights_status": "COMMONS_CC_BY_2_0_PROJECT_CC_BY_3_0_CONFLICT",
    "size": [
      8160,
      10880
    ],
    "conditional": [
      960,
      1280
    ],
    "tool": "TOOL_INACCESSIBLE"
  },
  {
    "slot": "268:7",
    "source_url": "https://archimedespalimpsest.org/assets/img/imaging_x12.jpg",
    "source_alt": "An Archimedes Palimpsest leaf mounted vertically on a scanning stage for X-ray fluorescence imaging at Stanford Synchrotron Radiation Laboratory.",
    "catalog_url": "https://www.archimedespalimpsest.org/about/imaging/capture.php",
    "rights_status": "PROJECT_SITE_STATIC_RIGHTS_UNVERIFIED",
    "size": null,
    "conditional": null,
    "tool": "WRAPPER_403"
  },
  {
    "slot": "268:8",
    "source_url": "https://archimedespalimpsest.org/assets/img/imaging_x9.jpg",
    "source_alt": "X-ray fluorescence result from a forged Archimedes Palimpsest page revealing erased ancient writing beneath the paint.",
    "catalog_url": "https://www.archimedespalimpsest.org/about/imaging/capture.php",
    "rights_status": "PROJECT_SITE_STATIC_RIGHTS_UNVERIFIED",
    "size": null,
    "conditional": null,
    "tool": "TOOL_INACCESSIBLE"
  },
  {
    "slot": "268:9",
    "source_url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/176r-173v%20Hype03r%20Sinar%20LED445-735%20pseudo%20%289734660151%29.jpg?width=960",
    "source_alt": "Processed multispectral image of a Palimpsest folio containing erased text by the Athenian orator Hyperides.",
    "catalog_url": "https://commons.wikimedia.org/wiki/File:176r-173v_Hype03r_Sinar_LED445-735_pseudo_(9734660151).jpg",
    "rights_status": "COMMONS_CC_BY_2_0_PROJECT_CC_BY_3_0_CONFLICT",
    "size": [
      6600,
      9500
    ],
    "conditional": [
      960,
      1382
    ],
    "tool": "TOOL_INACCESSIBLE"
  }
];
const ROOT_KEYS=["catalog_context","conclusions","date_local","evidence_scope","external_image_count","origin_distribution","rows","schema","source"];
const ROW_KEYS=["actions","candidate","post_id","post_url","retriever","slot","source_alt","source_kind","source_snapshot_blob","source_snapshot_ref","source_url"];
const CANDIDATE_KEYS=["attribution_finalized","binary_sha256","cache_or_rehost_authorized","catalog_native_dimensions","catalog_url","conditional_max960_dimensions","editor_visual_signoff","exact_pixel_identity_proven","relationship","rights_notes","rights_status"];
const RESULT_KEYS=["date_local","guest_browser_http_status","guest_current_src","guest_natural_dimensions","method","origin_http_status","result","uncached_transfer_bytes","visitor_broken"];
const ACTION_KEYS=["cache","download","homepage_change","wordpress_media_upload","wordpress_post_change"];
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const keys=(a,k)=>a&&typeof a==='object'&&!Array.isArray(a)&&eq(Object.keys(a).sort(),k);
const anyTrue=o=>Object.values(o).some(Boolean);
function validate(a){
 const errs=[]; const fail=x=>errs.push(x);
 if(!keys(a,ROOT_KEYS))fail('root_keys');
 if(a?.schema!=='fv-archimedes-source-rights-snapshot-v1')fail('schema');
 if(a?.date_local!=='2026-11-08')fail('date');
 if(a?.source?.blob_sha!=='6df3251e5a67a971d87a516a1ba4a0cc32f51f96' || a?.source?.post_id!==268)fail('snapshot_sha_or_post');
 if(a?.evidence_scope!=='FROZEN_OCT30_WORDPRESS_EDITOR_SOURCE_PLUS_NOV8_RETRIEVER_AND_PRIMARY_CATALOG; NOT FRESH WP OR BROWSER')fail('scope');
 if(a?.external_image_count!==10 || a?.origin_distribution?.wikimedia_redirect!==6||a?.origin_distribution?.project_site_static!==4)fail('counts');
 if(a?.rows?.length!==10)fail('count_rows');
 for(let i=0;i<10;i++){
  const r=a?.rows?.[i],e=EXPECTED[i];if(!keys(r,ROW_KEYS)){fail('row_keys_'+i);continue;}
  if(r.slot!==e.slot||r.post_id!==268||r.source_url!==e.source_url||r.source_alt!==e.source_alt||r.source_snapshot_blob!=='6df3251e5a67a971d87a516a1ba4a0cc32f51f96')fail('source_identity_'+i);
  if(r.source_kind!==(i===0||[2,3,5,6,9].includes(i)?'wikimedia_redirect':'external'))fail('source_kind_'+i);
  const v=r.retriever,c=r.candidate,ac=r.actions;
  if(!keys(v,RESULT_KEYS)||v?.method!=='web.open'||v?.date_local!=='2026-11-08'||v?.result!==e.tool||
     v?.origin_http_status!==null||v?.guest_browser_http_status!==null||v?.guest_current_src!==null||
     v?.guest_natural_dimensions!==null||v?.uncached_transfer_bytes!==null||v?.visitor_broken!==null)fail('retriever_not_browser_'+i);
  if(!keys(c,CANDIDATE_KEYS)||c?.catalog_url!==e.catalog_url||c?.rights_status!==e.rights_status||
   !eq(c?.catalog_native_dimensions,e.size)||!eq(c?.conditional_max960_dimensions,e.conditional)||
   c?.binary_sha256!==null||c?.exact_pixel_identity_proven!==false||c?.attribution_finalized!==false||
   c?.cache_or_rehost_authorized!==false||c?.editor_visual_signoff!==false)fail('candidate_hold_'+i);
  if(!keys(ac,ACTION_KEYS)||anyTrue(ac))fail('prohibited_write_'+i);
 }
 const c=a?.conclusions;
 if(c?.visitor_confirmed_broken_count!==null||c?.reported_42_guest_verified!==false||
    c?.reported_76_percent_wire_reduction_verified!==false||c?.approved_replacements!==0||
    c?.wordpress_writes!==0||c?.third_party_binary_downloads!==0||c?.spend_usd!==0)fail('false_conclusion');
 return {ok:errs.length===0,errors:errs};
}
module.exports={validate};
if(require.main===module){const fs=require('node:fs');const a=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const result=validate(a);console.log(JSON.stringify(result));process.exitCode=result.ok?0:1;}
