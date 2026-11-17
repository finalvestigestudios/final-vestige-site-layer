#!/usr/bin/env node
'use strict';
// Offline performance claim gate. Consumes independent Site QA evidence; performs no network or WP writes.
const fs = require('node:fs');
const SCHEMA = 'fv-paired-image-wire-v1';
const isObj = v => !!v && typeof v === 'object' && !Array.isArray(v);
const fail = m => { throw new Error(m); };
const goodInt = (x, min = 0) => Number.isSafeInteger(x) && x >= min;
function url(s) { try { const x = new URL(s); return typeof s === 'string' && x.protocol === 'https:' && !x.username && !x.password; } catch { return false; } }
function parseCensus(csv) {
  const lines = csv.trim().split(/\r?\n/);
  if (lines.shift() !== 'post_id,stored_img_src_count,offsite_src_count') fail('Unrecognized census CSV header');
  const posts = new Map(); let images = 0, offsite = 0;
  for (const l of lines) {
    const m = /^(\d+),(\d+),(\d+)$/.exec(l);
    if (!m) fail('Invalid census row');
    const [id, total, off] = m.slice(1).map(Number);
    if (!goodInt(id, 1) || !goodInt(total) || !goodInt(off) || off > total || posts.has(id)) fail('Invalid census counts');
    posts.set(id, { images: total, external: off }); images += total; offsite += off;
  }
  if (posts.size !== 61 || images !== 355 || offsite !== 286) fail('Historical census is not pinned 61/355/286');
  return { posts, images, offsite };
}
function verifyStorage(inv) {
  if (!isObj(inv) || inv.schema !== 'fv-oversize-runtime-proxy-crosscheck-v1' || !isObj(inv.oversize) || !Array.isArray(inv.oversize.assets) || !isObj(inv.focus)) fail('Invalid WordPress inventory');
  const all = inv.oversize.assets; const ids = new Set(); let total = 0;
  for (const a of all) {
    if (!goodInt(a.media_id, 1) || ids.has(a.media_id) || !url(a.source_url) || !goodInt(a.bytes, 1500001) || !goodInt(a.native_width, 1) || !goodInt(a.native_height, 1)) fail('Invalid oversize asset');
    ids.add(a.media_id); total += a.bytes;
  }
  if (all.length !== 20 || total !== 64385752 || inv.oversize.original_storage_bytes !== total || inv.oversize.count !== 20 || inv.oversize.decimal_byte_threshold !== 1500000) fail('Stored-byte census drift');
  if (!Array.isArray(inv.focus.records) || inv.focus.records.length !== 5) fail('Invalid five-proxy focus');
  const seen = new Set(); let focused = 0;
  for (const r of inv.focus.records) {
    const a = all.find(z => z.media_id === r.media_id);
    if (!a || seen.has(r.media_id) || r.wp_original_url !== a.source_url || r.wp_original_bytes !== a.bytes || !url(r.post_url) || !url(r.rendered_img_src) || !r.rendered_img_src.startsWith('https://i0.wp.com/finalvestige.com/') || r.currentSrc_in_guest_browser !== null || r.guest_get_http_status !== null || r.guest_transfer_bytes !== null) fail('Focus proxy is not a no-capture fact');
    seen.add(r.media_id); focused += a.bytes;
  }
  if (focused !== 13267538 || inv.focus.stored_bytes !== focused || inv.focus.count !== 5) fail('Focus stored-byte drift');
  return { all, focused, total, focus: inv.focus.records };
}
function checkRequest(r) {
  if (!isObj(r) || !url(r.url) || typeof r.request_id !== 'string' || !r.request_id || r.request_id.length > 128 || !goodInt(r.encoded_data_length) || !goodInt(r.http_status, 200) || r.http_status >= 300 || typeof r.mime_type !== 'string' || !/^image\//i.test(r.mime_type) || r.decoded !== true || r.from_cache !== false || r.from_service_worker !== false || r.from_prefetch !== false || r.redirected !== false) fail('Network record not a verified cold, decoded 2xx image request');
  return r.encoded_data_length;
}
function readPage(p, census) {
  if (!isObj(p) || !goodInt(p.post_id, 1) || !census.posts.has(p.post_id) || !url(p.url) || p.scrolled_to_end !== true || p.lazy_images_settled !== true || p.network_capture_complete !== true || !Array.isArray(p.image_requests) || p.image_requests.length === 0 || p.image_requests.length > 500 || p.visual_slots_preserved !== true) fail('Incomplete page network/visual capture');
  let bytes = 0; const ids = new Set();
  for (const r of p.image_requests) { if (ids.has(r.request_id)) fail('Duplicated request ID'); ids.add(r.request_id); bytes += checkRequest(r); }
  if (!Number.isSafeInteger(bytes)) fail('Unsafe byte accumulator');
  return bytes;
}
function compare(census, paired) {
  if (paired === null || paired === undefined) return { status: 'NO_BROWSER_CAPTURE', measured_page_count: 0, before_cdp_received_bytes: null, after_cdp_received_bytes: null, percent_reduction: null, claim_76_percent_verified: false };
  if (!isObj(paired) || paired.schema !== SCHEMA || !isObj(paired.environment) || !Array.isArray(paired.before) || !Array.isArray(paired.after)) fail('Invalid paired capture');
  const e = paired.environment;
  if (e.collector !== 'Site QA #154' || e.browser !== 'Chromium' || e.mode !== 'logged_out' || e.cache !== 'disabled' || e.service_workers_bypassed !== true || !goodInt(e.viewport_width, 1) || !goodInt(e.viewport_height, 1) || !Number.isFinite(e.dpr) || e.dpr <= 0 || typeof e.network_profile !== 'string' || !e.network_profile || typeof e.browser_version !== 'string' || !e.browser_version || typeof e.captured_at_before !== 'string' || typeof e.captured_at_after !== 'string' || !Number.isFinite(Date.parse(e.captured_at_before)) || !Number.isFinite(Date.parse(e.captured_at_after))) fail('Unmatched/invalid cold guest environment');
  if (!paired.before.length || paired.before.length !== paired.after.length || paired.before.length > 61) fail('Unpaired or empty page capture');
  const before = new Map(), after = new Map();
  for (const [arr, target] of [[paired.before, before], [paired.after, after]]) {
    for (const p of arr) { if (target.has(p.post_id)) fail('Duplicate page'); target.set(p.post_id, {url:p.url, bytes:readPage(p,census)}); }
  }
  let a = 0, b = 0;
  for (const [id, x] of before) {
    const y = after.get(id);
    if (!y || y.url !== x.url) fail('Pages not paired to same published URL');
    b += x.bytes; a += y.bytes;
  }
  if (!Number.isSafeInteger(a) || !Number.isSafeInteger(b) || b === 0) fail('Zero or unsafe baseline bytes');
  const complete = before.size === census.posts.size && [...census.posts.keys()].every(id => before.has(id));
  return {
    status: complete ? 'COMPLETE_61_PAGE_SELF_REPORTED_REVIEW_REQUIRED' : 'MEASURED_SUBSET_NOT_SITEWIDE',
    measured_page_count: before.size, expected_page_count: 61,
    before_cdp_received_bytes: b, after_cdp_received_bytes: a,
    percent_reduction: Math.round((1 - a/b) * 10000)/100,
    meets_76_percent_in_measured_sample: a/b <= 0.24,
    claim_76_percent_verified: false,
    caveat: 'CDP encodedDataLength is request-received bytes; sitewide claim needs independent trace and visual parity review; metadata is self-declared'
  };
}
function audit(censusCsv, inventory, paired = null) {
  const census = parseCensus(censusCsv), storage = verifyStorage(inventory);
  const wire = compare(census,paired);
  return {
    schema: 'fv-image-weight-claim-assessment-v1',
    scope: { historical_posts: census.posts.size, historical_inline_references: census.images, historical_source_offsite_refs: census.offsite, reported_broken_42_browser_verified: false },
    storage_only: { over_1500000_byte_originals: storage.all.length, original_bytes: storage.total, five_original_png_bytes: storage.focused, original_png_share_of_oversize_storage_percent: Math.round(storage.focused / storage.total * 10000) / 100 },
    observed_page_proxies: storage.focus.map(r => ({ post_id:r.post_id, media_id:r.media_id, original_url:r.wp_original_url, rendered_proxy_url:r.rendered_img_src, original_stored_bytes:r.wp_original_bytes, guest_http_status:null, guest_cdp_received_bytes:null, rights_review:r.item_rights_review, max_review_px:r.conditional_960_max_no_upscale_px })),
    wire,
    release: 'HOLD_NO_PRODUCTION_WRITES'
  };
}
module.exports = { parseCensus, verifyStorage, compare, audit };
if (require.main === module) {
  const [csvPath, invPath, capturePath] = process.argv.slice(2);
  if (!csvPath || !invPath) { console.error('Usage: node assess_image_wire_reduction.cjs qa/media/cms_image_census_20261030.csv qa/media-recovery/oversize_20_five_png_runtime_20261116_1130pt.json [site_qa_paired_capture.json]'); process.exit(2); }
  try { console.log(JSON.stringify(audit(fs.readFileSync(csvPath,'utf8'), JSON.parse(fs.readFileSync(invPath,'utf8')), capturePath ? JSON.parse(fs.readFileSync(capturePath,'utf8')) : null), null, 2)); }
  catch (e) { console.error('HOLD: ' + e.message); process.exit(1); }
}
