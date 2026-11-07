'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {validate,KEYS}=require('./validate_loc_fourteen_20261106.cjs');
const source=require('./loc_fourteen_primary_crosswalk_20261106.json'),clone=()=>JSON.parse(JSON.stringify(source));
test('baseline 14 records valid',()=>assert.deepEqual(validate(source),[]));
test('14 expected keys unique',()=>assert.equal(new Set(KEYS).size,14));
const scenarios=[
['invented 42 browser failures',a=>a.reference_cohort.confirmed_broken=42],
['invented 76pct saving',a=>a.reference_cohort.measured_transfer_reduction_percent=76],
['production enabled',a=>a.policy.no_wordpress_writes=false],
['unlicensed caching',a=>a.policy.no_unlicensed_caching=false],
['allow enlargement',a=>a.policy.no_upscaling=false],
['remove detailed panorama',a=>a.policy.map_panorama_full_detail_required=false],
['invent source 404',a=>a.records[0].source_http_status=404],
['invent browser 403',a=>a.records[0].browser_http_status=403],
['invent broken image',a=>a.records[0].visitor_broken=true],
['unapproved cache',a=>a.records[0].cache_authorized=true],
['unapproved wordpress',a=>a.records[0].production_write_authorized=true],
['unreviewed rights',a=>a.records[0].rights_decision='CLEARED'],
['invent source host',a=>a.records[0].original_url='https://bad.test/image.jpg'],
['catalog mismatch host',a=>a.records[0].archive_catalog_url='https://bad.test/item'],
['duplicate slot',a=>a.records[1].key=a.records[0].key],
['missing source',a=>a.records.pop()],
['incorrect post',a=>a.records[0].post_id=1],
['wrong catalog status',a=>a.records[0].archive_catalog_state='BROWSER_VERIFIED'],
['wrong summary count',a=>a.coverage.item_catalog_matches=777],
['preview without native',a=>a.records[0].conditional_preview_dimensions={width:960,height:500}],
['enlarged preview',a=>{a.records[0].native_dimensions={width:600,height:400};a.records[0].conditional_preview_dimensions={width:960,height:640}}],
['aspect ratio distortion',a=>{a.records[0].native_dimensions={width:2000,height:1000};a.records[0].conditional_preview_dimensions={width:960,height:960}}],
['native invalid',a=>a.records[0].native_dimensions={width:0,height:500}],
];
for(const [name,mutate]of scenarios)test('reject '+name,()=>{const a=clone();mutate(a);assert.ok(validate(a).length>0)});
