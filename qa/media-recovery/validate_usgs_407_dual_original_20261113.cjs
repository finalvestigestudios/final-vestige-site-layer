'use strict';
// Fail closed: verifies source path/provenance and protects against mistaking a
// web-tool binary wrapper for a visitor-visible HTTP failure.
// No network requests, filesystem writes or image fetching.
const ORIGIN = 'https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg';
const ALT = 'https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg';
const CATALOG_A = 'https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0';
const CATALOG_B = 'https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959';
function assess(x) {
  const errors = [];
  const check = (ok, message) => { if (!ok) errors.push(message); };
  check(x?.schema === 'fv-p0-usgs-dual-original-link-evidence-v1', 'schema');
  check(x?.source_item?.post_id === 407 && x?.source_item?.slot === '407:1' && x?.source_item?.status === 'publish', 'post_binding');
  check(x?.source_item?.stored_wordpress_src_readback_exact === true && x?.source_item?.published_src === ORIGIN, 'wordPress_exact_original');
  check(x?.primary_source_a?.catalog_url === CATALOG_A && x?.primary_source_a?.catalog_original_link_url === ORIGIN, 'usgs_original_link_a');
  check(x?.primary_source_b?.catalog_url === CATALOG_B && x?.primary_source_b?.catalog_original_link_url === ALT, 'usgs_original_link_b');
  check(x?.primary_source_a?.retriever_result === 'ERROR_WRAPPER_UNSUPPORTED_BINARY_OCTET_STREAM' && x?.primary_source_a?.retriever_wrapper_code === 400, 'tool_wrapper_not_origin');
  check(x?.primary_source_b?.retriever_result === 'IMAGE_RENDERED_BY_WEB_RETRIEVER', 'alternate_tool_display');
  for (const source of [x?.primary_source_a, x?.primary_source_b]) {
    check(source?.origin_http_status === null && source?.browser_http_status === null && source?.encoded_transfer_bytes === null, 'origin_browser_wire_unverified');
  }
  check(x?.primary_source_a?.browser_decoded_pixels === null, 'original_pixels_unverified');
  const i=x?.identity || {};
  check(i.publisher === 'U.S. Geological Survey' && i.photographer === 'J. R. Stacy' && i.filename_match === true, 'source_identity');
  check(i.same_binary_sha256 === null && i.verified_same_binary === false && i.verified_same_crop === false && i.native_dimensions_px === null, 'binary_crop_dimensions_unverified');
  check(ORIGIN.split('/').pop() === ALT.split('/').pop(), 'official_link_basename');
  const rights=x?.rights || {};
  check(rights.catalog_source_usage === 'Public Domain' && rights.credit === 'USGS photo by J. R. Stacy', 'official_rights_credit');
  check(rights.republishing_permission_review_completed === false && rights.third_party_caching_authorized === false && rights.wordpress_upload_authorized === false, 'no_rehosting_grant');
  const g=x?.release_gate || {};
  check(g.guest_failure_proven === false && g.guest_current_src === null && g.guest_http_status === null && g.guest_natural_width === null && g.guest_natural_height === null && g.guest_wire_bytes === null, 'guest_failure_not_proven');
  check(g.exact_byte_and_crop_parity_proven === false && g.rendered_css_width === null && g.device_pixel_ratio === null, 'visual_density_hold');
  check(g.conditional_max_derivative_width_px === 960 && g.no_upscale === true, '960_no_upscale');
  check(g.approved_to_swap_external_src === false && g.approved_to_rehost === false && g.disposition === 'HOLD_PENDING_SITEQA_GUEST_AND_VISUAL_RIGHTS_STAGING', 'release_hold');
  const b=x?.baseline || {};
  check(b.frozen_posts === 61 && b.frozen_inline_images === 355 && b.historical_broken_reports === 42 && b.guest_confirmed_broken_count === null, 'historical_not_confirmed');
  check(b.stored_wp_originals_above_decimal_1500000_bytes === 15 && b.stored_oversize_originals_bytes === 47096779 && b.claimed_savings_percent === 76 && b.claimed_savings_verified === false, 'weight_unmeasured');
  const safe=x?.safety || {};
  for(const k of ['external_image_downloads','third_party_copies','production_wordpress_writes','production_uploads','home_page_changes','merges','deployments','spend_usd'])
    check(safe[k] === 0, 'forbidden_change_'+k);
  return {ok:errors.length===0,errors};
}
if (require.main === module) {
  const fs=require('node:fs');
  const filename=process.argv[2];
  if (!filename || fs.statSync(filename).size > 100000) { console.error('Expected bounded JSON file'); process.exitCode=2; }
  else { const report=assess(JSON.parse(fs.readFileSync(filename,'utf8'))); console.log(JSON.stringify(report)); if(!report.ok) process.exitCode=1; }
}
module.exports={assess};
