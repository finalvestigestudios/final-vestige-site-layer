'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_mann_gulch_213_20261109.cjs');
const load=name=>JSON.parse(fs.readFileSync(path.join(__dirname,name),'utf8'));
const a=load('mann_gulch_213_seven_20261109.json'),c=load('offsite_upstream_288_20261109.json');
const p=load('mann_gulch_213_frozen_wp_fixture_20261109.json'); // Exact original fields pinned to source blob 0f3dfe398a76838049cebba7cb773d5c5a0c8c69
test('baseline seven-source audit',()=>assert.deepEqual(validate(a,c,p),{pass:true,slots:7,unique_urls:6,guest_statuses_verified:0}));
const mutations=[
 ['fake origin 404',x=>x.rows[0].origin_http_status=404],
 ['fake guest success',x=>x.rows[0].guest_browser_http_status=200],
 ['fake guest broken',x=>x.rows[3].visitor_broken=true],
 ['fake wire count',x=>x.rows[0].guest_wire_bytes=500],
 ['false 76 percent claim',x=>x.sitewide_baseline.percent_76_wire_reduction_measured=true],
 ['fictional width',x=>x.rows[0].catalog_native_px=[1000,700]],
 ['bad Commons dimensions',x=>x.rows[3].conditional_960px_size=[960,900]],
 ['remove source',x=>x.rows.pop()],
 ['change source URL',x=>x.rows[1].stored_url='https://example.com/new.jpg'],
 ['change frozen alt',x=>x.rows[0].frozen_alt='misleading'],
 ['unapproved cache',x=>x.rows[2].release.cache=true],
 ['rewrite blocked',x=>x.rows[6].release.gutenberg_rewrite=true],
 ['NYT license erased',x=>x.rows[5].rights_caveat='US government property'],
 ['unverified image identity asserted',x=>x.rows[4].binary_identity_verified=true],
 ['duplicate map unbound',x=>x.rows[6].duplicate_exact_stored_url_of=null],
 ['viewer status pretended',x=>x.rows[3].external_viewer_observation='IMAGE_DISPLAYED']
];
for(const[n,fn]of mutations)test('reject '+n,()=>{const x=structuredClone(a);fn(x);assert.throws(()=>validate(x,c,p))});
