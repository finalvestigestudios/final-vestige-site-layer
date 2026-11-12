'use strict';
/**
 * P1 960px responsive-feasibility and stored-byte reconciliation.
 * Offline/read-only. Not a network collector and never approves image copying.
 * Staging decisions MUST wait for Site QA #154 P0 browser evidence.
 */
const audit = require('./p1_15_responsive_960_feasibility_20261111.json');
const bridge = require('./browser_handoff_6_p0_15_oversize_20261110.json');
const BLOB = 'd1a9c7a499510ec37bcdba5858d45165752587e0';
const isInt=(x)=>Number.isSafeInteger(x);
function inspect(a=audit,b=bridge) {
 const errors=[];
 const bad=(e)=>errors.push(e);
 if (!a || a.schema!=='fv-media-15-responsive-960-feasibility-v1') bad('SCHEMA');
 if (a?.source_custody?.git_blob_sha!==BLOB)bad('SOURCE_SHA');
 if (a?.source_custody?.worklist_blob_sha!=='2acd06a4ca4317646006eb6591face3fe76fedec')bad('WORKLIST_SHA');
 if (a?.cohorts?.historical_posts!==61||a?.cohorts?.historical_inline_img!==355||
     a?.cohorts?.historical_external_src_positions!==288||
     a?.cohorts?.expanded_published_posts!==66||a?.cohorts?.expanded_inline_img!==361||
     a?.cohorts?.reported_broken_42_guest_verified!==false) bad('COHORT_OR_42_CLAIM');
 if (a?.counts?.oversized_originals_over_1500000_bytes!==15 ||
     a?.counts?.original_bytes_total!==47096779 ||
     a?.counts?.inline_exposed_originals!==11 ||
     a?.counts?.inline_exposed_original_bytes!==38480915 ||
     a?.counts?.not_mapped_inline_originals!==4 ||
     a?.counts?.not_mapped_inline_original_bytes!==8615864 ||
     a?.counts?.inline_without_registered_wp_subsizes!==5 ||
     a?.counts?.original_bytes_for_five_no_subsizes!==13267538)bad('ACCOUNTING');
 if (a?.performance?.original_storage_bytes_is_not_network_transfer!==true||
     a?.performance?.proposed_76_percent_transfer_reduction_unmeasured!==true||
     a?.performance?.actual_reduction_percent!==null||
     a?.performance?.guest_browser_measurements!==null)bad('UNPROVEN_TRANSFER_CLAIM');
 const policy=a?.staging_contract||{};
 for (const k of ['wordpress_production_writes','third_party_binary_downloads','homepage_visual_changes','merges_or_deployments','paid_services'])
   if(policy[k]!==false)bad('UNAUTHORIZED_ACTION_'+k);
 for (const k of ['never_upscale','derivatives_are_only_hypothetical','registered_subsize_or_srcset_review_required','rights_and_editorial_approval_required'])
   if(policy[k]!==true)bad('POLICY_'+k);
 if(policy.generic_width_ceiling_px!==960)bad('SIZE_CEILING');
 if(a?.p0_first?.confirmed_guest_failures!==0||
    JSON.stringify(a?.p0_first?.site_qa_existing_order)!==JSON.stringify(['285:5','285:2','287:5','418:1','418:2','407:1']))bad('P0_FIRST');
 if (!Array.isArray(a?.rows)||a.rows.length!==15||!Array.isArray(b?.oversized_media)||b.oversized_media.length!==15){
   bad('ROW_CARDINALITY');return {pass:false,errors};
 }
 const pinned=new Map(b.oversized_media.map(x=>[x.media_id,x]));
 const seen=new Set();let total=0,inlineTotal=0,inlineN=0,unsub=0,unsubBytes=0;
 for(const r of a.rows){
   if(!r||!isInt(r.media_id)||seen.has(r.media_id)||!pinned.has(r.media_id)){bad('MISSING_DUPLICATE_OR_FOREIGN_MEDIA');continue}
   seen.add(r.media_id);const m=pinned.get(r.media_id);
   if(r.original_url!==m.original_url||r.stored_original_bytes!==m.stored_original_bytes||
      !Array.isArray(r.native_px)||JSON.stringify(r.native_px)!==JSON.stringify(m.native_px)||
      JSON.stringify(r.published_inline_post_ids)!==JSON.stringify(m.inline_post_ids)||
      JSON.stringify(r.published_inline_source_urls)!==JSON.stringify(m.published_direct_srcs)||
      r.generated_wp_subsize_count!==m.generated_subsizes||
      r.item_rights_review!==m.rights_observation)bad('SOURCE_BINDING_'+r.media_id);
   if(m.stored_original_bytes<=1500000)bad('NOT_OVERSIZED');
   const width=Math.min(960,m.native_px[0]);
   const height=Math.round(m.native_px[1]*width/m.native_px[0]);
   if(JSON.stringify(r.conditional_no_upscale_960px)!==JSON.stringify([width,height])||
      r.conditional_max_css_width_px_at_dpr_1!==width ||
      r.conditional_max_css_width_px_at_dpr_2!==Math.floor(width/2) ||
      r.conditional_max_css_width_px_at_dpr_3!==Math.floor(width/3))bad('960_DPR_OR_ASPECT_RATIO_'+r.media_id);
   const five=[39,40,41,42,43].includes(r.media_id);
   if(r.html_width_attribute_hint_px!==(five?1024:null)||
      r.html_width_hint_exceeds_960px!==five||
      r.retina_2x_safe_at_html_width_hint!==false)bad('HTML_HINT_'+r.media_id);
   if(r.actual_rendered_css_width_px!==null||r.actual_browser_dpr!==null||
      r.actual_browser_selected_current_src!==null||r.actual_guest_http_status!==null||
      r.actual_guest_wire_bytes!==null||r.output_binary_created!==false||
      r.commercial_reuse_cleared!==false||r.exact_scene_cleared!==false||
      r.layout_approved!==false||r.production_edit_allowed!==false||
      r.stage_only_after_rights_and_visual_review!==true)bad('MEASUREMENT_RIGHTS_OR_RELEASE_'+r.media_id);
   const isInline=m.inline_post_ids.length>0;
   const expected=isInline?(m.generated_subsizes===0?'P1_REGISTER_RESPONSIVE_SUBSIZES_ONLY_AFTER_P0_RIGHTS_EDITOR_AND_BROWSER':'P1_CHECK_EXISTING_WP_SUBSIZES_AND_BROWSER_CURRENT_SRC_AFTER_P0'):'NOT_IN_PUBLISHED_INLINE_AUDIT_CHECK_FEATURED_PAGES_BEFORE_ACTION';
   if(r.recommendation!==expected)bad('WORKORDER_'+r.media_id);
   total+=m.stored_original_bytes;
   if(isInline){inlineN++;inlineTotal+=m.stored_original_bytes;if(!m.generated_subsizes){unsub++;unsubBytes+=m.stored_original_bytes}}
 }
 if(seen.size!==15||total!==47096779||inlineN!==11||inlineTotal!==38480915||unsub!==5||unsubBytes!==13267538)bad('RECALCULATED_TOTALS');
 return {pass:errors.length===0,errors};
}
module.exports={inspect,BLOB};
