'use strict';
// Synthetic assertions only; no guest HTTP, media copying or achieved-savings claim.
const {validateClaimSourceBindings}=require('./claim_source_identity_gate_20261103.cjs');
const inventory=require('./wire_source_inventory_20261030.json');
const parts=require('./validate_inventory.cjs').loadSnapshot().parts;
const sources=new Map(parts.flatMap(p=>p.images.map(im=>[im.key,im.source_url])));
const clone=x=>JSON.parse(JSON.stringify(x));
const assert=(v,m)=>{if(!v)throw Error(m)};
function fixture(){
 return {source_inventory_id:inventory.inventory_id,pairs:inventory.posts.map(p=>{
  const requests=p.expected_slots.map((slot,j)=>({request_id:'id'+j,slot_keys:[slot],request_url:sources.get(slot),
   dom_stored_sources:{[slot]:sources.get(slot)},dom_current_sources:{[slot]:sources.get(slot)}}));
  const mk=()=>({requests:clone(requests)});
  return {post_id:p.post_id,page_url:p.page_url,expected_slots:p.expected_slots.slice(),
   before:[mk(),mk(),mk()],after:[mk(),mk(),mk()]};
 })};
}
function runTests(){
 let passed=0;
 const valid=fixture(),result=validateClaimSourceBindings(valid,inventory,parts);
 assert(result.pass===true&&result.verified_post_count===61&&result.verified_slot_count===355,'valid full fixture '+result.reason_codes);passed++;
 const invalid=(name,mutate,reason)=>{
  const x=clone(valid);mutate(x);const v=validateClaimSourceBindings(x,inventory,parts);
  assert(v.pass===false&&v.reason_codes.some(x=>x.includes(reason)),name+': '+v.reason_codes);passed++;
 };
 invalid('placeholder swap',x=>x.pairs[0].after[0].requests[0].dom_stored_sources['34:0']='https://finalvestige.com/decoy.png','frozen stored URL drift');
 invalid('CDP unrelated URL',x=>x.pairs[0].after[0].requests[0].request_url='https://other.example/decoy.png','currentSrc/request URL mismatch');
 invalid('unbound current source',x=>delete x.pairs[0].before[0].requests[0].dom_current_sources,'missing/extra DOM source keys');
 invalid('extra slot map',x=>x.pairs[0].after[1].requests[0].dom_current_sources['99:0']='https://finalvestige.com/a.png','missing/extra DOM source keys');
 invalid('missing image',x=>x.pairs[0].before[0].requests=[],'uncaptured slot');
 invalid('insufficient repeat',x=>x.pairs[0].before.pop(),'missing repetitions');
 invalid('extra post',x=>x.pairs.push(clone(x.pairs[0])),'unmatched paired sitewide census');
 invalid('page drift',x=>x.pairs[0].page_url='https://finalvestige.com/another/','post/slot list drift');
 invalid('wrong inventory',x=>x.source_inventory_id='not-our-inventory','unmatched paired sitewide census');
 const modifiedParts=clone(parts);modifiedParts[0].images[0].source_url='https://finalvestige.com/replaced.png';
 const r=validateClaimSourceBindings(valid,inventory,modifiedParts);
 assert(!r.pass&&r.reason_codes.some(x=>x.includes('frozen stored URL drift')),'altered snapshot should not pass');passed++;
 const duplicate=clone(valid);const p=duplicate.pairs.find(p=>p.expected_slots.length>=2);
 p.after[1].requests[0].slot_keys.push(p.expected_slots[1]);
 p.after[1].requests[0].dom_stored_sources[p.expected_slots[1]]=sources.get(p.expected_slots[1]);
 p.after[1].requests[0].dom_current_sources[p.expected_slots[1]]=p.after[1].requests[0].request_url;
 const d=validateClaimSourceBindings(duplicate,inventory,parts);
 assert(!d.pass&&d.reason_codes.some(x=>x.includes('unrelated originals merged')),'unrelated image merger blocked');passed++;
 return {passed,scope:'synthetic 61 post/355 slot source bindings only',real_browser_runs:0,real_recovery_count:0};
}
module.exports={runTests};
if(require.main===module)console.log(JSON.stringify(runTests()));