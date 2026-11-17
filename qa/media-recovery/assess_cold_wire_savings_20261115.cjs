'use strict';

// Offline consumer of Site QA #154's exported, already-normalized CDP data.
// No browser automation, URLs fetched, WordPress mutations, or media downloads.
const fs = require('node:fs');
const crypto = require('node:crypto');

const SCHEMA = 'fv-media-siteqa154-cold-cdp-image-bytes-v1';
const SOURCE = 'CDP.Network.loadingFinished.encodedDataLength';
const COHORTS = Object.freeze({ 'frozen-61': 61, 'current-66': 66 });
const REJECT = (why) => { throw new Error('HOLD: ' + why); };
const goodInt = (n) => Number.isSafeInteger(n) && n >= 0;
const sha256 = (v) => typeof v === 'string' && /^[0-9a-f]{64}$/.test(v);
const isHttp = (v) => {
  try { const u = new URL(v); return ['http:', 'https:'].includes(u.protocol) && Boolean(u.hostname) && !u.username && !u.password; }
  catch { return false; }
};
const same = (a,b) => JSON.stringify(a) === JSON.stringify(b);

function validateCapture(capture, phase, options = {}) {
  if (!capture || capture.schema !== SCHEMA || capture.phase !== phase) REJECT(phase + ' schema/phase');
  if (!(capture.cohort in COHORTS)) REJECT(phase + ' unknown cohort');
  const expectedCount = COHORTS[capture.cohort];
  if (!capture.protocol || typeof capture.protocol !== 'object') REJECT(phase + ' protocol missing');
  const p = capture.protocol;
  const fields = ['collector', 'user_agent', 'browser_version', 'viewport_width_px', 'viewport_height_px',
    'device_scale_factor', 'network_profile', 'scroll_protocol', 'cache_mode', 'service_worker_mode', 'session_mode'];
  for (const f of fields) if (p[f] === undefined || p[f] === null || p[f] === '') REJECT(phase + ' protocol.' + f);
  if (p.collector !== 'siteqa-154-export' || p.cache_mode !== 'cold-disabled' ||
      p.service_worker_mode !== 'bypassed' || p.session_mode !== 'logged-out' ||
      p.scroll_protocol !== 'full-page-settle-all-lazy-images') REJECT(phase + ' incompatible collection protocol');
  if (!goodInt(p.viewport_width_px) || p.viewport_width_px < 320 ||
      !goodInt(p.viewport_height_px) || p.viewport_height_px < 320 ||
      !Number.isFinite(p.device_scale_factor) || p.device_scale_factor <= 0) REJECT(phase + ' viewport');
  if (!Array.isArray(capture.pages) || capture.pages.length !== (options.expectedCount ?? expectedCount))
    REJECT(phase + ' incomplete cohort/page count');
  if (options.expectedCount !== undefined && options.allowSyntheticTests !== true) REJECT('test-only override disabled');
  const ids = new Set(), urls = new Set();
  for (const page of capture.pages) {
    if (!goodInt(page.post_id) || page.post_id === 0 || ids.has(page.post_id)) REJECT(phase + ' missing/duplicate post');
    ids.add(page.post_id);
    if (!isHttp(page.url) || urls.has(page.url)) REJECT(phase + ' duplicate/invalid page URL');
    urls.add(page.url);
    if (!sha256(page.content_sha256) || !sha256(page.image_slot_manifest_sha256)) REJECT(phase + ' unpinned content/slots');
    if (page.all_lazy_images_requested !== true || page.load_completion_confirmed !== true) REJECT(phase + ' incomplete lazy-image traversal');
    if (!goodInt(page.dom_image_slots) || page.dom_image_slots === 0 ||
        page.decoded_image_slots !== page.dom_image_slots || page.broken_image_slots !== 0) REJECT(phase + ' visual integrity/decode hold');
    if (page.screenshot_review_passed !== true || page.rights_review_passed !== true ||
        typeof page.review_evidence !== 'string' || !page.review_evidence.trim()) REJECT(phase + ' image rights/visual signoff absent');
    if (!Array.isArray(page.requests) || page.requests.length === 0) REJECT(phase + ' no observed image requests');
    const requestIds = new Set();
    for (const r of page.requests) {
      if (typeof r.request_id !== 'string' || !r.request_id.trim() || requestIds.has(r.request_id)) REJECT(phase + ' duplicate/missing CDP request_id');
      requestIds.add(r.request_id);
      if (!isHttp(r.url) || r.resource_type !== 'Image' || r.byte_source !== SOURCE) REJECT(phase + ' unsupported image byte source');
      if (r.http_status !== 200 || r.mime_type?.split(';')[0]?.toLowerCase().startsWith('image/') !== true) REJECT(phase + ' unverified image HTTP/MIME');
      if (!goodInt(r.encoded_data_length) || r.encoded_data_length === 0) REJECT(phase + ' missing or zero actual wire bytes');
      if (r.response_finished !== true || r.redirect_chain_complete !== true ||
          r.from_disk_cache !== false || r.from_memory_cache !== false || r.from_service_worker !== false) REJECT(phase + ' cached/incomplete request');
    }
  }
  return capture;
}

