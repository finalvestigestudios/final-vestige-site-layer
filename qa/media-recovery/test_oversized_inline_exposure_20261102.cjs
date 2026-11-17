'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate,expectedFor}=require('./validate_oversized_inline_exposure_20261102.cjs');
const read=p=>JSON.parse(fs.readFileSync(path.join(__dirname,p),'utf8'));
const originals=read('oversize_originals_20261030.json');
const parts=Array.from({length:8},(_,i)=>read('parts/0'+(i+1)+'.json'));
const doc=read('oversized_inline_exposure_20261102.json');
const copy=x=>JSON.parse(JSON.stringify(x));
function rejected(mutator){
 const variant=copy(doc);mutator(variant);
 assert.throws(()=>validate(variant,originals,parts));
}
test('complete frozen 61/355/13 source census validates',()=>{
 assert.equal(validate(doc,originals,parts).oversized_originals_count,13);
});
test('independent regeneration equals checked-in ledger rows and summary',()=>{
 const expected=expectedFor(originals,parts);
 assert.deepEqual(expected.rows,doc.rows);
 assert.deepEqual(expected.summary,doc.summary);
});
test('seven inline originals: five PNG without variant and two Malbone with variants',()=>{
 assert.equal(doc.summary.oversized_originals_with_inline_reference,7);
 assert.equal(doc.summary.inline_without_recorded_1024_variant,5);
 assert.equal(doc.summary.inline_with_recorded_1024_variant,2);
 const p0=doc.rows.filter(x=>x.exposure_class==='INLINE_NO_RECORDED_RESPONSIVE_PROXY');
 assert.deepEqual(p0.map(x=>x.inline_references[0].image_key).sort(),['34:0','35:0','36:0','37:0','38:0']);
});
test('six non-inline originals are NOT claimed absent from other surfaces',()=>{
 assert.equal(doc.summary.oversized_originals_not_referenced_inline,6);
 assert.equal(doc.summary.not_referenced_inline_original_bytes,19903227);
 assert.ok(doc.rows.filter(x=>!x.inline_references.length).every(x=>x.exposure_class==='NOT_REFERENCED_INLINE_IN_FROZEN_61_POSTS'));
});
test('five PNG no-upscale plans use 960x540 without license or image-byte claims',()=>{
 const p0=doc.rows.filter(x=>x.exposure_class==='INLINE_NO_RECORDED_RESPONSIVE_PROXY');
 assert.ok(p0.every(x=>x.conditional_960px_derivative.width_px===960&&x.conditional_960px_derivative.height_px===540));
 assert.ok(p0.every(x=>x.rights_cleared_for_new_derivative===false&&x.actual_weight_savings_bytes===null));
});
test('two Malbone JPG no-upscale plans preserve different aspect ratios',()=>{
 const a=doc.rows.find(x=>x.media_id===1258), b=doc.rows.find(x=>x.media_id===1257);
 assert.deepEqual([a.conditional_960px_derivative.height_px,b.conditional_960px_derivative.height_px],[649,720]);
});
test('original storage sums never masquerade as guest transfer savings',()=>{
 assert.equal(doc.summary.oversized_original_bytes,43522829);
 assert.equal(doc.summary.inline_referenced_original_bytes,23619602);
 assert.ok(doc.rows.every(x=>x.guest_encoded_transfer_bytes===null&&x.guest_http_status===null));
});
test('fail closed: HTTP status invented',()=>rejected(d=>d.rows[0].guest_http_status=200));
test('fail closed: invented positive wire-byte amount',()=>rejected(d=>d.rows[3].guest_encoded_transfer_bytes=14000));
test('fail closed: fabricated 76% validated claim',()=>rejected(d=>d.summary.claimed_76_percent_wire_reduction_measured=true));
test('fail closed: fabricated 42 broken claim',()=>rejected(d=>d.summary.reported_42_broken_images_verified=true));
test('fail closed: changed source asset URL',()=>rejected(d=>d.rows[3].original_url='https://invalid.example/other.png'));
test('fail closed: replaced historical ALT',()=>rejected(d=>d.rows[3].inline_references[0].stored_alt='Different historical event'));
test('fail closed: changed stored image slot',()=>rejected(d=>d.rows[1].inline_references[0].image_key='621:7'));
test('fail closed: unauthorized CMS write',()=>rejected(d=>d.rows[3].production_wp_write_authorized=true));
test('fail closed: undocumented derivative license approval',()=>rejected(d=>d.rows[3].rights_cleared_for_new_derivative=true));
test('fail closed: claimed measured reduction',()=>rejected(d=>d.rows[3].actual_weight_savings_bytes=30000));
test('fail closed: derivative above 960px',()=>rejected(d=>d.rows[3].conditional_960px_derivative.width_px=961));
test('fail closed: invented responsive size record',()=>rejected(d=>d.rows[3].recorded_1024_variant_url='https://example.com/imaginary.png'));
test('fail closed: reclassified non-inline item as exposed',()=>rejected(d=>d.rows[0].exposure_class='INLINE_WITH_RECORDED_RESPONSIVE_PROXY'));
test('fail closed: altered total source bytes',()=>rejected(d=>d.summary.inline_referenced_original_bytes=999));
test('fail closed: duplicate Media Library IDs in input',()=>{
 const originalsCopy=copy(originals);originalsCopy[0].media_id=originalsCopy[1].media_id;
 assert.throws(()=>validate(doc,originalsCopy,parts));
});
test('fail closed: changed original bytes in input',()=>{
 const originalsCopy=copy(originals);originalsCopy[3].original_bytes+=1;
 assert.throws(()=>validate(doc,originalsCopy,parts));
});
test('fail closed: source inventory changes its declared image URL',()=>{
 const partsCopy=copy(parts),row=partsCopy.flatMap(p=>p.images).find(x=>x.key==='34:0');
 row.source_url='https://invalid.example/other.png';
 assert.throws(()=>validate(doc,originals,partsCopy));
});
