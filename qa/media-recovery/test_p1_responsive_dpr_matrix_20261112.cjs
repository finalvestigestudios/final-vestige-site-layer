'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const source=require('./p1_15_responsive_960_feasibility_20261111.json');
const matrix=require('./p1_15_responsive_dpr_matrix_20261112.json');
const {sourceOK,plan,verify}=require('./build_p1_responsive_dpr_matrix_20261112.cjs');
const copy=x=>JSON.parse(JSON.stringify(x));
test('pinned 15-source / 47,096,779 original bytes',()=>{
 assert.equal(sourceOK(source),true);assert.equal(verify(matrix,source),true);
 assert.equal(matrix.counts.originals,15);assert.equal(matrix.counts.conditional_geometry_cases,270);
 assert.equal(matrix.rows.reduce((s,r)=>s+r.stored_original_bytes,0),47096779);
});
test('5 no-subsize PNGs cannot satisfy real CSS 960 at 2x even with native pixels',()=>{
 assert.equal(matrix.counts.five_png_native_cannot_meet_css960_dpr2,5);
 for(const r of matrix.rows.filter(r=>r.wp_registered_subsize_count===0))
  assert.equal(r.geometry_cases.find(c=>c.css_width_px===960&&c.dpr===2).native_can_support,false);
});
test('960 width passes 390 CSS 2x but fails 390 CSS 3x and 640 CSS 2x',()=>{
 for(const r of matrix.rows){
  assert.equal(r.geometry_cases.find(c=>c.css_width_px===390&&c.dpr===2).static_960w_sufficient,true);
  assert.equal(r.geometry_cases.find(c=>c.css_width_px===390&&c.dpr===3).static_960w_sufficient,false);
  assert.equal(r.geometry_cases.find(c=>c.css_width_px===640&&c.dpr===2).static_960w_sufficient,false);
 }
});
test('no-upscale proposed physical pixel dimensions',()=>{
 for(const r of matrix.rows)for(const [w,h] of r.proposed_variant_dimensions_px){
  assert.ok(w<=r.native_px[0]);assert.ok(h<=r.native_px[1]);
 }
});
test('none implies rights, real browser transfer, derivative binary, WP production change',()=>{
 assert.equal(matrix.policy.actual_76_percent_network_reduction_measured,false);
 assert.equal(matrix.policy.no_wp_writes,true);assert.equal(matrix.policy.no_binaries_generated,true);
 for(const r of matrix.rows){
  assert.equal(r.licensed_for_rehost,false);assert.equal(r.binaries_created,false);
  assert.equal(r.actual_guest_http_status,null);assert.equal(r.actual_guest_wire_bytes,null);
 }
});
test('source, rights, dimensions, wire and fake performance claims fail closed',()=>{
 for(const f of [x=>x.rows[0].licensed_for_rehost=true,x=>x.rows[0].actual_guest_wire_bytes=200,
  x=>x.rows[0].original_url='https://example.org/other.jpg',
  x=>x.rows[3].proposed_variant_dimensions_px[0][0]=3000,
  x=>x.policy.actual_76_percent_network_reduction_measured=true]){
  const changed=copy(matrix);f(changed);assert.equal(verify(changed,source),false);
 }
 const changed=copy(source);changed.rows[0].commercial_reuse_cleared=true;
 assert.equal(sourceOK(changed),false);
});