function assess(before, after, options = {}) {
  validateCapture(before, 'before', options);
  validateCapture(after, 'after', options);
  if (before.cohort !== after.cohort || !same(before.protocol, after.protocol)) REJECT('cohorts or test protocols differ');
  const newPages = new Map(after.pages.map(p => [p.post_id, p]));
  let beforeBytes = 0n, afterBytes = 0n, beforeRequests = 0, afterRequests = 0;
  const perPage = [];
  for (const b of before.pages) {
    const a = newPages.get(b.post_id);
    if (!a || b.url !== a.url || b.content_sha256 !== a.content_sha256 ||
        b.image_slot_manifest_sha256 !== a.image_slot_manifest_sha256 ||
        b.dom_image_slots !== a.dom_image_slots) REJECT('changed article/image cohort or missing post ' + b.post_id);
    const bBytes = b.requests.reduce((x,r) => x + BigInt(r.encoded_data_length), 0n);
    const aBytes = a.requests.reduce((x,r) => x + BigInt(r.encoded_data_length), 0n);
    if (bBytes > BigInt(Number.MAX_SAFE_INTEGER) || aBytes > BigInt(Number.MAX_SAFE_INTEGER)) REJECT('page precision overflow');
    beforeBytes += bBytes; afterBytes += aBytes;
    beforeRequests += b.requests.length; afterRequests += a.requests.length;
    perPage.push({ post_id: b.post_id, before_wire_bytes: Number(bBytes), after_wire_bytes: Number(aBytes),
      image_request_count_before: b.requests.length, image_request_count_after: a.requests.length });
  }
  if (beforeBytes > BigInt(Number.MAX_SAFE_INTEGER) || afterBytes > BigInt(Number.MAX_SAFE_INTEGER)) REJECT('aggregate precision overflow');
  const pct = Number(beforeBytes - afterBytes) * 100 / Number(beforeBytes);
  return {
    schema: 'fv-media-measured-wire-reduction-v1', cohort: before.cohort,
    matched_pages: perPage.length, before_image_wire_bytes: Number(beforeBytes),
    after_image_wire_bytes: Number(afterBytes), image_requests_before: beforeRequests,
    image_requests_after: afterRequests, measured_reduction_percent: Math.round(pct * 10000) / 10000,
    meets_76_percent_threshold: pct >= 76,
    aggregation: 'sum of CDP image network encodedDataLength over matched, logged-out, fully-scrolled, cold pages; no original-file sizes or traffic weighting',
    proof_scope: 'Measured only for submitted paired full-cohort captures; not evidence of production deployment or future visitor experience',
    verified_visual_and_rights_signoff: true,
    per_page: perPage
  };
}

if (require.main === module) {
  try {
    if (process.argv.length !== 4) REJECT('usage: node assess_cold_wire_savings_20261115.cjs before.json after.json');
    const before = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
    const after = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
    const result = assess(before, after);
    process.stdout.write(JSON.stringify(result, null, 2) + '\n');
  } catch (err) { process.stderr.write(String(err.message) + '\n'); process.exitCode = 2; }
}
module.exports = { assess, validateCapture, SCHEMA, SOURCE };
