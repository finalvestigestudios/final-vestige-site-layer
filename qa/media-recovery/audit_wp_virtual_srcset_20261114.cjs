'use strict';
// Offline audit of proposed/draft markup against WordPress's advertised image renditions.
// Does not perform HTTP requests and never modifies posts or media.
const fs = require('node:fs');
const path = require('node:path');

function normalizeUrl(input) {
  if (typeof input !== 'string' || !input.trim()) throw new Error('URL missing');
  const u = new URL(input);
  if (!['https:', 'http:'].includes(u.protocol)) throw new Error('Non-HTTP URL');
  if (u.username || u.password) throw new Error('Credential-bearing URL');
  return u.href;
}
function parseSrcset(value) {
  if (typeof value !== 'string' || !value.trim()) throw new Error('srcset missing');
  return value.split(',').map((part) => {
    const m = part.trim().match(/^(\S+)\s+(\d+)w$/);
    if (!m) throw new Error('Invalid srcset descriptor');
    return { url: normalizeUrl(m[1]), width: Number(m[2]) };
  });
}
function localDerivativeCandidate(original, candidate) {
  const orig = new URL(normalizeUrl(original));
  const test = new URL(normalizeUrl(candidate));
  if (orig.origin !== test.origin) return false;
  const i = orig.pathname.lastIndexOf('.');
  if (i < 0) return false;
  const stem = orig.pathname.slice(0, i);
  const ext = orig.pathname.slice(i);
  return test.pathname.startsWith(stem + '-') && test.pathname.endsWith(ext) && /^\d+x\d+$/i.test(test.pathname.slice((stem + '-').length, -ext.length));
}
function audit(input) {
  if (!input || input.schema !== 'fv-draft-virtual-srcset-custody-v1') throw new Error('Unsupported audit schema');
  const a = input.asset, p = input.page;
  if (!a || !p || !Array.isArray(a.virtual_renditions) || !Array.isArray(p.images) || p.images.length > 20) throw new Error('Malformed audit');
  if (p.status !== 'draft' || p.id !== 2429 || a.id !== 2432 || p.images.length !== 1) throw new Error('Unexpected source custody');
  if (a.original_width !== 1280 || a.original_height !== 720 || a.original_bytes !== 2010886) throw new Error('Asset metadata drift');
  const original = normalizeUrl(a.original_url);
  if (!original.startsWith('https://finalvestige.com/wp-content/uploads/')) throw new Error('Unexpected original host');
  const approved = new Map([[original, 1280]]);
  for (const size of a.virtual_renditions) {
    if (!size.virtual || !Number.isInteger(size.width) || size.width < 1 || size.width > 1280) throw new Error('Invalid virtual rendition');
    const url = normalizeUrl(size.url);
    if (!new URL(url).hostname.match(/^i[012]\.wp\.com$/)) throw new Error('Virtual rendition not a documented proxy');
    if (approved.has(url)) throw new Error('Duplicate rendition URL');
    approved.set(url, size.width);
  }
  const img = p.images[0];
  if (img.slot !== '2429:0' || !img.alt || !img.alt.includes('Concept art, not finished merchandise')) throw new Error('Image meaning/disclosure drift');
  if (img.width !== 1280 || img.height !== 720) throw new Error('Image geometry drift');
  const candidates = [{location:'src',url:normalizeUrl(img.src), width:null}, ...parseSrcset(img.srcset).map(x=>({...x,location:'srcset'}))];
  const seen = new Set();
  const entries = candidates.map(x=>{
    const key=x.location+':'+x.url+':'+x.width;
    if(seen.has(key)) throw new Error('Duplicate URL/descriptor');
    seen.add(key);
    const advertisedWidth=approved.get(x.url);
    const advertised=advertisedWidth !== undefined;
    const virtualFilename=localDerivativeCandidate(original,x.url);
    if(x.location==='srcset' && (!Number.isInteger(x.width) || x.width<=0 || x.width>1280)) throw new Error('Bad width descriptor');
    if(advertised && x.width !== null && x.width!==advertisedWidth) throw new Error('Rendition width mismatch');
    return {location:x.location,url:x.url,descriptor_width:x.width,advertised_by_media_api:advertised,virtual_file_path_unverified:virtualFilename&&!advertised,guest_http_status:null,guest_current_src:null,transferred_bytes:null};
  });
  const flagged=entries.filter(x=>x.virtual_file_path_unverified);
  if (input.guest_browser_verified !== false || input.release_authorized !== false || input.wp_write_allowed !== false) throw new Error('Invalid release safety flags');
  if (input.reported_42_broken_guest_verified !== false || input.reported_76_percent_savings_measured !== false) throw new Error('False site-wide evidence claims');
  if (input.third_party_asset_download_allowed !== false || input.homepage_design_changes_allowed !== false || input.subscription_spend_usd !== 0) throw new Error('Disallowed operations');
  const c = input.snapshot_reconciliation;
  if (!c || c.nov_14_oversized_original_storage_bytes !== c.nov_8_matched_published_inline_bytes + c.nov_8_unmatched_published_inline_bytes + c.added_asset_after_old_scan_bytes || c.nov_14_oversized_originals_decimal_over_1500000 !== c.nov_8_matched_published_inline_originals + c.nov_8_unmatched_published_inline_originals + 1 || c.added_asset_after_old_scan_id !== 2432 || c.added_asset_now_attached_to_draft_page !== 2429 || c.no_inference_of_unused_or_deletable_assets !== true) throw new Error('Temporal media inventory mismatch');
  return {verdict:flagged.length?'HOLD_UNVERIFIED_VIRTUAL_FILE_PATH':'HOLD_GUEST_BROWSER_PROOF', flagged_count:flagged.length, inspected_url_count:entries.length, entries, source_claim:'CMS metadata vs draft source, NOT HTTP/404 verification', release_authorized:false};
}
if(require.main===module) {
  try {
    if(process.argv.length!==3) throw new Error('Usage: node audit_wp_virtual_srcset_20261114.cjs input.json');
    const file=path.resolve(process.argv[2]);
    if(fs.statSync(file).size>256*1024) throw new Error('Oversized input');
    console.log(JSON.stringify(audit(JSON.parse(fs.readFileSync(file,'utf8'))),null,2));
  }catch(error){console.error('MEDIA_VIRTUAL_SRCSET_AUDIT_ERROR: '+error.message);process.exitCode=2;}
}
module.exports={audit,normalizeUrl,parseSrcset,localDerivativeCandidate};
