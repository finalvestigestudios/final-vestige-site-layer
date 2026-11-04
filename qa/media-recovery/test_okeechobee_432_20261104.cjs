'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {readFileSync}=require('node:fs');
const {join}=require('node:path');
const {validate}=require('./validate_okeechobee_432_20261104.cjs');
const original=JSON.parse(readFileSync(join(__dirname,'okeechobee_432_canonical_redirect_20261104.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(original));
test('unaltered seven-item ledger must validate',()=>assert.deepEqual(validate(clone()),{ok:true,errors:[]}));
const attacks=[
 ['fabricated origin 200',d=>d.images[0].retrieval.actual_origin_http_status=200],
 ['invented visitor 404',d=>d.images[1].retrieval.guest_browser_http_status=404],
 ['invented browser image failure',d=>d.images[2].retrieval.broken_for_visitors=true],
 ['confuse wrapper 500 with real origin',d=>d.images[3].retrieval.tool_error='origin HTTP 500'],
 ['invented image bytes',d=>d.images[4].retrieval.image_transfer_bytes=58000],
 ['invented rendered pixels',d=>d.images[5].retrieval.natural_width_px=960],
 ['falsely approve license',d=>d.images[6].restoration.rights='PUBLIC_DOMAIN'],
 ['permit local cache',d=>d.images[0].restoration.local_cache_permitted=true],
 ['permit WP upload',d=>d.images[1].restoration.wordpress_upload_permitted=true],
 ['swap two historical photographs',d=>[d.images[1],d.images[2]]=[d.images[2],d.images[1]]],
 ['invent source path',d=>d.images[3].snapshot.original_src+='?new=true'],
 ['wrong archive item',d=>d.images[4].primary_archive.item_id='RC04343'],
 ['change archive catalog link',d=>d.images[5].primary_archive.catalog_url+='?q=1'],
 ['upgrade unknown geometry to 960x540',d=>d.images[5].restoration.target_height_px=540],
 ['invent 42 actual browser failures',d=>d.results.verified_broken_images=42],
 ['invent 76% achieved savings',d=>d.frozen_inventory.claimed_wire_savings_percent_unmeasured=0],
 ['erase modern 2001 photo context',d=>d.images[6].editorial.status='MATCH'],
 ['erase chronology warning',d=>d.images[3].editorial.suggested_alt_for_review=null],
 ['falsify frozen source hash',d=>d.frozen_inventory.blob_sha='abc'],
 ['add an unreviewed eighth image',d=>d.images.push(d.images[0])],
 ['drop one of seven original images',d=>d.images.pop()],
 ['swap actual redirect host',d=>d.images[1].retrieval.observed_redirect_target='https://unrelated.example/photo.jpg']
];
for(const [name,mutate] of attacks) test('deny '+name,()=>{const d=clone();mutate(d);const result=validate(d);assert.equal(result.ok,false,name);assert.ok(result.errors.length>0);});
