'use strict';
/** Offline West Loch NHHC archival/provenance audit. Never mutates WordPress or fetches media. */
const EXPECTED=new Map([
 ['370:0',['80-G-276907','1944-05-21',4320,4530]],
 ['370:1',['80-G-202485','1943-11-06',5860,4890]],
 ['370:3',['80-G-276940','1944-05-22',6254,5002]],
 ['370:4',['SC-427947','1944-05-22',6084,4942]]
]);
function validate(a,census){
 const errors=[];
 if(a?.schema!=='fv.media_recovery.nhhc_west_loch.v1'||a?.post_id!==370||a?.audit_date!=='2026-11-02')errors.push('audit_identity');
 if(a?.source_census_git_blob_sha!=='48e1ebf07207e948ba5802e714eb39659d2e1c1d')errors.push('frozen_census_blob');
 if(a?.verified_42_broken_claim!==false||a?.verified_76_percent_weight_reduction!==false||a?.production_repairs!==0)errors.push('unsupported_global_claim');
 if(!a?.rights_policy_url?.startsWith('https://www.history.navy.mil/'))errors.push('official_rights_policy_missing');
 const originals=(census?.images||[]).filter(x=>x.post_id===370);
 if(originals.length!==8||a?.scope?.stored_image_references!==8||
   a?.scope?.direct_nhhc_imageDownload_references!==4||
   a?.scope?.existing_firstparty_references!==4||!Array.isArray(a?.entries)||a.entries.length!==8)
  errors.push('scope_counts');
 const seen=new Set();
 for(let i=0;i<(a?.entries||[]).length;i++){
  const r=a.entries[i],s=originals[i];if(!r||!s){errors.push('entry_missing');continue}
  if(r.image_key!==s.key||r.post_id!==370||seen.has(r.image_key))errors.push('image_slot_identity');
  seen.add(r.image_key);
  if(r.source_url!==s.source_url||r.source_kind!==s.source_kind||r.stored_alt!==s.alt||
     r.source_census_blob_sha!==a.source_census_git_blob_sha)errors.push('published_source_identity:'+r.image_key);
  if(r.guest_browser_checked!==false||r.guest_http_status!==null||r.current_src!==null||
     r.decoded_width_px!==null||r.decoded_height_px!==null||r.transfer_bytes!==null||
     r.verified_broken_in_browser!==null)errors.push('fabricated_guest_metrics:'+r.image_key);
  const exp=EXPECTED.get(r.image_key);
  if(exp){
   if(r.handling!=='primary_catalog_match_defer_browser_rights_identity'||!r.independent_retrieval||
     r.independent_retrieval.method!=='web_open_exact_stored_url'||
     !['timeout_no_status','not_accessible_no_status'].includes(r.independent_retrieval.outcome)||
     r.independent_retrieval.http_status!==null)errors.push('retriever_evidence:'+r.image_key);
   const c=r.candidate;
   if(!c||c.catalog_number!==exp[0]||c.photograph_date!==exp[1]||
      !c.catalog_url?.startsWith('https://www.history.navy.mil/')||
      !['official_NHHC_page_open','official_NHHC_search_index'].includes(c.catalog_observation)||
      c.kind!=='catalog_identity_by_archival_id_not_binary_hash')errors.push('catalog_identity:'+r.image_key);
   if(!c?.rights_note||!c?.credit||c.identity_hash_checked!==false||
      c.rights_cleared_for_rehosting!==false||c.wp_media_upload_allowed!==false||
      c.post_rewrite_allowed!==false)errors.push('rights_or_publication_gate:'+r.image_key);
   if(c?.resize_limit_px!==960||c.no_upscaling!==true||
      c.candidate_binary_dimensions_px!==null||c.proposed_derived_dimensions_px?.width!==null||
      c.proposed_derived_dimensions_px?.height!==null||
      !/NOT verified intrinsic/.test(c.medium_rendition_catalog_label||''))errors.push('no_invented_resize:'+r.image_key);
   if(c?.catalog_high_tiff_reported_dimensions_px?.width!==exp[2]||
      c.catalog_high_tiff_reported_dimensions_px?.height!==exp[3])errors.push('catalog_high_tiff_metadata:'+r.image_key);
   try{
    const src=new URL(r.source_url),locator=src.searchParams.get('image');
    if(src.hostname!=='www.history.navy.mil'||src.pathname!=='/bin/imageDownload'||
       !locator?.endsWith('/'+exp[0])||!src.searchParams.get('rendition'))errors.push('imageDownload_selector:'+r.image_key);
   }catch{errors.push('imageDownload_invalid_url:'+r.image_key)}
  }else{
   if(r.source_kind!=='first_party'||r.candidate!==null||r.independent_retrieval!==null||
      r.handling!=='already_first_party_retain_no_auto_edit')errors.push('first_party_retention:'+r.image_key);
  }
  if(r.image_key==='370:1'&&!/NOT a West Loch/.test(r.candidate?.scene||''))
   errors.push('1943_comparison_scene_disclosure');
  if(r.image_key==='370:4'&&(!/Army Signal Corps/.test(r.candidate?.credit||'')||
    !/PROBABLY/.test(r.candidate?.scene||'')||!/MAY/.test(r.candidate?.scene||'')))
   errors.push('army_provenance_and_uncertain_ship_caption');
 }
 return [...new Set(errors)];
}
module.exports={validate};
if(require.main===module){
 const data=require('./nhhc_west_loch_370_source_crosswalk_20261102.json');
 const census=require('./parts/02.json');
 const e=validate(data,census);process.stdout.write(JSON.stringify({pass:e.length===0,errors:e})+'\n');
 process.exitCode=e.length?1:0;
}
