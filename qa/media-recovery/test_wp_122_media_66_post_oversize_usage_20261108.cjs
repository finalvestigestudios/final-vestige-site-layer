'use strict';
const assert=require('node:assert/strict');
const {test}=require('node:test');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_wp_122_media_66_post_oversize_usage_20261108.cjs');
const raw=JSON.parse(fs.readFileSync(path.join(__dirname,'wp_122_media_66_posts_oversize_usage_20261108.json'),'utf8'));
const copy=()=>JSON.parse(JSON.stringify(raw));
test('live 66-post metadata is source-only and internally reconciled',()=>{
 assert.deepEqual(validate(raw),[]);
 assert.equal(raw.rows.length,15);
 assert.equal(raw.counts.inline_matched_originals,11);
 assert.equal(raw.counts.unmatched_to_published_inline_images,4);
 assert.equal(raw.counts.published_post_count_with_inline_matches,8);
 assert.equal(raw.counts.inline_matched_original_stored_bytes,38480915);
 assert.equal(raw.counts.unmatched_original_stored_bytes,8615864);
 assert.equal(raw.counts.guest_browser_bytes_measured,0);
 assert.equal(raw.safeguards.wordpress_production_writes,0);
});
function blocked(name,mutation,reason){
 test(name,()=>{
  const d=copy();mutation(d);
  const errors=validate(d);
  assert.ok(errors.length>0,'mutation incorrectly passed validation');
  if(reason)assert.ok(errors.some(x=>x.includes(reason)),JSON.stringify(errors));
 });
}
blocked('fabricated 42 browser failures',x=>x.counts.reported_42_broken_verified=true,'false_42');
blocked('fabricated 76 percent reduction',x=>x.counts.reported_76_percent_transfer_reduction_verified=true,'false_42');
blocked('fabricated guest response 404',x=>x.rows[0].actual_guest_http_status=404,'fabricated_browser');
blocked('invented wire bytes',x=>x.counts.guest_browser_bytes_measured=200,'false_42');
blocked('storage sum substituted',x=>x.rows[0].stored_original_bytes=1,'source_or_storage');
blocked('incorrect 960px upscale',x=>x.rows[0].conditional_no_upscale_px=[1280,850],'no_upscale');
blocked('historical source mapped to another post',x=>x.rows[0].raw_published_post_occurrences[0].post_id=285,'post_identity');
blocked('transformed Jetpack source points at a different asset',x=>x.rows[0].raw_published_post_occurrences[0].source_url_in_raw_html='https://i0.wp.com/example.com/wrong.jpg','jetpack_identity');
blocked('invented cache and republication clearance',x=>x.rows[0].rights_release_authorized=true,'fabricated_browser');
blocked('unmatched archive image treated as published',x=>x.rows.find(y=>y.media_id===2148).raw_published_post_occurrences.push({...x.rows[0].raw_published_post_occurrences[0]}),'usage_count');
blocked('missing post in 66-post read',x=>x.current_published_post_ids.pop(),'census');
blocked('production WordPress writes prohibited',x=>x.safeguards.wordpress_production_writes=1,'unsafe');
blocked('published-byte arithmetic changed',x=>x.counts.inline_matched_original_stored_bytes++,'math');
blocked('no binary downloading or caching allowed',x=>x.safeguards.external_binary_downloads_or_caches++,'unsafe');
blocked('post content scan must not have errors',x=>x.scan_errors.push({id:299,error:'test'}),'unsafe');
