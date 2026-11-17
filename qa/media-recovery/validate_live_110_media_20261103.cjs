'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const AUDIT = 'live_110_media_13_oversize_scotch418_20261103.json';
function validate(a) {
  const s = a.summary, items = a.media_library_index, heavy = a.oversized_items;
  assert.equal(a.schema_version, 1);
  assert.equal(a.audit_date_utc, '2026-11-03');
  assert.equal(a.source_retrieval.media_count, 110);
  assert.deepEqual(a.source_retrieval.checked_post_ids, [34,35,36,37,38,299,621,418]);
  assert.equal(items.length, 110);
  assert.equal(items.reduce((n,x)=>n+x.original_bytes,0),64900772,'library original bytes mismatch');
  assert.equal(s.library_original_storage_bytes,64900772,'not visitor transfer bytes');
  assert.equal(new Set(items.map(x=>x.id)).size, 110);
  assert.equal(new Set(items.map(x=>x.source_url)).size, 110);
  for (const x of items) {
    assert.ok(Number.isSafeInteger(x.id) && x.id > 0, 'invalid CMS media ID');
    assert.ok(/^https:\/\/finalvestige\.com\/wp-content\/uploads\//.test(x.source_url), 'non-CMS original URL');
    assert.ok(Number.isSafeInteger(x.original_bytes) && x.original_bytes > 0, 'missing original byte count');
    assert.ok(Array.isArray(x.original_pixels) && x.original_pixels.length === 2 && x.original_pixels.every(z=>Number.isInteger(z)&&z>0),'missing dimensions');
    assert.ok(Number.isInteger(x.registered_subsizes) && x.registered_subsizes >= 0);
  }
  assert.equal(s.media_library_images,110);
  assert.equal(s.oversize_threshold_bytes_strictly_greater_than,1572864);
  const calculated=items.filter(x=>x.original_bytes>1572864);
  assert.equal(calculated.length,13);
  assert.equal(heavy.length,13);
  assert.deepEqual(heavy.map(x=>x.id).sort((a,b)=>a-b),calculated.map(x=>x.id).sort((a,b)=>a-b));
  const sum=heavy.reduce((n,x)=>n+x.original_bytes,0);
  assert.equal(sum,43522829);
  assert.equal(s.oversized_original_storage_bytes,sum);
  assert.equal(s.oversized_original_count,13);
  assert.equal(s.oversized_without_registered_subsizes,5);
  assert.equal(s.oversized_with_registered_responsive_variants,8);
  assert.equal(s.oversized_without_registered_subsizes_bytes,13267538);
  const index=new Map(items.map(x=>[x.id,x]));
  let noSizes=0,inline=0;
  for(const h of heavy) {
    const x=index.get(h.id);
    assert.ok(x,'missing id');
    assert.equal(h.source_url,x.source_url);
    assert.equal(h.original_bytes,x.original_bytes);
    assert.deepEqual(h.original_pixels,x.original_pixels);
    assert.equal(h.registered_size_keys.length,x.registered_subsizes);
    if(!h.registered_size_keys.length)noSizes++;
    assert.equal(h.upstream_rights_clearance,'HOLD_item_review');
    assert.equal(h.wordpress_write_approved,false);
    assert.equal(h.guest_http_status,null);
    assert.equal(h.guest_current_src,null);
    assert.equal(h.guest_transfer_bytes,null);
    const [w,d]=h.original_pixels,[cw,ch]=h.conditional_no_upscale_px;
    assert.equal(cw,Math.min(960,w),'upscaling/invalid width');
    assert.equal(ch,Math.round(cw*d/w),'wrong aspect ratio');
    assert.ok(ch<=d,'height upscale');
    for(const ref of h.source_matched_in_checked_posts) {
      inline++;
      assert.ok(a.source_retrieval.checked_post_ids.includes(ref.post_id),'unverified post');
      assert.ok(ref.actual_stored_url.startsWith('https://'),'invalid inline URL');
      assert.ok(ref.image_slot>=0 && Number.isInteger(ref.image_slot));
    }
  }
  assert.equal(noSizes,5);
  assert.equal(inline,10);
  assert.equal(s.matched_inline_slots_in_8_checked_posts,10);
  const p=a.scotch_cap_p0_recheck;
  assert.equal(p.post_id,418);
  assert.equal(p.total_inline_images,6);
  assert.equal(p.priority_sources.length,3);
  assert.deepEqual(p.priority_sources.map(x=>x.image_slot),[0,1,2]);
  assert.match(p.priority_sources[1].published_src,/^https:\/\/media\.defense\.gov\/2021\/Mar\/30\/2002610812\//);
  assert.match(p.priority_sources[2].published_src,/^https:\/\/www\.history\.uscg\.mil\/Portals\/6\//);
  for(const z of p.priority_sources) {
    assert.equal(z.post_id,418);
    assert.equal(z.guest_http_status,null);
    assert.equal(z.guest_decode_ok,null);
    assert.equal(z.web_open_403_is_origin_http,false);
    assert.equal(z.replacement_approved,false);
    assert.ok(z.rights_decision && z.rights_decision.length>20);
    if(z.conditional_no_upscale_px)assert.ok(z.conditional_no_upscale_px[0]<=960);
  }
  assert.equal(p.priority_sources[1].web_open_20261103,403);
  assert.equal(p.priority_sources[2].web_open_20261103,403);
  assert.equal(p.priority_sources[1].candidate,p.priority_sources[1].published_src);
  assert.match(p.priority_sources[1].official_catalog,/history\.uscg\.mil/);
  assert.equal(s.guest_http_failures_confirmed,0);
  assert.equal(s.guest_transfer_bytes,null);
  assert.equal(s.claimed_42_broken_verified,false);
  assert.equal(s.claimed_76_percent_savings_verified,false);
  assert.equal(s.production_replacements,0);
  assert.equal(a.guest_wire_method.measured_savings_percent,null);
  assert.ok(a.guest_wire_method.required_before_after.includes('cold cache'));
  assert.deepEqual(a.safety,{third_party_binaries_downloaded:false,wordpress_production_write:false,homepage_visual_work:false,unlicensed_asset_rehosting:false,permission_to_publish:false});
  return {assets:items.length,oversized:heavy.length,oversized_storage_bytes:sum,inline_checked: inline,guest_savings_measured:false};
}
if(require.main===module) {
  const p=process.argv[2]||path.join(__dirname,AUDIT);
  try{console.log(JSON.stringify(validate(JSON.parse(fs.readFileSync(p,'utf8'))))); }
  catch(e){console.error(e.message);process.exitCode=1;}
}
module.exports={validate};
