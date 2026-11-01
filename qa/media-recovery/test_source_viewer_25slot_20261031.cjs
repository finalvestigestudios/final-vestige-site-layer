'use strict';
/** Run: node --test qa/media-recovery/test_source_viewer_25slot_20261031.cjs */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const audit=JSON.parse(fs.readFileSync(path.join(__dirname,'source_viewer_25slot_20261031.json'),'utf8'));
const rows=audit.observations;
test('25 slots: three articles, unique keys, all third-party',()=>{
 assert.deepEqual(audit.posts.map(x=>[x.post_id,x.source_images]),[[268,10],[407,8],[432,7]]);
 assert.equal(rows.length,25);assert.equal(new Set(rows.map(x=>x.image_key)).size,25);
 assert.ok(rows.every(x=>new URL(x.exact_stored_url).hostname!=='finalvestige.com'));
});
test('independent image-viewer observations never masquerade as browser HTTP status',()=>{
 assert.equal(audit.scope.article_browser_verification,0);
 assert.ok(rows.every(x=>x.actual_browser_http_status===null&&x.actual_visitor_image_decoded===null&&x.verified_broken_for_visitors===null&&x.cdp_encoded_transfer_bytes===null));
 assert.equal(rows.filter(x=>x.viewer_result==='IMAGE_RENDERED_BY_VIEWER').length,8);
 assert.equal(rows.filter(x=>x.viewer_result!=='IMAGE_RENDERED_BY_VIEWER').length,17);
});
test('eight viewer redirect failures and one octet-stream issue are NOT 404 claims',()=>{
 const redirects=rows.filter(x=>x.viewer_result==='VIEWER_REDIRECT_DESTINATION_UNAVAILABLE');
 assert.equal(redirects.length,8);assert.equal(redirects.filter(x=>x.post_id===432).length,7);
 assert.ok(redirects.every(x=>x.viewer_redirect_destination_url===x.exact_stored_url.replace('https://www.','https://')));
 assert.deepEqual(rows.filter(x=>x.viewer_result==='VIEWER_UNSUPPORTED_BINARY_OCTET_STREAM').map(x=>x.image_key),['407:1']);
});
test('exact current CMS source and ALT match frozen census; archive leads preserved',()=>{
 assert.ok(rows.every(x=>x.source_url_and_alt_match_frozen_census===true&&x.stored_alt&&x.exact_stored_url.startsWith('https://')));
 assert.ok(rows.filter(x=>x.post_id===432).every(x=>x.official_candidate_record_url?.includes('floridamemory.com/items/show/')));
});
test('rights, exact binary identity, sizes, publishing and savings remain closed',()=>{
 assert.equal(audit.scope.production_images_changed,0);
 assert.ok(rows.every(x=>x.target_width_max_px===960&&x.target_dimensions_px===null&&x.original_image_dimensions_px===null&&x.allow_upscaling===false&&x.preserve_aspect_ratio===true&&x.original_asset_sha256===null&&x.binary_match_verified===false&&x.per_item_reuse_rights_cleared===false&&x.wordpress_upload_authorized===false&&x.wordpress_post_rewrite_authorized===false&&x.verified_76_percent_reduction===false));
});

test('USGS authoritative Original fallback decodes but is not an approved substitution',()=>{
 const r=rows.find(x=>x.image_key==='407:1'),c=r.publisher_original_candidate;
 assert.equal(c.record_url,'https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959');
 assert.equal(c.url,'https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg');
 assert.equal(c.publisher_label,'Original');assert.equal(c.viewer_result,'IMAGE_RENDERED_BY_VIEWER');
 assert.equal(c.source_record_photographer,'J. R. Stacy');assert.equal(c.record_rights_statement,'Public Domain');
 assert.equal(c.same_binary_as_stored_url_verified,false);assert.equal(c.per_item_editorial_rights_approval,false);
 assert.equal(c.maximum_proposed_output_width_px,960);assert.equal(c.target_dimensions_px,null);
 assert.equal(c.master_sha256,null);assert.equal(c.wordpress_upload_authorized,false);
});
