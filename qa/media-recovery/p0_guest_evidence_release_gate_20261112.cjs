'use strict';
/**
 * Read-only P0 evidence intake. Site QA #154 owns the actual Chrome/CDP collector.
 * This code does NOT request images, decide copyright, write WordPress or deploy.
 * It separates suspected, observed-broken, observed-loaded and candidate-review stages.
 */
const {verifyP0ReviewEvidence,verifyP0SourceMasterEvidence}=require('./verify_p0_review_evidence_20261112.cjs');
const SHA40=/^[a-f0-9]{40}$/;
const SHA256=/^[a-f0-9]{64}$/;
const https=x=>typeof x==='string'&&/^https:\/\/[^\s/?#]+\//.test(x);
const natural=n=>Number.isSafeInteger(n)&&n>=0;
const positive=n=>Number.isSafeInteger(n)&&n>0;
const P0=Object.freeze({
 '285:5':{post_id:285,page:'https://finalvestige.com/2026/08/19/the-light-said-closed-three-mile-island/',src:'https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg',catalog:'https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg'},
 '285:2':{post_id:285,page:'https://finalvestige.com/2026/08/19/the-light-said-closed-three-mile-island/',src:'https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg',catalog:'https://www.si.edu/object/report-presidents-commission-accident-three-mile-island-need-change-legacy-tmi%3Asiris_sil_765655'},
 '287:5':{post_id:287,page:'https://finalvestige.com/2026/08/19/the-warning-was-a-man-waving-sunshine-skyway/',src:'https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg',catalog:'https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg'},
 '418:1':{post_id:418,page:'https://finalvestige.com/2026/08/20/the-lighthouse-was-gone-at-dawn-1946-tsunami/',src:'https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG',catalog:'https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/'},
 '418:2':{post_id:418,page:'https://finalvestige.com/2026/08/20/the-lighthouse-was-gone-at-dawn-1946-tsunami/',src:'https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg',catalog:'https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/'},
 '407:1':{post_id:407,page:'https://finalvestige.com/2026/08/20/the-lake-wasnt-there-yesterday-hebgen/',src:'https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg',catalog:'https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0'}
});
const BASE={production_write_allowed:false,wordpress_upload_allowed:false,third_party_cache_allowed:false,
 historical_42_broken_verified:false,sitewide_76_percent_verified:false};
// A failed request for some other image must never count as a failure of this article's original.
// Rewrites and srcset selections require independent DOM-to-request custody, not a guessed identity.
const redirectEvidenceBound=g=>{
 if(g.request_url===g.final_response_url)return true;
 const chain=g.redirect_chain;
 return g.redirect_chain_verified===true&&Array.isArray(chain)&&chain.length>=2&&chain.length<=10&&
  chain[0]?.url===g.request_url&&chain[chain.length-1]?.url===g.final_response_url&&
  new Set(chain.map(h=>h?.url)).size===chain.length&&
  chain.every((h,i)=>h&&https(h.url)&&h.cdp_request_id===g.cdp_request_id&&
   (i===chain.length-1?h.response_status===g.final_status:[301,302,303,307,308].includes(h.response_status)));
};
const hold=(reason,slot=null)=>({...BASE,status:'HOLD',reason,slot,visitor_observation:null,staging_reviewer_packet:null});
/** Packet is an attached Site QA evidence record, not a self-attested 'broken' flag.
 * A Git SHA is only a pointer, not cryptographic validation without fetching the blob.
 */
function adjudicateP0(packet,review=null,artifacts=null){
 const slot=packet?.slot,locked=P0[slot];
 if(!locked)return hold('UNRECOGNIZED_P0_SLOT',slot??null);
 const g=packet?.guest;
 if(packet.siteqa_pr!==154||packet.method!=='SITEQA154_CHROME_CDP_LOGGED_OUT_COLD'||
  !SHA40.test(packet.capture_git_blob_sha||'')||!SHA256.test(packet.screenshot_sha256||'')||
  packet.post_id!==locked.post_id||packet.page_url!==locked.page||
  packet.published_original_src!==locked.src||
  !g||!https(g.current_src)||g.current_src!==g.request_url||g.current_src!==locked.src||
  !https(g.final_response_url)||typeof g.cdp_request_id!=='string'||!g.cdp_request_id.trim()||
  g.response_event_provenance!=='CDP_NETWORK_RESPONSE_RECEIVED'||
  g.completion_event_provenance!=='CDP_NETWORK_LOADING_FINISHED'||
  g.page_http_status!==200||g.full_scroll_complete!==true||
  g.network_capture_complete!==true||g.cache_disabled!==true||
  g.was_cached!==false||g.from_disk_cache!==false||g.from_memory_cache!==false||g.from_service_worker!==false||
  !positive(g.final_status)||g.final_status<200||g.final_status>599||
  !natural(g.natural_width)||!natural(g.natural_height)||
  typeof g.image_decoded!=='boolean'||
  !positive(g.viewport_css_width)||!positive(g.viewport_css_height)||
  !(typeof g.dpr==='number'&&Number.isFinite(g.dpr)&&g.dpr>=1&&g.dpr<=5)||
  !redirectEvidenceBound(g))
  return hold('MISSING_OR_UNBOUND_ACTUAL_GUEST_CDP_EVIDENCE',slot);
 // Do not call a timeout, wrapper 403 or bare user-provided "broken" label a visitor failure.
 if(g.final_status===200&&g.image_decoded===true&&
  positive(g.natural_width)&&positive(g.natural_height))
  return {...BASE,status:'GUEST_IMAGE_LOADED_KEEP_ORIGINAL',slot,visitor_observation:'CDP_HTTP_200_AND_DECODED',staging_reviewer_packet:null};
 const httpFailed=g.final_status>=400&&g.final_status<=599&&
  g.image_decoded===false&&g.natural_width===0&&g.natural_height===0;
 const decodeFailed=g.final_status===200&&g.image_decoded===false&&
  g.natural_width===0&&g.natural_height===0&&g.decode_error_recorded===true;
 if(!httpFailed&&!decodeFailed)
  return hold('INCONSISTENT_OR_INSUFFICIENT_VISITOR_FAILURE_EVIDENCE',slot);
 const observed=httpFailed?'CDP_HTTP_FAILURE_WITH_ZERO_DECODED_PIXELS':'CDP_200_EXPLICIT_DECODE_FAILURE';
 const pending={...BASE,status:'GUEST_FAILURE_EVIDENCE_RECORDED_REVIEW_REQUIRED',slot,
  visitor_observation:observed,staging_reviewer_packet:null,
  evidence_note:'Git blob and screenshot pointers must be independently read back by Site QA; this pure function cannot authenticate a CDP capture.'};
 if(!review)return pending;
 if(review.slot!==slot||review.candidate_catalog!==locked.catalog||
   !https(review.item_rights_evidence_url)||!https(review.asset_url)||
   !SHA256.test(review.asset_sha256||'')||
   !SHA40.test(review.rights_review_git_blob_sha||'')||
   review.item_level_reuse_permission_verified!==true||
   review.credit_and_restrictions_recorded!==true||
   review.scene_and_crop_reviewed_by_editor!==true||
   review.staging_editor_approved!==true||
   !['SAME_PHOTO','DISCLOSED_EDITORIAL_ALTERNATIVE'].includes(review.replacement_mode)||
   (review.replacement_mode==='SAME_PHOTO'&&review.exact_photo_identity_verified!==true)||
   (review.replacement_mode==='DISCLOSED_EDITORIAL_ALTERNATIVE'&&
    !(typeof review.revised_alt==='string'&&review.revised_alt.trim().length>=20&&review.alternative_disclosed===true)) )
   return {...pending,reason:'SOURCE_RIGHTS_SCENE_AND_STAGING_REVIEW_INCOMPLETE'};
 const z=review.geometry;
 if(!z||![z.native_width,z.native_height,z.output_width,z.output_height].every(positive)||
  !Number.isFinite(z.painted_css_width)||z.painted_css_width<=0||
  !Number.isFinite(z.painted_css_height)||z.painted_css_height<=0||
  !Number.isFinite(z.dpr)||z.dpr<1||z.dpr>5||
  z.output_width>960||z.output_width>z.native_width||z.output_height>z.native_height||
  z.output_width<Math.ceil(z.painted_css_width*z.dpr-1e-8)||
  z.output_height<Math.ceil(z.painted_css_height*z.dpr-1e-8)||
  Math.abs(z.output_width*z.native_height-z.output_height*z.native_width)>Math.max(z.native_width,z.native_height)||
  review.compared_screenshots_at_target_dpr!==true)
  return {...pending,reason:'960PX_NATIVE_SIZE_ASPECT_OR_TARGET_DPR_VISUAL_HOLD'};
 const verification=verifyP0ReviewEvidence(packet,review,artifacts);
 if(!verification.verified)return {...pending,reason:'BYTE_BOUND_ARTIFACTS_REQUIRED:'+verification.reason};
 const master=verifyP0SourceMasterEvidence(review,artifacts);
 if(!master.verified)return {...pending,reason:'BYTE_BOUND_SOURCE_MASTER_REQUIRED:'+master.reason};
 return {...pending,status:'STAGING_REVIEW_PACKET_ELIGIBLE_NO_WRITE',reason:null,
  staging_reviewer_packet:{slot,mode:review.replacement_mode,asset_url:review.asset_url,
   output_pixels:[z.output_width,z.output_height],credit_required:true,
   source_master_sha256:master.source_master_sha256,
   source_master_raster_decode_verified:master.source_master_raster_decode_verified},
  next_action:'Independent QA must verify evidence blobs, inspect rights and screen parity; prepare reversible staging proposal only.'};
}
module.exports={adjudicateP0,P0};
