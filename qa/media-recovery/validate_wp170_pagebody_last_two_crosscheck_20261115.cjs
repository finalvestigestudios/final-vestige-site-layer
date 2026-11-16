'use strict';
const fs = require('node:fs');
const path = require('node:path');
function validateAudit(d) {
  const e = [];
  const check = (ok,msg) => { if (!ok) e.push(msg); };
  check(d && d.schema === 'fv-media-pagebody-custody-v1','schema');
  if (!d || d.schema !== 'fv-media-pagebody-custody-v1') return e;
  check(d.observed_date_pt === '2026-11-15' && d.repository_pr === 183,'identity');
  check(typeof d.observation_method === 'string' && d.observation_method.includes('read only') && d.observation_method.includes('not an atomic database snapshot'),'method caveat');
  const s = d.scanned_pages || {};
  const p = s.pages || [];
  check(s.published_count === 92 && s.draft_count === 78 && s.total === 170 && p.length === 170,'page coverage');
  check(s.all_page_body_exact_reference_matches === 0,'zero exact reference matches claim');
  const expectedNeedles = ['050e21e0-7b54-4f9a-ba0b-7f594657af05','1927-caernarvon-levee-explosion-noaa-archive','data-attachment-id="482"','data-attachment-id="2148"'];
  check(JSON.stringify(s.comparison_needles) === JSON.stringify(expectedNeedles),'exact match needles');
  const keys = new Set();
  let published = 0, draft = 0;
  for (const row of p) {
    check(Number.isInteger(row.id) && row.id > 0 && !keys.has(row.id),'page id collision');
    keys.add(row.id);
    if (row.status === 'publish') published++;
    else if (row.status === 'draft') draft++;
    else e.push('unsupported page status');
    check(typeof row.modified === 'string' && /^2026-\d\d-\d\dT\d\d:\d\d:\d\d$/.test(row.modified),'modified timestamp');
    check(Array.isArray(row.matched_needles) && row.matched_needles.length === 0,'recorded exact reference match');
  }
  check(published === 92 && draft === 78,'status counts');
  for (const id of [2213,234,6,2762,2429,85,9]) check(keys.has(id),'required scan witness '+id);
  const m = d.media || [];
  check(m.length === 2 && m[0]?.id === 482 && m[1]?.id === 2148,'two known oversized assets');
  const expected = [
    [482,'image/png','https://finalvestige.com/wp-content/uploads/2026/08/050e21e0-7b54-4f9a-ba0b-7f594657af05.png',2293016,1672,941],
    [2148,'image/jpeg','https://finalvestige.com/wp-content/uploads/2026/11/1927-caernarvon-levee-explosion-noaa-archive.jpg',2030948,1821,1190]
  ];
  for(let i=0;i<2;i++) {
    const a=m[i] || {}, ex=expected[i], n=a.native || {}, c=a.candidate_max_960 || {};
    check(a.id===ex[0] && a.mime===ex[1] && a.source_url===ex[2] && a.file_bytes===ex[3],'asset metadata '+i);
    check(n.width===ex[4] && n.height===ex[5],'native geometry '+i);
    check(c.width===960 && c.height===Math.round(ex[5]*960/ex[4]) && c.width<=n.width,'no upscale and aspect geometry '+i);
    check(a.candidate_geometry_only===true && a.rights_hold===true && a.wp_upload_authorized===false && a.cache_authorized===false && a.publication_authorized===false,'rights and release holds '+i);
    check(a.prior_post_body_used===false && a.prior_featured_media_used===false && a.page_body_exact_ref_used===false && a.media_parent_post===null,'usage scoping '+i);
    check(a.disposition==='unresolved_in_other_surfaces_not_proven_orphan','no orphan inference '+i);
    check(a.guest_http_status===null && a.guest_encoded_bytes===null,'unknown visitor evidence '+i);
  }
  check(Array.isArray(m[1]?.catalogs) && m[1].catalogs.length===2 && m[1].catalogs[0].url==='https://www.noaa.gov/noaa-collections/photo-library/wea00739jpg' && m[1].catalogs[1].url==='https://commons.wikimedia.org/wiki/File:1927_Mississippi_Flood_Blowing_Levee.jpg','official/crop provenance');
  const c=d.counts || {}, sp=d.safe_change_policy || {};
  check(c.remaining_two_original_stored_bytes===4323964 && c.large_originals_over_1500000_bytes===20 && c.large_original_stored_bytes===64385752,'storage totals');
  check(c.reported_historical_broken_candidates===42 && c.claimed_browser_broken_from_this_audit===0 && c.validated_network_saving_percent===null,'unverified impact guard');
  check(c.frozen_baseline_posts===61 && c.frozen_baseline_inline_images===355 && c.current_post_body_census_posts===66 && c.current_post_body_census_inline_images===361,'cohort guard');
  for(const k of ['no_wordpress_writes','no_media_downloads','no_homepage_changes','no_subscriptions','not_deletion_authorization','not_publication_authorization']) check(sp[k]===true,'safety '+k);
  check(sp.site_qa_cold_browser_owner==='PR #154','collector ownership');
  return e;
}
if (require.main === module) {
 const target=process.argv[2] || path.join(__dirname,'wp170_pagebody_last_two_crosscheck_20261115.json');
 const errors=validateAudit(JSON.parse(fs.readFileSync(target,'utf8')));
 if (errors.length) { console.error(errors.join('\n')); process.exitCode=1; }
 else console.log('PASS: 170 pages, 2 oversized unresolved media, no bogus guest claims');
}
module.exports={validateAudit};
