'use strict';
const assert=require('node:assert/strict');
const {test}=require('node:test');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_apollo_434_20261103.cjs');
const raw=JSON.parse(fs.readFileSync(path.join(__dirname,'apollo_434_nasa_sources_20261103.json'),'utf8'));
const frozen=JSON.parse(fs.readFileSync(path.join(__dirname,'parts/01.json'),'utf8'));
const mutate=(cb)=>{const x=JSON.parse(JSON.stringify(raw));cb(x);assert.notDeepEqual(validate(x,frozen),[]);};
test('authentic source/archival six slots PASS',()=>assert.deepEqual(validate(raw,frozen),[]));
for(let i=0;i<6;i++){
 test('reject fabricated successful visitor response slot '+i,()=>mutate(x=>x.images[i].original_url_observation.guest_http_status=200));
 test('reject unsupported 961px derivative slot '+i,()=>mutate(x=>x.images[i].conditional_derivative_px[0]=961));
 test('reject license bypass slot '+i,()=>mutate(x=>x.images[i].rights.reuse_authorized=true));
 test('reject source mismatch slot '+i,()=>mutate(x=>x.images[i].source_url+='?other-file'));
}
test('reject unsourced 42 browser failures',()=>mutate(x=>x.sitewide_context.alleged_broken_42_guest_confirmed=true));
test('reject invented 76% wire savings',()=>mutate(x=>x.sitewide_context.claimed_wire_reduction_76_percent_measured=true));
test('reject 434:3 mockup-caption mismatch erasure',()=>mutate(x=>x.images[3].historical_caption_conflict=null));
test('reject post-publication permission',()=>mutate(x=>x.permissions.wordpress_write=true));
test('reject invented upstream origin 404',()=>mutate(x=>x.images[2].original_url_observation.origin_http_status=404));
test('reject wrong NASA photo ID',()=>mutate(x=>x.images[3].nasa_identifier='KSC-2017-0124-PH_KLS01-0129'));
