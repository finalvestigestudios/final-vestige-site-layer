'use strict';
// Source + editorial proposal integrity. No network, browser collection, media writes or CMS writes.
const PINNED = [
 {
  slot:'287:4',
  src:'https://www.flmd.uscourts.gov/sites/flmd/files/images/figure-9-sunshine-skyway-bridge-3.jpg',
  alt:'Federal archival view of the collapsed Sunshine Skyway Bridge and Summit Venture after the May 1980 accident.',
  caption:'The collapsed span and <em>Summit Venture</em> after the accident. Federal archival image.',
  newAlt:'Oblique aerial view of broken Sunshine Skyway Bridge spans with cranes and work vessels during recovery operations.',
  newCaption:'Broken Sunshine Skyway spans with cranes and work vessels during recovery operations. Federal court-hosted image.',
  issue:'PUBLISHED_ALT_AND_CAPTION_IDENTIFY_SUMMIT_VENTURE_BUT_VISIBLE_VESSELS_ARE_NOT_IDENTIFIABLE_AS_IT',
  catalog:'https://www.flmd.uscourts.gov/sites/flmd/files/images/figure-9-sunshine-skyway-bridge-3.jpg',
  display:'https://www.flmd.uscourts.gov/sites/flmd/files/images/figure-9-sunshine-skyway-bridge-3.jpg',
  original:'IMAGE_RENDERED_NO_HTTP_STATUS'
 },
 {
  slot:'287:5',
  src:'https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg',
  alt:'The old Sunshine Skyway wreckage and the later bridge replacement in Tampa Bay.',
  caption:'The Sunshine Skyway story did not end with replacement. Engineers also changed how the new crossing dealt with vessel impact.',
  newAlt:'The freighter Summit Venture beside the collapsed original Sunshine Skyway Bridge following the May 1980 collision.',
  newCaption:'The Sunshine Skyway story did not end with replacement. Engineers also changed how the new crossing dealt with vessel impact.',
  issue:'PUBLISHED_ALT_CLAIMS_NEW_REPLACEMENT_BRIDGE_VISIBLE_BUT_IMAGE_SHOWS_1980_SHIP_AND_COLLAPSED_OLD_SPAN',
  catalog:'https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/',
  display:'https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg',
  original:'RETRIEVER_WRAPPER_404_NOT_GUEST_HTTP'
 }
];
function validate(a){
 const errors=[];
 const check=(v,s)=>{if(!v) errors.push(s);};
 const keys=(v,k,s)=>check(v&&typeof v==='object'&&!Array.isArray(v)&&Object.keys(v).sort().join('|')===k.slice().sort().join('|'),s+' exact fields');
 keys(a,['schema','date_pt','method','post_id','post_url','post_modified','context','items','policy'],'root');
 if(!a||typeof a!=='object')return {ok:false,errors};
 check(a.schema==='fv-skyway-visual-fidelity-287-v1'&&a.date_pt==='2026-11-14','schema and date');
 check(a.method==='WORDPRESS_READ_ONLY_AND_INDEPENDENT_IMAGE_VISUAL_INSPECTION','evidence method');
 check(a.post_id===287&&a.post_url==='https://finalvestige.com/2026/08/19/the-warning-was-a-man-waving-sunshine-skyway/'&&a.post_modified==='2026-11-02T21:40:01','post identity');
 const c=a.context||{};
 keys(c,['frozen_posts','frozen_inline_images','expanded_posts','expanded_inline_images','reported_broken_42_guest_confirmed','proposed_76_pct_wire_reduction_measured','oversize_originals_over_1500000_last_confirmed','oversize_stored_bytes_last_confirmed'],'historical metrics');
 check(c.frozen_posts===61&&c.frozen_inline_images===355&&c.expanded_posts===66&&c.expanded_inline_images===361&&c.reported_broken_42_guest_confirmed===false&&c.proposed_76_pct_wire_reduction_measured===false,'unmeasured/frozen cohorts');
 check(c.oversize_originals_over_1500000_last_confirmed===16&&c.oversize_stored_bytes_last_confirmed===49107665,'stored originals not wire');
 check(Array.isArray(a.items)&&a.items.length===2,'two verified scene issues');
 for(let i=0;i<PINNED.length;i++){
  const r=(a.items||[])[i]||{},p=PINNED[i];
  keys(r,['slot','published_source_url','published_alt','published_caption_html','proposed_alt','proposed_caption_html','visual_issue','source_record_url','independent_display_url','original_retriever_observation','display_retriever_observation','actual_guest_http_status','actual_guest_natural_dimensions_px','native_file_dimensions_px','guest_wire_bytes','rights_to_copy_or_cache','copyright_review_complete','same_binary_or_crop_verified','max_conditional_derivative_width_px','no_upscale','proposed_image_src_change','editorial_status','wordpress_production_write'],'slot '+i);
  check(r.slot===p.slot&&r.published_source_url===p.src&&r.published_alt===p.alt&&r.published_caption_html===p.caption,'published exact scene '+i);
  check(r.proposed_alt===p.newAlt&&r.proposed_caption_html===p.newCaption&&r.visual_issue===p.issue,'reviewed visual correction '+i);
  check(r.source_record_url===p.catalog&&r.independent_display_url===p.display&&r.original_retriever_observation===p.original&&r.display_retriever_observation==='IMAGE_RENDERED_NO_HTTP_STATUS','source/visual retriever custody '+i);
  check(r.actual_guest_http_status===null&&r.actual_guest_natural_dimensions_px===null&&r.native_file_dimensions_px===null&&r.guest_wire_bytes===null,'no fabricated real-browser evidence '+i);
  check(r.rights_to_copy_or_cache===false&&r.copyright_review_complete===false&&r.same_binary_or_crop_verified===false&&r.max_conditional_derivative_width_px===960&&r.no_upscale===true,'copyright and no-upscale '+i);
  check(r.proposed_image_src_change===false&&r.editorial_status==='REVIEW_ONLY'&&r.wordpress_production_write===false,'editorial-only change HOLD '+i);
 }
 const pol=a.policy||{};
 keys(pol,['siteqa_pr','siteqa_browser_collector_modified','image_downloads','cache_or_rehost','wordpress_production_writes','homepage_design_modified','merge_or_deploy','spend_usd'],'policy');
 check(pol.siteqa_pr===154&&pol.siteqa_browser_collector_modified===false&&pol.image_downloads===0&&pol.cache_or_rehost===false&&pol.wordpress_production_writes===0&&pol.homepage_design_modified===false&&pol.merge_or_deploy===false&&pol.spend_usd===0,'no production or collector work');
 return {ok:errors.length===0,errors,proposed_editorial_items:errors.length?0:2,guest_broken_confirmed:0,ready_for_publication:false};
}
module.exports={validate};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const filename=process.argv[2]||path.join(__dirname,'skyway_visual_fidelity_287_20261114.json');
 try{const result=validate(JSON.parse(fs.readFileSync(filename,'utf8')));console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1}
 catch(e){console.error(e.message);process.exitCode=2}
}
