'use strict';
const fs = require('node:fs');
const path = require('node:path');
const EXACT_SRC = 'https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg';
const EXACT_ALT = 'Three Mile Island control panel showing dense rows of gauges, lights and switches.';
const CATALOG = 'https://commons.wikimedia.org/wiki/File:TMI-2_control_panel.png';
function invariant(condition, message) { if (!condition) throw new Error(message); }
function validate(a) {
  invariant(a && a.schema === 'fv-media-p0-tmi-panel-archival-recovery-v1', 'schema');
  invariant(a.provenance?.frozen_inventory_blob_sha === '49183f66f880f7c4dfd363acca906876877f2e5e', 'source blob');
  invariant(a.provenance?.site_qa_owner_pr === 154 && a.provenance?.media_recovery_owner_pr === 183, 'owner separation');
  const x=a.image; invariant(x?.key === '285:2' && x.post_id===285, 'slot identity');
  invariant(x.post_url === 'https://finalvestige.com/2026/08/19/the-light-said-closed-three-mile-island/', 'article');
  invariant(x.published_source_url === EXACT_SRC && x.published_alt === EXACT_ALT, 'frozen src/alt');
  invariant(x.published_html_width_px === null && x.published_html_height_px === null, 'stored dimensions unknown');
  const o=x.retriever_observation;
  invariant(o.method==='web_text_retriever_wrapper' && o.wrapper_status===500 && o.redirect_to === 'https://blog.ucs.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg', 'redirect wrapper evidence');
  invariant(o.origin_http_status === null && o.visitor_browser_http_status===null && o.is_proof_of_browser_failure===false, 'wrapper not a browser status');
  for(const k of ['confirmed_broken','current_src','http_status','mime','decoded_width_px','decoded_height_px','transferred_bytes','full_scroll_screenshot']) invariant(x.live_browser?.[k]===null, 'unverified browser field '+k);
  invariant(x.publisher_context?.url === 'https://blog.ucs.org/dlochbaum/nuclear-plant-accidents-three-mile-island/' && x.publisher_context.figure_number === 4 && x.publisher_context.credit==='Nuclear Regulatory Commission' && x.publisher_context.original_embedded_link_exact_published_source===true, 'publisher provenance');
  const c=x.recovery_candidate;
  invariant(c?.catalog_url===CATALOG && c.catalog_title==='TMI-2 control panel.png', 'candidate identity');
  invariant(c.catalog_original_width_px===604 && c.catalog_original_height_px===590 && c.catalog_original_mime==='image/png', 'catalog dimensions');
  invariant(c.catalog_source_publication.includes('page 97') && c.catalog_current_version_retouched===true, 'primary source and retouch');
  invariant(c.catalog_licensing_statement.includes('Public domain') && c.catalog_licensing_statement.includes('review'), 'rights caveat');
  invariant(c.candidate_photo_subject_match==='CONTROL_PANEL_WITH_MAINTENANCE_TAGS', 'panel subject');
  invariant(c.binary_identical_to_published_jpeg===null && c.same_exact_crop_to_published_jpeg===null && c.source_master_sha256===null, 'photo/binary comparison unproven');
  invariant(c.rights_republication_status==='HOLD_FINAL_ITEM_AND_RETOUCH_REVIEW', 'rights hold');
  invariant(c.conditional_max_output_width_px===604 && c.conditional_max_output_height_px===590 && c.requested_960px_upscale_allowed===false && c.do_not_crop_explanatory_header===true, 'native geometry and caption');
  invariant(c.proposed_editorial_alt_only?.includes('maintenance tags') && c.proposed_credit_only?.includes('1979'), 'editorial hold text');
  for(const key of ['rights_approved','visually_compared_originals','wp_media_upload_approved','wp_post_edit_approved','rehost_approved','visitor_failure_verified']) invariant(c.release?.[key]===false, 'unsafe release '+key);
  const gate=a.acceptance;
  for(const k of ['actual_guest_chrome_required','exact_image_identity_comparison_required','item_level_reuse_review_required','no_upscale','source_and_alt_rollback_required','cold_before_after_transfer_measurement_required']) invariant(gate?.[k]===true, 'missing gate '+k);
  invariant(gate.max_width_px===960 && gate.automatic_post_rewrite===false && gate.production_changes_made===0 && gate.binary_downloads_made===0, 'no write/download');
  const s=a.sitewide_baseline;
  invariant(s.previous_broken_claim===42 && s.previous_broken_claim_browser_verified===false && s.previous_wire_reduction_claim_percent===76 && s.previous_wire_reduction_measured===false, 'unproven claims');
  invariant(s.frozen_published_posts===61 && s.frozen_inline_images===355 && s.newer_published_posts_snapshot===66 && s.newer_inline_images_snapshot===361, 'census baselines');
  invariant(s.over_1point5MiB_wp_originals===13 && s.over_1point5MiB_wp_original_storage_bytes===43522829 && s.production_repairs_made===0, 'oversize/origin bytes');
  return {ok:true, slot:x.key, source:x.published_source_url, catalog:c.catalog_url, candidate_native_dimensions:[604,590], status:'GUEST_BROWSER_PENDING_RIGHTS_HOLD'};
}
if (require.main===module) {
  const input=process.argv[2] || path.join(__dirname,'p0_tmi_panel_source_recovery_20261105.json');
  try { console.log(JSON.stringify(validate(JSON.parse(fs.readFileSync(input,'utf8'))),null,2)); }
  catch(e){console.error('INVALID: '+e.message);process.exitCode=1;}
}
module.exports={validate};
