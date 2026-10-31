'use strict';
/** Offline fail-closed Palomares 367 provenance + aspect-ratio guard. No network/CMS access. */
const assert=require('node:assert/strict');
function validate(m,snapshot){
 const errors=[];
 const fail=(x)=>errors.push(x);
 if(!m||m.schema_version!==1||m.post_id!==367||m.image_count!==9||m.offsite_image_count!==8||m.source_or_catalog_records_mapped!==9)fail('scope_incorrect');
 if(m?.rights_cleared_count!==0||m?.live_broken_count_verified!==null||m?.reported_42_broken_verified!==false||m?.claimed_76_percent_reduction_verified!==false)fail('invented_success_claim');
 if(m?.cms_live_readback?.exact_nine_src_and_alt_match_snapshot!==true)fail('live_readback_missing');
 const obs=m?.source_viewer_observations;
 if(!Array.isArray(obs)||obs.length!==1||obs[0]?.image_key!=='367:4'||
    obs[0]?.exact_url!==m?.images?.[4]?.exact_stored_url||
    obs[0]?.result!=='viewer_decoded_image'||obs[0]?.http_status!==null||
    obs[0]?.natural_width_px!==null||obs[0]?.natural_height_px!==null||
    obs[0]?.content_type!==null||obs[0]?.transfer_bytes!==null||
    obs[0]?.browser_failure_conclusion!==null||obs[0]?.rights_cleared!==false)
    fail('viewer_observation_cannot_claim_browser_failure_or_rights');
 const a=m?.images||[],known=Array.isArray(snapshot)?snapshot:[];
 if(a.length!==9||known.length!==9)fail('nine_images_required');
 const seen=new Set();
 for(let i=0;i<a.length;i++){
  const v=a[i],k=known[i];if(!v||!k){fail('missing_row_'+i);continue}
  if(seen.has(v.image_key)||v.image_key!==k.key||v.slot!==i||v.post_id!==367||
     v.exact_stored_url!==k.source_url||v.stored_alt!==k.alt||v.stored_source_kind!==k.source_kind)fail('snapshot_identity_mismatch_'+i);
  seen.add(v.image_key);
  if(!/^https:\/\//.test(v.official_or_publisher_record_url||'')||!String(v.archive_record_id||'').trim())fail('missing_primary_record_'+i);
  if(!String(v.candidate_rights_basis||'').trim()||!String(v.required_credit||'').trim()||!String(v.source_chronology||'').trim())fail('missing_rights_or_chronology_'+i);
  if(v.source_binary_sha256!==null||v.exact_binary_identity_confirmed!==false||v.rights_cleared_for_republication!==false||
     v.browser_http_status!==null||v.source_asset_http_status!==null||v.actual_visitor_wire_bytes!==null||
     v.original_image_bytes_downloaded!==false||v.candidate_local_master_cached!==false||
     v.wordpress_media_id!==null||v.wordpress_upload_authorized!==false||v.post_rewrite_authorized!==false)fail('unsafe_or_fabricated_evidence_'+i);
  if(v.identity_confidence!=='catalog_filename_and_description_only'||!['REVIEW','LICENSE_CONDITIONS_REVIEW','HOLD_RIGHTS_UNKNOWN'].includes(v.rights_state))fail('overstated_identity_or_rights_'+i);
  const d=v.derivative_plan;
  if(!d||d.max_width_px!==960||d.preserve_aspect_ratio!==true||d.upscale!==false||d.manual_quality_review_required!==true||d.byte_savings_verified!==false)fail('invalid_derivative_policy_'+i);
  const w=v.source_original_width_px,h=v.source_original_height_px,tw=v.candidate_target_width_px,th=v.candidate_target_height_px;
  if(w===null||h===null){if(w!==null||h!==null||tw!==null||th!==null)fail('dimensions_must_stay_unknown_'+i)}
  else if(!Number.isSafeInteger(w)||!Number.isSafeInteger(h)||w<1||h<1||tw!==Math.min(w,960)||th!==Math.round(h*Math.min(w,960)/w)||th>h||tw>w)fail('distorted_or_upscaled_dimensions_'+i);
 }
 if(a[4]?.source_original_width_px!==null||a[4]?.rights_state!=='HOLD_RIGHTS_UNKNOWN')fail('naval_museum_thumbnail_held');
 if(a[1]?.rights_state!=='LICENSE_CONDITIONS_REVIEW'||!a[1]?.candidate_rights_basis?.includes('CC BY-SA 2.5'))fail('chrome_dome_attribution_gate');
 if(a[5]?.source_chronology?.indexOf('1971')===-1)fail('brashear_year_wrong');
 if(a[7]?.candidate_target_width_px!==500||a[8]?.candidate_target_width_px!==617)fail('small_image_upscale');
 return{ok:errors.length===0,errors,checked:a.length};
}
module.exports={validate};
