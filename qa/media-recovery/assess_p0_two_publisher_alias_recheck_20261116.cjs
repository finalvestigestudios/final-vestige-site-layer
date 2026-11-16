'use strict';
// Static, OFFLINE historical web-reader recheck; never fetches media or authorizes WordPress writes.
function assess(x){
 const errors=[];const must=(ok,c)=>{if(!ok)errors.push(c)};
 const pins=[
  ["287:5",287,"https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg","https://i0.wp.com/stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg?ssl=1","RETRIEVER_404",404,"https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg","https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/","SAME_PUBLISHER_SAME_BASENAME_NOT_BINARY_PROVEN","HOLD_PRIVATE_PUBLISHER_PHOTO"],
  ["418:2",418,"https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg","https://i0.wp.com/www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg?ssl=1","RETRIEVER_403",403,"https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/5_-Scotch_Cap_debris2_1946-600x463.jpg","https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/","SAME_NAMED_HISTORIC_PHOTO_PREVIEW_UNHASHED","HOLD_ITEM_LEVEL_REPRODUCTION_REVIEW"]
 ];
 must(x?.schema==="fv-p0-alias-independent-recheck-v1","schema");
 must(x?.observed_at_local==="2026-11-16T09:30:31-08:00"&&x?.method==="PUBLIC_WEB_RETRIEVER_NOT_COLD_VISITOR_BROWSER","method");
 must(x?.source_custody?.p0_manifest_blob_sha==="93ed6631518dc0c06253719b61d1cf50b623f6f0"&&x.source_custody.p0_git_commit==="4366489a68620d26592d8438b4402feb453c3166"&&x.source_custody.skyway_git_blob_sha==="e6027acdd0adc97ed84725b11f2262d2d5f03daa","source_custody");
 must(x?.historical_cohort?.posts===61&&x.historical_cohort.image_refs===355&&x.historical_cohort.offsite_refs_site_qa===286&&x.historical_cohort.offsite_refs_media===288&&x?.later_cohort?.posts===66&&x.later_cohort.image_refs===361,"cohorts");
 must(x?.reported_42_browser_failures_confirmed===false&&x?.claimed_76_percent_visitor_wire_reduction_verified===false,"unverified_claims");
 must(x?.oversized_wp_originals?.count===20&&x.oversized_wp_originals.stored_bytes===64385752&&x.oversized_wp_originals.guest_wire_bytes===null,"storage_not_wire");
 must(x?.new_image_downloads===0&&x.production_wordpress_writes===0&&x.homepage_design_changes===0&&x.paid_actions===0,"no_writes");
 must(x?.next_gate==="SITE_QA_154_GUEST_BROWSER_CURRENT_SRC_HTTP_MIME_DECODE_SCREENSHOT_WIRE_BYTES_THEN_ITEM_RIGHTS_FRAME_AND_STAGING_REVIEW","guest_gate");
 must(Array.isArray(x?.rows)&&x.rows.length===2,"two_slots");
 for(let i=0;i<2;i++){
  const r=x?.rows?.[i],p=pins[i];if(!r){must(false,"missing_slot_"+i);continue}
  must(r.slot===p[0]&&r.post_id===p[1],"slot_identity_"+i);
  must(r.stored_image_url===p[2]&&r.recorded_jetpack_view_url===p[3],"exact_wp_url_"+i);
  must(r.reader_source_result===p[4]&&r.reader_source_tool_error_code===p[5]&&r.source_numeric_http_get_status===null,"reader_not_http_"+i);
  must(r.reader_proxy_result==="TOOL_INACCESSIBLE"&&r.proxy_numeric_http_get_status===null,"proxy_not_http_"+i);
  must(r.candidate_asset_url===p[6]&&r.candidate_catalog_url===p[7]&&r.candidate_reader_result==="IMAGE_DISPLAYED"&&r.candidate_numeric_http_get_status===null,"candidate_reader_not_http_"+i);
  must(r.candidate_relation===p[8]&&r.candidate_rights===p[9]&&typeof r.required_credit==="string"&&r.required_credit.length>10,"candidate_rights_"+i);
  must(typeof r.editorial_flag==="string"&&r.editorial_flag.length>20,"editorial_"+i);
  must(r.candidate_native_dimensions===null&&r.max_derivative_width_px===960&&
    (i===0?r.review_dimensions===null:r.review_dimensions?.width===600&&r.review_dimensions.height===463&&r.review_dimensions.basis==="PUBLISHER_PREVIEW_SUFFIX_600x463_UNVERIFIED_SOURCE_BINARY"),"no_upscale_geometry_"+i);
  must([r.browser_current_src,r.browser_http_get_status,r.browser_natural_width,r.browser_decoded,r.browser_transfer_bytes,r.browser_screenshot].every(z=>z===null),"no_guest_claim_"+i);
  must(r.same_frame_crop_proven===false&&r.candidate_sha256===null&&r.cache_authorized===false&&r.wp_upload_authorized===false&&r.wp_post_edit_authorized===false&&r.decision==="HOLD","release_hold_"+i);
 }
 return {ok:errors.length===0,errors,review_only:true,visitor_broken_confirmed:0,wordpress_writes_allowed:false};
}
module.exports={assess};
if(require.main===module){const fs=require('node:fs');const p=require('node:path');const a=JSON.parse(fs.readFileSync(p.join(__dirname,'p0_two_publisher_alias_recheck_20261116_0930pt.json'),'utf8'));const r=assess(a);console.log(JSON.stringify(r));if(!r.ok)process.exitCode=1}
