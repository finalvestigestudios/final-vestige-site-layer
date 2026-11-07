'use strict';
function validateNavyAudit(d) {
  function need(ok, msg) { if (!ok) throw new Error(msg); }
  const toId = s => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
  need(d && d.schema === 'fv-media-navy-fifteen-v1', 'schema');
  need(d.method.includes('read-only') && !d.method.includes('guest-browser network capture completed'), 'method');
  need(Array.isArray(d.articles) && d.articles.length === 4, 'four live source posts');
  need(Array.isArray(d.records) && d.records.length === 15, 'fifteen images');
  need(d.totals.published_posts_examined === 4 && d.totals.navy_img_references === 15 &&
    d.totals.official_catalog_accession_matches === 10 && d.totals.pending_individual_catalog_identity === 5 &&
    d.totals.catalog_master_pixel_geometry_candidates === 7 && d.totals.conflicting_80_G_202485_high_res_variants === 2, 'frozen totals');
  const expectedPosts = [274,280,288,370], expectedSlots = [3,6,2,4];
  const slots = new Set(), recordsByPost = new Map(expectedPosts.map(n => [n,0]));
  for (let i=0;i<expectedPosts.length;i++) {
    const a=d.articles[i];
    need(a.post_id === expectedPosts[i] && a.navy_image_count === expectedSlots[i], 'post cohort/count');
    need(a.post_url.startsWith('https://finalvestige.com/') &&
      typeof a.last_modified === 'string' && a.last_modified.length >= 10 &&
      Number.isInteger(a.published_image_count) && a.published_image_count >= a.navy_image_count, 'published post metadata');
  }
  let matched=0, pending=0, geometries=0, variantGroups=0;
  for (const r of d.records) {
    need(Number.isInteger(r.post_id) && recordsByPost.has(r.post_id) && new RegExp('^'+r.post_id+':\\d+$').test(r.key) && !slots.has(r.key), 'unique valid slot');
    slots.add(r.key); recordsByPost.set(r.post_id, recordsByPost.get(r.post_id)+1);
    need(r.post_url === d.articles.find(a=>a.post_id===r.post_id).post_url, 'article exact URL');
    need(typeof r.published_src === 'string' && r.published_src.startsWith('https://www.history.navy.mil/') &&
      typeof r.published_alt === 'string' && r.published_alt.trim().length >= 3, 'live source and ALT');
    for (const k of ['http_status','current_src','natural_width','natural_height','encoded_bytes','broken'])
      need(r.guest_browser && r.guest_browser[k] === null, 'no invented guest evidence: '+k);
    need(r.rights && r.rights.status === 'HOLD_ITEM_LEVEL' && r.rights.permission_to_cache === false &&
      r.rights.permission_to_rehost === false && r.rights.attribution_review_required === true &&
      r.word_press_write_authorized === false, 'rights/rehost/production hold');
    const c=r.source_catalog;
    need(c && Array.isArray(c.variant_masters), 'source-catalog structure');
    if (c.accession) {
      matched++;
      need(c.review === 'ITEM_IDENTIFIED_ON_OFFICIAL_NHHC_CATALOG_PAGE_BINARY_MATCH_UNCHECKED' &&
        c.url.startsWith('https://www.history.navy.mil/') &&
        toId(c.url).includes(toId(c.accession)) && toId(r.published_src).includes(toId(c.accession)) &&
        typeof c.credit === 'string' && c.credit.length >= 4 && typeof c.identity_and_chronology_note === 'string', 'matched accession/source and attribution');
      if (c.high_master_pixels) {
        geometries++;
        const m=c.high_master_pixels, p=r.safe_960px_preview_candidate;
        need(Number.isInteger(m.width) && Number.isInteger(m.height) && m.width>0 && m.height>0, 'catalog native dimensions');
        const w=Math.min(960,m.width),h=Math.round(m.height*w/m.width);
        need(p && p.width === w && p.height === h && p.width<=960 &&
          p.width<=m.width && p.height<=m.height &&
          p.derived_from==='official_high_resolution_catalog_entry' &&
          p.not_actual_download_dimensions===true, '960px / no-upscale / aspect gate');
      } else need(r.safe_960px_preview_candidate===null,'no geometry without a known master');
    } else {
      pending++;
      need(c.review==='PHOTO_ITEM_IDENTITY_PENDING' && c.url===null && c.high_master_pixels===null &&
        c.credit===null && r.safe_960px_preview_candidate===null, 'uncatalogued image cannot be cleared');
    }
    if (c.variant_masters.length) {
      variantGroups++;
      need(r.key==='370:1' && c.accession==='80-G-202485' &&
        c.variant_masters.length===2 && c.high_master_pixels===null &&
        r.safe_960px_preview_candidate===null, 'unresolved 80-G-202485 crop lock');
      const [a,b]=c.variant_masters;
      for (const v of [a,b]) need(v.catalog_url.startsWith('https://www.history.navy.mil/') &&
        Number.isInteger(v.width) && Number.isInteger(v.height) && v.width>0 && v.height>0, 'catalog variants');
      const difference=Math.abs(a.width/a.height - b.width/b.height)/(a.width/a.height);
      need(difference>0.01 && difference<0.1, 'conflicting official master aspect ratios must remain distinct');
    }
  }
  need(expectedPosts.every((n,i)=>recordsByPost.get(n)===expectedSlots[i]), 'source cohort coverage');
  need(matched===10 && pending===5 && geometries===7 && variantGroups===1, 'crosswalk completeness');
  const v=d.caveats;
  need(v && v.visitor_confirmed_broken_images===null && v.reported_42_broken_images_unverified===true &&
    v.claimed_76_percent_wire_reduction_unmeasured===true &&
    v.production_images_repaired===0 && v.wordpress_writes===0 &&
    v.third_party_image_downloads===0 && v.third_party_image_caches===0 &&
    v.additional_spend_usd===0, 'no fabricated claims, reads only');
  need(d.preview_policy.includes('never upscale') && d.official_archive_policy==='https://www.history.navy.mil/our-collections/photography.html', 'safe policy');
  return {ok:true, examined_posts:4, image_slots:15, primary_catalog_items:matched, pending_ids:pending,
    provisional_geometry:geometries, conflicting_variant_groups:variantGroups};
}
module.exports = {validateNavyAudit};
if (typeof require !== 'undefined' && require.main === module) {
  const fs = require('node:fs'), path = require('node:path');
  const data = JSON.parse(fs.readFileSync(process.argv[2] || path.join(__dirname,'navy_fifteen_primary_catalog_20261106.json'),'utf8'));
  try { process.stdout.write(JSON.stringify(validateNavyAudit(data))+'\n'); }
  catch(e) { console.error(e.message); process.exitCode=1; }
}
