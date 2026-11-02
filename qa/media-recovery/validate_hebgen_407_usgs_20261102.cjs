'use strict';
/** Read-only, fail-closed USGS Hebgen recovery ledger validator; no network, WordPress or media writes. */
const validateHebgen=function validateHebgen(ledger,sourcePart){
 const errors=[],fail=(ok,msg)=>{if(!ok)errors.push(msg)};
 if(!ledger||!sourcePart)return ['missing_inputs'];
 const expected=(sourcePart.images||[]).filter(x=>x.post_id===407).sort((a,b)=>a.slot-b.slot);
 const rows=ledger.rows||[],provenance=ledger.provenance||{};
 fail(ledger.schema_version===1,'schema');
 fail(provenance.post_id===407&&provenance.git_frozen_path==='qa/media-recovery/parts/02.json'&&provenance.git_frozen_blob_sha==='48e1ebf07207e948ba5802e714eb39659d2e1c1d','frozen_provenance');
 fail(provenance.post_url==='https://finalvestige.com/2026/08/20/the-lake-wasnt-there-yesterday-hebgen/','article_url');
 fail(expected.length===8&&rows.length===8&&new Set(rows.map(r=>r.image_key)).size===8,'eight_unique_slots');
 const statuses=['displayed','retriever_unsupported_octet_stream','displayed','not_accessible_no_status','displayed','displayed','displayed','displayed'];
 for(let i=0;i<8;i++){
  const e=expected[i],r=rows[i];if(!e||!r){errors.push('missing_row:'+i);continue}
  fail(r.image_key===e.key&&r.slot===i&&r.post_id===407,'slot_identity:'+i);
  fail(r.published_source_url===e.source_url&&r.published_alt===e.alt,'unchanged_source_alt:'+i);
  fail(r.published_source_url.startsWith('https://d9-wret.s3.us-west-2.amazonaws.com/'),'source_host:'+i);
  fail(r.usgs_primary?.catalog_url?.startsWith('https://www.usgs.gov/media/images/')===true,'usgs_primary_catalog:'+i);
  fail(r.usgs_primary?.source_usage_label==='Public Domain'&&typeof r.usgs_primary.creator_credit==='string'&&r.usgs_primary.creator_credit.length>4,'rights_and_creator:'+i);
  fail(['opened','search_index_primary_catalog_open_timeout'].includes(r.usgs_primary?.catalog_access),'catalog_evidence_method:'+i);
  const v=r.independent_retriever||{},c=r.recovery_candidate||{},geo=r.conditional_960_no_upscale||{};
  fail(v.method==='web_viewer_render_or_web_retriever_wrapper_not_visitor_browser'&&v.published_asset_result===statuses[i],'web_only_status:'+i);
  fail(v.published_origin_http_status===null&&v.guest_browser_http_status===null&&v.guest_current_src===null&&v.decoded_width_px===null&&v.encoded_transfer_bytes===null,'no_invented_guest_evidence:'+i);
  fail(v.wrapper_code===(i===1?400:null),'wrapper_only_on_octet_stream:'+i);
  fail(geo.max_width_px===960&&Number.isInteger(geo.reference_width_px)&&Number.isInteger(geo.reference_height_px)&&geo.reference_width_px>0&&geo.reference_height_px>0,'geometry_inputs:'+i);
  fail(geo.proposed_width_px===Math.min(960,geo.reference_width_px)&&geo.proposed_height_px===Math.round(geo.reference_height_px*geo.proposed_width_px/geo.reference_width_px),'no_upscale_ratio:'+i);
  fail(geo.source_master_dimensions_verified===false&&geo.output_binary_created===false,'dimensions_conditional:'+i);
  fail(c.pixel_hash_match_verified===false&&r.rights_review_complete===false&&r.permission_to_cache_in_wordpress===false&&r.permission_to_modify_published_post===false,'permissions_hold:'+i);
  if(i===1){
   fail(c.official_original_asset_url==='https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg'&&c.candidate_displayed_in_independent_viewer===true,'specific_official_original_relocation');
   fail(c.official_original_asset_url!==r.published_source_url,'candidate_must_be_different_route');
   fail(geo.dimension_evidence_kind==='viewer_preview_official_original_alternate','alternate_preview_not_published');
  }else fail(c.official_original_asset_url===null&&c.candidate_displayed_in_independent_viewer===null,'no_fabricated_candidate:'+i);
 }
 const counts=ledger.scope||{};
 fail(counts.source_slots===8&&counts.third_party_slots===8&&counts.displayed_published_assets_in_independent_viewer===6&&counts.unsupported_published_assets_in_independent_retriever===1&&counts.unavailable_without_status===1&&counts.guest_browser_verified_failures===0&&counts.production_repairs===0,'counts');
 fail(ledger.reported_42_broken_guest_confirmed===false&&ledger.claimed_76pct_wire_saving_measured===false&&ledger.source_binary_downloaded_or_rehosted===false,'no_fabricated_42_76_or_copies');
 fail(rows[7]?.usgs_primary?.photographed_on_or_about==='2023-06-27'&&rows[2]?.usgs_primary?.photographed_on_or_about==='1959-08-21','historical_chronology');
 return errors;
};
module.exports={validateHebgen};
