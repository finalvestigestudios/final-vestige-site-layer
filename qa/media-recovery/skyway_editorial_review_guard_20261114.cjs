'use strict';
// Read-only Gutenberg image-slot editorial preflight. No HTTP, CMS API or writes.
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const SHA = s => crypto.createHash('sha256').update(s, 'utf8').digest('hex');
const EXPECTED_SOURCE_AUDIT = 'fv-skyway-visual-fidelity-287-v1';
const IMAGE_BLOCK = /<!-- wp:image(?:\s+[^>]*?)? -->([\s\S]*?)<!-- \/wp:image -->/g;
function attr(tag, key) {
  const m = tag.match(new RegExp('(?:^|\\s)' + key + '="([^"]*)"'));
  return m ? m[1] : null;
}
function inspectImageBlocks(html) {
  const out = [];
  for (const match of html.matchAll(IMAGE_BLOCK)) {
    const inner = match[1];
    const tags = [...inner.matchAll(/<img\b[^>]*>/gi)];
    const caps = [...inner.matchAll(/<figcaption\b[^>]*>([\s\S]*?)<\/figcaption>/gi)];
    if (tags.length !== 1 || caps.length !== 1) throw Error('image_block_not_single_img_caption');
    const src = attr(tags[0][0], 'src'), alt = attr(tags[0][0], 'alt');
    if (!src || alt === null) throw Error('image_block_src_alt_missing');
    out.push({slot: `287:${out.length}`, src, alt, caption_html: caps[0][1], block_sha256: SHA(match[0])});
  }
  return out;
}
function validateProposalText(value, field) {
  if (typeof value !== 'string' || value.length < 15 || value.length > 280 || /[<>\x00-\x1f]/.test(value)) {
    throw Error(`unsafe_${field}`);
  }
}
function review(post, audit) {
  if (!post || post.id !== 287 || post.status !== 'publish' || typeof post.content !== 'string' || post.content.length > 200000) throw Error('post_identity_or_content_invalid');
  if (!audit || audit.schema !== EXPECTED_SOURCE_AUDIT || audit.post_id !== 287 || audit.post_modified !== post.modified) throw Error('stale_or_wrong_audit');
  if (!Array.isArray(audit.items) || audit.items.length !== 2) throw Error('expected_two_review_items');
  if (!audit.policy || audit.policy.wordpress_production_writes !== 0 || audit.policy.cache_or_rehost !== false || audit.policy.homepage_design_modified !== false) throw Error('unsafe_audit_policy');
  const blocks = inspectImageBlocks(post.content);
  if (blocks.length !== 6) throw Error('unexpected_gutenberg_image_count');
  const diffs = [], unique = new Set();
  for (const item of audit.items) {
    if (!item || !['287:4', '287:5'].includes(item.slot) || unique.has(item.slot)) throw Error('wrong_or_duplicate_slot');
    unique.add(item.slot);
    const b = blocks[Number(item.slot.split(':')[1])];
    if (b.slot !== item.slot || b.src !== item.published_source_url || b.alt !== item.published_alt || b.caption_html !== item.published_caption_html) throw Error('live_image_block_drift');
    if (item.proposed_image_src_change !== false || item.wordpress_production_write !== false || item.rights_to_copy_or_cache !== false || item.copyright_review_complete !== false || item.same_binary_or_crop_verified !== false || item.actual_guest_http_status !== null || item.guest_wire_bytes !== null || item.editorial_status !== 'REVIEW_ONLY') throw Error('unsupported_source_or_rights_claim');
    validateProposalText(item.proposed_alt, 'proposed_alt');
    // Existing caption may contain inline markup. The suggested caption here must be plain text.
    validateProposalText(item.proposed_caption_html, 'proposed_caption');
    if (item.proposed_alt === b.alt && item.proposed_caption_html === b.caption_html) throw Error('no_actual_editorial_delta');
    diffs.push({slot:item.slot, source_url:b.src, block_sha256:b.block_sha256,
      alt:{before:b.alt, after:item.proposed_alt},
      caption_html:{before:b.caption_html, after:item.proposed_caption_html},
      image_source_changed:false, safe_to_auto_apply:false, editorial_approval_required:true});
  }
  return {
    status:'EDITORIAL_REVIEW_ONLY_NOT_APPLIED', post_id:287, post_modified:post.modified,
    wordpress_content_sha256:SHA(post.content), inspected_image_blocks:blocks.length,
    unchanged_image_slots:blocks.filter(b => !unique.has(b.slot)).map(b=>b.slot),
    source_custody:'EXACT_PUBLISHED_URL_MATCH',
    browser_status:'UNVERIFIED', visitor_network_bytes:null, source_images_downloaded:0,
    generated_image_derivatives:0, wordpress_writes:0, content_mutated:false,
    proposed_diffs:diffs
  };
}
if (require.main === module) {
  try {
    if (process.argv.length !== 4) throw Error('Usage: node skyway_editorial_review_guard_20261114.cjs post_snapshot.json audit.json');
    const read = file => {
      if (fs.statSync(file).size > 300000) throw Error('input_too_large');
      return JSON.parse(fs.readFileSync(file, 'utf8'));
    };
    process.stdout.write(JSON.stringify(review(read(process.argv[2]),read(process.argv[3])),null,2)+'\n');
  } catch (e) { process.stderr.write('REVIEW_HOLD: '+e.message+'\n'); process.exitCode=2; }
}
module.exports={attr,inspectImageBlocks,review};
