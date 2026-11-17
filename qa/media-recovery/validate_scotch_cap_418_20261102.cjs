'use strict';
/** Fail-closed Scotch Cap archival/rights/chronology audit validator. No I/O or WordPress writes. */
function validate(packet,sourceRows){
 const errors=[],fail=s=>errors.push(s),arr=packet?.rows;
 if(packet?.schema_version!==1||packet?.post_id!==418||!Array.isArray(arr)||arr.length!==6)fail('exact_six_slots_required');
 if(packet?.source_evidence?.source_src_alt_exact_matches!==6||packet?.source_evidence?.current_authenticated_wp_readback!==true)fail('authenticated_source_parity_required');
 if(packet?.source_evidence?.frozen_git_blob_sha!=='948bc1b65b42799aa40cfdb810ddf6ffd80886b6')fail('frozen_blob_mismatch');
 if(packet?.external_historical_conflict?.correct_disaster_year!==1946||packet?.external_historical_conflict?.chronology_gate!=='REJECT_GALLERY_1964_CAPTION'||!/1964/.test(packet?.external_historical_conflict?.erroneous_noaa_gallery_claim||''))fail('noaa_1964_conflict_must_be_preserved');
 if(packet?.all_media_cache_approval!==false||packet?.all_WP_changes_approved!==false)fail('publication_gate');
 if(packet?.corpus?.reported_42_broken_guest_verified!==false||packet?.corpus?.claimed_76_percent_savings_wire_measured!==false||packet?.corpus?.production_repaired!==0)fail('unsupported_site_claim');
 if(!Array.isArray(sourceRows)||sourceRows.length!==6)fail('frozen_source_rows_required');
 const allowed=new Set(['RETRIEVER_403','INACCESSIBLE_NO_HTTP','IMAGE_RENDERER_DISPLAYED']),used=new Set();
 for(let i=0;i<(arr||[]).length;i++){
  const r=arr[i],src=sourceRows?.[i],p=r?.independent_retrieval,d=r?.conditional_derivative,a=r?.authority,c=r?.caching;
  if(r?.image_key!==`418:${i}`||r?.slot!==i||r?.post_id!==418||used.has(r?.image_key))fail('wrong_or_duplicate_slot:'+i);
  used.add(r?.image_key);
  if(!src||r?.source_url!==src.source_url||r?.alt!==src.alt)fail('frozen_source_url_or_alt_drift:'+i);
  if(!/^https:\/\//.test(r?.source_url||'')||!/^https:\/\//.test(a?.catalog_url||''))fail('non_https_source:'+i);
  if(!allowed.has(p?.outcome)||p?.method!=='web_retriever_or_image_renderer_2026_11_02_NOT_guest_Chrome')fail('unsupported_retrieval:'+i);
  if(p?.retriever_wrapper_code!==(i===1||i===2?403:null))fail('retriever_wrapper_error_drift:'+i);
  if(p?.outcome!==(i===1||i===2?'RETRIEVER_403':i===0||i===3?'INACCESSIBLE_NO_HTTP':'IMAGE_RENDERER_DISPLAYED'))fail('published_retrieval_result_drift:'+i);
  for(const field of ['origin_http_status','guest_browser_http_status','guest_browser_current_src','guest_browser_decoded_px','guest_browser_encoded_transfer_bytes','visibly_broken_in_guest_browser'])if(p?.[field]!==null)fail('fabricated_browser_proof:'+i+':'+field);
  if(a?.exact_binary_identity_verified!==false||a?.asset_binary_sha256!==null||a?.rights_review!=='ITEM_REVIEW_REQUIRED')fail('unverified_identity_rights:'+i);
  if(d?.maximum_width_px!==960||d?.target_width_px!==null||d?.target_height_px!==null||d?.source_intrinsic_width_px!==null||d?.source_intrinsic_height_px!==null||d?.downscale_only!==true||d?.aspect_ratio_preserved!==true||d?.do_not_crop!==true)fail('unverified_dimensions:'+i);
  if(c?.wordpress_media_cache_permitted!==false||c?.wordpress_post_edit_permitted!==false)fail('unauthorized_cache_or_edit:'+i);
 }
 if(packet?.third_party_mirror?.image_key!=='418:2'||packet?.third_party_mirror?.same_binary_proven!==false||packet?.third_party_mirror?.third_party_mirror_caching_approved!==false)fail('unlicensed_mirror_approval');
 return{ok:errors.length===0,errors};
}
module.exports={validate};
