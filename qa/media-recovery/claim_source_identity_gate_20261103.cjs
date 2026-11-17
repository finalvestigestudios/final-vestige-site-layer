'use strict';
/**
 * Supplemental frozen-source identity gate for sitewide CDP wire-byte claims.
 * No network, media downloads, CMS changes, or license grants.
 * It validates asserted source bindings, NOT proof of a real CDP capture.
 */
const normalized=u=>typeof u==='string'&&/^https?:\/\/[^\s/?#]+(?:[/?#]|$)/i.test(u)?u:null;
const equal=(a,b)=>!!normalized(a)&&normalized(a)===normalized(b);
const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
function validateClaimSourceBindings(data,inventory,parts){
 const errors=[],fail=e=>{if(errors.length<40)errors.push(e)};
 const posts=new Map(),sources=new Map();
 const out=()=>({schema_version:1,gate:'FROZEN_SOURCE_AND_CURRENT_SRC_BINDING',
  pass:errors.length===0,reason_codes:errors,verified_post_count:posts.size,
  verified_slot_count:sources.size,original_binary_identity_verified:false,
  genuine_cdp_capture_verified:false,visitor_broken_images_confirmed:null,
  cdp_wire_savings_measured:false,wordpress_republication_authorized:false});
 if(!inventory||inventory.schema_version!==1||inventory.posts_count!==61||
   inventory.image_slot_count!==355||!Array.isArray(inventory.posts)||
   !Array.isArray(inventory.source_parts)||inventory.source_parts.length!==8||
   !Array.isArray(parts)||parts.length!==8)return {...out(),pass:false,reason_codes:['invalid immutable census inputs']};
 for(const p of inventory.posts){
  if(!Number.isInteger(p.post_id)||posts.has(p.post_id)||!normalized(p.page_url)||
    !Array.isArray(p.expected_slots))fail('invalid frozen post');
  else posts.set(p.post_id,p);
 }
 for(let i=0;i<8;i++){
  const part=parts[i],decl=inventory.source_parts[i];
  if(!part||part.batch!==i+1||!Array.isArray(part.images)||!Array.isArray(part.posts)||
    part.images.length!==decl.declared_slots||part.posts.length!==decl.declared_posts){
   fail('incomplete frozen part '+(i+1));continue;
  }
  for(const im of part.images){
   const p=posts.get(im?.post_id);
   if(!p||sources.has(im.key)||!p.expected_slots.includes(im.key)||
     !equal(im.post_url,p.page_url)||!normalized(im.source_url))fail('invalid frozen image '+im?.key);
   else sources.set(im.key,im.source_url);
  }
 }
 if(posts.size!==61||sources.size!==355||
   ![...posts.values()].every(p=>p.expected_slots.every(s=>sources.has(s))))fail('missing frozen post/slot census');
 if(!data||data.source_inventory_id!==inventory.inventory_id||!Array.isArray(data.pairs)||
   data.pairs.length!==61)return {...out(),pass:false,reason_codes:[...errors,'unmatched paired sitewide census']};
 const seenPosts=new Set();
 for(const pair of data.pairs){
  const p=posts.get(pair?.post_id),tag='post:'+pair?.post_id;
  if(!p||seenPosts.has(pair.post_id)||!equal(pair.page_url,p.page_url)||
    !Array.isArray(pair.expected_slots)||pair.expected_slots.length!==p.expected_slots.length||
    !p.expected_slots.every(x=>pair.expected_slots.includes(x))){
   fail('post/slot list drift '+tag);continue;
  }
  seenPosts.add(pair.post_id);
  if(!Array.isArray(pair.before)||!Array.isArray(pair.after)||
    pair.before.length!==pair.after.length||pair.before.length<3) {fail('missing repetitions '+tag);continue}
  for(const phase of ['before','after'])for(let i=0;i<pair[phase].length;i++){
   const run=pair[phase][i],seen=new Set();
   if(!run||!Array.isArray(run.requests)){fail('missing requests '+tag+':'+phase+':'+i);continue}
   for(const request of run.requests){
    if(!request||!Array.isArray(request.slot_keys)||!request.slot_keys.length||
      !normalized(request.request_url)){fail('invalid mapped image request '+tag);continue}
    const stored=request.dom_stored_sources,current=request.dom_current_sources;
    const exactKeys=m=>m&&typeof m==='object'&&!Array.isArray(m)&&
      Object.keys(m).length===request.slot_keys.length&&request.slot_keys.every(k=>own(m,k));
    if(!exactKeys(stored)||!exactKeys(current)){fail('missing/extra DOM source keys '+tag);continue}
    const distinctOriginals=new Set();
    for(const slot of request.slot_keys){
     if(!p.expected_slots.includes(slot)||seen.has(slot))fail('unexpected/repeated slot '+tag+':'+slot);
     seen.add(slot);
     if(!equal(stored[slot],sources.get(slot)))fail('frozen stored URL drift '+tag+':'+slot);
     if(!equal(current[slot],request.request_url))fail('currentSrc/request URL mismatch '+tag+':'+slot);
     distinctOriginals.add(sources.get(slot));
    }
    if(distinctOriginals.size>1)fail('unrelated originals merged into one request '+tag);
   }
   for(const s of p.expected_slots)if(!seen.has(s))fail('uncaptured slot '+tag+':'+s);
  }
 }
 if(seenPosts.size!==61)fail('partial sitewide post coverage');
 return out();
}
module.exports={validateClaimSourceBindings};