'use strict';
// Offline verifier; Site QA #154 owns real browser capture. Never mutates WordPress.
const audit=require('./p0_primary_rights_scene_readiness_20261112.json');
const bridge=require('./browser_handoff_6_p0_15_oversize_20261110.json');
const slots=['285:5','285:2','287:5','418:1','418:2','407:1'];
function validate(a=audit,b=bridge){
 if(!a||a.schema!=='fv-p0-original-source-primary-rights-readiness-20261112-v1'||
    a.pinned_bridge_blob_sha!=='d1a9c7a499510ec37bcdba5858d45165752587e0'||
    a.site_qa_pr!==154||a.media_recovery_pr!==1703||
    a.historical?.posts!==61||a.historical?.images!==355||a.historical?.offsite!==288||
    a.historical?.reported_broken_unconfirmed!==42||
    a.historical?.oversized_originals!==15||a.historical?.oversized_stored_bytes!==47096779||
    a.historical?.wire_reduction_76_percent_measured!==false||
    a.policy?.no_wordpress_write!==true||a.policy?.no_cache!==true||
    a.policy?.no_download!==true||a.policy?.siteqa_owns_browser!==true||
    !Array.isArray(a.records)||a.records.length!==6||!Array.isArray(b.p0_queue)||b.p0_queue.length!==6)return false;
 const seen=new Set();
 for(const r of a.records){
  const origin=b.p0_queue.find(x=>x.slot===r.slot);
  if(!origin||!slots.includes(r.slot)||seen.has(r.slot)||r.post_id!==origin.post_id||
     r.exact_stored_src!==origin.original_src||
     !r.candidate_catalog?.startsWith('https://')||
     !r.rights_evidence_url?.startsWith('https://')||
     !r.scene_relation||!r.rights_tier||
     r.retriever_observation?.method!=='WEB_OPEN_WRAPPER_NOT_GUEST'||
     r.retriever_observation.code!==origin.retriever_only.wrapper_code||
     r.guest_http_status!==null||r.origin_http_status!==null||r.guest_wire_bytes!==null||
     r.exact_binary_identity_verified!==false||r.item_reuse_approved!==false||
     r.visual_editor_approved!==false||r.wordpress_upload_approved!==false)return false;
  const dim=r.conditional_960_no_upscale_px;
  if(dim!==null&&(!Array.isArray(dim)||dim.length!==2||dim.some(n=>!Number.isSafeInteger(n)||n<1)||dim[0]>960))return false;
  seen.add(r.slot);
 }
 return seen.size===6;
}
const hold=(slot,reason)=>({status:'HOLD',slot,reason,production_write_approved:false,cache_approved:false});
function triage(e){
 if(!validate())return hold(null,'FROZEN_CUSTODY_INTEGRITY_FAILED');
 const slot=e?.slot;
 if(!slots.includes(slot))return hold(slot,'UNLISTED_SLOT');
 if(e.site_qa_result==='BROWSER_VERIFIED_LOADED')return hold(slot,'ORIGINAL_VISITOR_IMAGE_LOADED_KEEP_IT');
 if(e.site_qa_result!=='BROWSER_CONFIRMED_BROKEN'||typeof e.site_qa_evidence_blob_sha!=='string'||e.site_qa_evidence_blob_sha.length!==40)
  return hold(slot,'AWAIT_SITE_QA_154_GUEST_CDP_EVIDENCE');
 if(e.exact_same_scene_verified!==true||e.photo_fingerprint_reviewed!==true)
  return hold(slot,'SOURCE_SCENE_CROP_OR_PIXEL_MATCH_UNVERIFIED');
 if(e.item_rights_checked!==true||e.source_attribution_recorded!==true)
  return hold(slot,'ITEM_RIGHTS_AND_CREDIT_HOLD');
 if(e.no_upscale_at_max_960_verified!==true||e.dpr_visual_quality_approved!==true)
  return hold(slot,'RESPONSIVE_VISUAL_HOLD');
 if(e.editor_staging_approved!==true)return hold(slot,'STAGING_EDITOR_HOLD');
 return {status:'STAGING_REVIEW_ONLY',slot,production_write_approved:false,cache_approved:false,
  next_action:'prepare_reversible_plan_for_separate_human_review_no_live_changes'};
}
module.exports={validate,triage,slots};
