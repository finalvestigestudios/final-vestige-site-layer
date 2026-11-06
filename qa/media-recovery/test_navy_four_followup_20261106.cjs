'use strict';
const assert=require('node:assert/strict');
const test=require('node:test');
const fs=require('node:fs'),path=require('node:path');
const {validateManifest}=require('./validate_navy_four_followup_20261106.cjs');
const load=()=>JSON.parse(fs.readFileSync(path.join(__dirname,'navy_four_catalog_followup_20261106.json'),'utf8'));
test('baseline: 4 source-only records, no fabricated visitor evidence',()=>assert.equal(validateManifest(load()).ok,true));
const unsafe=[
 ['claim measured 76%',m=>m.catalog_review.measured_wire_reduction_percent=76],
 ['declare 42 failures proven',m=>m.catalog_review.original_42_broken_proven=true],
 ['invent visitor 404',m=>m.records[0].original_guest_browser_http=404],
 ['invent HTTP 200',m=>m.records[1].original_origin_http_status=200],
 ['invent decoded pixels',m=>m.records[2].decoded_pixels=819],
 ['invent transfer size',m=>m.records[3].cold_transfer_bytes=3],
 ['invent browser breakage',m=>m.records[1].visitor_broken=true],
 ['authorize caching',m=>m.records[2].rehost_or_cache_permission=true],
 ['authorize upload',m=>m.records[1].wordpress_upload_authorized=true],
 ['authorize post edit',m=>m.records[2].wordpress_post_edit_authorized=true],
 ['approve photo binary match',m=>m.records[0].candidate_binary_identity_verified=true],
 ['unhold rights',m=>m.records[3].rights_review='APPROVED'],
 ['change catalog identity',m=>m.records[1].candidate_catalog_id='NH 75561'],
 ['call Banner photo exact',m=>m.records[2].match_basis='EXACT_MATCH'],
 ['call Navy generic photo a slug match',m=>m.records[3].match_basis='SAME_SHIP_ONLY'],
 ['claim false 960x960 dimensions',m=>m.records[3].conditional_960.height=960],
 ['upscale beyond max width',m=>m.records[0].conditional_960.width=1280],
 ['create dimensions from unknown',m=>m.records[1].conditional_960={width:960,height:960}],
 ['tamper source URL',m=>m.records[1].original_src='https://example.com/a.jpg'],
 ['enable WordPress write',m=>m.release.wordpress_production_writes=true],
 ['enable binary download',m=>m.release.binary_download=true],
 ['remove a record',m=>m.records.pop()],
 ['duplicate key',m=>m.records[3].key='274:2'],
 ['remove source pin',m=>m.basis.previous_15_row_blob_sha='unverified']
];
for(const [name,mutate] of unsafe)test('reject '+name,()=>{const m=load();mutate(m);assert.equal(validateManifest(m).ok,false)});
