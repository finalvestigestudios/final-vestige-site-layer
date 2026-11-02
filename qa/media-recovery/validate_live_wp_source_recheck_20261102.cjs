'use strict';
/**
 * Fail-closed source provenance checker for the Nov 2 WP edit-context census.
 * Stored WordPress src attributes are not visitor-browser HTTP evidence.
 * No network, CMS writes, media copying or mutation.
 */
function originClass(src) {
  if (typeof src !== 'string') return 'NON_HTTP_OR_INVALID';
  const match = /^https?:\/\/([^\/?#]+)(?:\/([^?#]*))?/i.exec(src);
  if (!match) return 'NON_HTTP_OR_INVALID';
  const host = match[1].toLowerCase().split(':')[0];
  if (host === 'finalvestige.com' || host === 'www.finalvestige.com') return 'FIRST_PARTY';
  if (/^i[0-9]\.wp\.com$/.test(host)) {
    const origin = (match[2] || '').split('/')[0].toLowerCase();
    return origin === 'finalvestige.com' || origin === 'www.finalvestige.com'
      ? 'FIRST_PARTY_JETPACK' : 'THIRD_PARTY_JETPACK';
  }
  return 'THIRD_PARTY';
}
function validateLiveCensus(summary, liveParts, frozenParts) {
  const issues = [];
  const err = (condition, message) => { if (!condition) issues.push(message); };
  err(summary && summary.schema_version === 1, 'summary_schema');
  err(Array.isArray(liveParts) && liveParts.length === 8, 'live_part_count');
  err(Array.isArray(frozenParts) && frozenParts.length === 8, 'frozen_part_count');
  if (!summary || !Array.isArray(liveParts) || liveParts.length !== 8 || !Array.isArray(frozenParts) || frozenParts.length !== 8) return issues;
  const frozen = new Map();
  const oldPosts = new Map();
  for (const part of frozenParts) {
    for (const img of part.images || []) {
      if (frozen.has(img.key)) issues.push('frozen_duplicate:' + img.key);
      frozen.set(img.key, img);
    }
    for (const post of part.posts || []) oldPosts.set(post.id, post);
  }
  const known = new Map();
  const counts = {FIRST_PARTY:0,FIRST_PARTY_JETPACK:0,THIRD_PARTY:0,THIRD_PARTY_JETPACK:0};
  const proxyThird = [], proxyFirst = [];
  let posts = 0;
  const postIds = new Set();
  for (let i = 0; i < liveParts.length; i++) {
    const part = liveParts[i];
    err(part.schema_version === 1 && part.part === i + 1, 'part_number:' + i);
    err(part.frozen_git_blob_sha === summary.old_snapshot?.[i]?.git_blob_sha, 'old_sha_reference:' + i);
    err(summary.new_wp_snapshots?.[i]?.image_count === part.counts?.inline_img_tags, 'part_image_count:' + i);
    err(part.rights_cleared_for_rehosting === false && part.wordpress_writes_authorized === false, 'part_rights_and_cms_hold:' + i);
    err(part.network_source_statuses_verified === false && part.measured_weight_reduction_pct === null, 'part_network_weight_hold:' + i);
    err(part.claimed_42_broken_images_confirmed === false, 'part_42_unverified:' + i);
    const imagesInPart = (part.posts || []).reduce((sum, p) => sum + (p.slots || []).length, 0);
    err(imagesInPart === part.counts?.inline_img_tags, 'part_slot_tally:' + i);
    err((part.posts || []).length === part.counts?.published_posts, 'part_post_tally:' + i);
    for (const p of part.posts || []) {
      posts++;
      if (postIds.has(p.id)) issues.push('duplicate_post:' + p.id);
      postIds.add(p.id);
      const old = oldPosts.get(p.id);
      err(!!old && old.modified === p.modified && old.url === p.url, 'post_source_drift:' + p.id);
      err(p.status === 'publish', 'post_not_published:' + p.id);
      err(p.stored_inline_count === (p.slots || []).length, 'post_slot_count:' + p.id);
      for (let j = 0; j < (p.slots || []).length; j++) {
        const s = p.slots[j], key = p.id + ':' + j, previous = frozen.get(key);
        err(s.key === key && !known.has(key), 'duplicate_or_wrong_key:' + key);
        known.set(key, s);
        err(!!previous && previous.source_url === s.source_url && previous.alt === s.alt, 'image_source_drift:' + key);
        err(s.matches_20261030_snapshot === true, 'source_match_assertion:' + key);
        const computed = originClass(s.source_url);
        err(computed === s.origin_class && Object.hasOwn(counts, computed), 'image_origin_class:' + key);
        if (Object.hasOwn(counts, computed)) counts[computed]++;
        if (computed === 'THIRD_PARTY_JETPACK') proxyThird.push(key);
        if (computed === 'FIRST_PARTY_JETPACK') proxyFirst.push(key);
        err(s.guest_browser_http_status === null && s.guest_browser_decoded === null && s.visitor_transfer_bytes === null, 'fabricated_guest_network:' + key);
      }
    }
  }
  const a = summary.aggregate || {};
  err(posts === 61 && oldPosts.size === 61, 'site_posts_not_61');
  err(known.size === 355 && frozen.size === 355, 'site_images_not_355');
  err(a.published_posts === posts && a.stored_image_slots === known.size && a.unique_image_keys === known.size, 'aggregate_total_mismatch');
  for (const [kind, prop] of [['FIRST_PARTY','first_party_direct'],['FIRST_PARTY_JETPACK','first_party_jetpack'],['THIRD_PARTY','third_party_direct'],['THIRD_PARTY_JETPACK','third_party_via_jetpack']]) err(a[prop] === counts[kind], 'aggregate_class:' + kind);
  err(a.external_origin_total === counts.THIRD_PARTY + counts.THIRD_PARTY_JETPACK, 'external_origin_aggregate');
  err(counts.THIRD_PARTY === 286 && counts.THIRD_PARTY_JETPACK === 2 && counts.FIRST_PARTY === 60 && counts.FIRST_PARTY_JETPACK === 7, 'expected_origin_census');
  err(proxyThird.sort().join(',') === ['285:1','291:0'].join(','), 'third_party_proxy_identity');
  err(proxyFirst.sort().join(',') === ['299:0','299:1','299:2','299:3','299:4','299:5','299:7'].join(','), 'first_party_proxy_identity');
  err(a.reported_42_broken_guest_verified === false && a.claimed_76_percent_wire_weight_saved_measured === false && a.production_media_repairs === 0, 'fabricated_failure_savings_or_repairs');
  err(summary.interpretation?.publish_permission === false, 'unapproved_publication');
  err((summary.priority_source_identity || []).length === 5, 'priority_queue_count');
  for (const q of summary.priority_source_identity || []) {
    const actual = known.get(q.image_key);
    err(!!actual && actual.source_url === q.stored_image_url && actual.alt === q.alt, 'priority_image_identity:' + q.image_key);
    err(q.visitor_browser_http_status === null && q.original_source_http_status === null && q.transfer_bytes === null && q.decoded_width_px === null, 'priority_fabricated_http:' + q.image_key);
    err(q.rights_to_republish === 'HOLD' && q.cache_to_wordpress === 'HOLD' && q.derivative_max_width_px === 960 && q.no_upscale === true, 'priority_rights_geometry:' + q.image_key);
  }
  return issues;
}
module.exports = {originClass, validateLiveCensus};
