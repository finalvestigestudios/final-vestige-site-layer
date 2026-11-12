'use strict';
/**
 * Frozen-source binding for the 6 suspected missing images and the 11 published
 * inline >1.5MB WP originals. Offline-only consumer of Site QA #154 captures.
 * Resolves a measurement blind spot: the paired byte evaluator's ledger SHA
 * is a cohort label; it did not compare a CDP slot's stored HTML src/ALT to the
 * actual 2026-10-30 Gutenberg record. That can measure a different photograph.
 * Do not count retriever wrapper codes as visitor HTTP, or authorize a rewrite.
 */
const {compareColdPairVisualParity}=require('./compare_cold_pair_visual_parity_20261111.cjs');
const ledger=require('./priority_17_frozen_source_binding_20261111.json');
const PRIORITY_LEDGER_GIT_BLOB='f1346309322220d03ebdfb20a3558a739cdd68b9';
const BRIDGE_GIT_BLOB='d1a9c7a499510ec37bcdba5858d45165752587e0';
const hold=(reason,slot=null)=>({status:'HOLD',reason,slot,
  source_binding_verified:false,measured_transfer_savings_percent:null,
  sitewide_transfer_savings_verified:false,production_change_allowed:false});
function validateLedger(x=ledger){
 if(!x||x.schema!=='fv-priority-17-exact-frozen-source-bind-v1'||
    x.bridge_git_blob_sha!==BRIDGE_GIT_BLOB||
    x.frozen_source?.posts!==61||x.frozen_source?.inline_images!==355||
    x.frozen_source?.offsite_positions!==288||
    !Array.isArray(x.frozen_source?.part_blob_shas)||
    x.frozen_source.part_blob_shas.length!==8||
    !Array.isArray(x.rows)||x.rows.length!==17) return false;
 const keys=new Set(),groups={P0_SUSPECTED_BROKEN:0,P1_GT_1_5MB_INLINE:0};let stored=0;
 for(const row of x.rows){
  if(!row||!Number.isSafeInteger(row.post_id)||row.post_id<=0||
     typeof row.slot!=='string'||
     !new RegExp('^'+row.post_id+':\\d+$').test(row.slot)||
     keys.has(row.slot)||
     typeof row.stored_original_src!=='string'||
     !/^https:\/\/[^\s/]+\//.test(row.stored_original_src)||
     !/^https:\/\/finalvestige\.com\//.test(row.post_url)||
     typeof row.frozen_alt!=='string'||!(row.priority in groups)||
     row.guest_http_status!==null||row.guest_wire_bytes!==null||
     row.publication_approved!==false||row.candidate_rights_cleared!==false)
    return false;
  keys.add(row.slot);groups[row.priority]++;
  if(row.priority==='P0_SUSPECTED_BROKEN'){
   if(row.web_retriever_only?.method!=='RETRIEVER_NOT_GUEST_ORIGIN'||
      !Number.isSafeInteger(row.web_retriever_only.wrapper_code))return false;
  }else{
   if(!Number.isSafeInteger(row.stored_original_bytes)||
      row.stored_original_bytes<=1500000||!Number.isSafeInteger(row.media_id)||
      !Array.isArray(row.native_media_dimensions_px)||
      row.native_media_dimensions_px.some(n=>!Number.isSafeInteger(n)||n<=0)||
      !Array.isArray(row.conditional_no_upscale_960px)||
      row.conditional_no_upscale_960px.length!==2||
      row.conditional_no_upscale_960px[0]>960||
      row.conditional_no_upscale_960px.some(n=>!Number.isSafeInteger(n)||n<=0))
    return false;
   stored+=row.stored_original_bytes;
  }
 }
 return keys.size===17 && groups.P0_SUSPECTED_BROKEN===6 &&
   groups.P1_GT_1_5MB_INLINE===11 && stored===38480915;
}
function sourceRow(slot){return ledger.rows.find(x=>x.slot===slot)||null}
/** Does not adjudicate broken or displayed. Site QA #154 runs the P0 gate. */
function boundP0Evidence(slot,evidence){
 if(!validateLedger())return hold('PINNED_LEDGER_SCHEMA_INVALID',slot);
 const row=sourceRow(slot);
 if(!row||row.priority!=='P0_SUSPECTED_BROKEN')return hold('NOT_A_PINNED_P0',slot);
 if(!evidence||evidence.post_id!==row.post_id||
    evidence.page_url!==row.post_url||
    evidence.stored_inline_ordinal!==Number(slot.split(':')[1])||
    evidence.stored_original_src!==row.stored_original_src||
    evidence.dom_img_src!==row.stored_original_src||
    evidence.dom_alt!==row.frozen_alt)
    return hold('P0_GUEST_SOURCE_NOT_PINNED',slot);
 return {status:'SOURCE_BOUND_ONLY_SITE_QA_P0_ADJUDICATION_REQUIRED',
   slot,source_binding_verified:true,observed_guest_http_status:null,
   source_retriever_wrapper_code:row.web_retriever_only.wrapper_code,
   confirmed_broken:false,sitewide_transfer_savings_verified:false,
   production_change_allowed:false};
}
/** The second-stage quality gate is called ONLY after exact frozen URL+ALT proof. */
function comparePrioritySourceBoundVisualPair(pair){
 if(!validateLedger())return hold('PINNED_LEDGER_SCHEMA_INVALID');
 if(!pair||!Number.isSafeInteger(pair.post_id)||!Array.isArray(pair.expected_slots)||
    pair.expected_slots.length<1||new Set(pair.expected_slots).size!==pair.expected_slots.length||
    !pair.before||!pair.after||
    !Array.isArray(pair.before.images)||!Array.isArray(pair.after.images)||
    pair.source_ledger_blob_sha!==BRIDGE_GIT_BLOB)
  return hold('PAIR_SCHEMA_OR_FROZEN_BRIDGE_MISMATCH');
 const before=new Map(pair.before.images.map(i=>[i.slot,i]));
 const after=new Map(pair.after.images.map(i=>[i.slot,i]));
 for(const slot of pair.expected_slots){
  const bound=sourceRow(slot);
  if(!bound)return hold('SLOT_NOT_IN_17_PRIORITY_LEDGER',slot);
  if(bound.priority!=='P1_GT_1_5MB_INLINE')
   return hold('P0_GUEST_BROKEN_TRIAGE_REQUIRED_BEFORE_PERFORMANCE',slot);
  if(bound.post_id!==pair.post_id||
     pair.before.page_url!==bound.post_url||
     pair.after.page_url!==bound.post_url)
   return hold('PINNED_POST_ID_OR_PERMALINK_MISMATCH',slot);
  const b=before.get(slot),a=after.get(slot);
  if(!b||!a||
     b.stored_original_src!==bound.stored_original_src||
     a.stored_original_src!==bound.stored_original_src||
     b.dom_img_src!==bound.stored_original_src||
     a.dom_img_src!==bound.stored_original_src||
     b.dom_alt!==bound.frozen_alt||a.dom_alt!==bound.frozen_alt)
   return hold('FROZEN_STORED_URL_OR_ALT_MISMATCH',slot);
 }
 // Other frozen inline slots on the article are not represented by this pair.
 // Never promote any measured subset to a site-wide, full-article or CWV claim.
 const result=compareColdPairVisualParity(pair);
 if(result.status!=='VERIFIED_SINGLE_POST_COLD_PAIR_WITH_VISUAL_PARITY')
  return hold('SECOND_STAGE_'+(result.reason||'UNVERIFIED'),result.slot||null);
 return {...result,status:'VERIFIED_PRIORITY_SUBSET_SOURCE_BOUND_VISUAL_PAIR',
   frozen_source_ledger_git_blob:PRIORITY_LEDGER_GIT_BLOB,
   source_binding_verified:true,full_post_image_census_verified:false,
   sitewide_transfer_savings_verified:false,production_change_allowed:false,
   caveat:'Measured only pinned inline slots from one post; neither full-page nor sitewide savings. Browser capture + independent rights approval remain prerequisites.'};
}
module.exports={validateLedger,boundP0Evidence,comparePrioritySourceBoundVisualPair,
  PRIORITY_LEDGER_GIT_BLOB,BRIDGE_GIT_BLOB};
