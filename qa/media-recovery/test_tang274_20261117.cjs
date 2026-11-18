'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {verify,sha,PIN}=require('./validate_tang274_20261117.cjs');
const dir=__dirname, sourcePath=path.join(dir,'live_66_view_slice_5_20261117.json'),ledgerPath=path.join(dir,'tang274_navy_seven_20261117_2330pt.json');
const raw=fs.readFileSync(sourcePath,'utf8'),src=JSON.parse(raw),base=JSON.parse(fs.readFileSync(ledgerPath,'utf8'));
const clone=()=>JSON.parse(JSON.stringify(base));
test('source SHA pinned',()=>assert.equal(sha(raw),PIN));
test('seven-slot baseline',()=>assert.equal(verify(base,src,raw).slots,7));
test('new NH 45641 candidate is caption-match-only and held',()=>{
 const c=base.slots[3];
 assert.equal(c.official_candidate.accession,'NH 45641');
 assert.equal(c.official_candidate.match_level,'caption_subject_match_only');
 assert.equal(c.official_candidate.identical_raster_verified,false);
 assert.equal(c.geometry.provisional_960w_height_px,1079);
 assert.equal(c.rights.rehost_approved,false);
 assert.equal(verify(base,src,raw).official_candidates,7);
});
const invalid=[
 ['absent browser evidence object',a=>delete a.slots[0].guest_chromium],
 ['missing guest decode key',a=>delete a.slots[1].guest_chromium.decoded],
 ['false origin 404 from retriever 502',a=>{a.slots[1].public_retriever.result='RETRIEVER_HTTP_ERROR';a.slots[1].public_retriever.reported_status=404;}],
 ['wrong Navy accession',a=>a.slots[0].official_candidate.accession='NH 00000'],
 ['invented visitor HTTP',a=>a.slots[6].guest_chromium.http_status=404],
 ['invented wire bytes',a=>a.slots[0].guest_chromium.transferred_bytes=9],
 ['false 42 guest failures',a=>a.scope.reported_broken_42_guest_confirmed=42],
 ['false 76% saving',a=>a.scope.claimed_76_percent_wire_reduction_measured=true],
 ['false transfer total',a=>a.scope.visitor_wire_bytes=950],
 ['rights released without clearance',a=>a.slots[0].rights.rehost_approved=true],
 ['rights cleared without verification',a=>a.slots[0].rights.item_specific_rights_confirmed=true],
 ['unauthorized Momsen substitute',a=>a.slots[3].official_candidate={accession:'x',catalog_url:'https://www.history.navy.mil/x',match_level:'subject_match_only'}],
 ['invented Momsen exact-pixel identity',a=>a.slots[3].official_candidate.identical_raster_verified=true],
 ['invented Navy catalog HTTP status',a=>a.slots[3].official_candidate.actual_navy_record_http_status=200],
 ['wrong catalog master width',a=>a.slots[3].geometry.catalog_reported_master_width_px=1280],
 ['fabricated 960px derived height',a=>a.slots[3].geometry.provisional_960w_height_px=500],
 ['false Momsen publisher rights clearance',a=>a.slots[3].rights.publisher_original_rights_still_unverified=false],
 ['altered exact origin',a=>a.slots[6].source_origin_url='https://fake.test/missing.jpg'],
 ['fabricated successful HTTP',a=>a.slots[0].public_retriever.reported_status=200],
 ['overwidth derivative',a=>a.slots[2].geometry.max_width_px=1280],
 ['lost slot',a=>a.slots.pop()],
 ['duplicate slot',a=>a.slots[1].slot='274:0'],
 ['unofficial catalog',a=>a.slots[2].official_candidate.catalog_url='https://other.test/x'],
 ['production change allowed',a=>a.source_policy.no_wordpress_writes=false]
];
for(const [name,change] of invalid)test(name,()=>{const a=clone();change(a);assert.throws(()=>verify(a,src,raw));});
