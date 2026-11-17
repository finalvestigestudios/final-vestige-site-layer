'use strict';
/** Offline fail-closed validation of the single NOAA catalogue lead; no media download. */
const fs=require('node:fs'),path=require('node:path');
const STORED='https://www.hawaiimagazine.com/wp-content/uploads/2020/12/Tsunami1946NOAA2.jpg';
const SOURCE='https://prod-01-alb-www-noaa.woc.noaa.gov/noaa-collections/photo-library/pl23theb2705jpg';
function validate(row){
 const errors=[];
 const eq=(ok,label)=>{if(!ok)errors.push(label)};
 eq(row?.image_key==='418:4'&&row?.post_id===418,'incorrect_image_identity');
 eq(row?.exact_stored_url===STORED,'stored_source_mismatch');
 eq(row?.source_catalog_candidate?.institution==='National Oceanic and Atmospheric Administration (NOAA)'&&
    row?.source_catalog_candidate?.catalog_id==='theb2705'&&
    row?.source_catalog_candidate?.catalog_page===SOURCE,'unverified_primary_catalog_id');
 eq(row?.source_catalog_candidate?.mapping_strength==='high_confidence_same_historical_scene_catalog_candidate_not_binary_verified'&&
    row?.source_catalog_candidate?.original_binary_sha256===null&&
    row?.source_catalog_candidate?.same_binary_as_stored_url===null&&
    row?.source_catalog_candidate?.exact_binary_match_tested===false,'fabricated_binary_identity');
 eq(row?.source_catalog_candidate?.original_intrinsic_width_px===null&&
    row?.source_catalog_candidate?.original_intrinsic_height_px===null,'fabricated_intrinsic_dimensions');
 eq(Array.isArray(row?.evidence)&&row.evidence.length>=3&&
    row.evidence.some(x=>x.basis==='primary_noaa_archived_manual_visual')&&
    row.evidence.some(x=>x.basis==='publisher_caption')&&
    row.evidence.some(x=>x.basis==='independent_secondary_catalog_credit_conflict'),'incomplete_documentary_chain');
 eq(row?.rights?.status==='HELD_ITEM_LEVEL_REVIEW'&&row?.rights?.public_domain_assumed===false,'rights_not_cleared');
 const p=row?.candidate_delivery;
 eq(p?.max_width_px===960&&p?.preserve_aspect_ratio===true&&p?.upscale===false&&p?.crop===false,'unsafe_derivative_dimensions');
 eq(p?.source_master_sha256===null&&p?.proposed_width_px===null&&p?.proposed_height_px===null&&
    p?.encoded_candidate_bytes===null&&p?.wordpress_media_id===null,'fabricated_derivative_or_wp_id');
 eq(p?.wordpress_upload_authorized===false&&p?.wordpress_post_rewrite_authorized===false,'unauthorized_production_write');
 const v=row?.visitor_verification;
 eq(v?.original_image_http_status===null&&v?.browser_current_src===null&&v?.browser_decoded_natural_width_px===null&&
    v?.browser_transferred_bytes===null&&v?.verified_broken_in_browser===null&&
    v?.image_weight_reduction_percent===null,'invented_browser_or_weight_evidence');
 eq(row?.p0_candidate_tracking?.previously_documented_candidates===35&&
    row?.p0_candidate_tracking?.catalog_candidate_count_with_this_lead===36&&
    row?.p0_candidate_tracking?.source_candidate_only_not_rights_or_binary_clearance===true,'inaccurate_candidate_scope');
 return {ok:errors.length===0,errors};
}
if(require.main===module){const file=path.join(__dirname,'tsunami_418_noaa_catalog_20261031.json');const v=validate(JSON.parse(fs.readFileSync(file,'utf8')));console.log(JSON.stringify(v));if(!v.ok)process.exitCode=1}
module.exports={validate};
