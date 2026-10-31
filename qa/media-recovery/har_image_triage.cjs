'use strict';
/**
 * Offline, read-only HAR -> article-image triage. Does not certify visual failure,
 * image identity after a redirect, reuse rights, or compression improvements.
 * Accepts only Chrome's explicit Image resource-type evidence (not Fetch/XHR).
 */
const fs = require('node:fs');
const {sameSource} = require('./browser_probe_core.cjs');
const {scopeHarToArticle} = require('./har_page_scope_core.cjs');

const MAX_HAR_BYTES = 25 * 1024 * 1024;
function safeUrl(v) {
  if (typeof v !== 'string') return null;
  try {
    const u = new URL(v);
    return ['https:', 'http:'].includes(u.protocol) ? u.href : null;
  } catch { return null; }
}
function safeSize(v) { return Number.isSafeInteger(v) && v >= 0 ? v : null; }
function safeStatus(v) { return Number.isInteger(v) && v >= 100 && v <= 599 ? v : null; }
function safeMime(v) { return typeof v === 'string' ? v.split(';')[0].trim().toLowerCase().slice(0, 120) : null; }
function scrubQuerySecrets(raw) {
  const u = new URL(raw);
  let redacted = false;
  for (const key of [...u.searchParams.keys()]) {
    if (/^(?:token|access_?token|api_?key|auth(?:orization)?|signature|sig|session|password|secret|x-amz-|x-goog-)/i.test(key)) {
      u.searchParams.set(key, '[REDACTED]'); redacted = true;
    }
  }
  return {url: u.href, query_secrets_redacted: redacted};
}
function classifyObservation(e) {
  const status = safeStatus(e.response?.status);
  const mime = safeMime(e.response?.content?.mimeType);
  const brokenHttp = status !== null && status >= 400;
  const nonImageSuccess = status !== null && status >= 200 && status < 300 && mime !== null && !mime.startsWith('image/');
  const redirect = status !== null && status >= 300 && status < 400;
  let state = 'HAR_STATUS_OR_MIME_UNVERIFIED';
  if (brokenHttp) state = 'HAR_IMAGE_HTTP_ERROR_OBSERVED';
  else if (nonImageSuccess) state = 'HAR_IMAGE_NONIMAGE_RESPONSE_OBSERVED';
  else if (redirect) state = 'HAR_IMAGE_REDIRECT_INCOMPLETE';
  else if (status !== null && status >= 200 && status < 300 && mime?.startsWith('image/')) state = 'HAR_IMAGE_HTTP_SUCCESS_NOT_VISUAL_PROOF';
  return {http_status: status, response_mime_type: mime, observation: state,
    har_reported_transfer_size_bytes: safeSize(e.response?._transferSize),
    har_reported_body_size_bytes: safeSize(e.response?.bodySize),
    // HAR body/transfer fields are NOT interchangeable with CDP encodedDataLength.
    cdp_encoded_data_length_bytes: null,
    decoded_natural_width_px: null,
    image_visible_to_visitor: null,
    verified_broken_in_browser: null};
}
/** Build all 61/355 stored slots; the six-post P0 queue only provides optional leads. */
function buildSiteQueue(parts, p0 = {rows: []}) {
  if (!Array.isArray(parts) || parts.length !== 8) throw Error('Eight frozen census parts required');
  const posts = parts.flatMap(p => p.posts || []);
  const images = parts.flatMap(p => p.images || []);
  if (posts.length !== 61 || images.length !== 355) throw Error('Frozen census must contain 61 posts and 355 image slots');
  if (!Array.isArray(p0.rows)) throw Error('Invalid P0 overlay');
  const byKey = new Map(p0.rows.map(r => [r.image_key, r]));
  const seen = new Set();
  const rows = images.map(img => {
    if (seen.has(img.key)) throw Error('Duplicate image key in census');
    seen.add(img.key);
    const post = posts.find(p => p.id === img.post_id);
    if (!post || post.url !== img.post_url) throw Error('Broken census article identity '+img.key);
    const p0row = byKey.get(img.key);
    if (p0row && p0row.exact_stored_url !== img.source_url) throw Error('P0 snapshot drift '+img.key);
    return {post_id: img.post_id, image_key: img.key, slot: img.slot,
      article_url: post.url, exact_stored_url: img.source_url,
      source_host: img.source_host,
      official_record_url: p0row?.official_record_url || null,
      official_record_id: p0row?.official_record_id || null};
  });
  return {date: parts[0].date, census_posts: posts.length, census_slots: images.length, rows};
}
function reconcileHar(har, queue, postId) {
  if (!har || !har.log || !Array.isArray(har.log.entries)) throw Error('Valid HAR log.entries required');
  if (!queue || !Array.isArray(queue.rows)) throw Error('Valid priority queue rows required');
  if (!Number.isSafeInteger(postId) || postId <= 0) throw Error('Valid post-id required');
  const rows = queue.rows.filter(x => x.post_id === postId);
  if (!rows.length) throw Error('post-id not in frozen 61-post census');
  const urls = new Set(rows.map(x => x.article_url));
  if (urls.size !== 1 || ![...urls][0].startsWith('https://finalvestige.com/')) throw Error('Invalid post URL in queue');
  for (const row of rows) if (!safeUrl(row.exact_stored_url) || !/^\d+:\d+$/.test(row.image_key)) throw Error('Invalid queue image');

  const observed = [];
  let ignoredWrongResourceType = 0;
  for (const entry of har.log.entries) {
    const raw = safeUrl(entry?.request?.url);
    if (!raw || !rows.some(row => sameSource(row.exact_stored_url, raw))) continue;
    if (entry._resourceType !== 'image' && entry._resourceType !== 'Image') { ignoredWrongResourceType++; continue; }
    if (entry.request?.method !== 'GET') { ignoredWrongResourceType++; continue; }
    const safe = scrubQuerySecrets(raw);
    observed.push({url: raw, public_url: safe.url, query_secrets_redacted: safe.query_secrets_redacted,
      ...classifyObservation(entry)});
  }
  const findings = rows.map(row => {
    const matches = observed.filter(o => sameSource(row.exact_stored_url, o.url));
    const distinctSlotCount = rows.filter(other => matches.some(o => sameSource(other.exact_stored_url, o.url))).length;
    return {image_key: row.image_key, post_id: row.post_id, slot: row.slot,
      exact_stored_url: row.exact_stored_url, source_host: row.source_host,
      official_record_url: row.official_record_url || null,
      official_record_id: row.official_record_id || null,
      max_candidate_width_px: 960, upscale_permitted: false,
      source_reuse_rights_verified: false, wordpress_write_authorized: false,
      har_image_request_count: matches.length,
      har_request_identity_ambiguous_across_slots: distinctSlotCount > 1,
      har_observations: matches.map(({url, ...safe}) => safe),
      result: !matches.length ? 'NO_MATCHING_IMAGE_REQUEST_IN_HAR' :
        distinctSlotCount > 1 ? 'SHARED_IMAGE_URL_SLOT_ATTRIBUTION_UNVERIFIED' :
        matches.length > 1 ? 'MULTIPLE_HAR_IMAGE_REQUESTS_REVIEW' : 'SINGLE_HAR_IMAGE_REQUEST_OBSERVED',
      verified_broken_in_browser: null,
      image_identity_after_redirect_verified: false,
      rights_cleared: false,
      measured_article_wire_savings_percent: null};
  });
  return {schema_version: 1, source: 'locally_supplied_chrome_har_not_live_probe',
    post_id: postId, article_url: [...urls][0], queue_snapshot_date: queue.date || null,
    har_page_identity_verified: false,
    browser_dom_decode_evidence_supplied: false,
    http_statuses_are_from_supplied_har_only: true,
    chrome_har_transfer_size_not_comparable_to_cdp_encoded_bytes: true,
    reported_42_broken_images_verified: false, reported_76_percent_saving_verified: false,
    note: 'HAR Image requests are network clues, not DOM visibility, an unaltered historical source, copyright permission or actual page-weight savings. Capture currentSrc/naturalWidth/screenshot with independent logged-out browser probe.',
    input_har_entries: har.log.entries.length, matching_image_requests: observed.length,
    excluded_same_source_nonimage_requests: ignoredWrongResourceType,
    findings};
}
/**
 * CLI-safe entry: never allow unrelated HAR pages/tabs to inject a photograph's
 * response status into the current article. Consistency of untrusted HAR metadata
 * is not independent proof of a logged-out browser load or DOM image decoding.
 */
