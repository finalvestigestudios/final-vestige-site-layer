'use strict';
// Offline, read-only validation of WordPress API rendered HTML and NPS primary catalogs.
// This is a SOURCE/RIGHTS gate; it never tests real browser HTTP/bytes or authorizes writes.
function validateLedger(d) {
 const errors=[],check=(ok,key)=>{if(!ok) errors.push(key);};
 check(d?.schema_version===1,'schema');
 check(d?.kind==='read_only_cms_rendered_source_transport_and_primary_archive_review_NOT_BROWSER_PROOF','kind');
 check(d?.article?.post_id===211 && d?.article?.status==='publish','post');
 check(d?.article?.frozen_inventory_blob_sha==='0f3dfe398a76838049cebba7cb773d5c5a0c8c69','frozen_blob');
 check(Array.isArray(d?.rows)&&d.rows.length===6,'six_rows');
 check(d?.article?.live_images_count===6 && d.article.rendered_jp_proxy_upstreams===6,'live_six');
 check(d?.article?.wp_last_modified==='2026-11-02T21:39:32','live_modified');
 check(d?.summary?.published_slots===6 && d.summary.upstream_verified_path_matches===6 &&
       d.summary.independent_retriever_inaccessible_without_origin_status===6,'summary');
 check(d?.summary?.nps_item_ids===5 && d.summary.missing_html_dimensions===1 &&
       d.summary.possible_visual_ratio_conflict===1,'source_gaps');
 check(d?.summary?.confirmed_guest_broken_images===0 &&
       d?.summary?.confirmed_guest_broken_images_observed===false &&
       d?.summary?.weight_reduction_pct_measured===null &&
       d?.summary?.wordpress_replacements_made===0,'fabricated_result');
 check(d?.baseline?.site_posts===61 && d?.baseline?.stored_image_refs===355 &&
       d?.baseline?.stored_offsite_refs===288 && d?.baseline?.oversized_wp_originals===13 &&
       d?.baseline?.purported_broken_42_browser_verified===false &&
       d?.baseline?.purported_image_wire_savings_76_measured===false,'baseline');
 check(JSON.stringify(d?.article?.html_missing_width_height_slots)==='["211:4"]','missing_dimension_slot');
 check(JSON.stringify(d?.article?.original_master_ratio_conflict_slots)==='["211:1"]','ratio_slot');
 const ids=['POCH 2.078','POCH 2.115','POCH 2-113','POCH 2-056',null,'POCH 2-055'];
 const page='https://www.nps.gov/poch/learn/photosmultimedia/colorized-photographs.htm';
 const seen=new Set(); let noDims=0, ratioFlag=0;
 const path=s=>{let m=typeof s==='string'&&s.match(/^https:\/\/[^/]+(\/[^?#]*)/i);return m?m[1]:null;};
 for(let i=0;i<(d?.rows||[]).length;i++) {
  const x=d.rows[i],k='211:'+i; if(!x){errors.push('missing_row:'+k);continue}
  check(!seen.has(x.image_key),'duplicate:'+k);seen.add(x.image_key);
  check(x.image_key===k && x.post_id===211,'slot_order:'+k);
  check(/^https:\/\/www\.nps\.gov\//.test(x.archived_20261030_url||''),'archive_origin:'+k);
  check(/^https:\/\/i0\.wp\.com\/www\.nps\.gov\//.test(x.wp_api_rendered_img_url||''),'live_proxy:'+k);
  check(path(x.wp_api_rendered_img_url)?.replace(/^\/www\.nps\.gov/,'')===path(x.archived_20261030_url),'upstream_changed:'+k);
  check(x.origin_host==='www.nps.gov'&&x.effective_rendered_src_host==='i0.wp.com'&&
   x.proxy_upstream_host==='www.nps.gov'&&x.same_upstream_path_as_frozen===true,'not_first_party_cache:'+k);
  check(typeof x.archived_alt==='string'&&x.archived_alt.length>20&&x.wp_api_rendered_alt===x.archived_alt,'alt:'+k);
  check(x.registered_nps_item_id===ids[i],'photo_identity:'+k);
  check(x.nps_primary_catalog_url===(i===4?'https://www.nps.gov/poch/learn/historyculture/the-mutiny-trial.htm':page),'catalog:'+k);
  check(x.exact_master_binary_or_crop_verified===false && x.original_intrinsic_width_px===null &&
        x.original_intrinsic_height_px===null,'guessed_master:'+k);
  const t=x.source_transport;
  check(t?.method==='independent_text_web_retriever'&&t?.outcome==='TOOL_INACCESSIBLE_NO_ORIGIN_HTTP' &&
        t?.numeric_origin_http_status===null && t?.guest_browser_http_status===null &&
        t?.guest_browser_decoded===null&&t?.guest_current_src===null&&
        t?.guest_cdp_uncached_wire_bytes===null,'invented_origin_or_guest_http:'+k);
  check(x.rights?.item_level_rights_approved===false && x.rights?.manual_credit_review_required===true &&
       x.rights?.ref==='https://www.nps.gov/poch/learn/photosmultimedia/photogallery.htm','rights:'+k);
  check(x.hold?.original_replacement===false && x.hold?.wordpress_upload===false &&
       x.hold?.wordpress_post_edit===false && x.hold?.duplicate_or_cropped_candidate===false,'unsafe_release:'+k);
  const box=x.conditional_960_derivative;
  check(box?.no_upscale_pending===true&&box?.source_intrinsic_unverified===true &&
       (box.width_px===null||(Number.isSafeInteger(box.width_px)&&box.width_px>0&&box.width_px<=960)) &&
       (box.height_px===null||(Number.isSafeInteger(box.height_px)&&box.height_px>0)),'bad_width:'+k);
  if(i===4){noDims++;check(x.wp_html_img_width_px===null&&x.wp_html_img_height_px===null &&
       box.width_px===null&&box.height_px===null,'missing_dimensions_not_preserved:'+k)}
  else {
   check(Number.isSafeInteger(x.wp_html_img_width_px)&&x.wp_html_img_width_px===1024&&
         Number.isSafeInteger(x.wp_html_img_height_px)&&x.wp_html_img_height_px>0 &&
         box.width_px===960&&box.height_px===Math.round(960*x.wp_html_img_height_px/1024) &&
         box.based_on==='live_rendered_HTML_geometry_not_original_pixel_dimensions',
         'conditional_html_geometry:'+k);
  }
  if(i===1){
   ratioFlag++;
   check(x.master_aspect_ratio_conflict===true &&
    x.nps_gallery_master_candidate?.source_record==='POCH 2.115' &&
    x.nps_gallery_master_candidate?.width_px===1588 &&
    x.nps_gallery_master_candidate?.height_px===2026 &&
    x.nps_gallery_master_candidate?.proven_same_binary===false &&
    x.wp_html_img_width_px/x.wp_html_img_height_px>1 &&
    x.nps_gallery_master_candidate.width_px/x.nps_gallery_master_candidate.height_px<1,
    'source_candidate_orientation_conflict');
  } else check(x.master_aspect_ratio_conflict===false && x.nps_gallery_master_candidate===null,'master_unverified:'+k);
 }
 check(noDims===1&&ratioFlag===1,'risk_flags');
 check(d?.release_gate?.max_width_px===960&&d.release_gate.no_upscale_required===true &&
       d.release_gate.rights_per_item_required===true && d.release_gate.visual_subject_crop_match_required===true &&
       d.release_gate.guest_chrome_actual_get_decode_and_cdp_bytes_required===true &&
       d.release_gate.site_qa_pr_154_owns_browser_tests===true&&
       d.release_gate.wp_production_write_authorized===false&&
       d.release_gate.homepage_design_unchanged===true&&d.release_gate.no_spend===true,'release_gate');
 return {ok:errors.length===0,errors:[...new Set(errors)],image_count:(d?.rows||[]).length};
}
if (typeof require==='function'&&typeof module!=='undefined'&&require.main===module){
 const fs=require('node:fs');
 const d=JSON.parse(fs.readFileSync(__dirname+'/port_chicago_211_nps_proxy_20261103.json','utf8'));
 const result=validateLedger(d);console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1;
}
if(typeof module!=='undefined')module.exports={validateLedger};
