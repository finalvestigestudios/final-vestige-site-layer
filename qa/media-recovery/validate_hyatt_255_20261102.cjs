'use strict';
// Offline, read-only validation of a frozen WordPress source inventory against
// an independent archival candidate packet. Never treats a retriever error
// as a successful browser test or grants production publication permission.
const EXPECTED_IDS = ['70172329','HRWalkway.svg','Hyatt Regency collapse support.PNG','70172360','70172364','Hyatt Regency collapse floor view.PNG','70172359'];
const EXPECTED_SIZES = [[3019,2384],[720,420],[477,330],[3019,2384],[3019,2384],[463,342],[3019,2384]];
const EXPECTED_KIND = ['federal_photo','vector_diagram','author_photo','federal_photo','federal_photo','author_photo','federal_photo'];
const CENSUS_BLOB = '9b16b828342a9ac338f3e65610fd3d8d508355e9';
function validateHyatt255(audit, frozenImages) {
 const errors=[],bad=x=>errors.push(x);
 if(!audit||audit.schema!=='fv-media-hyatt-255-v1'||audit.post_id!==255
   ||audit.census_origin!=='qa/media-recovery/parts/05.json'
   ||audit.census_blob_sha!==CENSUS_BLOB||audit.total_image_refs!==7||audit.external_refs!==7
   ||audit.archived_authoritative_canonical_catalogs!==7) bad('header_census');
 if(audit?.fresh_wordpress_read!==false||audit?.publish_approved!==false
   ||audit?.media_download_or_cache_approved!==false||audit?.wordpress_write_approved!==false
   ||audit?.rights_review_completed!==false) bad('release_hold');
 if(audit?.confirmed_visitor_broken_count!==0||audit?.reported_broken_42!=='NOT_VERIFIED'
   ||audit?.reported_weight_reduction_76_percent!=='NOT_MEASURED') bad('measurement_claim');
 if(!Array.isArray(frozenImages)||frozenImages.length!==7||!Array.isArray(audit?.images)||audit.images.length!==7) bad('source_count');
 const seen=new Set();
 for(let i=0;i<7;i++){
   const src=frozenImages?.[i],r=audit?.images?.[i];
   if(!src||!r){bad('missing_'+i);continue;}
   if(r.key!==`255:${i}`||r.slot!==i||r.post_id!==255
      ||src.key!==r.key||src.slot!==r.slot||src.post_id!==r.post_id
      ||r.published_source_url!==src.source_url||r.source_alt!==src.alt
      ||r.source_host!==src.source_host||r.source_kind!==src.source_kind
      ||r.stored_width_attribute_px!==src.width_px||r.stored_height_attribute_px!==src.height_px
      ||r.source_kind!=='wikimedia_redirect')bad('frozen_source_drift_'+i);
   if(seen.has(r.key))bad('duplicate_'+i);seen.add(r.key);
   if(!r.published_source_url?.startsWith('https://commons.wikimedia.org/wiki/Special:Redirect/file/')
       ||!r.source_alt||r.source_alt.length<20) bad('source_url_alt_'+i);
   if(r.exact_published_retriever?.method!=='web.open'
      ||r.exact_published_retriever?.result!=='INACCESSIBLE_BY_RETRIEVER_NO_ORIGIN_HTTP'
      ||r.exact_published_retriever?.numeric_origin_http_status!==null
      ||r.origin_http_status!==null ||r.visitor_browser_http_status!==null
      ||r.visitor_current_src!==null||r.visitor_decode_success!==null
      ||r.visitor_natural_width_px!==null||r.visitor_encoded_transfer_bytes!==null
      ||r.observed_broken_for_visitors!==null)bad('unproved_browser_status_'+i);
   if(r.source_binary_sha256!==null||r.exact_crop_verified!==false
       ||r.rights_signed_off!==false||r.localization_approved!==false)bad('unsafe_release_'+i);
   const c=r.catalog,wh=EXPECTED_SIZES[i];
   if(!c||c.record_id!==EXPECTED_IDS[i]||c.source_kind!==EXPECTED_KIND[i]
       ||c.catalog_original_width_px!==wh[0]||c.catalog_original_height_px!==wh[1]
       ||c.catalog_page_accessible!==true
       ||c.relationship!=='same_catalog_filename_match_not_binary_verified'
       ||!c.url?.startsWith('https://commons.wikimedia.org/wiki/File:')
       ||!c.rights_note?.includes('before reuse') && !c.rights_note?.includes('pending'))bad('catalog_identity_or_rights_'+i);
   const w=c?.conditional_target_width_px,h=c?.conditional_target_height_px;
   if(!Number.isInteger(w)||!Number.isInteger(h)||w!==Math.min(960,wh[0])
       ||h!==Math.round(wh[1]*w/wh[0])||w>wh[0]||h>wh[1]||w>960)bad('no_upscale_geometry_'+i);
 }
 return {status: errors.length?'HOLD_INVALID':'HOLD_VALIDATED_SOURCE_ONLY',errors,
   frozen_image_records_validated:errors.length?0:7,confirmed_visitor_broken_count:0,
   production_release_authorized:false};
}
module.exports={validateHyatt255};
