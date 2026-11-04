'use strict';
/**
 * Strict offline attribution for the public "76% image-wire saved" badge.
 * Paired uncached CDP totals can establish a byte delta without explaining
 * what caused it. Only transfer differences on explicitly approved changed
 * source slots may support an optimization claim in this source-replacement lane.
 * Server/CDN same-URL optimization requires a separate deployment attestation.
 * No browser, WordPress, network, download or production writes.
 */
const safe=x=>Number.isSafeInteger(x)&&x>=0;
function groups(page,label,errors){
 const net=new Map(),byId=new Map(),bySig=new Map(),seen=new Set();
 for(const n of page?.network_images||[])if(n?.request_id)net.set(n.request_id,n);
 for(const slot of page?.stored_images||[]){
  const key=slot?.image_key,id=slot?.request_id;
  if(typeof key!=='string'||seen.has(key)||!id||!net.has(id)){
   errors.push(label+':unbound_or_duplicate_slot');continue;
  }
  seen.add(key);
  if(!byId.has(id))byId.set(id,[]);
  byId.get(id).push(key);
 }
 for(const [id,keys] of byId){
  keys.sort();const signature=JSON.stringify(keys),n=net.get(id);
  if(bySig.has(signature)||!safe(n?.encoded_data_length)||n.encoded_data_length===0)
    errors.push(label+':invalid_or_duplicate_request_group');
  else bySig.set(signature,{keys,bytes:n.encoded_data_length});
 }
 return bySig;
}
function assessApprovedWireAttribution(before,after,changedKeys){
 const reasons=[],changed=new Set(changedKeys||[]),postAfter=new Map((after?.pages||[]).map(p=>[p.post_id,p]));
 let approvedBefore=0,approvedAfter=0,unchangedGroups=0,changedGroups=0;
 if(!changed.size)reasons.push('no_approved_changed_image_sources');
 for(const b of before?.pages||[]){
  const a=postAfter.get(b.post_id);
  if(!a){reasons.push('missing_candidate_post:'+b.post_id);continue;}
  const prior=groups(b,'before:'+b.post_id,reasons),next=groups(a,'after:'+b.post_id,reasons);
  if(prior.size!==next.size)reasons.push('changed_network_request_grouping:'+b.post_id);
  for(const [signature,p] of prior){
   const q=next.get(signature);
   if(!q){reasons.push('changed_network_request_grouping:'+b.post_id);continue;}
   const n=p.keys.filter(key=>changed.has(key)).length;
   if(n&&n!==p.keys.length){reasons.push('mixed_changed_and_unchanged_shared_request:'+signature);continue;}
   if(n){
    changedGroups++;approvedBefore+=p.bytes;approvedAfter+=q.bytes;
   }else{
    unchangedGroups++;
    if(p.bytes!==q.bytes)reasons.push('unattributed_unchanged_source_wire_delta:'+signature);
   }
  }
 }
 const approvedSavings=approvedBefore-approvedAfter;
 if(!safe(approvedBefore)||!safe(approvedAfter)||!Number.isSafeInteger(approvedSavings))
   reasons.push('unsafe_approved_source_byte_sum');
 if(changed.size&&!changedGroups)reasons.push('changed_sources_not_in_bound_requests');
 const pass=reasons.length===0;
 return {pass,reasons:[...new Set(reasons)],
   changed_image_source_slots:changed.size,changed_network_request_groups:changedGroups,
   unchanged_network_request_groups:unchangedGroups,
   approved_before_bytes:pass?approvedBefore:null,
   approved_after_bytes:pass?approvedAfter:null,
   approved_source_savings_bytes:pass?approvedSavings:null,
   note:'This proves attribution within provided paired CDP records only, not actual browser capture authenticity, licensing, or release permission.'};
}
module.exports={assessApprovedWireAttribution};
