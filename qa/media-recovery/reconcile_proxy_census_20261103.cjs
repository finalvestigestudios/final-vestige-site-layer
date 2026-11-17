'use strict';
/**
 * Independent, read-only 61-post source-census reconciliation.
 * A Jetpack CDN URL is NOT automatically first-party:
 * i0.wp.com/OTHER-SITE/... proxies an offsite original.
 * This module never accesses network, WordPress or image binaries.
 */
function classifySource(value) {
  if (typeof value !== 'string' || value.length > 4096) throw Error('invalid source URL');
  let u;
  try { u = new URL(value); } catch (_) { throw Error('invalid source URL'); }
  if (!['https:', 'http:'].includes(u.protocol) || u.username || u.password) throw Error('unsafe source URL');
  const delivery = u.hostname.toLowerCase().replace(/^www\./, '');
  let upstream = delivery, proxy = false;
  if (/^i[012]\.wp\.com$/.test(delivery)) {
    proxy = true;
    const segment = u.pathname.split('/')[1] || '';
    try { upstream = decodeURIComponent(segment).toLowerCase().replace(/^www\./, ''); }
    catch (_) { throw Error('malformed Jetpack upstream host'); }
    if (!/^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\.[a-z]{2,}$/.test(upstream) ||
        upstream.includes('..')) throw Error('missing or invalid Jetpack upstream host');
  }
  return { delivery_host: delivery, upstream_host: upstream,
    proxy, offsite_origin: upstream !== 'finalvestige.com' };
}
function parseCsv(csv) {
  if (typeof csv !== 'string') throw Error('CSV required');
  const lines = csv.trim().split(/\r?\n/);
  if (lines.shift() !== 'post_id,stored_img_src_count,offsite_src_count') throw Error('unexpected CSV header');
  const rows = new Map();
  for (const line of lines) {
    const m = /^(\d+),(\d+),(\d+)$/.exec(line);
    if (!m) throw Error('invalid CSV data');
    const id = +m[1], count = +m[2], offsite = +m[3];
    if (!id || rows.has(id) || offsite > count) throw Error('duplicate/invalid CSV row');
    rows.set(id, { count, offsite });
  }
  return rows;
}
function reconcile(parts, siteQaCsv, audit) {
  if (!Array.isArray(parts) || parts.length !== 8 || !audit ||
      !Array.isArray(audit.delta_rows) || audit.delta_rows.length !== 2) throw Error('incomplete inputs');
  const rows = parseCsv(siteQaCsv), posts = new Map(), images = new Map();
  for (const [i, part] of parts.entries()) {
    if (part.batch !== i + 1 || part.post_count !== part.posts.length ||
        part.image_count !== part.images.length) throw Error('invalid frozen part');
    for (const p of part.posts) {
      if (posts.has(p.id)) throw Error('duplicate post');
      posts.set(p.id, p);
    }
    for (const im of part.images) {
      if (images.has(im.key) || im.key !== im.post_id + ':' + im.slot || !posts.has(im.post_id) &&
          !parts.some(p => p.posts.some(q => q.id === im.post_id))) throw Error('invalid image slot');
      if (im.actual_http_status !== null || im.broken_in_browser !== null ||
          im.allowed_to_localize !== false || im.target_max_width_px !== 960) throw Error('invented live result/approval');
      images.set(im.key, im);
    }
  }
  if (posts.size !== 61 || images.size !== 355 || rows.size !== 61) throw Error('census denominator drift');
  const byPost = new Map([...posts.keys()].map(id => [id, { slots: 0, offsite: 0 }]));
  for (const im of images.values()) {
    const c = classifySource(im.source_url), p = byPost.get(im.post_id);
    if (!p) throw Error('orphan image');
    if (c.offsite_origin !== (im.source_kind === 'external' || im.source_kind === 'wikimedia_redirect')) {
      throw Error('source kind inconsistent with effective origin ' + im.key);
    }
    p.slots++; p.offsite += Number(c.offsite_origin);
  }
  const deltas = []; let qaOffsite = 0, freshOffsite = 0, totalSlots = 0;
  for (const [id, p] of posts) {
    const source = byPost.get(id), old = rows.get(id);
    if (!old || source.slots !== p.images || old.count !== source.slots) throw Error('article-level count drift ' + id);
    totalSlots += source.slots; qaOffsite += old.offsite; freshOffsite += source.offsite;
    if (old.offsite !== source.offsite) deltas.push({ post_id:id, old_offsite:old.offsite, new_offsite:source.offsite });
  }
  deltas.sort((a,b)=>a.post_id-b.post_id);
  const expected = audit.delta_rows.map(r => ({post_id:r.post_id,old_offsite:r.siteqa_offsite,new_offsite:r.media_offsite})).sort((a,b)=>a.post_id-b.post_id);
  if (JSON.stringify(deltas) !== JSON.stringify(expected)) throw Error('unexplained delta');
  if (qaOffsite !== 286 || freshOffsite !== 288 || totalSlots !== 355) throw Error('reported totals drift');
  for (const row of audit.delta_rows) {
    const im = images.get(row.image_key);
    if (!im || im.post_id !== row.post_id || im.source_url !== row.exact_current_source_url ||
        !classifySource(im.source_url).proxy || !classifySource(im.source_url).offsite_origin) throw Error('wrong proxy evidence');
    if (row.origin_http_status !== null || row.guest_browser_http_status !== null ||
        row.browser_broken !== null || row.rights_clearance !== 'HOLD' ||
        row.wordpress_upload_authorized !== false || row.wordpress_edit_authorized !== false ||
        row.output_max_width_px !== 960 || row.intrinsic_source_width_px !== null ||
        row.intrinsic_source_height_px !== null || row.pixel_identity_verified !== false) {
      throw Error('unauthorized image/release claim');
    }
  }
  return { status:'SOURCE_COUNTS_RECONCILED_NOT_BROWSER_VERIFIED', posts:61, slots:355,
    siteqa_offsite:qaOffsite, media_offsite:freshOffsite, delta:2, unexplained_post_deltas:0, delta_rows:deltas,
    browser_verified_broken_count:null, visitor_wire_bytes:null, weight_reduction_percent:null, publish_authorized:false };
}
module.exports = { classifySource, parseCsv, reconcile };