function reconcilePageScopedHar(har, queue, postId) {
  const rows = queue?.rows?.filter(x => x.post_id === postId) || [];
  if (!rows.length || new Set(rows.map(x => x.article_url)).size !== 1)
    throw Error('Post ID must have a single article URL in frozen queue');
  const scoped = scopeHarToArticle(har, rows[0].article_url);
  const report = reconcileHar({log:{entries:scoped.scoped_entries}}, queue, postId);
  return {...report,
    input_har_entries: scoped.input_entry_count,
    scoped_har_entries: scoped.scoped_entries.length,
    excluded_unscoped_har_entries: scoped.excluded_unscoped_entries,
    har_declared_article_scope_consistent: scoped.ok,
    har_scope_status: scoped.reason,
    har_page_identity_verified: false,
    note: scoped.ok ?
      report.note + ' Matching page/document/pageref metadata is internally consistent but remains user-supplied, not independently attested.' :
      'HAR page/document attribution unverified. Image statuses deliberately withheld. Export a single-tab Chrome HAR with page and pageref metadata, or run the logged-out CDP probe.'
  };
}
function main(argv) {
  const args = Object.fromEntries(argv.slice(2).filter(x => x.includes('=')).map(x => x.split(/=(.*)/s).slice(0,2)));
  if (!args['--har'] || !args['--post-id'] || !args['--out']) throw Error('Usage: node har_image_triage.cjs --har=logged-out.har --post-id=268 --out=triage.json');
  const bytes = fs.statSync(args['--har']).size;
  if (bytes > MAX_HAR_BYTES) throw Error('HAR exceeds 25 MiB safety limit');
  const har = JSON.parse(fs.readFileSync(args['--har'], 'utf8'));
  const path = require('node:path');
  const parts = Array.from({length: 8}, (_, i) => JSON.parse(fs.readFileSync(path.join(__dirname, 'parts', String(i+1).padStart(2,'0')+'.json'), 'utf8')));
  const p0 = JSON.parse(fs.readFileSync(path.join(__dirname, 'p0_recovery_queue_20261030.json'), 'utf8'));
  const queue = buildSiteQueue(parts, p0);
  const report = reconcilePageScopedHar(har, queue, Number(args['--post-id']));
  fs.writeFileSync(args['--out'], JSON.stringify(report, null, 2) + '\n', {flag: 'wx', mode: 0o600});
  process.stdout.write(JSON.stringify({output: args['--out'], post_id: report.post_id, matching_image_requests: report.matching_image_requests, image_slots: report.findings.length})+'\n');
}
if (require.main === module) { try { main(process.argv); } catch (e) { process.stderr.write(String(e.message)+'\n'); process.exitCode = 1; } }
module.exports = {safeUrl, safeSize, safeStatus, safeMime, scrubQuerySecrets, classifyObservation, buildSiteQueue, reconcileHar, reconcilePageScopedHar};
