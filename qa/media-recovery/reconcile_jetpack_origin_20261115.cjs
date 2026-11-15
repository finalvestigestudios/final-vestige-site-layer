'use strict';
/** Frozen Gutenberg image-source audit. Offline; never requests or mirrors media. */
const fs = require('node:fs');
const path = require('node:path');

function classifyStoredUrl(value) {
  if (typeof value !== 'string' || !value.trim()) return 'unverifiable';
  let u;
  try { u = new URL(value); } catch { return 'unverifiable'; }
  if (!['http:', 'https:'].includes(u.protocol) || u.username || u.password) return 'unverifiable';
  const host = u.hostname.toLowerCase().replace(/\.$/, '');
  if (host === 'finalvestige.com' || host === 'www.finalvestige.com') return 'owned_direct';
  if (/^i[012]\.wp\.com$/.test(host)) {
    const origin = (u.pathname.split('/')[1] || '').toLowerCase();
    if (!/^[a-z0-9.-]+$/.test(origin)) return 'unverifiable';
    return origin === 'finalvestige.com' || origin === 'www.finalvestige.com'
      ? 'owned_jetpack_origin' : 'external_jetpack_origin';
  }
  return 'external_direct';
}
function reconcile(parts) {
  if (!Array.isArray(parts) || parts.length !== 8) throw Error('Require the eight frozen inventory parts');
  const rows = parts.flatMap((p, i) => {
    if (p.batch !== i + 1 || !Array.isArray(p.images) || p.images.length !== p.image_count)
      throw Error('Frozen image batch metadata mismatch: ' + (i + 1));
    return p.images;
  });
  const byPost = new Map();
  const byClass = {owned_direct:0, owned_jetpack_origin:0, external_jetpack_origin:0, external_direct:0, unverifiable:0};
  const sourceKindErrors = [];
  for (const x of rows) {
    if (!Number.isSafeInteger(x.post_id) || !Number.isSafeInteger(x.slot) || x.key !== String(x.post_id)+':'+x.slot)
      throw Error('Invalid source/image slot identity');
    const type = classifyStoredUrl(x.source_url);
    byClass[type]++;
    const p = byPost.get(x.post_id) || {post_id:x.post_id, images:0, external:0};
    p.images++;
    if (type.startsWith('external_')) p.external++;
    byPost.set(x.post_id,p);
    const expected = type === 'owned_direct' ? 'first_party' : type === 'owned_jetpack_origin' ? 'jetpack_proxy' : type.startsWith('external_') ? (x.source_kind === 'wikimedia_redirect' ? 'wikimedia_redirect' : 'external') : null;
    if (expected !== x.source_kind) sourceKindErrors.push(x.key);
  }
  if (rows.length !== 355 || byPost.size !== 61 || sourceKindErrors.length || byClass.unverifiable)
    throw Error('Frozen census coverage / independent classification mismatch: ' + sourceKindErrors.join(','));
  const offsite = byClass.external_jetpack_origin + byClass.external_direct;
  const special = rows.filter(x => classifyStoredUrl(x.source_url) === 'external_jetpack_origin');
  if (offsite !== 288 || byClass.owned_direct !== 60 || byClass.owned_jetpack_origin !== 7 ||
      special.length !== 2 || special.map(x=>x.key).sort().join(',') !== '285:1,291:0')
    throw Error('Frozen proxy-origin reconciliation changed; revalidate sources before release');
  return {
    schema:'fv-frozen-proxy-origin-reconciliation-v1', posts:byPost.size, stored_slots:rows.length,
    classification:byClass, external_source_slots:offsite,
    site_qa_154_csv_prior_external_count:286, prior_csv_vs_reconciled_delta:offsite-286,
    mismatches_with_qa_154_csv:[
      {post_id:285, qa154_csv_offsite:5, verified_offsite:byPost.get(285).external, slot:'285:1'},
      {post_id:291, qa154_csv_offsite:5, verified_offsite:byPost.get(291).external, slot:'291:0'}
    ],
    external_proxy_sources:special.map(x=>({key:x.key,stored_url:x.source_url,source_host:x.source_host,source_kind:x.source_kind})),
    browser_http_verified:false, broken_external_image_count_verified:null,
    visitor_transfer_bytes:null, claimed_76_percent_transfer_reduction_verified:false,
    rights_clear_to_cache:false, wordpress_write_authorized:false,
    owner_site_qa_pr:154, remediation_branch:'existing draft PR #183 only'
  };
}
if (require.main === module) {
  try {
    const dir = process.argv[2] || path.join(__dirname, 'parts');
    const parts = Array.from({length:8},(_,i) => JSON.parse(fs.readFileSync(path.join(dir, String(i+1).padStart(2,'0')+'.json'),'utf8')));
    console.log(JSON.stringify(reconcile(parts),null,2));
  } catch(e) { console.error('FROZEN_SOURCE_RECONCILIATION_HOLD: '+e.message); process.exitCode=2; }
}
module.exports = {classifyStoredUrl,reconcile};
