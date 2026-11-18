'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {verify}=require('./okeechobee432_florida_seven_20261117_1730pt_validator.cjs');
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'okeechobee432_florida_seven_20261117_1730pt.json'),'utf8'));
const scenarios=[["baseline",true,""],["fake browser status",false,"a.images[0].guest_image_http_status=404"],["fake origin 500",false,"a.images[0].original_origin_http_status=500"],["fake decode",false,"a.images[0].guest_decode=true"],["fake byte count",false,"a.images[0].guest_wire_bytes=300"],["missing image",false,"a.images.pop()"],["reordered slot",false,"a.images[1].slot_id='432:0'"],["wrong archive ID",false,"a.images[2].archive_id='RC04344'"],["wrong canonical path",false,"a.images[4].original_url='https://www.floridamemory.com/fpc/reference/rc04343.jpg'"],["fake official catalog",false,"a.images[3].official_catalog_url='https://other.com/test'"],["wrong image",false,"a.images[1].catalog_image_url='https://floridamemory.com/fpc/other.jpg'"],["false date",false,"a.images[6].catalog_year=1928"],["lost alt correction",false,"a.images[3].proposed_alt=null"],["2001 alt no date",false,"a.images[6].proposed_alt='Historic burial site'"],["invented dimensions",false,"a.images[2].master_pixel_width=960"],["invented derivative",false,"a.images[0].derived_width=960"],["unauthorized mirroring",false,"a.images[0].rehosting_allowed=true"],["rights override",false,"a.images[1].rights_state='CLEARED'"],["wordpress write",false,"a.production_writes=1"],["wordpress upload",false,"a.authorized_wordpress_upload=true"],["unlicensed download",false,"a.authorized_binary_download=true"],["upscale switch",false,"a.allow_upscale=true"],["fictitious savings",false,"a.claimed_76_percent_savings_verified=true"],["fictitious 42 broken",false,"a.claimed_42_guest_confirmed=true"],["SHA drift",false,"a.source_git_sha='unverified'"],["route provenance",false,"a.images[5].published_jetpack_url='https://images.example.com/test.jpg'"],["not verified status semantics",false,"a.image_source_retriever_result='HTTP 500 confirmed'"]];
for(const [name,expectSuccess,mutation] of scenarios){
 const a=JSON.parse(JSON.stringify(fixture));
 if(mutation)new Function('a',mutation)(a);
 if(expectSuccess)assert.equal(verify(a).status,'REVIEW_ONLY',name);
 else assert.throws(()=>verify(a),undefined,name);
}
console.log('PASS '+scenarios.length+'/'+scenarios.length);
