'use strict';
/**
 * Offline 61-post paired guest-Chromium weight-claim gate. Not a browser probe.
 * Consume qa/media-recovery/browser_probe_chrome.cjs JSON from TWO full, same-
 * profile --all runs. Recompute CDP requestId attribution; never derive
 * "76% savings" from uploaded originals, cached bytes or incomplete pages.
 */
const {scopeByRequestId}=require('./request_id_wire_core.cjs');
const {assessApprovedWireAttribution}=require('./approved_wire_attribution_20261104.cjs');
const {assessPage}=require('./image_census_coverage_core.cjs');
const HTTPS=/^https:\/\/[^\s/]+\//i;
const UINT=x=>Number.isSafeInteger(x)&&x>=0;
function validateRun(run,label,errors){
 if(!run||typeof run!=='object'||Array.isArray(run)){errors.push(label+':missing_run');return null}
 if(run.mode!=='all'||run.requested_pages!==61||!Array.isArray(run.pages)||run.pages.length!==61)errors.push(label+':full_61_post_census_required');
 if(run.status!=='complete_browser_image_census'||run.image_census_coverage?.complete!==true||
   run.image_census_coverage?.confirmed_broken_count!==0||
   run.confirmed_broken_count!==0)errors.push(label+':broken_or_incomplete_census');
 if(!run.run_profile?.cache_disabled||!run.run_profile?.service_worker_bypassed||
   !run.browser_product||!['390x844','1440x900'].includes(run.viewport))
    errors.push(label+':uncached_same_profile_browser_required');
 if(!Number.isFinite(Date.parse(run.created||'')))errors.push(label+':missing_capture_time');
 const pages=new Map();let slots=0,bytes=0;
 for(const page of (Array.isArray(run.pages)?run.pages:[])){
  const id=page?.post_id;
  if(!Number.isSafeInteger(id)||id<=0||pages.has(id)){errors.push(label+':duplicate_or_bad_post_id');continue}
  pages.set(id,page);
  if(!HTTPS.test(page.url||''))errors.push(label+':invalid_page_url:'+id);
  if(page.page_result!=='inspected_browser'||!page.scroll_coverage?.complete||
    page.scroll_coverage?.state!=='full_height_scanned')
    errors.push(label+':incomplete_scroll:'+id);
  if(!UINT(page.stored_image_count)||!Array.isArray(page.stored_images)||
    page.stored_images.length!==page.stored_image_count)
     {errors.push(label+':missing_stored_slots:'+id);continue}
  slots+=page.stored_images.length;
  const seen=new Set();
  for(const s of page.stored_images){
   if(!s||s.image_key?.split(':')[0]!==String(id)||seen.has(s.image_key)||!HTTPS.test(s.stored_url||'')){
    errors.push(label+':invalid_image_key_or_url:'+id);break
   }
   seen.add(s.image_key);
  }
  const census=assessPage(page);
  if(!census.complete||census.known_broken_count!==0||census.known_loaded_count!==page.stored_image_count||
    page.image_census?.complete!==true||page.image_census?.known_broken_count!==0)
    errors.push(label+':images_not_proven_loaded:'+id);
  const wire=scopeByRequestId(page.stored_images,page.network_images);
  if(!wire.complete||page.article_wire_evidence_complete!==true||
    page.article_wire_attribution_mode!=='strict_cdp_request_id'||
    !Number.isSafeInteger(page.article_image_wire_bytes_total)||
    page.article_image_wire_bytes_total<=0||
    page.article_image_wire_bytes_total!==wire.article_bytes||
    page.matched_article_network_requests!==wire.matched_request_count||
    page.unattributed_image_wire_bytes_total!==wire.unattributed_bytes||
    page.unmeasured_article_network_requests!==0||
    !UINT(page.image_wire_bytes_total)||page.image_wire_bytes_total<wire.article_bytes||
    !UINT(page.browser_wire_bytes_total)||page.browser_wire_bytes_total<page.image_wire_bytes_total)
    errors.push(label+':article_wire_attribution_unverified:'+id);
  else bytes+=wire.article_bytes;
 }
 if(pages.size!==61||slots!==355)errors.push(label+':61_posts_355_images_required');
 return {pages,bytes,slots};
}
function validateApproval(a,oldRow,newRow){
 if(!a||a.image_key!==oldRow.image_key||a.before_source_url!==oldRow.stored_url||
  a.after_source_url!==newRow.stored_url||!HTTPS.test(a.after_source_url||''))return false;
 try{
  const p=new URL(a.after_source_url);
  const firstParty=p.hostname==='finalvestige.com'||
   (/^i\d?\.wp\.com$/.test(p.hostname)&&p.pathname.startsWith('/finalvestige.com/'));
  return firstParty&&a.rights_clearance_recorded===true&&a.same_scene_crop_review_passed===true&&
    a.no_upscale_confirmed===true&&a.publication_authorized===true&&
    Number.isSafeInteger(a.derivative_width_px)&&a.derivative_width_px>0&&a.derivative_width_px<=960&&
    Number.isSafeInteger(a.derivative_height_px)&&a.derivative_height_px>0;
 }catch{return false}
}
function assessPair(baseline,candidate,approvals=[]){
 const errors=[],b=validateRun(baseline,'baseline',errors),a=validateRun(candidate,'candidate',errors);
 if(!b||!a)return {status:'NOT_MEASURED',reasons:[...new Set(errors)],savings_percent:null};
 if(!(Date.parse(candidate.created)>Date.parse(baseline.created)))errors.push('candidate_capture_not_later');
 for(const key of ['viewport','browser_product']){
  if(baseline[key]!==candidate[key])errors.push('capture_profile_differs:'+key);
 }
 for(const key of ['cache_disabled','service_worker_bypassed','scroll_step_px','scroll_wait_ms','settle_wait_ms']){
  if(baseline.run_profile?.[key]!==candidate.run_profile?.[key])
   errors.push('capture_profile_differs:'+key);
 }
 const approved=new Map();
 if(!Array.isArray(approvals))errors.push('approval_manifest_invalid');
 else for(const row of approvals){
  if(!row||typeof row.image_key!=='string'||approved.has(row.image_key)){errors.push('duplicate_or_invalid_approval');continue}
  approved.set(row.image_key,row);
 }
 const changed=[];
 for(const [id,bp] of b.pages){
  const ap=a.pages.get(id);
  if(!ap||bp.url!==ap.url||bp.stored_image_count!==ap.stored_image_count){
   errors.push('page_or_image_count_drift:'+id);continue;
  }
  const afterSlots=new Map(ap.stored_images.map(x=>[x.image_key,x]));
  for(const oldRow of bp.stored_images){
   const newRow=afterSlots.get(oldRow.image_key);
   if(!newRow){errors.push('image_slot_drift:'+oldRow.image_key);continue}
   if(oldRow.stored_url!==newRow.stored_url){
    changed.push(oldRow.image_key);
    if(!validateApproval(approved.get(oldRow.image_key),oldRow,newRow))
      errors.push('unapproved_or_unverified_media_change:'+oldRow.image_key);
   }
  }
 }
 if([...approved.keys()].some(k=>!changed.includes(k)))errors.push('unmatched_approval_manifest_entry');
 if(errors.length||b.bytes<=0)return {status:'NOT_MEASURED',reasons:[...new Set(errors.length?errors:['baseline_zero'])],
  measured_sitewide_image_bytes_before:null,measured_sitewide_image_bytes_after:null,
  savings_percent:null,claim_76_percent_supported:false,production_changes_approved_by_this_tool:false};
 const saved=b.bytes-a.bytes,percent=saved*100/b.bytes;
 // Measured transfer savings and *attributable* optimization savings differ.
 // Without a changed approved source, CDN variability or server-side
 // recompression of an unchanged URL cannot substantiate an editorial claim.
 const attribution=assessApprovedWireAttribution(baseline,candidate,changed);
 const attributable=attribution.pass&&attribution.approved_source_savings_bytes===saved;
 return {status:'MEASURED',basis:'sum_of_61_per_page_uncached_CDPA_article_image_requestId_bytes',
  approved_source_attribution:attribution,
  optimization_claim_attributable:attributable,
  measured_post_count:61,measured_slot_count:355,approved_changed_slots:changed.sort(),
  measured_sitewide_image_bytes_before:b.bytes,measured_sitewide_image_bytes_after:a.bytes,
  savings_bytes:saved,savings_percent:Math.round(percent*100)/100,
  claim_76_percent_supported:percent>=76&&attributable,
  production_changes_approved_by_this_tool:false,
  interpretation:'Equal-weight one uncached visit per article; not a production analytics traffic-weighted result.'};
}
module.exports={validateRun,validateApproval,assessPair};
