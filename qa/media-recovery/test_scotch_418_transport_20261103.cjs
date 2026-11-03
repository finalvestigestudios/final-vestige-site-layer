'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_scotch_418_transport_20261103.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'scotch_418_six_slot_verified_transport_20261103.json'),'utf8'));
test('exact source ledger passes without inventing visitor failures',()=>assert.equal(validate(original),true));
const mutations=[
 ['browser 404',v=>v.images[0].retrieval.browser_http_status=404],
 ['origin 403',v=>v.images[1].retrieval.origin_http_status=403],
 ['guessed decode result',v=>v.images[3].retrieval.browser_decodes=false],
 ['overwide target',v=>v.images[2].candidate.max_width_px=1200],
 ['upscaled museum file',v=>v.images[3].candidate.displayed_derivative.width=960],
 ['WordPress write',v=>v.policies.wp_write_authorized=true],
 ['scraping enabled',v=>v.policies.allow_scrape=true],
 ['upscaling enabled',v=>v.policies.allow_upscale=true],
 ['invented 76 percent',v=>v.performance.claimed_saved_percent=76],
 ['invented 42 broken',v=>v.performance.verified_sitewide_broken_count=42],
 ['invented CDP bytes',v=>v.performance.actual_cold_browser_bytes=99],
 ['claimed production repairs',v=>v.totals.first_party_repairs=1],
 ['claimed visitor failure',v=>v.totals.visitor_broken_verified=2],
 ['duplicate slot',v=>v.images[2].key='418:1'],
 ['truncated ledger',v=>v.images.pop()],
 ['missing rights',v=>v.images[4].candidate.rights=''],
 ['removed release hold',v=>v.images[0].hold=[]]
];
for(const [name,mutation] of mutations){
 test('fail closed: '+name,()=>{
   const copy=structuredClone(original); mutation(copy);
   assert.throws(()=>validate(copy));
 });
}
