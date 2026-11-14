'use strict';
const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');
const path=require('node:path');const {validate}=require('./validate_p0_six_recheck_20261114.cjs');
const snapshot=JSON.parse(fs.readFileSync(path.join(__dirname,'p0_six_retriever_recheck_20261114.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(snapshot));
function rejection(title,mutate,expect){test(title,()=>{const a=clone();mutate(a);const r=validate(a);
 assert.equal(r.ok,false,JSON.stringify(r));assert.ok(r.errors.some(x=>x.includes(expect)),JSON.stringify(r));});}
test('unaltered six-P0 actual URL/wrapper audit is internally consistent, but does not clear releases',()=>{
 const r=validate(snapshot);assert.deepEqual(r,{ok:true,errors:[]});
 assert.equal(snapshot.release.all_hold,true);assert.equal(snapshot.historical_census.broken_guest_verified,null);
});
for(let i=0;i<6;i++){
 rejection('source URL drift row '+i,a=>a.rows[i].published_src_prior_wp_readback+='?changed=1','source_candidate_or_rights_drift');
 rejection('unverified origin HTTP row '+i,a=>a.rows[i].fresh_retriever.origin_http_status=404,'fabricated_guest_or_origin_evidence');
 rejection('web wrapper cannot become guest HTTP row '+i,a=>a.rows[i].fresh_retriever.logged_out_browser_http_status=404,'fabricated_guest_or_origin_evidence');
 rejection('unapproved cache row '+i,a=>a.rows[i].release.download_or_cache=true,'unauthorized_replacement_or_cache');
 rejection('rights cannot be silently approved row '+i,a=>a.rows[i].candidate.item_republication_rights_cleared=true,'unsupported_clearance_or_identity');
 rejection('candidate URL changed row '+i,a=>a.rows[i].candidate.catalog_or_candidate_url+='?other=1','source_candidate_or_rights_drift');
 rejection('rights note changed row '+i,a=>a.rows[i].candidate.rights_status='PUBLIC_DOMAIN','source_candidate_or_rights_drift');
 rejection('fabricated wrapper result row '+i,a=>a.rows[i].fresh_retriever.tool_result_code=200,'unverified_retriever_result');
}
rejection('reported 42 is not guest verified',a=>a.historical_census.broken_guest_verified=42,'census_or_fabricated_proof');
rejection('76 percent claim cannot be marked measured',a=>a.historical_census.sitewide_wire_reduction_76_percent_measured=true,'census_or_fabricated_proof');
rejection('stored-original bytes cannot be visitor traffic',a=>a.last_verified_large_wp_origins.actual_visitor_bytes=49107665,'stored_bytes_mislabeled_as_wire');
rejection('historical media vs QA offsite discrepancy must be preserved',a=>a.historical_census.external_refs_media=286,'census_or_fabricated_proof');
rejection('candidate 960px derivative must not upscale 819px original',a=>a.rows[0].candidate.conditional_no_upscale_960px_dimensions=[960,719],'tmi_native_no_upscale_geometry');
rejection('other candidate dimensions remain unknown',a=>a.rows[1].candidate.native_dimensions_px=[960,540],'invented_candidate_dimensions');
rejection('duplicate key cannot inflate six-P0 coverage',a=>a.rows[1].slot=a.rows[0].slot,'unexpected_or_duplicate_slot');
rejection('missing row is not a completed batch',a=>a.rows.pop(),'six_rows_required');
rejection('no production WordPress uploads',a=>a.release.wordpress_prod_writes=1,'release_gate_violation');
rejection('no auto-release or WordPress post block change',a=>a.rows[2].release.wordpress_write=true,'unauthorized_replacement_or_cache');
rejection('no homepage edits',a=>a.release.homepage_design_writes=1,'release_gate_violation');
rejection('no subscription spending',a=>a.release.subscriptions_usd=1,'release_gate_violation');
rejection('no current WordPress readback claimed',a=>a.source_custody.live_wp_verified_this_sprint=true,'source_custody');
rejection('no unverified scene parity',a=>a.rows[3].candidate.historical_scene_verified_for_replacement=true,'unsupported_clearance_or_identity');
