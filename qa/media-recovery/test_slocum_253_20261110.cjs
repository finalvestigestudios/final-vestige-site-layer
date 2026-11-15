'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {validate}=require('./validate_slocum_253_20261110.cjs');
const A=require('./slocum_253_seven_loc_20261110.json'),C=require('./coverage_188_exact_pr1703_20261110.json');
const copy=x=>JSON.parse(JSON.stringify(x));
test('reconciled 7-image audit / 288-slot census',()=>assert.equal(validate(A,C),true));
const mutations=[
 ['forged visitor HTTP',a=>a.entries[0].guest_http_status=404],
 ['forged visitor success',a=>a.entries[1].guest_http_status=200],
 ['forged wire bytes',a=>a.entries[2].guest_wire_bytes=10000],
 ['forged 76% saving',a=>a.measured_wire_reduction_76_percent=true],
 ['invented 42 confirmed',a=>a.reported_42_browser_verified=true],
 ['unlicensed source mirroring',a=>a.entries[3].cache_allowed=true],
 ['false rights clearance',a=>a.entries[6].rights_cleared=true],
 ['illegal upscaling',a=>a.entries[1].conditional_960px=[960,615]],
 ['incorrect LOC accession',a=>a.entries[5].primary_archive_item_url='https://www.loc.gov/item/0000000000/'],
 ['changed published source',a=>a.entries[4].original_published_url='https://example.com/photo.jpg']
];
for(const [label,change] of mutations)test('reject '+label,()=>{const a=copy(A);change(a);assert.throws(()=>validate(a,C));});
test('reject false global researched count',()=>{const c=copy(C);c.counts.researched_unique=189;assert.throws(()=>validate(A,c));});
test('reject unauthorized WP upload',()=>{const c=copy(C);c.rows.find(x=>x.slot==='253:3').wordpress_media_upload_authorized=true;assert.throws(()=>validate(A,c));});
test('reject changed external source in census',()=>{const c=copy(C);c.rows.find(x=>x.slot==='253:1').stored_url='https://example.com/other.jpg';assert.throws(()=>validate(A,c));});
