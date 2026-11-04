'use strict';
// Read-only source-evidence gate for the 2026-11-04 USS Pueblo six-slot recovery ledger.
// This must NEVER modify a WordPress post, download binaries, or certify a browser failure.
const EXPECTED_IDS=['428-GX-USN-1129207','NH 75559','NH 75561','K-64683','NH 68705','K-64728'];
const EXPECTED_CATALOG=[
'https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/ships-us/ships-usn-p/uss-pueblo-ager-2/428-gx-usn-1129207.html',
'https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-75000/NH-75559.html',
'https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-75000/NH-75561.html',
'https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g-k/80-G-K-60000/K-64683.html',
'https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-68000/NH-68705.html',
'https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g-k/80-G-K-60000/K-64728.html'
];
const PINS={part:'qa/media-recovery/parts/03.json',blob:'49183f66f880f7c4dfd363acca906876877f2e5e',post:280,refs:6};
const CATALOG_DIMENSIONS=[[3263,2244],[null,null],[null,null],[6184,4978],[6312,4750],[null,null]];
function validate(audit,part,actualBlobSha) {
  const errors=[];
  function check(ok,label) {if(!ok) errors.push(label);}
  check(audit && audit.schema==='fv.media_recovery.pueblo_280.v1','schema');
  check(audit && audit.mode==='SOURCE_ONLY_READ_ONLY','read_only_mode');
  check(actualBlobSha===PINS.blob,'live_git_blob_pin');
  check(audit?.frozen?.git_blob_sha===PINS.blob && audit?.frozen?.part_path===PINS.part,'recorded_blob_pin');
  check(audit?.frozen?.post_id===PINS.post && audit?.frozen?.original_refs===6,'post_pin');
  check(audit?.frozen?.baseline_posts===61 && audit?.frozen?.baseline_images===355 &&
        audit?.frozen?.external_refs===288 && audit?.frozen?.oversize_originals===13,'baseline');
  check(audit?.live_wordpress_readonly?.method==='WordPress posts.get context=edit, read-only; no production writes' &&
        audit?.live_wordpress_readonly?.status==='publish' &&
        audit?.live_wordpress_readonly?.post_id===280 &&
        audit?.live_wordpress_readonly?.modified_utc==='2026-11-02T21:39:55' &&
        audit?.live_wordpress_readonly?.html_image_tags===6 &&
        audit?.live_wordpress_readonly?.exact_src_matches_frozen===6 &&
        audit?.live_wordpress_readonly?.exact_alt_matches_frozen===6 &&
        audit?.live_wordpress_readonly?.images_with_html_width_and_height===0 &&
        audit?.live_wordpress_readonly?.loaded_image_bytes===null &&
        audit?.live_wordpress_readonly?.guest_browser_successes===null &&
        audit?.live_wordpress_readonly?.origin_statuses===null,'live_wordpress_read_only_integrity');
  check(audit?.results?.live_cms_src_matches===6 &&
        audit?.results?.live_cms_alt_matches===6 &&
        audit?.results?.html_image_dimension_attributes_present===0,'live_rendered_img_dimensions');
  check(audit?.frozen?.reported_broken_42==='UNVERIFIED' &&
        audit?.frozen?.claimed_wire_reduction_76_percent==='UNMEASURED','unverified_claims');
  check(audit?.results?.origin_http_codes_verified===0 &&
        audit?.results?.guest_browser_failures_verified===0 &&
        audit?.results?.production_replacements===0 &&
        audit?.results?.exact_binary_identity_verifications===0,'no_invented_proof');
  check(Array.isArray(audit?.images) && audit.images.length===PINS.refs,'ledger_count');
  check(Array.isArray(part?.images),'source_part_present');
  const source=Array.isArray(part?.images)?part.images.filter(x=>x.post_id===PINS.post):[];
  check(source.length===PINS.refs,'source_part_six_slots');
  if(!Array.isArray(audit?.images)) return errors;
  const seen=new Set();
  for(let i=0;i<audit.images.length;i++){
    const row=audit.images[i], original=source[i], dim=CATALOG_DIMENSIONS[i];
    check(row?.key==='280:'+i && !seen.has(row?.key),'key_'+i);seen.add(row?.key);
    check(row?.post_id===PINS.post,'post_'+i);
    check(original?.key===row?.key &&
          row?.original_src===original?.source_url &&
          row?.original_alt===original?.alt &&
          row?.html_width_px===original?.width_px &&
          row?.html_height_px===original?.height_px,'original_identity_'+i);
    check(row?.archive?.publisher==='Naval History and Heritage Command' &&
          row?.archive?.catalog_id===EXPECTED_IDS[i] &&
          row?.archive?.catalog_url===EXPECTED_CATALOG[i],'primary_catalog_'+i);
    check(row?.archive?.source_binary_sha256===null &&
          row?.archive?.original_binary_identity_verified===false,'no_binary_claim_'+i);
    check(row?.retrieval?.original_url===row?.original_src &&
          row?.retrieval?.method==='web.open text retriever, NOT visitor browser' &&
          row?.retrieval?.tool_outcome===(i===4?'TOOL_ACCESS_UNAVAILABLE':'WRAPPER_502'),'transport_evidence_'+i);
    check(row?.retrieval?.actual_origin_http_status===null &&
          row?.retrieval?.guest_browser_http_status===null &&
          row?.retrieval?.mime_type===null &&
          row?.retrieval?.natural_width_px===null &&
          row?.retrieval?.natural_height_px===null &&
          row?.retrieval?.decoded===null &&
          row?.retrieval?.wire_bytes===null &&
          row?.retrieval?.broken_for_visitors===null,'no_fake_browser_status_'+i);
    check(row?.retrieval?.image_search_displayed===((i===2||i===5)?true:null),'image_search_observation_'+i);
    const [w,h]=dim;
    check(row?.derivative?.source_catalog_master_width_px===w &&
          row?.derivative?.source_catalog_master_height_px===h,'catalog_dimensions_'+i);
    check(row?.derivative?.no_upscale===true && row?.derivative?.max_width_px===960 &&
          row?.derivative?.conditional_height_px===(w===null?null:Math.round(960*h/w)),'proportional_960px_'+i);
    check(row?.rights?.status==='ITEM_SPECIFIC_REVIEW_REQUIRED' &&
          row?.rights?.license===null &&
          row?.rights?.wordPress_upload_allowed===false &&
          row?.rights?.local_cache_allowed===false &&
          row?.rights?.post_rewrite_allowed===false,'rights_hold_'+i);
  }
  check(audit.images[4]?.archive?.mapping_kind==='DIFFERENT_ASSET_ALTERNATE_NOT_IDENTICAL' &&
        /not an exact replacement/i.test(audit.images[4]?.review_flag||''),'banner_different_photo_hold');
  check(/HOLD all caching\/WP writes/.test(audit?.wordpress_plan||''),'wordpress_hold');
  return errors;
}
module.exports={validate};
