'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_west_loch_370_20261107.cjs');
const base=JSON.parse(fs.readFileSync(path.join(__dirname,'west_loch_370_sources_20261107.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(base));
test('unmodified eight-source archival ledger is safe',()=>assert.deepEqual(validate(base),{pass:true,errors:[]}));
const faults=[
 ['fake HTTP 404',x=>x.images[0].guest_http_status=404],['fake origin 200',x=>x.images[1].origin_http_status=200],
 ['fake transfer',x=>x.images[0].guest_encoded_bytes=123],['fake decode',x=>x.images[1].guest_decode_pixels=600],
 ['fake broken',x=>x.images[2].visitor_broken=true],['rights cleared',x=>x.images[2].archive_rights='CLEARED'],
 ['cache enabled',x=>x.images[0].copy_or_cache_authorized=true],['WP upload enabled',x=>x.images[5].wp_upload_authorized=true],
 ['binary identity false claim',x=>x.images[0].identical_published_binary=true],
 ['width exceeds 960',x=>x.images[3].conditional_preview_960.width=1280],
 ['stretch or crop',x=>x.images[0].conditional_preview_960.height=960],
 ['catalog scan conflict ignored',x=>x.images[1].conditional_preview_960={width:960,height:768}],
 ['catalog scan conflict erased',x=>x.images[1].scan_conflict=false],
 ['certainty fabricated',x=>x.images[4].historical_identity='Definitely USS LST-480'],
 ['wrong SC image',x=>x.images[2].historical_identity='LST-480 only'],
 ['2024 chronology dropped',x=>x.images[7].historical_identity='Historic 1944 grave marker'],
 ['42 broken asserted',x=>x.unsupported_claims.reported_42_broken='VERIFIED'],
 ['76 reduction asserted',x=>x.unsupported_claims.target_76_percent_savings='MEASURED'],
 ['storage assumed transfer',x=>x.baseline.oversized_visitor_bytes=43522829],
 ['61 changed to 66',x=>x.baseline.oct30_posts=66],
 ['WP writes',x=>x.actions.wordpress_write=true],['cached binaries',x=>x.actions.cache=true],
 ['post changed',x=>x.post.id=371],['image removed',x=>x.images.pop()],
 ['duplicate source',x=>x.images[2].source_url=x.images[0].source_url],
 ['fake source dimensions',x=>x.images[5].width_attr='960'],
 ['wrong origin',x=>x.images[2].origin_class='external']
];
for(const [label,mut] of faults)test('reject '+label,()=>{const x=clone();mut(x);assert.equal(validate(x).pass,false,label)});
