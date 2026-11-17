'use strict';
/**
 * Read-only identity gate for before/after media-weight claims. A pair of
 * arbitrary 61-page, 355-slot Chrome logs is NOT a Final Vestige census.
 * Pin the exact archived Gutenberg image-source inventory before allowing
 * the separate CDP wire-byte evaluator to report a measured site claim.
 * No HTTP fetch, image copying, WordPress writes or publication permissions.
 */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const FROZEN_PART_BLOBS=Object.freeze([
 '948bc1b65b42799aa40cfdb810ddf6ffd80886b6',
 '48e1ebf07207e948ba5802e714eb39659d2e1c1d',
 '49183f66f880f7c4dfd363acca906876877f2e5e',
 '6df3251e5a67a971d87a516a1ba4a0cc32f51f96',
 '9b16b828342a9ac338f3e65610fd3d8d508355e9',
 '0f3dfe398a76838049cebba7cb773d5c5a0c8c69',
 '21095161e633aba093b74c0ead9936c9f6186d00',
 '5659ec243c188928be3f89c0f96354b660608ca2'
]);
const gitBlobSha=buffer=>crypto.createHash('sha1').update('blob '+buffer.length+'\0').update(buffer).digest('hex');
function checkPinnedParts(root=__dirname,expected=FROZEN_PART_BLOBS){
 if(!Array.isArray(expected)||expected.length!==8||expected.some(s=>!/^[a-f\d]{40}$/.test(s)))
  throw Error('invalid_frozen_blob_manifest');
 for(let i=0;i<8;i++){
  const rel='parts/'+String(i+1).padStart(2,'0')+'.json';
  const actual=gitBlobSha(fs.readFileSync(path.join(root,rel)));
  if(actual!==expected[i])throw Error('frozen_source_part_mismatch:'+rel);
 }
 return true;
}
function checkFrozenBaseline(snapshot,baseline){
 const errors=[],posts=new Map(),images=new Map(),seen=new Set();
 if(!Array.isArray(snapshot?.parts)||snapshot.parts.length!==8)
  return ['frozen_8_parts_required'];
 for(const part of snapshot.parts){
  if(!Array.isArray(part?.posts)||!Array.isArray(part?.images))return ['frozen_part_invalid'];
  for(const p of part.posts){
   if(!Number.isSafeInteger(p.id)||posts.has(p.id)||typeof p.url!=='string')
    errors.push('duplicate_or_invalid_frozen_post');
   else posts.set(p.id,p);
  }
  for(const im of part.images){
   if(typeof im?.key!=='string'||images.has(im.key)||!Number.isSafeInteger(im.post_id)||
      typeof im.source_url!=='string'||im.key!==im.post_id+':'+im.slot)
    errors.push('duplicate_or_invalid_frozen_image');
   else images.set(im.key,im);
  }
 }
 if(posts.size!==61||images.size!==355)errors.push('frozen_61_355_count_mismatch');
 if(!Array.isArray(baseline?.pages)||baseline.pages.length!==posts.size)
  return [...new Set([...errors,'baseline_post_set_not_frozen'])];
 let checkedSlots=0;
 for(const p of baseline.pages){
  if(!Number.isSafeInteger(p?.post_id)||seen.has(p.post_id)){
   errors.push('baseline_duplicate_or_invalid_post_id');continue;
  }
  seen.add(p.post_id);
  const frozen=posts.get(p.post_id);
  if(!frozen||p.url!==frozen.url){errors.push('baseline_post_url_not_in_frozen_census:'+p.post_id);continue}
  if(!Array.isArray(p.stored_images)||p.stored_images.length!==frozen.images||
     p.stored_image_count!==frozen.images){
   errors.push('baseline_image_count_not_frozen:'+p.post_id);continue;
  }
  const keys=new Set();
  for(const im of p.stored_images){
   checkedSlots++;
   const k=im?.image_key,original=images.get(k);
   if(typeof k!=='string'||keys.has(k)||!original||original.post_id!==p.post_id||
      im.stored_url!==original.source_url){
    errors.push('baseline_image_not_frozen:'+String(k));continue;
   }
   keys.add(k);
  }
 }
 if(seen.size!==posts.size||checkedSlots!==images.size)errors.push('baseline_slot_set_not_frozen');
 return [...new Set(errors)];
}
function assessFrozenPair(before,after,approvals=[],root=__dirname){
 let snapshot;
 try{
  checkPinnedParts(root);
  const inventory=require('./validate_inventory.cjs');
  snapshot=inventory.loadSnapshot(root);
  const result=inventory.validateSnapshot(snapshot);
  if(!result.ok)throw Error('frozen_inventory_schema_invalid:'+result.errors.join(','));
 }catch(e){return {status:'NOT_MEASURED',reasons:['frozen_census_unverified:'+String(e.message||e)],
  savings_percent:null,claim_76_percent_supported:false,production_changes_approved_by_this_tool:false}}
 const errors=checkFrozenBaseline(snapshot,before);
 if(errors.length)return {status:'NOT_MEASURED',reasons:errors,savings_percent:null,
  claim_76_percent_supported:false,production_changes_approved_by_this_tool:false};
 const result=require('./weight_claim_pair_gate_20261102.cjs').assessPair(before,after,approvals);
 return result.status==='MEASURED'?{...result,frozen_source_identity_verified:true,
  census_origin_date:'2026-10-30',frozen_part_git_blob_shas:[...FROZEN_PART_BLOBS]}:result;
}
module.exports={FROZEN_PART_BLOBS,gitBlobSha,checkPinnedParts,checkFrozenBaseline,assessFrozenPair};
