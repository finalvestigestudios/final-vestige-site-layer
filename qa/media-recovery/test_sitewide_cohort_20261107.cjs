'use strict';
const assert=require('node:assert/strict');
const {test}=require('node:test');
const {validateManifest,loadManifest}=require('./validate_sitewide_cohort_20261107.cjs');
const original=loadManifest();
const clone=()=>JSON.parse(JSON.stringify(original));
function rejects(name,change,reason){
 test(name,()=>{const m=clone();change(m);const r=validateManifest(m);
  assert.equal(r.ok,false);assert.ok(r.errors.some(s=>s.includes(reason)),JSON.stringify(r.errors));
  assert.equal(r.not_a_76_percent_measurement,true);});
}
test('original 61 versus 66 post frozen manifest is consistent',()=>{
 const r=validateManifest(clone());assert.equal(r.ok,true,JSON.stringify(r.errors));
 assert.deepEqual(r.metrics,{old_posts:61,old_slots:355,expanded_posts:66,expanded_slots:361,
  delta_posts:5,delta_slots:6,zero_inline_image_post_id:1922});
 assert.equal(r.not_guest_browser_verified,true);
 assert.equal(r.not_a_76_percent_measurement,true);
 assert.equal(r.wordpress_write_authorized,false);
});
test('original list includes exact high-priority external image URLs',()=>{
 const m=clone(), p=m.rows.find(x=>x.id===287),q=m.rows.find(x=>x.id===285);
 assert.equal(p.slots[5].source_url,'https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg');
 assert.ok(q.slots[5].source_url.includes('images.saymedia-content.com'));
});
rejects('cannot misstate legacy slot count',m=>m.legacy.expected_slots=356,'legacy_header');
rejects('cannot misstate expanded slot count',m=>m.expanded.expected_slots=360,'expanded_header');
rejects('cannot double-count a published post',m=>m.rows[1].id=m.rows[0].id,'duplicate_or_invalid_post');
rejects('cannot fabricate a sixth new post',m=>m.expanded.post_ids[64]=2222,'expanded_post_not_covered');
rejects('cannot replace frozen image URL with non-HTTP source',m=>m.rows[0].slots[0].source_url='javascript:alert(1)','slot_identity_or_source');
rejects('cannot shift historical slot indices',m=>m.rows.find(x=>x.id===285).slots[5].key='285:4','slot_identity_or_source');
rejects('cannot invent an image for zero-image Change Blindness post',m=>m.rows.find(x=>x.id===1922).slots.push({key:'1922:0',source_url:'https://example.com/x.jpg'}),'new_post_slots');
rejects('cannot drop one historical image and still pass total',m=>m.rows.find(x=>x.id===287).slots.pop(),'slot_totals');
rejects('cannot lose snapshot origin provenance',m=>m.provenance[2].git_blob_sha='invalid','source_blob_2');
rejects('cannot reclassify mixed-date old post as fresh read',m=>m.rows.find(x=>x.id===285).capture_date='2026-11-07','source_date_285');
rejects('cannot treat historical/expanded cohorts as interchangeable',m=>m.data_cohorts_not_interchangeable=false,'cohorts_not_distinct');
rejects('cannot authorize production publication in audit',m=>m.rights_and_post_edits_authorized=true,'unauthorized_publication');
rejects('cannot declare guest capture unnecessary',m=>m.requires_guest_chrome_and_raw_cdp_before_after=false,'browser_evidence_claim');
