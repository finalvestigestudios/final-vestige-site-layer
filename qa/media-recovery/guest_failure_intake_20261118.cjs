'use strict';
// Read-only intake of Site QA guest traces. This is NOT a browser collector,
// rights grant, image-downloader, WordPress writer or release approval.
const { sourceMatches } = require('./jetpack_source_identity_20261118.cjs');
const REQUIRED=new Set(['285:5','285:2','287:5','418:1','418:2','407:1','274:6']);
const hex64 = x => typeof x === 'string' && /^[a-f0-9]{64}$/.test(x);
const https = x => { try { const u=new URL(x); return typeof x==='string' && u.protocol==='https:' && !u.username && !u.password && !u.hash; } catch {return false;} };
function fail(x) { throw new Error(x); }
function validateQueue(q) {
  if (!q || q.schema !== 'fv-guest-failure-intake-20261118-v1' || !Array.isArray(q.slots) || q.slots.length !== 7 || !hex40(q.p0_source_blob)) fail('Unpinned or incomplete seven-slot source queue');
  const seen=new Set();
  for (const s of q.slots) {
    if (!/^\d+:\d+$/.test(s.slot||'') || seen.has(s.slot) || !https(s.post_url) || !https(s.authored_src) || !https(s.origin_url) || !s.candidate || !https(s.candidate.catalog_url)) fail('Invalid or duplicate source slot');
    if (!s.authored_src.startsWith('https://i0.wp.com/') && !/^https:\/\/i[1-3]\.wp\.com\//.test(s.authored_src)) fail('Unsupported authored Jetpack source');
    const p=new URL(s.authored_src), match=/^\/([^/]+)(\/.*)$/.exec(p.pathname);
    if (!match || ('https://'+match[1]+match[2])!==s.origin_url || !sourceMatches(s.authored_src,s.origin_url)) fail('Source origin or encoded path mismatch');
    if (s.guest_http!==null || s.guest_decode!==null || s.guest_current_src!==null || s.rehosting_approved!==false || s.wp_write_approved!==false) fail('Queue must not invent guest checks or authorize publishing');
    if (!s.origin_probe || !['HTTP_ERROR','TOOL_ERROR'].includes(s.origin_probe.kind) || (s.origin_probe.kind==='HTTP_ERROR' ? !Number.isInteger(s.origin_probe.status)||s.origin_probe.status<400||s.origin_probe.status>599 : s.origin_probe.status!==null)) fail('Origin retriever result incorrectly categorized');
    if (!s.candidate || !['HOLD','REVIEW'].includes(s.candidate.rights_status) || s.candidate.exact_raster_verified!==false || s.candidate.rehost_approved!==false) fail('Unknown asset rights/identity');
    if (s.candidate.native_width!==null || s.candidate.native_height!==null) {
      if (!Number.isSafeInteger(s.candidate.native_width) || !Number.isSafeInteger(s.candidate.native_height) || s.candidate.native_width<1 || s.candidate.native_height<1) fail('Invalid source geometry');
    }
    if (s.candidate.derivative_width!==null) {
      if (!Number.isSafeInteger(s.candidate.derivative_width) || s.candidate.derivative_width<1 || s.candidate.derivative_width>960 || s.candidate.native_width===null || s.candidate.derivative_width>s.candidate.native_width) fail('Unverified or upscaled derivative');
    }
    seen.add(s.slot);
  }
  if (seen.size!==REQUIRED.size || [...REQUIRED].some(k=>!seen.has(k))) fail('Missing expected P0 source slots');
  return true;
}
const hex40=x=>typeof x==='string'&&/^[a-f0-9]{40}$/.test(x);
function evaluate(q, traces=[]) {
  validateQueue(q);
  if (!Array.isArray(traces)) fail('Trace evidence must be an array');
  const keyed=new Map(q.slots.map(s=>[s.slot,s])), rows=[],seen=new Set();
  for (const t of traces) {
    if (!t || !keyed.has(t.slot) || seen.has(t.slot)) fail('Unknown or duplicate guest slot');
    seen.add(t.slot);
    const source=keyed.get(t.slot);
    if (t.collector!=='Site QA #154' || t.browser!=='Chromium' || t.session!=='logged_out' || t.cache_disabled!==true || t.service_workers_bypassed!==true ||
      t.post_url!==source.post_url || t.authored_src!==source.authored_src || !https(t.current_src) || !sourceMatches(t.current_src,t.authored_src) || !https(t.response_url) ||
      !hex64(t.screenshot_sha256) || typeof t.captured_at!=='string' || !/^2026-/.test(t.captured_at) ||
      !Number.isSafeInteger(t.viewport_width) || t.viewport_width<240 || !Number.isFinite(t.dpr) || t.dpr<=0 || t.dpr>8 ||
      typeof t.request_id!=='string' || !t.request_id) fail('Unverified or mismatched guest trace envelope');
    // The final URL may differ only through a fully recorded redirect chain.
    if (t.response_url!==t.current_src) {
      if (!Array.isArray(t.redirect_chain) || t.redirect_chain.length<1 || t.redirect_chain.length>6) fail('Missing redirect provenance');
      let cursor=t.current_src;const visited=new Set([cursor]);
      for (const hop of t.redirect_chain) {
        if (!hop || hop.from!==cursor || !https(hop.to) || visited.has(hop.to) || ![301,302,303,307,308].includes(hop.status)) fail('Invalid redirect chain');
        cursor=hop.to;visited.add(cursor);
      }
      if (cursor!==t.response_url) fail('Redirect endpoint drift');
    } else if (t.redirect_chain!==undefined && (!Array.isArray(t.redirect_chain) || t.redirect_chain.length!==0)) fail('Spurious redirect chain');
    const code=t.final_http;
    if (code!==null && (!Number.isInteger(code) || code<100 || code>599)) fail('Invalid actual HTTP status');
    if (code===null && (!['ERR_FAILED','ERR_NAME_NOT_RESOLVED','ERR_CONNECTION_TIMED_OUT','ERR_CONNECTION_RESET'].includes(t.network_error) || t.decoded!==false)) fail('Missing documented network failure');
    if (code!==null && t.network_error!==null) fail('HTTP response is not a network error');
    if (code===200 && t.decoded===true && !sourceMatches(t.response_url,t.authored_src)) fail('Unreviewed final image source after redirect');
    if (typeof t.decoded!=='boolean') fail('Missing decode result');
    if (t.decoded && (code!==200 || !/^image\/(jpeg|png|webp|gif|avif)$/i.test(t.mime||'') || !Number.isSafeInteger(t.natural_width) || t.natural_width<1 || !Number.isSafeInteger(t.natural_height) || t.natural_height<1 || !Number.isSafeInteger(t.wire_bytes) || t.wire_bytes<1)) fail('Inconsistent successful decode');
    if (!t.decoded && code!==null && code===200 && !/^image\//i.test(t.mime||'')) {
      // A 200 HTML/error page with a failed decode is a valid broken-image observation.
    }
    rows.push({slot:t.slot,origin_probe_status:source.origin_probe.status,guest_claim: t.decoded ? 'RENDERED_NEEDS_INDEPENDENT_REVIEW':'FAILED_NEEDS_INDEPENDENT_REVIEW', guest_http:code,production_write_allowed:false,rehosting_allowed:false});
  }
  for (const s of q.slots) if (!seen.has(s.slot)) rows.push({slot:s.slot,origin_probe_status:s.origin_probe.status,guest_claim:'UNKNOWN_NEEDS_SITEQA_CAPTURE',guest_http:null,production_write_allowed:false,rehosting_allowed:false});
  rows.sort((a,b)=>a.slot.localeCompare(b.slot,undefined,{numeric:true}));
  return {schema:'fv-guest-failure-triage-report-v1',source_slots:7,traces_received:traces.length,guest_confirmed_broken:null,claimed_42_broken_verified:false,claimed_76_percent_wire_savings_verified:false, production_write_allowed:false,rows,caveat:'Collector metadata, browser statuses and screenshot hashes are not independently authenticated here. Independent QA review is required before marking images broken or repaired.'};
}
module.exports={validateQueue,evaluate};
