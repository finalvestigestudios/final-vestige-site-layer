'use strict';
// Offline reconciliation of frozen Gutenberg source URLs against an older QA CSV.
// No network requests, asset copies, WordPress writes, or guest/browser claims.
const fs = require('node:fs');
const path = require('node:path');
const PROXY_HOSTS = new Set(['i0.wp.com', 'i1.wp.com', 'i2.wp.com']);
const EXPECTED = Object.freeze({ posts: 61, images: 355, offsite: 288, stored_qa_offsite: 286, other_offsite: 170, wikimedia_redirect: 118, first_party: 60, first_party_proxy: 7 });
const EXPECTED_DIFFS = Object.freeze({ 285: 1, 291: 1 });
const SOURCE_KINDS = new Set(['first_party','jetpack_proxy','external','wikimedia_redirect']);
function classifySource(src) {
  if (typeof src !== 'string' || !src.trim()) throw Error('Missing source URL');
  let u;
  try { u = new URL(src); } catch { throw Error('Malformed source URL'); }
  if (u.protocol !== 'https:' && u.protocol !== 'http:') throw Error('Non-HTTP source URL');
  const transport = u.hostname.toLowerCase().replace(/\.$/, '');
  const isProxy = PROXY_HOSTS.has(transport);
  // WordPress image CDN paths begin with the upstream host, e.g. /finalvestige.com/... .
  // The mere presence of i0.wp.com does NOT establish ownership of the underlying image.
  const segment = isProxy ? u.pathname.split('/')[1] : null;
  const upstream = isProxy && /^[a-z\d.-]+\.[a-z]{2,}$/i.test(segment || '') ? segment.toLowerCase() : transport;
  const firstParty = upstream === 'finalvestige.com' || upstream === 'www.finalvestige.com';
  let kind = firstParty ? (isProxy ? 'jetpack_proxy' : 'first_party') : 'external';
  if (!isProxy && transport === 'commons.wikimedia.org' && u.pathname.startsWith('/wiki/Special:Redirect/file/')) kind = 'wikimedia_redirect';
  return { kind, transport_host: transport, upstream_host: upstream, proxy: isProxy, first_party_origin: firstParty };
}
function parseCsv(csv) {
  if (typeof csv !== 'string') throw Error('Missing QA CSV');
  const lines = csv.trim().split(/\r?\n/);
  if (lines.shift() !== 'post_id,stored_img_src_count,offsite_src_count') throw Error('Unexpected CSV header');
  const map = new Map();
  for (const line of lines) {
    if (!/^\d+,\d+,\d+$/.test(line)) throw Error('Invalid CSV row');
    const [id, images, offsite] = line.split(',').map(Number);
    if (map.has(id) || offsite > images) throw Error('Duplicate/invalid QA row');
    map.set(id, { images, offsite });
  }
  return map;
}
function reconcile(parts, csv, options = {}) {
  if (!Array.isArray(parts) || parts.length < 1) throw Error('Missing image census parts');
  const qa = parseCsv(csv); const entries = new Map(); const posts = new Map();
  const kinds = { first_party: 0, jetpack_proxy: 0, external: 0, wikimedia_redirect: 0 };
  for (const part of parts) {
    if (!part || !Array.isArray(part.images) || !Array.isArray(part.posts) || part.image_count !== part.images.length || part.post_count !== part.posts.length) throw Error('Invalid part totals');
    for (const post of part.posts) {
      if (!Number.isInteger(post.id) || posts.has(post.id) || !Number.isInteger(post.images)) throw Error('Duplicate/invalid post');
      posts.set(post.id, { images: post.images, seen: 0, offsite: 0, proxy_external_slots: [] });
    }
    for (const row of part.images) {
      if (!Number.isInteger(row.post_id) || !Number.isInteger(row.slot) || row.key !== `${row.post_id}:${row.slot}` || entries.has(row.key)) throw Error('Duplicate/invalid image slot');
      if (!SOURCE_KINDS.has(row.source_kind)) throw Error('Unknown source kind');
      const p = posts.get(row.post_id);
      if (!p) throw Error('Image has no article in its part');
      const check = classifySource(row.source_url);
      if (row.source_kind !== check.kind) throw Error(`Stored kind mismatch: ${row.key}`);
      entries.set(row.key, row.source_url); kinds[check.kind]++; p.seen++;
      if (!check.first_party_origin) p.offsite++;
      if (check.proxy && !check.first_party_origin) p.proxy_external_slots.push({ slot: row.key, original_src: row.source_url, upstream_host: check.upstream_host });
    }
  }
  for (const [id, p] of posts) if (p.seen !== p.images) throw Error(`Post ${id} image count mismatch`);
  if (qa.size !== posts.size) throw Error('QA/post cohort mismatch');
  const differences = [];
  for (const [id, p] of posts) {
    const a = qa.get(id);
    if (!a || a.images !== p.images) throw Error(`QA image-count mismatch for ${id}`);
    if (p.offsite !== a.offsite) differences.push({ post_id: id, qa_offsite: a.offsite, corrected_offsite: p.offsite, delta: p.offsite - a.offsite, third_party_jetpack_slots: p.proxy_external_slots });
  }
  differences.sort((a,b)=>a.post_id-b.post_id);
  const offsite = kinds.external + kinds.wikimedia_redirect;
  const qaTotal = [...qa.values()].reduce((sum, x)=>sum+x.offsite,0);
  if (options.enforceFrozen !== false) {
    if (posts.size !== EXPECTED.posts || entries.size !== EXPECTED.images || offsite !== EXPECTED.offsite || qaTotal !== EXPECTED.stored_qa_offsite || kinds.external !== EXPECTED.other_offsite || kinds.wikimedia_redirect !== EXPECTED.wikimedia_redirect || kinds.first_party !== EXPECTED.first_party || kinds.jetpack_proxy !== EXPECTED.first_party_proxy) throw Error('Frozen 61/355 corpus totals changed');
    if (differences.length !== 2 || differences.some(d => EXPECTED_DIFFS[d.post_id] !== d.delta || d.third_party_jetpack_slots.length !== 1)) throw Error('Unexpected frozen census discrepancy');
    const byPost = Object.fromEntries(differences.map(d=>[d.post_id,d.third_party_jetpack_slots[0].slot]));
    if (byPost[285] !== '285:1' || byPost[291] !== '291:0') throw Error('Unexpected external Jetpack origin');
  }
  return { schema: 'fv-source-origin-reconciliation-v1', method: 'OFFLINE_FROZEN_EDITOR_SOURCE_ONLY', guest_http_verified: false, rights_verified: false, visitor_broken_count: null, actual_wire_bytes: null, percentage_savings_measured: null, posts: posts.size, stored_image_slots: entries.size, qa_offsite: qaTotal, corrected_offsite: offsite, on_origin_first_party: kinds.first_party, first_party_jetpack: kinds.jetpack_proxy, generic_external_including_third_party_jetpack: kinds.external, wikimedia_redirect: kinds.wikimedia_redirect, differences };
}
if (require.main === module) {
  try {
    if (process.argv.length !== 4) throw Error('Usage: node reconcile.cjs parts_directory qa_census.csv');
    const dir = process.argv[2]; const names = fs.readdirSync(dir).filter(x=>/^0[1-8]\.json$/.test(x)).sort();
    if (names.length !== 8) throw Error('Expected eight frozen part files 01.json..08.json');
    const parts = names.map(n=>{const full=path.join(dir,n);if (fs.statSync(full).size>400000) throw Error('Oversized input');return JSON.parse(fs.readFileSync(full,'utf8'));});
    const csvPath=process.argv[3];if(fs.statSync(csvPath).size>30000)throw Error('Oversized CSV');
    console.log(JSON.stringify(reconcile(parts,fs.readFileSync(csvPath,'utf8')),null,2));
  } catch (err) { console.error('FV_MEDIA_RECONCILIATION_ERROR: '+err.message); process.exitCode=2; }
}
module.exports={classifySource,parseCsv,reconcile};
