'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_pulaski_428.cjs');
const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'pulaski_428_idaho_loc_20261101.json'),'utf8'));
const frozen=JSON.parse(fs.readFileSync(path.join(__dirname,'parts','01.json'),'utf8'));
const copy=o=>JSON.parse(JSON.stringify(o));
test('exact six-source census, rights and unknown browser evidence passes',()=>{
 assert.deepEqual(validate(manifest,frozen),[]);
});
const adversarial=[
 ['schema changed',d=>{d.schema_version=2},'schema'],
 ['post changed',d=>{d.post.id=427},'post'],
 ['claimed different published image count',d=>{d.post.live_cms_img_count=5},'post'],
 ['falsified CMS source match',d=>{d.post.matched_frozen_exact_src_alt=false},'post'],
 ['falsified total posts',d=>{d.sitewide.published_posts=62},'census'],
 ['falsified offsite image count',d=>{d.sitewide.offsite_stored_refs=42},'census'],
 ['reported 42 prematurely confirmed',d=>{d.sitewide.reported_broken_42_browser_verified=true},'unsupported_claim'],
 ['reported 76pct prematurely measured',d=>{d.sitewide.reported_reduction_76_percent_measured=true},'unsupported_claim'],
 ['invented production repair',d=>{d.sitewide.production_images_repaired=1},'unsupported_claim'],
 ['six-slot audit shortened',d=>{d.rows.pop()},'row_count'],
 ['image identity slot swapped',d=>{d.rows[2].key='428:3'},'key_2'],
 ['post image URL changed',d=>{d.rows[1].published_source_url='https://bad.example/bigburn23.jpg'},'source_alt_1'],
 ['post alt changed without editorial review',d=>{d.rows[1].published_alt+=' changed'},'source_alt_1'],
 ['official identifier changed',d=>{d.rows[3].candidate.catalog_id='FAKE'},'archival_id_3'],
 ['lookalike catalog domain',d=>{d.rows[1].candidate.archive_record_url='https://bad.example/items/bigburn23.html'},'archival_id_1'],
 ['publisher asset replaced despite same basename',d=>{d.rows[2].candidate.candidate_asset_url='https://elsewhere.example/bigburn38.jpg'},'archival_id_2'],
 ['master hash invented',d=>{d.rows[2].candidate.master_binary_sha256='abc'},'fabricated_binary_identity_2'],
 ['pixel-identical asset fabricated',d=>{d.rows[0].candidate.confirmed_same_binary=true},'fabricated_binary_identity_0'],
 ['retriever inaccessible relabeled as 404',d=>{d.rows[0].retrieval.result='RETRIEVER_FETCH_404'},'fabricated_http_0'],
 ['web viewer called public Chrome',d=>{d.rows[1].retrieval.method='logged_out_Chrome'},'fabricated_http_1'],
 ['origin HTTP 200 invented',d=>{d.rows[2].retrieval.origin_http_status=200},'fabricated_http_2'],
 ['visitor HTTP 404 invented',d=>{d.rows[3].retrieval.visitor_http_status=404},'fabricated_http_3'],
 ['visitor byte count guessed',d=>{d.rows[4].retrieval.transferred_bytes=15000},'fabricated_http_4'],
 ['public domain signal changed to blanket license',d=>{d.rows[1].rights.archive_rights_signal='CC0'},'rights_1'],
 ['rights granted without approval',d=>{d.rows[4].rights.cache_reproduction_permission='APPROVED'},'rights_4'],
 ['archive credit removed',d=>{d.rows[3].rights.credit='source unknown'},'rights_3'],
 ['960px limit exceeded',d=>{d.rows[2].geometry.max_width_px=1280},'geometry_2'],
 ['master dimensions asserted without binary',d=>{d.rows[4].geometry.master_width_px=1200},'geometry_4'],
 ['upscaling allowed',d=>{d.rows[5].geometry.no_upscale=false},'geometry_5'],
 ['visitor naturalWidth invented',d=>{d.rows[1].guest_browser.natural_width_px=1000},'fabricated_browser_1_natural_width_px'],
 ['visitor broken flag invented',d=>{d.rows[0].guest_browser.visibly_broken=true},'fabricated_browser_0_visibly_broken'],
 ['visual screenshot invented',d=>{d.rows[0].guest_browser.screenshot_evidence_url='https://example.test/screenshot.png'},'fabricated_browser_0_screenshot_evidence_url'],
 ['staging readiness bypassed',d=>{d.rows[1].release.stage_ready=true},'release_1'],
 ['WordPress upload bypassed',d=>{d.rows[0].release.wordpress_media_upload_authorized=true},'release_0'],
 ['WordPress post rewrite bypassed',d=>{d.rows[4].release.wordpress_post_edit_authorized=true},'release_4'],
 ['editorial overclaim omitted',d=>{d.rows[4].visual_integrity.review_required=false},'editorial_integrity_4'],
 ['falsified WordPress original bytes',d=>{d.rows[0].wordpress_media_proof.wordpress_original_storage_bytes=5000000},'wordpress_media_0'],
 ['current WordPress image falsely upscaled',d=>{d.rows[0].wordpress_media_proof.no_upscale_maximum_for_present_wordpress_media_px.width=960},'wordpress_media_0'],
 ['guessed Jetpack visitor bytes',d=>{d.rows[0].wordpress_media_proof.actual_guest_transfer_bytes=90157},'wordpress_media_0']
];
for(const [name,change,expected] of adversarial){
 test(name,()=>{const mutated=copy(manifest);change(mutated);assert.ok(validate(mutated,frozen).includes(expected),name+' should fail closed on '+expected)});
}
