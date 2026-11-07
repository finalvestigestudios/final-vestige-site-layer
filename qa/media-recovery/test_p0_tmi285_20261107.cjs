'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {errorsFor}=require('./validate_p0_tmi285_20261107.cjs');
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'p0_tmi285_primary_alternatives_20261107.json'),'utf8'));
const clone=()=>structuredClone(data);
test('exact machine ledger passes source/rights/no-upscale verification',()=>assert.deepEqual(errorsFor(data),[]));
const badCases=[
 ['invent confirmed visitor failures',x=>x.metrics.visitor_confirmed_broken=42],
 ['claim 76 percent measured',x=>x.metrics.achieved_savings_percent=76],
 ['invent browser bytes',x=>x.metrics.visitor_image_bytes_measured=2400],
 ['falsify web wrapper as origin HTTP',x=>x.metrics.origin_http_observations=1],
 ['production upload',x=>x.slots[0].uploaded_to_wp=true],
 ['media downloads',x=>x.metrics.media_downloads=1],
 ['site QA ownership drift',x=>x.scope.site_qa_owner='our new browser collector'],
 ['wrong source url',x=>x.slots[0].src='https://example.org/guess.jpg'],
 ['swap slot identifiers',x=>x.slots[1].slot='285:2'],
 ['alter post date',x=>x.slots[1].wp_modified='2026-01-01'],
 ['fabricate image status',x=>x.slots[0].browser.http_status=200],
 ['fabricate image decoding',x=>x.slots[1].browser.natural_width=960],
 ['fabricate screenshot proof',x=>x.slots[0].browser.visually_broken=true],
 ['mislabel wrapper result',x=>x.slots[0].retriever.method='guest Chrome'],
 ['inflate tool code to 200',x=>x.slots[1].retriever.tool_reported_status=200],
 ['clear rights prematurely',x=>x.slots[0].candidates[0].rights_review='CLEARED'],
 ['assert image binary match',x=>x.slots[1].candidates[0].binary_match_verified=true],
 ['approve source rehosting',x=>x.slots[1].candidates[1].rehosting_approved=true],
 ['approve editorial image swap',x=>x.slots[1].candidates[1].editorial_swap_approved=true],
 ['upscale 819px Commons source',x=>x.slots[1].candidates[0].proposed_preview_px=[960,720]],
 ['distort 1979 DOE composition',x=>x.slots[1].candidates[1].proposed_preview_px=[960,610]],
 ['upscale 604px report image',x=>x.slots[0].candidates[0].proposed_preview_px=[960,938]],
 ['omit DOE 1979 alternative',x=>x.slots[1].candidates.pop()],
 ['replace Commons provenance with invented source',x=>x.slots[1].candidates[0].catalog_url='https://example.org/file'],
 ['erase source attribution',x=>x.slots[0].candidates[0].proposed_credit=''],
 ['add nonexistent P0 verified slot',x=>x.scope.p0_other_slots_not_modified.push('1:1')],
];
for(const [label,mutate] of badCases) test('reject: '+label,()=>{
 const invalid=clone();mutate(invalid);
 assert.notEqual(errorsFor(invalid).length,0,label);
});
