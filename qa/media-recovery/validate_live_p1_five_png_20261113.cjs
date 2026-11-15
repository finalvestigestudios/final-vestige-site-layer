'use strict';
// Offline integrity gate for a dated WordPress media audit; never fetches or writes a site.
const fs = require('node:fs');
const EXPECTED = Object.freeze([
  [34,39,'bceca0bd-a16f-44f7-be08-16376fbf08ca.png',2892087],
  [35,40,'377e08da-e121-4f57-9174-1548343402b3.png',2552136],
  [36,41,'a44f673d-a8a8-4c83-9f29-7e24dd55156b.png',2498247],
  [37,42,'c1237ffd-4a47-4988-8254-e3b021069e72.png',2488823],
  [38,43,'01340c2e-1165-4ca0-aa96-87398a83d13a.png',2836245]
]);
const exactUrl = file => 'https://finalvestige.com/wp-content/uploads/2026/08/' + file;
const isInt = n => Number.isSafeInteger(n);
const noClaim = r => ['wordpress_api_image_response_http_status','guest_browser_image_http_status','guest_browser_current_src','guest_browser_transferred_bytes','guest_browser_css_width','guest_browser_dpr','proposed_derivative_actual_bytes','actual_wire_savings_bytes'].every(k => r[k] === null);
function validateAudit(d) {
  const errors = [];
  const fail=(id,msg)=>errors.push(id+':'+msg);
  if(!d || typeof d!=='object' || Array.isArray(d)) return {status:'HOLD',errors:['invalid-document'],production_write_allowed:false};
  if(d.schema!=='fv-p1-five-png-live-inline-visual-weight-20261113-v1') fail('document','schema');
  if(d.captured_date!=='2026-11-13') fail('document','date');
  if(d.sources?.baseline_media_15_blob!=='5e474e1cb293353b2226d84fceedca0a182894d8') fail('document','historical-baseline-blob');
  if(d.sources?.historical_worklist_blob!=='2acd06a4ca4317646006eb6591face3fe76fedec') fail('document','worklist-blob');
  if(!Array.isArray(d.rows) || d.rows.length!==5) fail('document','five-rows-required');
  const seen=new Set();
  let total=0;
  for (const r of Array.isArray(d.rows)?d.rows:[]) {
    if(!r || typeof r!=='object'){fail('row','invalid');continue}
    const id=r.media_id, key=EXPECTED.find(x=>x[1]===id),p=String(id);
    if(!key){fail(p,'unknown-media');continue}
    if(seen.has(id)) fail(p,'duplicate');seen.add(id);
    const [post,media,file,bytes]=key,url=exactUrl(file);
    if(r.post_id!==post || r.media_id!==media || r.post_status!=='publish' || r.media_status!=='inherit') fail(p,'post-or-media-custody');
    if(r.media_source_url!==url || r.published_image_src!==url || r.archived_20261108_source_url!==url) fail(p,'exact-original-url');
    if(!String(r.post_img_class||'').split(/\s+/).includes('wp-image-'+media)) fail(p,'post-media-id-binding');
    if(r.stored_original_bytes!==bytes || r.archived_20261108_stored_bytes!==bytes) fail(p,'stored-size-custody');
    if(r.native_width!==1672 || r.native_height!==941 || r.wp_generated_subsize_count!==0 || r.media_mime!=='image/png') fail(p,'png-native-subsize-custody');
    if(r.published_html_width!==1024 || r.published_html_height!==576) fail(p,'html-declared-size');
    if(typeof r.published_alt!=='string' || !r.published_alt.trim() || /AI-assisted/i.test(r.published_alt)) fail(p,'image-alt-snapshot-mismatch');
    if(typeof r.published_caption!=='string' || !r.published_caption.startsWith('AI-assisted historical reconstruction')) fail(p,'published-caption-disclosure-lost');
    if(typeof r.media_library_alt!=='string' || !r.media_library_alt.startsWith('AI-assisted historical reconstruction') || r.editor_alternate_text_candidate!==r.media_library_alt) fail(p,'media-alt-custody');
    if(r.archived_rights_status!=='HISTORICAL_RECONSTRUCTION_CREATOR_LICENSE_UNVERIFIED' || r.source_rights_cleared!==false) fail(p,'unverified-creator-rights');
    if(r.proposed_derivative_max_width!==960 || r.proposed_derivative_max_height!==540 || !['WEBP_OR_PNG_AFTER_VISUAL_TEST'].includes(r.proposed_format)) fail(p,'conditional-960-geometry');
    if(!noClaim(r)) fail(p,'unmeasured-network-or-derivative-claimed');
    if(r.derivative_produced!==false || r.post_rewritten!==false || r.disposition!=='HOLD_IMAGE_RENDER_AND_RIGHTS_REVIEW') fail(p,'unauthorized-release-claim');
    total+=bytes;
  }
  if(seen.size!==5) fail('document','source-coverage');
  const c=d.counts||{};
  for(const [k,n] of Object.entries({posts_checked:5,media_originals_checked:5,direct_src_equality_confirmed:5,none_with_wp_generated_subsizes:5,caption_ai_assisted_disclosures_present:5,media_alt_ai_disclosures_present:5,published_img_alts_without_ai_phrase:5,stored_original_total_bytes:13267538,actual_visitor_transfer_bytes_measured:0,browser_confirmed_broken_images:0,derivatives_produced:0,production_writes:0})) if(c[k]!==n) fail('counts',k);
  if(total!==13267538) fail('document','recomputed-stored-size');
  for(const k of ['production_wp_posts_media_write','homepage_visual_design_change','image_binary_download','unlicensed_rehosting','subscription_spend','auto_rewrite_blocks','automatic_960px_derivatives']) if(d.safety?.[k]!==false) fail('safety',k);
  if(d.safety?.qa_intake_ownership!=='Site QA #154') fail('safety','collector-ownership');
  return {status:errors.length?'HOLD':'AUDIT_VALIDATED_HOLD_NO_RELEASE',errors,production_write_allowed:false,visitor_savings_verified:false};
}
if(require.main===module){
  const f=process.argv[2];if(!f){console.error('usage: node validate_live_p1_five_png_20261113.cjs <audit.json>');process.exit(2)}
  try{const out=validateAudit(JSON.parse(fs.readFileSync(f,'utf8')));console.log(JSON.stringify(out));if(out.status!=='AUDIT_VALIDATED_HOLD_NO_RELEASE')process.exitCode=1}
  catch(e){console.error('HOLD: '+e.message);process.exitCode=1}
}
module.exports={validateAudit};
