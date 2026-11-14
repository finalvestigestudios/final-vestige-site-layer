'use strict';
const assert=require('node:assert/strict');
const {validate}=require('./validate_malbone_621_two_media_preflight_20261114.cjs');
const baseline=require('./malbone_621_two_media_preflight_20261114.json');
assert.deepEqual(validate(baseline),[]);
const edits=[x=>x.cohort.original_stored_bytes++,
x=>x.cohort.reported_42_broken_browser_confirmed=true,
x=>x.cohort.proposed_76_percent_wire_saving_measured=true,
x=>x.policy.wp_write_authorized=true,
x=>x.policy.rehost_or_cache_authorized=true,
x=>x.policy.max_width_px=1024,
x=>x.post.guest_currentSrc_measured=true,
x=>x.items.reverse(),
x=>x.items[0].stored_original_url="https://wrong.example/asset.jpg",
x=>x.items[0].stored_bytes++,
x=>x.items[0].native_px[0]=3000,
x=>x.items[0].wordpress_large.url="https://i0.wp.com/other.example/file.jpg",
x=>x.items[0].wordpress_large.virtual=false,
x=>x.items[0].conditional_960px.height=800,
x=>x.items[0].conditional_960px.approved=true,
x=>x.items[1].conditional_960px.derivative_url="https://invented.example/file.jpg",
x=>x.items[0].visitor_http=200,
x=>x.items[1].visitor_bytes=100000,
x=>x.items[0].rights_approved=true,
x=>x.items[0].release="READY",
x=>x.items[1].provenance.map_readability_hold=false,
x=>x.items[1].provenance.primary_catalog_url="https://wrong.example",
x=>x.items[0].provenance.primary_catalog_url="https://commons.wikimedia.org/File:unverified"];
for(let i=0;i<edits.length;i++){let a=structuredClone(baseline);edits[i](a);assert.ok(validate(a).length,'mutation '+i+' should fail');}
console.log('PASS '+(edits.length+1)+'/'+(edits.length+1)+' Malbone offline assertions');
