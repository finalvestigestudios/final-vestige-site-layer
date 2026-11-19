'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const data=require('./source_census_delta_61posts_20261116.json');
const {verify}=require('./verify_source_census_delta_20261116.cjs');
const clone=()=>JSON.parse(JSON.stringify(data));
test('canonical 61-post comparison passes without making browser claims',()=>{
 const r=verify(clone());assert.equal(r.posts,61);assert.equal(r.images,355);assert.equal(r.delta,2);assert.equal(r.confirmed_guest_failures,0);
});
const unsafe=[
 ['fabricated failure',x=>x.suspected_origin_classification_slots[0].browser_failure_proven=true],
 ['fabricated HTTP status',x=>x.suspected_origin_classification_slots[0].guest_http_status=404],
 ['fabricated traffic savings',x=>x.measured_76_percent_reduction=76],
 ['invented image dimensions',x=>x.suspected_origin_classification_slots[1].native_dimensions_px=[960,800]],
 ['premature rights release',x=>x.suspected_origin_classification_slots[0].rights_status='CLEARED'],
 ['unlicensed caching',x=>x.suspected_origin_classification_slots[0].cached_to_wordpress=true],
 ['upscale beyond cap',x=>x.suspected_origin_classification_slots[0].max_derivative_width_px=1200],
 ['claimed publishing',x=>x.production_writes=1],
 ['claim 42 confirmed',x=>x.reported_42_broken_confirmed=true],
 ['change attribution host',x=>x.suspected_origin_classification_slots[0].upstream_host='finalvestige.com'],
 ['lose a row',x=>x.rows.pop()],
 ['duplicate post ID',x=>x.rows[0].post_id=x.rows[1].post_id],
 ['change QA count',x=>x.rows[0].qa_offsite++],
 ['change recovery count',x=>x.rows[0].recovery_offsite++],
 ['unrecognized mismatch',x=>x.rows[0].delta=1],
 ['source blob pin removed',x=>x.provenance.media_parts[0].blob=''],
 ['false wire byte evidence',x=>x.oversized_wp_originals.network_transfer_bytes=123],
 ['change culprit URL',x=>x.suspected_origin_classification_slots[0].source_url='https://finalvestige.com/image.jpg'],
];
for(const [name,modify] of unsafe) test('reject '+name,()=>{const x=clone();modify(x);assert.throws(()=>verify(x));});
