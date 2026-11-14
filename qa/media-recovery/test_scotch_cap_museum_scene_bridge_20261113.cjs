'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_scotch_cap_museum_scene_bridge_20261113.cjs');
const original=JSON.parse(fs.readFileSync(path.join(__dirname,'scotch_cap_418_2_museum_scene_bridge_20261113.json'),'utf8'));
let tests=0;
function check(description,fn){
 const copy=structuredClone(original);
 fn(copy);
 const result=validate(copy);
 assert.equal(result.ok,false,description+' erroneously accepted'); tests++;
}
assert.equal(validate(original).ok,true,'baseline source-locked record rejected');tests++;
const mutations=[
 ['schema',a=>a.schema='other'],
 ['slot',a=>a.site_post.slot='418:3'],
 ['original url',a=>a.site_post.stored_src='https://example.com/not-original'],
 ['unproven current wp read',a=>a.site_post.current_wp_src_reverified_this_run=true],
 ['wrapper 200',a=>a.source_observation.retriever_status=200],
 ['invented guest 404',a=>a.source_observation.guest_http=404],
 ['invented guest broken',a=>a.source_observation.guest_broken=true],
 ['invented bytes',a=>a.source_observation.guest_encoded_bytes=1000],
 ['unrelated museum asset',a=>a.candidates[0].url='https://example.com/other.jpg'],
 ['fabricated pixel identity',a=>a.candidates[0].pixels_match_original=true],
 ['fabricated rehosting rights',a=>a.candidates[0].right_to_rehost=true],
 ['upscaled 960 substitution',a=>a.candidates[0].published_image_px=[960,741]],
 ['unsubstantiated public-domain statement',a=>a.candidates[0].license='PUBLIC_DOMAIN_CONFIRMED'],
 ['false exact alternative',a=>a.candidates[1].relation='SAME_EXACT_IMAGE'],
 ['false disaster year',a=>a.candidates[3].event_date='1964-01-01'],
 ['remove NOAA-date warning',a=>a.editorial_hazards[0]='No conflict'],
 ['approved release',a=>a.gate.release='APPROVED'],
 ['invented confirmed browser failure',a=>a.gate.confirmed_browser_failure=true],
 ['authorize caching',a=>a.gate.right_to_cache=true],
 ['authorize WP upload',a=>a.gate.wordpress_media_write=true],
 ['allow upscale',a=>a.gate.no_upscale=false],
 ['raise size cap',a=>a.gate.source_max_width_px=1920],
 ['invented 76% result',a=>a.context.measured_visitor_wire_reduction_percent=76],
 ['invented broken count',a=>a.context.reported_broken_unverified=0]
];
for(const [label,fn] of mutations)check(label,fn);
console.log('PASS '+tests+'/'+tests+' frozen source, scene, licensing, geometry and release tests; native Node; no network calls');
