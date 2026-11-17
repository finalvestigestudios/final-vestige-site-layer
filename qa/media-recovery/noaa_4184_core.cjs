'use strict';
const EXTERNAL='https://www.hawaiimagazine.com/wp-content/uploads/2020/12/Tsunami1946NOAA2.jpg';
const POST='https://finalvestige.com/2026/08/20/the-lighthouse-was-gone-at-dawn-1946-tsunami/';
const NOAA='https://prod-01-alb-www-noaa.woc.noaa.gov/noaa-collections/photo-library/pl23theb2705jpg';
const PDF='https://repository.library.noaa.gov/view/noaa/41185/noaa_41185_DS3.pdf';
function validateNoaa(d){
 const errors=[],bad=x=>errors.push(x);
 if(d?.schema_version!==1||d.image_key!=='418:4'||d.post_id!==418||d.post_url!==POST||d.exact_stored_image_url!==EXTERNAL||!Number.isFinite(Date.parse(d.reviewed_at_utc)))bad('post/source mismatch');
 if(d.publisher_article_url!=='https://www.hawaiimagazine.com/three-tsunamis-that-changed-hilo-and-hawaiis-big-island/'||!d.publisher_context?.includes('NOAA'))bad('publisher metadata mismatch');
 const p=d.primary_source_links;
 if(p?.noaa_photo_library_search_index_record!==NOAA||p.noaa_photo_library_item_slug!=='pl23theb2705jpg'||p.noaa_original_label!=='pl23_theb2705.jpg'||p.noaa_catalog_credit!=='NOAA'||p.noaa_catalog_display_date!=='Apr-46'||p.noaa_catalog_location!=='Hilo, Hawaii'||!p.noaa_catalog_description?.includes('man on pier'))bad('NOAA source metadata mismatch');
 if(p?.noaa_library_safety_manual_pdf!==PDF||p.noaa_library_pdf_page_index_zero_based!==36||p.noaa_library_pdf_printed_page!==33||p.noaa_library_manual_photo_credit!=='NOAA/NGDC and Pacific Tsunami Museum')bad('NOAA PDF provenance mismatch');
 if(p?.usgs_independent_caption_pdf!=='https://pubs.usgs.gov/gip/7000036/report.pdf')bad('USGS context missing');
 const e=d.identity_evidence;
 if(e?.publisher_jpeg_viewer_displayed!==true||e.noaa_pdf_page_screenshot_inspected!==true||e.same_historic_pier_scene_observed!==true||e.distinctive_arrow_marked_person_corroborated!==true||e.noaa_catalog_exact_binary_match_proved!==false||e.publisher_jpeg_sha256!==null||e.noaa_original_jpeg_sha256!==null||e.classification!=='strong_visual_scene_corroboration_not_binary_identity'||!e.limitations?.includes('503'))bad('source proof overclaimed');
 const r=d.reuse_and_hosting;
 if(r?.rights_status!=='HOLD__item_level_review_required'||!r.reason?.includes('Pacific Tsunami Museum')||r.proposed_max_width_px!==960||r.no_upscale!==true||r.preserve_aspect_ratio!==true||r.known_intrinsic_width_px!==null||r.known_intrinsic_height_px!==null||r.calculated_target_dimensions_px!==null||r.resize_output_format!==null||r.original_download_sha256!==null||r.candidate_wordpress_media_id!==null||r.rights_verified!==false||r.wordpress_upload_approved!==false||r.wordpress_post_rewrite_approved!==false||r.optimized_file_created!==false)bad('unsafe reproduction/release gate');
 const q=d.performance_proof;
 if(q?.finalvestige_logged_out_browser_tested!==false||q.finalvestige_browser_http_status!==null||q.finalvestige_browser_natural_width_px!==null||q.finalvestige_browser_encoded_transfer_bytes!==null||q.confirmed_broken_in_browser!==null||q.measured_weight_savings_percent!==null||q.reported_42_broken_images_confirmed!==null||q.reported_76_percent_savings_confirmed!==null)bad('fabricated visitor or savings evidence');
 return{ok:!errors.length,errors,source_identity_candidates:1,new_binary_verified:0,new_browser_broken_verified:0,approved_wp_actions:0};
}
module.exports={validateNoaa};
