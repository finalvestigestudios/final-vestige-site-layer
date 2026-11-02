'use strict';
/** Fail-closed, source-only 418:4 NOAA catalog lead validation. No network/write operations. */
const assert=require('node:assert/strict');
const FROZEN={
 key:'418:4',
 page:'https://finalvestige.com/2026/08/20/the-lighthouse-was-gone-at-dawn-1946-tsunami/',
 url:'https://www.hawaiimagazine.com/wp-content/uploads/2020/12/Tsunami1946NOAA2.jpg',
 alt:'Tsunami water inundating the Hilo waterfront in April 1946, with a person visible near the advancing water.',
 official:'https://prod-01-alb-www-noaa.woc.noaa.gov/noaa-collections/photo-library/pl23theb2705jpg',
 policy:'https://oceanservice.noaa.gov/about/faq.html'
};
function validate(d){
 const errors=[];const check=(ok,message)=>{if(!ok)errors.push(message)};
 check(d?.schema_version===1,'schema');
 check(d?.baseline?.published_posts===61&&d?.baseline?.stored_image_slots===355&&d?.baseline?.external_references===288,'frozen_site_scope');
 check(d?.baseline?.prior_p0_source_candidates===35&&d?.baseline?.prior_p0_source_slots===36&&d?.baseline?.now_p0_candidates_with_contextual_primary_lead===36,'candidate_count_not_live_health');
 check(d?.baseline?.reported_broken_42_verified===false&&d?.baseline?.claimed_transfer_savings_76_percent_measured===false&&d?.baseline?.images_repaired_in_production===0,'no_fabricated_42_76_repair');
 check(d?.post?.id===418&&d?.post?.url===FROZEN.page,'post_identity');
 const x=d?.record||{},p=x.primary_candidate||{},b=x.visitor||{},r=x.rights||{},dim=x.dimensions||{};
 check(x.image_key===FROZEN.key&&x.slot===4&&x.stored_url===FROZEN.url&&x.stored_alt===FROZEN.alt,'frozen_image_identity');
 check(x.publisher_article==='https://www.hawaiimagazine.com/three-tsunamis-that-changed-hilo-and-hawaiis-big-island/','publisher_article');
 check(x.publisher_evidence?.visual_similarity_to_candidate==='scene_and_description_consistent_not_binary_verified'&&x.publisher_evidence?.publisher_image_retrieval==='WEB_RETRIEVER_IMAGE_DISPLAYED_NOT_BROWSER','visual_claim_is_bounded');
 check(p.institution==='National Oceanic and Atmospheric Administration'&&p.collection==='Historic Coast & Geodetic Survey'&&p.catalog_id==='theb2705'&&p.catalog_filename==='pl23_theb2705.jpg'&&p.catalog_url===FROZEN.official&&p.catalog_credit==='NOAA'&&p.display_date==='1946-04','official_noaa_candidate');
 check(p.published_original_exact_binary_match_verified===false&&p.master_sha256===null&&p.source_master_dimensions_px===null,'no_invented_binary_or_size');
 check(Array.isArray(x.supporting_records)&&x.supporting_records.length>=3&&x.supporting_records.some(s=>s.source===FROZEN.official),'primary_sources_logged');
 check(Array.isArray(x.retrieval_observations)&&x.retrieval_observations.length>=3&&x.retrieval_observations.every(s=>s.origin_http_status===null&&s.guest_browser_status===null&&/^https:\/\//.test(s.url)),'retriever_not_http');
 check(r.candidate_agency_credit==='NOAA'&&r.source_policy_url===FROZEN.policy&&r.cache_or_republication_review==='HOLD'&&r.source_id_item_release_verification==='NOT_VERIFIED_TO_ORIGINAL_BINARY'&&r.publisher_mirror_not_a_license===true&&r.photo_of_identifiable_person===true&&r.wp_media_upload_authorized===false&&r.wordpress_post_rewrite_authorized===false,'rights_hold');
 check(dim.max_width_px===960&&dim.no_upscale===true&&dim.preserve_aspect_ratio===true&&dim.master_width_px===null&&dim.master_height_px===null&&dim.proposed_width_px===null&&dim.proposed_height_px===null&&dim.conversion_performed===false,'no_upscale_or_fake_derivative');
 check(b.http_status===null&&b.current_src===null&&b.final_image_url===null&&b.natural_width_px===null&&b.image_transfer_bytes===null&&b.verified_broken===null,'no_guest_proof_claim');
 check(d?.safety?.no_unlicensed_downloads===true&&d?.safety?.no_wordpress_writes===true&&d?.safety?.no_homepage_work===true&&d?.safety?.no_spend===true&&d?.safety?.live_broken_count_claim===null&&d?.safety?.transfer_reduction_percent_claim===null,'no_release_or_savings_claim');
 return errors;
}
if(require.main===module){
 const data=require('./hilo_noaa_theb2705_418_4_20261101.json');
 const errors=validate(data);if(errors.length){console.error(errors.join('\\n'));process.exitCode=1}else console.log('PASS NOAA 418:4 source-only audit');
}
module.exports={validate,FROZEN};
