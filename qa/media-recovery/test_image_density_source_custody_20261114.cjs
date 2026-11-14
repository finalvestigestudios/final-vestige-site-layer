'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {assess}=require('./image_density_release_gate_20261114.cjs');
const raw=JSON.parse(fs.readFileSync(path.join(__dirname,'image_density_preflight_nine_20261114.json'),'utf8')),clone=()=>JSON.parse(JSON.stringify(raw));
const row=(r,slot)=>r.results.find(x=>x.slot===slot);
test('baseline nine source rows valid but release on HOLD',()=>{const r=assess(clone());assert.equal(r.source_inventory_valid,true);assert.equal(r.results.length,9);assert.equal(r.release_authorized,false)});
for(const item of raw.items)for(const field of ['source_kind','historical_scene_identity','provenance_note']){
 test(item.slot+' '+field+' unauthorized mutation fails source validity',()=>{
  const a=clone(),x=a.items.find(y=>y.slot===item.slot);x[field]=field==='historical_scene_identity'?(x[field]==='UNVERIFIED'?'RECONSTRUCTION_SAME_SOURCE':'UNVERIFIED'):x[field]+'__unsourced';
  const r=assess(a);assert.equal(r.source_inventory_valid,false);assert.ok(row(r,item.slot).reasons.includes('source_provenance_drift'));assert.equal(r.release_authorized,false);
 });
}
test('removing historical attribution fails',()=>{const a=clone();delete a.items[0].provenance_note;assert.equal(assess(a).source_inventory_valid,false)});
test('swapping two photo rights notes fails for both originals',()=>{const a=clone(),u=a.items.find(x=>x.slot==='285:5'),v=a.items.find(x=>x.slot==='418:2');[u.provenance_note,v.provenance_note]=[v.provenance_note,u.provenance_note];const r=assess(a);assert.equal(r.source_inventory_valid,false);assert.ok(row(r,'285:5').reasons.includes('source_provenance_drift'));assert.ok(row(r,'418:2').reasons.includes('source_provenance_drift'))});
test('museum image cannot be relabeled unrestricted PD',()=>{const a=clone();a.items.find(x=>x.slot==='418:2').source_kind='UNRESTRICTED_PD';assert.equal(assess(a).source_inventory_valid,false)});
test('P0 publisher photo cannot be relabeled an AI reconstruction',()=>{const a=clone(),x=a.items.find(x=>x.slot==='285:5');x.historical_scene_identity='RECONSTRUCTION_SAME_SOURCE';x.source_kind='FIRST_PARTY_AI_ASSISTED_RECONSTRUCTION';assert.equal(assess(a).source_inventory_valid,false)});
test('passing image density cannot erase false rights statement',()=>{const a=clone();a.items[0].source_kind='LICENSE_CLEARED';const o={'34:0':{css_width_px:400,css_height_px:225,dpr:2,cold_browser_verified:true,candidate_http_status:200,candidate_decoded:true,candidate_current_src:'https://finalvestige.com/wp-content/example.webp',candidate_natural_width_px:960,candidate_natural_height_px:540,asset_identity_verified:true}};const r=assess(a,o);assert.equal(r.results[0].density,'DENSITY_SCREEN_PASS');assert.equal(r.source_inventory_valid,false);assert.equal(r.release_authorized,false)});
