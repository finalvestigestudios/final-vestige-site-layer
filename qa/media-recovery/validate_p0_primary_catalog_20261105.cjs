'use strict';
/** Offline candidate-release integrity gate. No network, files, or WP access. */
const PUBLISHED = Object.freeze({
  '285:5': {post_id:285,url:'https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg',alt:'Aerial view of the Three Mile Island nuclear generating station on the Susquehanna River.'},
  '287:5': {post_id:287,url:'https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg',alt:'The old Sunshine Skyway wreckage and the later bridge replacement in Tampa Bay.'}
});
function verify(a) {
 const errors=[];
 const ok=(cond,msg)=>{if(!cond)errors.push(msg)};
 ok(a && a.schema==='fv-media-p0-primary-record-correction-20261105-v1','schema');
 ok(a?.provenance?.pinned_prior_image_inventory_git_blob==='49183f66f880f7c4dfd363acca906876877f2e5e','pinned_source_sha');
 ok(a?.provenance?.pinned_p0_disposition_git_blob==='9bf9a973fce37a546f8c3e79ecd0c34345eb2457','pinned_p0_sha');
 const s=a?.scope||{};
 ok(s.inspected_priority_slots===2 && s.published_article_baseline===66 && s.published_image_slots_baseline===361,'scope_size');
 ok(s.old_reported_broken===42 && s.old_reported_broken_status==='UNVERIFIED','unverified_broken');
 ok(s.claimed_reduction_percent===76 && s.claimed_reduction_status==='UNMEASURED','unmeasured_76');
 ok(s.live_wordpress_changes===0 && s.image_binary_downloads===0 && s.public_release_authorized===false,'no_production_authorization');
 ok(Array.isArray(a?.rows)&&a.rows.length===2,'exact_two_rows');
 const rows=Array.isArray(a?.rows)?a.rows:[];
 ok(new Set(rows.map(r=>r.key)).size===2,'unique_keys');
 for(const r of rows){
  const p=PUBLISHED[r.key];
  ok(Boolean(p),'known_key_'+r.key);
  if(!p)continue;
  ok(r.post_id===p.post_id && r.published_source_url===p.url && r.published_alt===p.alt,'source_alt_identity_'+r.key);
  ok(r.page_url?.startsWith('https://finalvestige.com/'),'page_url_'+r.key);
  const v=r.retriever_observation||{};
  ok(v.method==='independent_web_text_retriever_wrapper'&&v.wrapper_code===404&&v.origin_http===false&&v.visitor_browser_http===false,'wrapper_not_origin_'+r.key);
  for(const field of ['visitor_http_status','visitor_current_src','visitor_natural_width','visitor_natural_height','visitor_encoded_data_length','visitor_broken']){
   ok(r[field]===null,'guest_unknown_'+r.key+'_'+field);
  }
  const rel=r.release||{};
  for(const k of ['image_mirror_approved','wp_upload_approved','published_post_edit_approved'])ok(rel[k]===false,'no_write_'+r.key+'_'+k);
  for(const k of ['staging_requires_guest_failure','staging_requires_same_scene_editorial_review','staging_requires_binary_decode','staging_requires_source_attribution_and_disclaimer','staging_requires_responsive_screenshots'])ok(rel[k]===true,'stage_gate_'+r.key+'_'+k);
 }
 const c=rows.find(r=>r.key==='285:5')?.replacement_candidate||{};
 ok(c.catalog_url==='https://wwwn.cdc.gov/phil/Details.aspx?pid=1194'&&c.catalog_id==='CDC-PHIL-1194','cdc_primary');
 ok(c.content_provider==='CDC/ Dr. Ewing'&&c.photographer==='Dr. Ewing'&&c.creation_date===null,'cdc_credit_date');
 ok(c.catalog_high_resolution_label==='4.91 MB'&&c.cdc_highres_intrinsic_px===null,'cdc_master_unknown');
 ok(c.secondary_file_catalog==='https://commons.wikimedia.org/wiki/File:Three_Mile_Island_nuclear_power_plant.jpg','cdc_secondary');
 ok(c.secondary_original_width_px===2843&&c.secondary_original_height_px===1817&&c.proposed_secondary_960px_width===960&&c.proposed_secondary_960px_height===614,'cdc_commons_geometry');
 ok(c.identical_to_published_photo===null&&c.identical_to_official_cdc_master===null&&c.matches_subject==='PLANT_ONLY_AERIAL_COMPOSITION_UNVERIFIED','cdc_not_same_photo');
 ok(c.reuse_policy_url==='https://www.cdc.gov/other/agencymaterials.html'&&c.rights_copyright_classification==='OFFICIAL_ITEM_PUBLIC_DOMAIN'&&c.reuse_policy_verified===true,'cdc_policy');
 for(const f of ['agency_attribution_required','individual_credit_required','source_site_link_required','prominent_nonendorsement_disclaimer_required','free_original_source_statement_required','substantive_content_change_prohibited'])ok(c[f]===true,'cdc_rights_'+f);
 ok(c.rights_release_review==='HOLD_SITE_CONTEXT_AND_CREDIT_QA'&&c.proposed_credit==='CDC / Dr. Ewing. Source: CDC Public Health Image Library, image 1194.','cdc_credit_hold');
 const f=rows.find(r=>r.key==='287:5')?.replacement_candidate||{};
 ok(f.catalog_url==='https://floridamemory.com/items/show/131903'&&f.catalog_id==='K894127','fl_primary');
 ok(f.catalog_date==='1987 (circa)'&&f.photographer==='Stewart, H. Milo'&&f.depicts_old_and_replacement_bridge===true,'fl_1987_both_bridges');
 ok(f.matches_subject==='OLD_AND_NEW_BRIDGES_SAME_THEME_NOT_PROVEN_IDENTICAL_PHOTO'&&f.exact_pixel_match_to_published_src===null,'fl_not_same_photo');
 ok(f.catalog_image_relative_path==='/fpc/commerce/K894127.jpg'&&f.catalog_image_url_derived_not_http_checked==='https://floridamemory.com/fpc/commerce/K894127.jpg','fl_asset_link_only_derived');
 ok(f.archive_item_rights_field==='NOT_EXPLICITLY_LICENSED_ON_ITEM_PAGE'&&f.rights_release_review==='HOLD_ITEM_LICENSE_AND_CREDIT_QA','fl_rights_hold');
 ok(f.catalog_original_pixel_width===null&&f.catalog_original_pixel_height===null&&f.conditional_max_derivative_width_px===960&&f.conditional_derivative_height_px===null&&f.no_upscale===true,'fl_unknown_dimensions');
 ok(f.alternate_rejected_for_this_alt?.catalog_id==='RC09237'&&f.alternate_rejected_for_this_alt?.date==='1980-05-09'&&f.alternate_rejected_for_this_alt?.reason?.includes('does not depict the later replacement bridge'),'fl_1980_not_dropin');
 return {pass:errors.length===0,errors};
}
module.exports={verify};
