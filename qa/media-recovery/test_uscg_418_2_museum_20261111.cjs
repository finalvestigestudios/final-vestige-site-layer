'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const path = require('node:path');
const { assess } = require('./validate_uscg_418_2_museum_20261111.cjs');
const a = JSON.parse(readFileSync(path.join(__dirname,'uscg_418_2_museum_same_scene_20261111.json'),'utf8'));
const mutate = (fn) => { const x = structuredClone(a); fn(x); return assess(x); };
test('the pinned museum, mirror and Coast Guard source audit is consistent and held', () => {
  const result=assess(a); assert.deepEqual(result.errors,[]); assert.equal(result.valid,true); assert.equal(result.decision,'HOLD_FOR_GUEST_RIGHTS_AND_VISUAL_QA');
});
const negative = [
  ['wrong original image URL', x=>x.article.published_original_src='https://www.example.org/fake.jpg'],
  ['wrong article', x=>x.article.url='https://finalvestige.com/'],
  ['wrong image slot', x=>x.article.slot='418:1'],
  ['turning retriever 403 into real guest 403', x=>x.observations.actual_guest_cdp.image_request_status=403],
  ['unknown guest CDN request reported', x=>x.observations.actual_guest_cdp.current_src=x.article.published_original_src],
  ['inventing transfer bytes', x=>x.observations.actual_guest_cdp.encoded_transfer_bytes=1024],
  ['inventing successful museum HTTP', x=>x.observations.museum_preview_retriever.origin_http_status=200],
  ['inventing successful mirror HTTP', x=>x.observations.lighthousefriends_retriever.guest_http_status=200],
  ['treating retriever wrapper as origin status', x=>x.observations.original_retriever.method='ORIGIN_RESPONSE'],
  ['missing museum media URL', x=>x.candidate_mapping[0].preview_image_url='https://example.org/foo.jpg'],
  ['missing original Coast Guard photo credit', x=>x.candidate_mapping[0].displayed_credit='unknown'],
  ['misstating the filename preview as full native', x=>x.candidate_mapping[0].original_native_dimensions_px=[600,463]],
  ['inventing 960px derivative', x=>x.candidate_mapping[0].conditional_960px_output_px=[960,741]],
  ['inventing binary/pixel match', x=>x.candidate_mapping[0].exact_pixel_or_file_hash_identity_proven=true],
  ['inventing museum license approval', x=>x.candidate_mapping[0].item_specific_commercial_reuse_clearance=true],
  ['inventing mirror permission', x=>x.candidate_mapping[1].cache_or_mirror_approved=true],
  ['turning same-scene evidence into same-file identity', x=>x.candidate_mapping[1].subject_scene_correspondence='BINARY_IDENTICAL'],
  ['unverified 960px upscale', x=>x.rights_and_size.derivative_960px_authorized=true],
  ['unsafe crop', x=>x.rights_and_size.no_crop=false],
  ['direct production block rewrite', x=>x.decision.wordpress_block_rewrite_approved=true],
  ['unauthorized media upload', x=>x.decision.wordpress_media_upload_approved=true],
  ['premature guest failure claim', x=>x.decision.confirmed_guest_failure=true],
  ['invented 76% measurement', x=>x.sitewide_baseline.measured_cold_image_transfer_reduction_pct=76],
  ['confused 61/66 cohorts', x=>x.sitewide_baseline.historical_posts=66],
  ['incorrect oversize threshold count', x=>x.sitewide_baseline.oversized_wordpress_originals_gt_1500000_bytes=14],
  ['unauthorized cache', x=>x.decision.binary_download_or_rehost_approved=true],
  ['authorization to deploy', x=>x.decision.merge_or_deploy_approved=true]
];
for (const [name, edit] of negative) test('reject '+name,()=>{const result=mutate(edit);assert.equal(result.valid,false,name);assert.ok(result.errors.length>0,name)});
