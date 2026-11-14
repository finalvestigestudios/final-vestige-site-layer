'use strict';
/** Read-only fail-closed stored-media baseline validator; no network/CMS operations. */
const LEGACY_IDS = [39,40,41,42,43,293,382,388,389,405,482,1257,1258,1714,2148];
function validate(data) {
 const errors=[];
 const fail=x=>errors.push(x);
 if(!data || typeof data!=='object' || Array.isArray(data))return {ok:false,errors:['invalid_audit']};
 if(data.schema!=='fv-media-current-16-draft-exposure-20261113-v1')fail('schema');
 if(data.source_method!=='read-only authenticated WordPress media.list images pages 1+2, posts.list published and pages.get 2429 edit')fail('source_method');
 const meta=data.inventory||{},rows=data.oversized_media;
 if(!Array.isArray(rows)||rows.length!==16)fail('row_count');
 if(meta.published_post_count!==66||meta.wordpress_image_media_count!==123||meta.older_frozen_post_count!==61||meta.older_frozen_inline_image_count!==355)fail('cohort_counts');
 if(meta.originals_above_1500000_decimal_bytes!==16||meta.originals_above_1500000_total_storage_bytes!==49107665||meta.prior_15_originals_total_storage_bytes!==47096779)fail('storage_baseline');
 if(meta.added_original_media_id!==2432||meta.added_original_stored_bytes!==2010886||meta.added_media_parent_page_id!==2429||meta.added_media_parent_status!=='draft'||meta.added_media_is_proven_published_article_image!==false||meta.added_media_published_inline_usage!==null)fail('draft_exposure');
 if(meta.historical_reported_broken_42_guest_confirmed!==false||meta.claimed_76_percent_wire_reduction_measured!==false)fail('unsupported_claim');
 const policy=data.rights_and_quality_policy||{};
 for(const x of ['exact_scene_and_crop_review_required','rights_copyright_attribution_review_required','no_upscale','css_width_dpr_verification_required','cold_uncached_browser_bytes_required'])if(policy[x]!==true)fail('policy_'+x);
 for(const x of ['wordpress_rewrites_authorized','binary_downloads_authorized','cache_authorized','homepage_design_in_scope'])if(policy[x]!==false)fail('unsafe_policy_'+x);
 if(policy.max_conditional_width_px!==960||data.visitor_verified_repair_count!==0||data.production_media_changes!==0)fail('release_claim');
 const ids=new Set();let stored=0,legacy=0;
 for(const r of Array.isArray(rows)?rows:[]){
  if(!Number.isSafeInteger(r.media_id)||ids.has(r.media_id))fail('duplicate_or_invalid_media_id');
  ids.add(r.media_id);
  if(typeof r.source_url!=='string'||!/^https:\/\/finalvestige\.com\/wp-content\/uploads\/[^\s]+$/i.test(r.source_url))fail('media_origin');
  if(!Number.isSafeInteger(r.original_stored_bytes)||r.original_stored_bytes<=1500000)fail('threshold');
  stored+=Number.isSafeInteger(r.original_stored_bytes)?r.original_stored_bytes:0;
  if(LEGACY_IDS.includes(r.media_id))legacy+=r.original_stored_bytes;
  const d=r.native_dimensions_px||{},z=r.conditional_derivative_max_px||{};
  if(!Number.isSafeInteger(d.width)||d.width<1||!Number.isSafeInteger(d.height)||d.height<1||!Number.isSafeInteger(z.width)||z.width<1||z.width>960||z.width>d.width||!Number.isSafeInteger(z.height)||z.height<1||z.height>d.height||Math.abs(z.height-Math.round(d.height*z.width/d.width))>1||z.no_upscale!==true||z.approved!==false)fail('unsafe_derivative');
  if(!Array.isArray(r.wordpress_size_descriptors)||r.wordpress_size_descriptors.some(x=>typeof x.name!=='string'||typeof x.virtual!=='boolean'))fail('size_evidence');
  if(r.rights_status!=='PENDING_ITEM_LEVEL_REVIEW'||r.rights_to_rehost_verified!==false||r.exact_visual_parity_verified!==false||r.visitor_image_http_status!==null||r.visitor_encoded_transfer_bytes!==null||r.local_copy_or_cache_authorized!==false)fail('fabricated_rights_or_browser_evidence');
  if(r.media_id===2432&& (r.parent_content_id!==2429||r.original_stored_bytes!==2010886||r.native_dimensions_px.width!==1280||r.native_dimensions_px.height!==720||!r.source_url.endsWith('/2026/11/final-vestige-artifact-editions-editorial-concept.png')))fail('new_draft_asset_identity');
 }
 if(ids.size!==16||LEGACY_IDS.some(id=>!ids.has(id))||!ids.has(2432))fail('membership');
 if(stored!==49107665||legacy!==47096779)fail('sum_mismatch');
 return {ok:errors.length===0,errors:[...new Set(errors)]};
}
module.exports={validate};
