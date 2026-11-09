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
const FROZEN_META={"source":{"repo":"finalvestigestudios/final-vestige-site-layer","ref":"65c214a1ae6e43534090584d56bbd783251e315c","path":"qa/media-recovery/parts/04.json","blob_sha":"6df3251e5a67a971d87a516a1ba4a0cc32f51f96","post_id":268,"post_title":"They Painted Over Archimedes","post_modified_snapshot":"2026-10-30T01:10:13"},"catalog_context":{"walters_project_image_bank_license_notice":"https://archimedespalimpsest.org/digital/image-bank.php","research_license":"CC BY 3.0 stated for Image Bank; narrative images not auto-cleared","commons_license_caution":"Five Flickr-origin Wikimedia files display CC BY 2.0 while underlying scholarly metadata cites CC BY 3.0. Record both, do not silently treat one as universal."},"conclusions":{"visitor_confirmed_broken_count":null,"reported_42_guest_verified":false,"reported_76_percent_wire_reduction_verified":false,"original_wp_over_1_5_decimal_MB_last_known":15,"wp_originals_stored_bytes_last_known":47096779,"approved_replacements":0,"wordpress_writes":0,"third_party_binary_downloads":0,"spend_usd":0},"evidence_scope":"FROZEN_OCT30_WORDPRESS_EDITOR_SOURCE_PLUS_NOV8_RETRIEVER_AND_PRIMARY_CATALOG; NOT FRESH WP OR BROWSER"};
const FROZEN_ITEM_TEXT=[{"post_url":"https://finalvestige.com/2026/08/18/they-painted-over-archimedes/","source_snapshot_ref":"qa/media-recovery/parts/04.json","source_kind":"wikimedia_redirect","rights_notes":"Public domain in the United States; uploader's source and visual frame still require review","relationship":"SAME_EXACT_COMMONS_FILE_TITLE_UNVERIFIED_PIXEL_IDENTITY"},{"post_url":"https://finalvestige.com/2026/08/18/they-painted-over-archimedes/","source_snapshot_ref":"qa/media-recovery/parts/04.json","source_kind":"external","rights_notes":"The scholarly Image Bank CC BY 3.0 notice does not prove the separately embedded narrative JPEG's item rights","relationship":"OFFICIAL_PROJECT_CONTEXT_UNVERIFIED_BINARY_CUSTODY"},{"post_url":"https://finalvestige.com/2026/08/18/they-painted-over-archimedes/","source_snapshot_ref":"qa/media-recovery/parts/04.json","source_kind":"wikimedia_redirect","rights_notes":"Commons Flickr-reviewed CC BY 2.0; underlying project metadata states CC BY 3.0; attribution and provenance review","relationship":"SAME_EXACT_COMMONS_FILE_TITLE_UNVERIFIED_PIXEL_IDENTITY"},{"post_url":"https://finalvestige.com/2026/08/18/they-painted-over-archimedes/","source_snapshot_ref":"qa/media-recovery/parts/04.json","source_kind":"wikimedia_redirect","rights_notes":"Commons Flickr-reviewed CC BY 2.0; project image-bank notice CC BY 3.0; attribution and image identity review","relationship":"SAME_EXACT_COMMONS_FILE_TITLE_UNVERIFIED_PIXEL_IDENTITY"},{"post_url":"https://finalvestige.com/2026/08/18/they-painted-over-archimedes/","source_snapshot_ref":"qa/media-recovery/parts/04.json","source_kind":"external","rights_notes":"The scholarly Image Bank CC BY 3.0 notice does not prove the separately embedded narrative JPEG's item rights","relationship":"OFFICIAL_PROJECT_CONTEXT_UNVERIFIED_BINARY_CUSTODY"},{"post_url":"https://finalvestige.com/2026/08/18/they-painted-over-archimedes/","source_snapshot_ref":"qa/media-recovery/parts/04.json","source_kind":"wikimedia_redirect","rights_notes":"Commons Flickr-reviewed CC BY 2.0; project metadata includes owner copyright language; further rights review","relationship":"SAME_EXACT_COMMONS_FILE_TITLE_UNVERIFIED_PIXEL_IDENTITY"},{"post_url":"https://finalvestige.com/2026/08/18/they-painted-over-archimedes/","source_snapshot_ref":"qa/media-recovery/parts/04.json","source_kind":"wikimedia_redirect","rights_notes":"Commons Flickr-reviewed CC BY 2.0; underlying project image metadata CC BY 3.0; XRF iron-map identity must be preserved","relationship":"SAME_EXACT_COMMONS_FILE_TITLE_UNVERIFIED_PIXEL_IDENTITY"},{"post_url":"https://finalvestige.com/2026/08/18/they-painted-over-archimedes/","source_snapshot_ref":"qa/media-recovery/parts/04.json","source_kind":"external","rights_notes":"The scholarly Image Bank CC BY 3.0 notice does not prove the separately embedded narrative JPEG's item rights","relationship":"OFFICIAL_PROJECT_CONTEXT_UNVERIFIED_BINARY_CUSTODY"},{"post_url":"https://finalvestige.com/2026/08/18/they-painted-over-archimedes/","source_snapshot_ref":"qa/media-recovery/parts/04.json","source_kind":"external","rights_notes":"The scholarly Image Bank CC BY 3.0 notice does not prove the separately embedded narrative JPEG's item rights","relationship":"OFFICIAL_PROJECT_CONTEXT_UNVERIFIED_BINARY_CUSTODY"},{"post_url":"https://finalvestige.com/2026/08/18/they-painted-over-archimedes/","source_snapshot_ref":"qa/media-recovery/parts/04.json","source_kind":"wikimedia_redirect","rights_notes":"Commons Flickr-reviewed CC BY 2.0; underlying project metadata copyright owner notice; Hyperides folio visual review","relationship":"SAME_EXACT_COMMONS_FILE_TITLE_UNVERIFIED_PIXEL_IDENTITY"}];
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
 if(!eq(a?.source,FROZEN_META.source)||!eq(a?.catalog_context,FROZEN_META.catalog_context)||!eq(a?.conclusions,FROZEN_META.conclusions)||a?.evidence_scope!==FROZEN_META.evidence_scope)fail('frozen_header');
 for(let i=0;i<10;i++){
  const r=a?.rows?.[i],e=EXPECTED[i];if(!keys(r,ROW_KEYS)){fail('row_keys_'+i);continue;}
  const lock=FROZEN_ITEM_TEXT[i];
  if(r.post_url!==lock.post_url||r.source_snapshot_ref!==lock.source_snapshot_ref||r.source_kind!==lock.source_kind||r.candidate?.rights_notes!==lock.rights_notes||r.candidate?.relationship!==lock.relationship)fail('frozen_rights_and_source_'+i);
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
