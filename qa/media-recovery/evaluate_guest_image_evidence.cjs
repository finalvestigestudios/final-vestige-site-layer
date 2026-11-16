#!/usr/bin/env node
'use strict';
// Offline consumer of Site QA's *existing* guest-Chromium evidence. No fetch/WordPress writes.
const fs = require('node:fs');

const MANIFEST_SCHEMA = 'fv-p0-web-retriever-matrix-v1';
const CAPTURE_SCHEMA = 'fv-siteqa-guest-image-evidence-v1';
const STATUS = Object.freeze({
  UNOBSERVED: 'UNOBSERVED',
  MISSING_CAPTURE: 'MISSING_CAPTURE',
  SOURCE_DRIFT: 'SOURCE_DRIFT_REVIEW',
  RENDERED: 'CAPTURE_REPORTS_RENDERED',
  BROKEN: 'CAPTURE_REPORTS_BROKEN',
  TRANSPORT: 'CAPTURE_REPORTS_TRANSPORT_FAILURE_DECODE_UNKNOWN',
  INCONCLUSIVE: 'INCONCLUSIVE'
});
const isObject = x => x && typeof x === 'object' && !Array.isArray(x);
const isInt = x => Number.isSafeInteger(x);
function requireString(x, label, max = 8192) {
  if (typeof x !== 'string' || !x.trim() || x.length > max) throw new Error(\`Invalid \${label}\`);
  return x;
}
function requireHttpUrl(x,label) {
  requireString(x,label);
  let u;
  try { u = new URL(x); } catch { throw new Error(\`Invalid \${label} URL\`); }
  if (!['https:', 'http:'].includes(u.protocol) || u.username || u.password) throw new Error(\`Invalid \${label} scheme\`);
  return u;
}
function optionalBool(x,label) {
  if (x !== null && x !== undefined && typeof x !== 'boolean') throw new Error(\`Invalid \${label}\`);
  return x ?? null;
}
function optionalNonnegativeInt(x,label) {
  if (x !== null && x !== undefined && (!isInt(x) || x < 0)) throw new Error(\`Invalid \${label}\`);
  return x ?? null;
}
function sourceMatches(current, row) {
  if (current === row.jetpack_view_url || current === row.authored_url) return true;
  // Jetpack may swap between i0/i1/i2/i3 and append safe resize parameters.
  const u = requireHttpUrl(current, 'current_src');
  const expected = requireHttpUrl(row.jetpack_view_url, 'jetpack_view_url');
  const jetpack = /^i[0-3]\.wp\.com$/;
  if (!jetpack.test(u.hostname) || !jetpack.test(expected.hostname) || u.protocol !== 'https:') return false;
  if (decodeURIComponent(u.pathname) !== decodeURIComponent(expected.pathname)) return false;
  for (const [k,v] of expected.searchParams) {
    if (!u.searchParams.has(k) || u.searchParams.get(k) !== v) return false;
  }
  return [...u.searchParams.keys()].every(k => ['ssl','resize','w','h','fit','crop','quality','strip','zoom'].includes(k));
}
function validateManifest(manifest) {
  if (!isObject(manifest) || manifest.schema !== MANIFEST_SCHEMA || !Array.isArray(manifest.rows) || manifest.rows.length !== 6) throw new Error('Expected six-slot pinned P0 matrix');
  const seen = new Set();
  for (const row of manifest.rows) {
    if (!isObject(row) || !/^\d+:\d+$/.test(requireString(row.key,'key',64)) || seen.has(row.key)) throw new Error('Duplicate/invalid P0 key');
    seen.add(row.key);
    requireHttpUrl(row.post_url,'post_url');
    requireHttpUrl(row.authored_url,'authored_url');
    requireHttpUrl(row.jetpack_view_url,'jetpack_view_url');
  }
  return manifest;
}
function validateCapture(capture, manifest) {
  if (capture === undefined || capture === null) return null;
  if (!isObject(capture) || capture.schema !== CAPTURE_SCHEMA || !isObject(capture.environment) || !Array.isArray(capture.slots) || capture.slots.length > 6) throw new Error('Invalid capture schema');
  const env = capture.environment;
  if (env.browser !== 'chromium' || env.session !== 'logged_out' || env.collector !== 'Site QA #154' || env.cache !== 'disabled') throw new Error('Not identified as logged-out, cache-disabled Site QA Chromium');
  const at = requireString(env.captured_at_utc,'capture timestamp',64);
  if (!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z$/.test(at) || !Number.isFinite(Date.parse(at))) throw new Error('Invalid capture timestamp');
  const known = new Set(manifest.rows.map(r => r.key));
  const seen = new Set();
  for (const s of capture.slots) {
    if (!isObject(s) || !known.has(s.key) || seen.has(s.key)) throw new Error('Unknown/duplicate capture slot');
    seen.add(s.key);
    requireHttpUrl(s.post_url, 'post_url');
    requireHttpUrl(s.current_src, 'current_src');
    if (!isObject(s.request)) throw new Error('Missing network request');
    requireHttpUrl(s.request.url,'request url');
    const http = optionalNonnegativeInt(s.request.http_status, 'http_status');
    if (http !== null && (http < 100 || http > 599)) throw new Error('Invalid HTTP status');
    const wire = optionalNonnegativeInt(s.request.wire_bytes, 'wire_bytes');
    const fromCache = optionalBool(s.request.from_cache, 'from_cache');
    if (fromCache !== false && wire !== null) throw new Error('Cached/unknown-cache wire bytes cannot be counted');
    if (s.request.mime_type !== null && s.request.mime_type !== undefined && (typeof s.request.mime_type !== 'string' || s.request.mime_type.length > 128)) throw new Error('Invalid MIME');
    optionalBool(s.complete,'complete');
    optionalBool(s.decode_succeeded,'decode_succeeded');
    optionalNonnegativeInt(s.natural_width,'natural_width');
    optionalNonnegativeInt(s.natural_height,'natural_height');
    if (s.request.network_error !== null && s.request.network_error !== undefined && (typeof s.request.network_error !== 'string' || s.request.network_error.length > 256)) throw new Error('Invalid network error');
  }
  return capture;
}
function evaluate(manifest, providedCapture) {
  validateManifest(manifest);
  const capture = validateCapture(providedCapture,manifest);
  const byKey = new Map((capture?.slots || []).map(x => [x.key,x]));
  let measuredCount = 0, measuredSum = 0;
  const rows = manifest.rows.map(row => {
    const slot = byKey.get(row.key);
    const out = {
      key: row.key, post_url: row.post_url, expected_jetpack_url: row.jetpack_view_url,
      reported_current_src: slot?.current_src ?? null,
      browser_http_status: slot?.request?.http_status ?? null,
      browser_mime_type: slot?.request?.mime_type ?? null,
      browser_wire_bytes: null,
      decoding_observed: slot?.decode_succeeded ?? null,
      delivery: !capture ? STATUS.UNOBSERVED : STATUS.MISSING_CAPTURE,
      source_unchanged: null,
      production_replacement_allowed: false
    };
    if (!slot) return out;
    if (slot.post_url !== row.post_url || slot.current_src !== slot.request.url || !sourceMatches(slot.current_src,row)) {
      out.delivery = STATUS.SOURCE_DRIFT;
      out.source_unchanged = false;
      return out;
    }
    out.source_unchanged = true;
    if (slot.request.from_cache === false && slot.request.wire_bytes !== null && slot.request.wire_bytes !== undefined) {
      out.browser_wire_bytes = slot.request.wire_bytes;
      measuredCount++;
      measuredSum += slot.request.wire_bytes;
      if (!Number.isSafeInteger(measuredSum)) throw new Error('Wire-byte sum overflow');
    }
    const code = slot.request.http_status;
    const failedTransport = (code !== null && code !== undefined && code >= 400) || Boolean(slot.request.network_error);
    const complete = slot.complete === true;
    const natural0 = slot.natural_width === 0 && slot.natural_height === 0;
    const pixelOK = (slot.natural_width ?? 0) > 0 && (slot.natural_height ?? 0) > 0;
    if (complete && natural0 && slot.decode_succeeded === false && failedTransport) out.delivery = STATUS.BROKEN;
    else if (complete && natural0 && slot.decode_succeeded === false && code >= 200 && code < 300) out.delivery = STATUS.BROKEN;
    else if (complete && pixelOK && slot.decode_succeeded === true && code >= 200 && code < 300 && /^image\//i.test(slot.request.mime_type ?? '')) out.delivery = STATUS.RENDERED;
    else if (failedTransport) out.delivery = STATUS.TRANSPORT;
    else out.delivery = STATUS.INCONCLUSIVE;
    return out;
  });
  return {
    schema: 'fv-p0-guest-evidence-evaluation-v1',
    provenance: capture ? 'COLLECTOR_SUPPLIED_UNINDEPENDENTLY_VERIFIED' : 'NO_GUEST_CAPTURE',
    source: MANIFEST_SCHEMA,
    capture_time_utc: capture?.environment.captured_at_utc ?? null,
    summary: {
      expected_slots: 6,
      provided_capture_slots: capture?.slots.length ?? 0,
      reported_broken_slots: rows.filter(x=>x.delivery===STATUS.BROKEN).length,
      reported_rendered_slots: rows.filter(x=>x.delivery===STATUS.RENDERED).length,
      unresolved_slots: rows.filter(x=>![STATUS.BROKEN,STATUS.RENDERED].includes(x.delivery)).length,
      wire_byte_slots: measuredCount,
      observed_partial_wire_bytes: measuredCount ? measuredSum : null,
      complete_six_slot_wire_bytes: measuredCount===6 ? measuredSum : null,
      reported_42_broken_sitewide_verified: false,
      claimed_76_percent_sitewide_wire_savings_verified: false
    },
    rows
  };
}
if (require.main === module) {
  try {
    if (process.argv.length < 3 || process.argv.length > 4) throw new Error('Usage: node evaluate_guest_image_evidence.cjs <p0_reader_matrix.json> [site_qa_guest_capture.json]');
    const manifest = JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
    const capture = process.argv[3] ? JSON.parse(fs.readFileSync(process.argv[3],'utf8')) : null;
    process.stdout.write(JSON.stringify(evaluate(manifest,capture),null,2)+'\n');
  } catch (e) { process.stderr.write(\`HOLD: \${e.message}\n\`); process.exitCode = 1; }
}
module.exports = {evaluate,validateManifest,validateCapture,sourceMatches,STATUS};
