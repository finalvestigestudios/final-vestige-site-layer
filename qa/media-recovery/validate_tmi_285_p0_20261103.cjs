"use strict";
/** P0 Three Mile Island isolated rights and exact-origin evidence gate; no network and no publishing. */
function validate(a, frozen, actualBlobSha) {
  const errors=[];
  const need=(ok,msg)=>{if(!ok)errors.push(msg);};
  need(a && a.schema_version===1,"schema");
  need(a?.inventory_blob_sha==="49183f66f880f7c4dfd363acca906876877f2e5e" && a.inventory_blob_sha===actualBlobSha,"frozen SHA mismatch");
  const saved=(frozen?.images||[]).filter(x=>x.post_id===285).sort((x,y)=>x.slot-y.slot);
  need(saved.length===6 && a?.rows?.length===6,"six exact slots required");
  need(a?.word_press?.status==="publish" && a.word_press.exact_source_and_alt_match===6,"live source inventory not verified");
  need(a?.historic_baseline?.published_posts===61 && a.historic_baseline.image_slots===355 && a.historic_baseline.external_source_slots===288 && a.historic_baseline.oversized_wp_originals_over_1_5_mib===13,"baseline mismatch");
  need(a?.historic_baseline?.reported_broken_browser_verified===false && a.historic_baseline.weight_reduction_measured===false && a.historic_baseline.production_replacements===0,"unsupported release/savings claim");
  need(a?.observation_protocol?.visitor_chromium_executed===false,"unsubstantiated browser claim");
  const rows=a?.rows||[];need(new Set(rows.map(x=>x.image_key)).size===6,"duplicate image key");
  for(let i=0;i<6;i++){
    const r=rows[i],s=saved[i];if(!r||!s)continue;
    need(r.image_key===s.key && r.source_url===s.source_url && r.alt===s.alt && r.post_url===s.post_url && r.source_host===s.source_host,"source/ALT mismatch "+i);
    need(r.rights_review==="HOLD" && r.wordpress_write_authorized===false && r.source_cache_authorized===false,"unapproved publication "+i);
    need(r.target_max_width_px===960,"resize cap "+i);
    need(r.exact_binary_and_crop_equivalence_verified===false,"unverified source image identity "+i);
    const seen=[0,1,3,4].includes(i);
    need(r.retriever_status===(seen?"DISPLAYED_INDEPENDENT_VIEWER":i===2?"RETRIEVER_REDIRECT_INACCESSIBLE":"RETRIEVER_FETCH_404"),"incorrect retriever result "+i);
    need(r.retriever_wrapper_code===(i===2?500:i===5?404:null),"wrapper status not substantiated "+i);
    need(Object.values(r.browser||{}).length===9 && Object.values(r.browser).every(x=>x===null),"guest browser values not collected "+i);
    if(i!==5){need(r.verified_original_width_px===null && r.verified_original_height_px===null && r.conditional_derivative_width_px===null && r.conditional_derivative_height_px===null,"invented image dimensions "+i);}
  }
  const r=rows[5]||{},candidate=r.primary_candidate||{},other=r.different_scene_historical_option||{};
  need(r.verified_original_width_px===819 && r.verified_original_height_px===614 && r.conditional_derivative_width_px===819 && r.conditional_derivative_height_px===614,"catalog original must remain 819x614 no-upscale");
  need(candidate.catalog_url==="https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg" && candidate.original_file_url==="https://upload.wikimedia.org/wikipedia/commons/0/09/Three_mile_island_062010.jpg","publisher-linked archival source mismatch");
  need(candidate.release_candidate===false && candidate.license==="PD_SELF_CATALOG_ASSERTION_ITEM_RIGHTS_REVIEW_REQUIRED","rights overclaim");
  need(typeof r.visual_crop_difference==="string" && r.visual_crop_difference.includes("16:9") && r.visual_crop_difference.includes("819x614"),"crop difference risk lost");
  need(other.exact_scene_equivalent===false && other.publication_allowed===false && other.conditional_no_upscale_px?.[0]===960,"1979 image swapped for 2010 scene");
  need(a?.editorial_proposals?.length===2 && a.editorial_proposals.every(p=>p.publish_approved===false),"editorial publication unauthorized");
  return errors;
}
module.exports={validate};
