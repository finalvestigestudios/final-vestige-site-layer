'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const original=require('./live_p1_five_png_caption_weight_20261113.json');
const {validateAudit}=require('./validate_live_p1_five_png_20261113.cjs');
const clone=()=>JSON.parse(JSON.stringify(original));
function expectHeld(name,mutate,reason){
  test(name,()=>{const doc=clone();mutate(doc);const result=validateAudit(doc);
    assert.equal(result.status,'HOLD');assert.equal(result.production_write_allowed,false);
    assert.equal(result.visitor_savings_verified,false);
    if(reason)assert.ok(result.errors.some(x=>x.includes(reason)),JSON.stringify(result.errors));
  });
}
test('verified snapshot is sound but explicitly not release-approved',()=>{
  const r=validateAudit(clone());
  assert.deepEqual(r.errors,[]);assert.equal(r.status,'AUDIT_VALIDATED_HOLD_NO_RELEASE');
  assert.equal(r.production_write_allowed,false);assert.equal(r.visitor_savings_verified,false);
});
test('all five source URLs direct, original and dated worklist bytes agree',()=>{
  const d=clone();assert.equal(d.rows.length,5);
  assert.equal(d.rows.reduce((s,r)=>s+r.stored_original_bytes,0),13267538);
  for(const r of d.rows){assert.equal(r.media_source_url,r.published_image_src);
    assert.equal(r.media_source_url,r.archived_20261108_source_url);
    assert.equal(r.wp_generated_subsize_count,0);
    assert.match(r.published_caption,/^AI-assisted historical reconstruction/);
    assert.ok(!/AI-assisted/i.test(r.published_alt));
    assert.equal(r.guest_browser_image_http_status,null);
    assert.equal(r.guest_browser_transferred_bytes,null);
  }
});
expectHeld('missing source image',d=>d.rows.pop(),'five-rows-required');
expectHeld('duplicate source even with five rows',d=>d.rows[1]=d.rows[0],'duplicate');
expectHeld('extra source',d=>d.rows.push(d.rows[0]),'five-rows-required');
expectHeld('unapproved third-party URL substitution',d=>d.rows[0].media_source_url='https://archive.example/moved.png','exact-original-url');
expectHeld('synchronized URL substitution still rejected',d=>{d.rows[0].media_source_url=d.rows[0].published_image_src=d.rows[0].archived_20261108_source_url='https://finalvestige.com/wp-content/uploads/2026/08/fake.png'},'exact-original-url');
expectHeld('post/media mismatch',d=>d.rows[0].post_id=999,'post-or-media-custody');
expectHeld('stale image class',d=>d.rows[0].post_img_class='wp-image-40','post-media-id-binding');
expectHeld('silently edited original stored byte count',d=>d.rows[2].stored_original_bytes-=200,'stored-size-custody');
expectHeld('false WordPress subsize admission',d=>d.rows[0].wp_generated_subsize_count=1,'png-native-subsize-custody');
expectHeld('false 960px source native width',d=>d.rows[3].native_width=960,'png-native-subsize-custody');
expectHeld('disclosure removed from public caption',d=>d.rows[4].published_caption='Cistern after the disaster','published-caption-disclosure-lost');
expectHeld('image ALT snapshot changed without refreshing source',d=>d.rows[0].published_alt+=' AI-assisted','image-alt-snapshot-mismatch');
expectHeld('media ALT changed from original art attribution',d=>d.rows[1].media_library_alt='A boat','media-alt-custody');
expectHeld('copyright erroneously precleared',d=>d.rows[1].source_rights_cleared=true,'unverified-creator-rights');
expectHeld('upscaled derivative',d=>d.rows[2].proposed_derivative_max_width=1920,'conditional-960-geometry');
expectHeld('claimed guest HTTP 200 without browser collector',d=>d.rows[2].guest_browser_image_http_status=200,'unmeasured-network-or-derivative-claimed');
expectHeld('claimed visitor bytes without browser',d=>d.rows[2].guest_browser_transferred_bytes=123456,'unmeasured-network-or-derivative-claimed');
expectHeld('claimed hypothetical 76% wire saving',d=>d.rows[2].actual_wire_savings_bytes=100,'unmeasured-network-or-derivative-claimed');
expectHeld('derivative allegedly already produced',d=>d.rows[3].derivative_produced=true,'unauthorized-release-claim');
expectHeld('production write allegedly authorized',d=>d.safety.production_wp_posts_media_write=true,'production_wp_posts_media_write');
expectHeld('someone claims a competing browser collector',d=>d.safety.qa_intake_ownership='Media Recovery','collector-ownership');
expectHeld('false stored-byte totals',d=>d.counts.stored_original_total_bytes=100,'stored_original_total_bytes');
expectHeld('historical worklist SHA removed',d=>d.sources.historical_worklist_blob='invalid','worklist-blob');
