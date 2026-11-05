'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_p0_source_relocations_20261105.cjs');
const load=()=>JSON.parse(fs.readFileSync(path.join(__dirname,'p0_source_relocations_20261105.json'),'utf8'));
test('exact migration ledger passes without calling origin 404/browser broken',()=>{let r=validate(load());assert.equal(r.rows,2);assert.equal(r.release,'HOLD')});
const mutations=[
 ['invented old origin HTTP',d=>d.rows[0].source_error_is_origin_http=true],
 ['invented visitor failure',d=>d.rows[1].guest_broken=true],
 ['invented visitor status',d=>d.rows[0].candidate_guest_http_status=200],
 ['42 confirmed without evidence',d=>d.sitewide_baseline.alleged_broken_42='VERIFIED'],
 ['76% claimed measured',d=>d.sitewide_baseline.claimed_weight_reduction_76='MEASURED'],
 ['false rights clearance',d=>d.rows[1].rights='APPROVED'],
 ['unauthorized hotlink',d=>d.rows[0].external_hotlink_permission_verified=true],
 ['unauthorized cache',d=>d.rows[1].caching_authorized=true],
 ['WordPress write',d=>d.rows[0].wordpress_post_edit_authorized=true],
 ['invented image SHA',d=>d.rows[0].candidate_original_binary_sha256='0'.repeat(64)],
 ['Scotch upscaling to 960px',d=>d.rows[1].proposed_derivative_dimensions_px=[960,741]],
 ['invented Skyway dimensions',d=>d.rows[0].catalog_dimensions_px=[1000,667]],
 ['incorrect historical date',d=>d.rows[1].historical_event_date='1964-01-01'],
 ['invalid new publisher location',d=>d.rows[0].proposed_source='https://evil.example/x.jpg'],
 ['deleted Skyway context',d=>d.rows[0].visual_integrity_issue='none'],
 ['deleted Scotch caption conflict',d=>d.rows[1].visual_integrity_issue='none'],
 ['wrong frozen inventory',d=>d.frozen_inventory_git_blobs[0]='0'.repeat(40)],
 ['missing second image',d=>d.rows.pop()]
];
for(const [name,mutate] of mutations)test('reject: '+name,()=>{const d=load();mutate(d);assert.throws(()=>validate(d))});
