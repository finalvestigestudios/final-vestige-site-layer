'use strict';
/** Source-only, fail-closed visual-integrity audit. No network, media or CMS writes. */
const fs = require('node:fs');
const path = require('node:path');
const EXPECTED = 'https://cloudfront-us-east-1.images.arcpublishing.com/deseretnews/PLWPL72QKJB7BBFJWTXJWVK6QQ.JPG';
const CATALOG = 'https://commons.wikimedia.org/wiki/File:Teton_Dam_Embankment_Leak_-_DPLA_-_fee62ebfb4a83f7a00334af1e3dbc6bc.jpg';
function validate(a) {
  const errors = [], must = (v, why) => { if (!v) errors.push(why); };
  must(a?.schema === 'fv-teton-291-duplicate-scene-gate-v1', 'schema');
  must(a?.post?.id === 291 && a.post.status === 'publish' && a.post.url === 'https://finalvestige.com/2026/08/19/one-bulldozer-never-came-back-teton-dam/', 'live post identity');
  must(a?.pinned_inventory?.git_blob === '48e1ebf07207e948ba5802e714eb39659d2e1c1d', 'pinned inventory');
  must(a?.source_reused === EXPECTED && a?.renderer?.exact_url_rendered === true, 'repeated exact source and retriever observation');
  must(a?.renderer?.origin_http_status === null && a.renderer.guest_browser_http_status === null && a.renderer.bytes_transferred === null && a.renderer.image_dimensions_px === null, 'no fabricated browser/network measurements');
  must(Array.isArray(a?.rows) && a.rows.length === 2, 'two slots');
  const one = a?.rows?.find(r => r.key === '291:2'), two = a?.rows?.find(r => r.key === '291:5');
  must(one && two && one.source_url === EXPECTED && two.source_url === EXPECTED, 'both slots still same URL');
  must(one?.alt === 'Growing breach in Teton Dam during the final hour before collapse.' && one?.claim_subject === 'dam_breach_progression' && one?.retrieved_visual_matches_claim === false && one?.visitor_visual_status === 'UNVERIFIED', 'incorrect breach-scene disclosure');
  must(two?.alt === 'Aftermath of the Teton Dam failure and downstream cleanup in Idaho.' && two?.claim_subject === 'downstream_cleanup' && two?.retrieved_visual_matches_claim === true && two?.visitor_visual_status === 'UNVERIFIED', 'aftermath scene disclosure');
  must(one?.caption === 'The failure progressed rapidly enough to be photographed frame by frame.' && two?.caption === 'The Teton failure became both a disaster scene and a forensic engineering site.', 'exact current Gutenberg captions');
  must(one?.action === 'REVIEW_REPLACEMENT_FOR_INCORRECT_HISTORICAL_SCENE' && two?.action === 'RETAIN_FOR_SCENE_PENDING_ORIGIN_RIGHTS_AND_BROWSER_QA', 'no automatic rewrite');
  const c = a?.candidate_for_291_2;
  must(c?.naid === 28894684 && c?.rendition_catalog === CATALOG && c?.historical_date === '1976-06-05' && c?.candidate_is_different_photo === true && c?.same_original_binary === false, 'archival photo identity');
  must(c?.master_width_px === 2558 && c.master_height_px === 1728 && c.conditional_width_px === 960 && c.conditional_height_px === Math.round(1728 * 960 / 2558) && c.no_upscale === true, 'no upscale and correct geometry');
  must(c?.rights_rehosting_authorized === false && c?.binary_fetched === false && c?.scene_subject_match === 'CATALOG_AND_RETRIEVED_VISUAL_MATCH_TO_GROWING_BREACH_NOT_BINARY_VERIFIED' && c?.current_rendition_cropped_since_2023 === true && c?.avoid_likely_duplicate_with_post_image_291_0 === true && JSON.stringify(c?.prior_uncropped_rendition_dimensions_px) === '[2852,1980]', 'rights / source limits');
  const d = a?.decision;
  must(d?.browser_broken_images_confirmed === null && d?.sitewide_claim_42_broken_verified === false && d?.sitewide_claim_76_percent_weight_reduction_verified === false && d?.image_transfer_reduction_measured === null, 'no unverifiable visitor/performance claims');
  must(d?.wordpress_media_upload_authorized === false && d.wordpress_edit_authorized === false && d.cache_authorized === false && d.publish_authorized === false && d.production_repairs === 0, 'no production or copyright permission');
  return {ok:errors.length===0, errors, slots:2, documented_visual_mismatch:!!one && one.retrieved_visual_matches_claim===false, production_changes:0};
}
if (require.main === module) {
  try { const p = process.argv[2] || path.join(__dirname,'teton_291_live_visual_mismatch_20261105.json'); const result = validate(JSON.parse(fs.readFileSync(p,'utf8'))); console.log(JSON.stringify(result,null,2)); if (!result.ok) process.exitCode=1; }
  catch(e) { console.error('TETON_AUDIT_ERROR '+e.message); process.exitCode=2; }
}
module.exports = {validate};
