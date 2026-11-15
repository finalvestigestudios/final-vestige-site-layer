'use strict';
/** Frozen Gutenberg image-source audit. Offline; never requests or mirrors media. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

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
const EXPECTED_PART_BLOBS = Object.freeze(["948bc1b65b42799aa40cfdb810ddf6ffd80886b6","48e1ebf07207e948ba5802e714eb39659d2e1c1d","49183f66f880f7c4dfd363acca906876877f2e5e","6df3251e5a67a971d87a516a1ba4a0cc32f51f96","9b16b828342a9ac338f3e65610fd3d8d508355e9","0f3dfe398a76838049cebba7cb773d5c5a0c8c69","21095161e633aba093b74c0ead9936c9f6186d00","5659ec243c188928be3f89c0f96354b660608ca2"]);
function gitBlobSha(data) {
  const bytes=Buffer.from(data,'utf8');
  return crypto.createHash('sha1').update(Buffer.from('blob '+bytes.length+'\0')).update(bytes).digest('hex');
}
function loadPinnedParts(dir) {
  return EXPECTED_PART_BLOBS.map((expected,i)=>{
    const raw=fs.readFileSync(path.join(dir,String(i+1).padStart(2,'0')+'.json'),'utf8');
    if(gitBlobSha(raw)!==expected) throw Error('Frozen source part blob SHA mismatch: '+(i+1));
    return JSON.parse(raw);
  });
}

function assertCompleteCoverage(batches) {
  const postIds = new Set(), keys = new Set();
  for (let i=0;i<batches.length;i++) {
    const p=batches[i];
    if (!p || p.batch!==i+1 || !Array.isArray(p.posts) || !Array.isArray(p.images) || p.post_count!==p.posts.length || p.image_count!==p.images.length) throw Error('Frozen batch structure mismatch');
    const meta=new Map(), slots=new Map();
    for (const z of p.posts) {
      if (!Number.isSafeInteger(z.id) || z.id<=0 || !Number.isSafeInteger(z.images) || z.images<0 || typeof z.url!=='string' || typeof z.title!=='string' || postIds.has(z.id)) throw Error('Duplicate or malformed frozen post');
      postIds.add(z.id); meta.set(z.id,z); slots.set(z.id,new Set());
    }
    for (const x of p.images) {
      const z=meta.get(x.post_id);
      if (!z || !Number.isSafeInteger(x.slot) || x.slot<0 || x.slot>=z.images || x.key!==`${x.post_id}:${x.slot}` || keys.has(x.key)) throw Error('Duplicate, orphan, or out-of-range frozen image slot');
      if (x.post_url!==z.url || x.post_title!==z.title) throw Error('Frozen image differs from parent post metadata');
      keys.add(x.key);slots.get(z.id).add(x.slot);
    }
    for (const z of p.posts) {
      if (slots.get(z.id).size!==z.images) throw Error('Frozen post has missing or duplicate slots');
      for (let n=0;n<z.images;n++) if (!slots.get(z.id).has(n)) throw Error('Non-contiguous frozen post slots');
    }
  }
  return {posts:postIds.size,slots:keys.size};
}

function reconcile(parts) {
  if (!Array.isArray(parts) || parts.length !== 8) throw Error('Require the eight frozen inventory parts');
  const rows = parts.flatMap((p, i) => {
    if (p.batch !== i + 1 || !Array.isArray(p.images) || p.images.length !== p.image_count)
      throw Error('Frozen image batch metadata mismatch: ' + (i + 1));
    return p.images;
  });
  assertCompleteCoverage(parts);
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
    const parts = loadPinnedParts(dir);
    console.log(JSON.stringify(reconcile(parts),null,2));
  } catch(e) { console.error('FROZEN_SOURCE_RECONCILIATION_HOLD: '+e.message); process.exitCode=2; }
}
module.exports = {classifyStoredUrl,reconcile,assertCompleteCoverage,gitBlobSha,loadPinnedParts,EXPECTED_PART_BLOBS};
