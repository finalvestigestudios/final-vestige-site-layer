'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_palomares_367_20261107.cjs');
const source=JSON.parse(fs.readFileSync(path.join(__dirname,'palomares_367_nine_catalog_20261107.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(source));
assert.equal(validate(source).ok,true,'committed audit passes');
const mutations=[
x=>x.rows[1].actual_guest_http=200,x=>x.rows[3].actual_guest_broken=true,x=>x.rows[4].actual_guest_encoded_bytes=500,
x=>x.rows[2].published_src='https://example.com/b.jpg',x=>x.rows[3].catalog_url=x.rows[5].catalog_url,
x=>x.rows[7].preview_max_960_px=[960,484],x=>x.rows[4].preview_max_960_px=[960,100],
x=>x.rows[1].rights_review='APPROVED',x=>x.rows[5].rehost_authorized=true,x=>x.rows[6].binary_match_verified=true,
x=>x.rows[8].published_alt='',x=>x.rows[1].published_caption=null,x=>x.reported_42_broken='CONFIRMED',
x=>x.claimed_76_percent_transfer_reduction='VERIFIED',x=>x.production_writes=1,x=>x.asset_downloads=1,
x=>x.rows[2].html_dimensions=[960,703],x=>x.rows[8].requested_width_px=100,x=>x.rows[7].kind='first_party',
x=>x.rows[6].slot='367:10',x=>x.summary.requested_larger_than_catalog=0,x=>x.rows.pop(),
x=>x.article.id=268,x=>x.rows[0].rights_label='',x=>x.rows[4].catalog_master_px=[1000,1000]
];
for(const [i,mutate] of mutations.entries()){const copy=clone();mutate(copy);assert.equal(validate(copy).ok,false,'unsafe mutation '+i)}
console.log(JSON.stringify({ok:true,tests:mutations.length+1,negative_rejected:mutations.length}));
