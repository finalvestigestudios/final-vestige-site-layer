'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_usgs_hebgen_original_route_20261115_2222pt.cjs');
const base=JSON.parse(fs.readFileSync(path.join(__dirname,'usgs_hebgen_407_1_official_original_route_20261115_2222pt.json'),'utf8'));
const cloned=()=>JSON.parse(JSON.stringify(base));
test('real immutable observations validate without claiming a live failure',()=>{
 const out=validate(cloned());assert.equal(out.status,'HOLD_GUEST_BROWSER_AND_PIXEL_RIGHTS');
 assert.equal(out.guest_http_status,null);assert.equal(out.upload_approved,false);
});
const mutants=[
 ['fake 404',x=>{x.wordpress.guest_http_status=404;}],
 ['fake 200',x=>{x.route_observations[1].http_status=200;}],
 ['fake guest pass',x=>{x.wordpress.guest_decode_ok=true;}],
 ['fake break',x=>{x.wordpress.confirmed_broken=true;}],
 ['fake wire savings',x=>{x.baselines.measured_wire_reduction_percent=76;}],
 ['wrong WP image',x=>{x.wordpress.view_src='https://example.com/img7535.jpg';}],
 ['wrong official URL',x=>{x.official.original=x.wordpress.authored_origin;}],
 ['wrong catalog',x=>{x.official.catalog='https://example.com';}],
 ['invented exact-match',x=>{x.official.same_pixel_hash_proven=true;}],
 ['fake image width',x=>{x.official.native_width=1000;}],
 ['premature 960 geometry',x=>{x.review_derivative.output_width=960;}],
 ['rehosting allowed',x=>{x.review_derivative.upload_approved=true;}],
 ['cache allowed',x=>{x.review_derivative.cache_approved=true;}],
 ['WordPress write',x=>{x.guardrails.wordpress_writes=1;}],
 ['direct media mirroring',x=>{x.guardrails.image_downloads_or_mirrors=1;}],
 ['wrong method',x=>{x.route_observations[2].method='guest-chromium';}],
 ['wrong status meaning',x=>{x.route_observations[3].outcome='404';}],
 ['missing route',x=>{x.route_observations.pop();}],
 ['fabricated broken tally',x=>{x.baselines.guest_confirmed_broken_count=42;}],
 ['homepage modification',x=>{x.guardrails.homepage_design_changes=1;}]
];
for(const [name,mutation] of mutants)
 test('fail closed: '+name,()=>{const d=cloned();mutation(d);assert.throws(()=>validate(d),/^Error: HOLD:/);});
