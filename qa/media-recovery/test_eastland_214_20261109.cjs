'use strict';
const assert=require('node:assert/strict');
const {test}=require('node:test');
const {validateData,EXPECTED}=require('./validate_eastland_214_20261109.cjs');
const a=require('./eastland_214_six_loc_nara_20261109.json');
const clone=()=>JSON.parse(JSON.stringify(a));
function rejects(name,mutation){test(name,()=>{const d=clone();mutation(d);assert.ok(validateData(d,EXPECTED).length>0);});}
test('canonical frozen evidence is valid',()=>assert.deepEqual(validateData(clone(),EXPECTED),[]));
for(let i=0;i<6;i++){
 rejects('immutable source '+i,d=>d.rows[i].stored_original_url+='?altered');
 rejects('immutable ALT '+i,d=>d.rows[i].stored_alt+=' fabricated');
 rejects('guest status must be null '+i,d=>d.rows[i].source_observation.guest_http_status=404);
 rejects('no invented broken outcome '+i,d=>d.rows[i].source_observation.confirmed_broken=true);
 rejects('rights not pre-cleared '+i,d=>d.rows[i].candidate.item_rights_cleared=true);
 rejects('no media cache '+i,d=>d.rows[i].release.cache_rehost=true);
 rejects('valid non-upscaled conditional dimensions '+i,d=>d.rows[i].candidate.conditional_960px_no_upscale_dimensions_px=[960,960]);
 rejects('no fabricated wire bytes '+i,d=>d.rows[i].source_observation.guest_encoded_transfer_bytes=12345);
}
rejects('not 42 confirmed failures',d=>d.site_baseline.historic_broken_report_unverified=0);
rejects('76 percent is unmeasured',d=>d.site_baseline.claimed_76_percent_cold_wire_savings_verified=true);
rejects('decimal threshold remains 15',d=>d.site_baseline.wp_originals_over_1500000_bytes=14);
rejects('preserve NARA historic integrity',d=>d.rows[5].candidate.historical_visual_integrity='');
rejects('primary LOC source immutable',d=>d.rows[4].candidate.catalog_url='https://example.invalid');
