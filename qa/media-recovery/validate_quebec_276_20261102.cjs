'use strict';
function validateQuebec276(audit, frozen) {
  const errors=[];
  const fail=(x)=>errors.push(x);
  if(!audit || audit.schema!=='fv-media-quebec-276-v1'|| audit.post_id!==276 || audit.total_image_refs!==6 ||audit.external_refs!==6)fail('census_header');
  if(!Array.isArray(frozen)|| frozen.length!==6||!Array.isArray(audit?.images)||audit.images.length!==6)fail('count');
  if(audit?.live_cms_read_during_this_batch!==false ||audit?.publication_approved!==false||audit?.cache_or_download_approved!==false||audit?.word_press_write_approved!==false||audit?.rights_signoff!==false)fail('release_hold');
  if(audit?.claimed_broken_42!=='NOT_VERIFIED'||audit?.claimed_image_weight_reduction_76_percent!=='NOT_MEASURED'||audit?.confirmed_guest_browser_failures!==0)fail('unproved_metrics');
  const allowed=new Set(['IMAGE_DISPLAYED','TOOL_TIMEOUT_NO_ORIGIN_STATUS','TOOL_WRAPPER_520_NO_ORIGIN_STATUS']);
  const keys=new Set();
  for(let i=0;i<6;i++){
    const src=frozen?.[i], row=audit?.images?.[i];
    if(!src||!row){fail('missing_'+i);continue;}
    if(row.slot!==i || row.key!==`276:${i}` || row.key!==src.key ||row.post_id!==src.post_id||row.published_source_url!==src.source_url||row.source_alt!==src.alt||row.source_kind!=='external'||row.source_host!==src.source_host)fail('source_drift_'+i);
    if(keys.has(row.key))fail('duplicate_'+i);keys.add(row.key);
    if(!/^https:\/\//.test(row.published_source_url) || !row.source_alt ||row.source_alt.length<12)fail('url_alt_'+i);
    if(!allowed.has(row.viewer?.result)||row.viewer?.numeric_origin_http_status!==null||row.actual_origin_http_status!==null||row.visitor_browser_http_status!==null||row.visitor_current_src!==null||row.visitor_natural_width_px!==null||row.visitor_encoded_transfer_bytes!==null||row.broken_for_visitors!==null)fail('invented_browser_evidence_'+i);
    if(row.approved_for_localization!==false||row.visual_identity_verified!==false||row.publisher_binary_sha256!==null||row.target_max_width_px!==960)fail('publication_or_identity_'+i);
    const c=row.catalog;
    if(!c || !c.rights || typeof c.rights!=='string'||!c.relationship||!c.institution)fail('missing_provenance_'+i);
    if(c?.conditional_derivative_width_px!==null || c?.conditional_derivative_height_px!==null){
      const w=c?.original_width_px,h=c?.original_height_px,dw=c?.conditional_derivative_width_px,dh=c?.conditional_derivative_height_px;
      if(!Number.isInteger(w)||!Number.isInteger(h)||!Number.isInteger(dw)||!Number.isInteger(dh)||dw>Math.min(960,w)||dw<1||dh!==Math.round(h*dw/w))fail('geometry_'+i);
    }
    if(i===0&&(c.record_id!=='HS85/10/18815'||c.creator!=='F. E. Cudworth'||c.original_width_px!==2780||c.original_height_px!==2180))fail('british_library_id');
    if(i===2 && (!String(c.record_id).includes('NMAH-AC1026-0000002') || !/NOT license/i.test(c.rights)))fail('smithsonian_rights');
    if(i===3 &&(c.record_id!==null||c.relationship!=='no_verified_matching_original'))fail('unverified_original');
    if((i===1||i===5)&&(!/Contact|Owner requests contact/i.test(c.rights)||c.conditional_derivative_width_px!==null))fail('historicbridges_rights');
    if(i===4 &&(!/12000x9000 TIFF/.test(c.rights)||c.original_width_px!==2048))fail('tiff_derivative_distinction');
  }
  return {status:errors.length?'HOLD_INVALID':'HOLD_VALIDATED_SOURCE_ONLY',errors,verified_frozen_image_count:errors.length?0:6,visitor_broken_images_confirmed:0,production_approved:false};
}
module.exports={validateQuebec276};
