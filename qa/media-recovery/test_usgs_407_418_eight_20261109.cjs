'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const {validate}=require('./validate_usgs_407_418_eight_20261109.cjs');
const original=JSON.parse(fs.readFileSync(__dirname+'/usgs_407_418_eight_20261109.json','utf8'));
assert.deepEqual(validate(original),[]);
const changes=[
x=>x.rows[0].stored_url+='?switched=1',
x=>x.rows[0].post_id=5,
x=>x.rows[0].retriever.origin_http=200,
x=>x.rows[0].retriever.visitor_http=404,
x=>x.rows[0].visitor.confirmed_broken=true,
x=>x.rows[0].visitor.cold_wire_bytes=500,
x=>x.rows[0].visitor.natural_width=960,
x=>x.rows[0].authority.rights_approved=true,
x=>x.rows[0].authority.exact_image_match=true,
x=>x.rows[0].authority.candidate_catalog_url='https://example.com',
x=>x.rows[0].sizing.native_width=1200,
x=>x.rows[0].sizing.output_width=960,
x=>x.rows[0].sizing.max_width=1500,
x=>x.rows[0].sizing.upscale=true,
x=>x.rows[0].release.download=true,
x=>x.rows[0].release.cache=true,
x=>x.rows[0].release.wordpress=true,
x=>x.rows[0].visual.crop_approved=true,
x=>x.rows[0].retriever.observation='TOOL_INACCESSIBLE',
x=>x.rows[1].slot=x.rows[0].slot,
x=>x.counts.guest_tested=8,
x=>x.performance.measured_reduction_percent=76,
x=>x.site_qa.duplicate_collector=true,
x=>x.rows[6].visual.observed_scene='1959 earthquake eyewitness',
x=>x.rows[7].visual.observed_scene='Scotch Cap',
x=>x.rows[4].visual.observed_scene='Damage from earthquake'
];
for(let i=0;i<changes.length;i++){const changed=structuredClone(original);changes[i](changed);assert.notDeepEqual(validate(changed),[],String(i));}
console.log((changes.length+1)+'/'+(changes.length+1)+' controls + mutation regressions passed');
