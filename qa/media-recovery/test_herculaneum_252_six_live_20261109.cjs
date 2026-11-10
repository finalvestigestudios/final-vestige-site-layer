'use strict';
const assert=require('node:assert/strict');
const test=require('node:test');
const {validate}=require('./validate_herculaneum_252_six_live_20261109.cjs');
const source=require('./herculaneum_252_six_live_20261109.json');
const clone=()=>JSON.parse(JSON.stringify(source));
test('accepts complete exact-source live census with no visitor-failure claims',()=>assert.equal(validate(source).ok,true));
const probes=[
['missing source',a=>{a.rows.pop()}],
['duplicate key',a=>{a.rows[1].slot='252:0'}],
['source swap',a=>{a.rows[0].published_src=a.rows[1].published_src}],
['ALT rewrite not authorized',a=>{a.rows[1].published_alt='wrong'}],
['wrong post',a=>{a.rows[0].post_id=253}],
['wrong census blob',a=>{a.frozen_inventory.blob_sha='0000000000000000000000000000000000000000'}],
['invent browser 404',a=>{a.rows[2].viewer.origin_http_status=404}],
['invent guest 200',a=>{a.rows[3].viewer.guest_browser_status=200}],
['invent natural width',a=>{a.rows[4].viewer.guest_natural_width=500}],
['invent transferred bytes',a=>{a.rows[0].viewer.guest_encoded_bytes=1200}],
['invent 76 percent saving',a=>{a.measurement.measured_image_wire_reduction_pct=76}],
['invent confirmed failure',a=>{a.rows[1].viewer.definitively_broken=true}],
['authorize cache',a=>{a.rows[0].permissions.cache=true}],
['authorize download',a=>{a.rows[0].permissions.download=true}],
['authorize WP upload',a=>{a.rows[1].permissions.wordpress_upload=true}],
['authorize Gutenberg rewrite',a=>{a.rows[2].permissions.post_block_rewrite=true}],
['invent rights clearance',a=>{a.rows[3].permissions.rights_review='CLEAR'}],
['invent binary match',a=>{a.rows[4].catalog.verified_binary_identity=true}],
['enlarge 876px source',a=>{a.rows[2].derivative.conditional_max_width_px=960}],
['wrong 960px geometry',a=>{a.rows[0].derivative.conditional_height_px=800}],
['erase floorplan mismatch',a=>{a.rows[1].fidelity.issue=null}],
['erase handwritten-copy warning',a=>{a.rows[5].fidelity.editor_review_required=false}],
['alter source catalog',a=>{a.rows[1].catalog.url='https://example.com/not-the-source'}],
['claim live source mismatch',a=>{a.live_wordpress_readback.exact_matches=5}],
['reclassify tool error as HTTP',a=>{a.rows[0].viewer.result='http_404'}],
['invent native binary download',a=>{a.rows[0].derivative.image_binary_downloaded=true}]
];
probes.forEach(([name,mutate])=>test('rejects '+name,()=>{const a=clone();mutate(a);assert.equal(validate(a).ok,false,name)}));
