'use strict';
/** Read-only second-stage quality gate, using Site QA #154's existing CDP evidence.
 * No download, mirror, WordPress write, browser collector, or publication approval.
 */
const {evaluatePair}=require('./measure_image_transfer_pair_20261111.cjs');
const positive=n=>Number.isSafeInteger(n)&&n>0;
const finite=n=>typeof n==='number'&&Number.isFinite(n)&&n>0;
const hold=(reason,slot=null)=>({status:'HOLD',reason,slot,quality_preserved:false,
 measured_76_percent_with_visual_parity:false,sitewide_transfer_savings_verified:false,
 production_change_allowed:false});
const FITS=new Set(['contain','cover','fill','none','scale-down']);
const HASH64=/^[a-f0-9]{64}$/;
// URLs, dimensions and caller-provided identity labels do not prove the image
// has the same content. Explicit independent scene review is required even
// if the URL is unchanged; hashes are pointers, NOT byte-verified here.
function reviewedScene(pair,slot,b,a){
 const r=pair?.independent_visual_review?.[slot];
 return !!r && r.method==='SIDE_BY_SIDE_STAGING_SCREENSHOT_REVIEW' &&
  r.before_run_id===pair.before.run_id&&r.after_run_id===pair.after.run_id&&
  r.before_current_src===b.current_src&&r.after_current_src===a.current_src&&
  HASH64.test(r.before_screenshot_sha256)&&HASH64.test(r.after_screenshot_sha256)&&
  r.same_scene_verified===true&&r.same_crop_verified===true&&
  r.alt_fidelity_verified===true&&r.independent_editor_reviewed===true&&
  typeof r.review_evidence_url==='string'&&/^https:\/\/[^\s/]+\//.test(r.review_evidence_url);
}
function frame(row,dpr){
 if(!row||!positive(row.decoded_selected_physical_width)||
  !positive(row.decoded_selected_physical_height)||
  row.decoded_source_provenance!=='BROWSER_DECODED_CURRENT_SRC'||
  row.decoded_selected_resource_url!==row.current_src||
  !finite(row.painted_css_width)||!finite(row.painted_css_height)||
  row.image_rendered_visible!==true||!FITS.has(row.object_fit)||
  typeof row.object_position!=='string'||!row.object_position.trim())
   return {error:'MISSING_SELECTED_SOURCE_PHYSICAL_OR_PAINT_EVIDENCE'};
 // naturalWidth is potentially density-corrected: use selected-source physical pixels.
 if(row.decoded_selected_physical_width<Math.ceil(row.painted_css_width*dpr-1e-8)||
    row.decoded_selected_physical_height<Math.ceil(row.painted_css_height*dpr-1e-8))
   return {error:'LOW_DENSITY_OR_UPSCALED_SELECTED_IMAGE'};
 const ratio=row.decoded_selected_physical_width/row.decoded_selected_physical_height;
 const domRatio=row.natural_width/row.natural_height;
 if(!(Number.isFinite(domRatio)&&Math.abs(ratio-domRatio)<=Math.max(.015,ratio*.01)))
   return {error:'SELECTED_SOURCE_AND_DOM_ASPECT_DISAGREE'};
 return {ok:true};
}
function compareColdPairVisualParity(pair){
 const measured=evaluatePair(pair);
 if(measured.status!=='VERIFIED_SINGLE_POST_COLD_PAIR')
   return hold('BASE_TRANSFER_PAIR_'+measured.reason,measured.detail);
 const b=new Map(pair.before.images.map(x=>[x.slot,x]));
 const a=new Map(pair.after.images.map(x=>[x.slot,x]));
 for(const slot of pair.expected_slots){
  const prev=b.get(slot),next=a.get(slot);
  const bp=frame(prev,pair.before.dpr);
  if(!bp.ok)return hold('BASELINE_'+bp.error,slot);
  const ap=frame(next,pair.after.dpr);
  if(!ap.ok)return hold('CANDIDATE_'+ap.error,slot);
  if(prev.painted_css_width!==next.painted_css_width||
     prev.painted_css_height!==next.painted_css_height||
     prev.object_fit!==next.object_fit||
     prev.object_position!==next.object_position)
    return hold('IMAGE_PRESENTATION_OR_CROP_CHANGED',slot);
  // Preserve framing across cold runs even when a CDN keeps the same URL.
  // Aspect drift changes cover cropping, contain borders, or fill distortion.
  const baselineAspect=prev.decoded_selected_physical_width/prev.decoded_selected_physical_height;
  const candidateAspect=next.decoded_selected_physical_width/next.decoded_selected_physical_height;
  if(Math.abs(baselineAspect-candidateAspect)>
     Math.max(.0025,Math.max(baselineAspect,candidateAspect)*.005))
    return hold('SELECTED_SOURCE_ASPECT_OR_CROP_DRIFT',slot);
  if(prev.current_src!==next.current_src){
   const r=pair.independent_replacement_review?.[slot];
   if(!r||r.original_src!==prev.current_src||r.candidate_src!==next.current_src||
     r.pixel_scene_parity_verified!==true||
     r.item_level_reuse_rights_verified!==true||
     r.staging_editor_approved!==true||
     typeof r.provenance_evidence_url!=='string'||!/^https:\/\//.test(r.provenance_evidence_url)||
     typeof r.rights_evidence_url!=='string'||!/^https:\/\//.test(r.rights_evidence_url))
    return hold('SOURCE_CHANGE_NEEDS_INDEPENDENT_SCENE_RIGHTS_EDITOR_REVIEW',slot);
  }
  if(!reviewedScene(pair,slot,prev,next))
   return hold('MISSING_OR_STALE_INDEPENDENT_SCENE_REVIEW',slot);
 }
 return {...measured,status:'VERIFIED_SINGLE_POST_COLD_PAIR_WITH_VISUAL_PARITY',
  quality_preserved:true,visual_scene_review_asserted:true,
  screenshot_artifact_bytes_verified:false,
  measured_76_percent_with_visual_parity:measured.target_76_percent_met,
  sitewide_transfer_savings_verified:false,production_change_allowed:false,
  caveat:'Manual scene review and screenshot hashes are assertions; screenshot artifact bytes have NOT been checked here. No sitewide savings or publication authorization.'};
}
module.exports={compareColdPairVisualParity,frame};
