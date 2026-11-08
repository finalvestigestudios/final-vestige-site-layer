'use strict';
/** Fail-closed completeness gate for historical inline-image browser census.
 * Synthetic/offline policy only: this module never fetches media or authorizes publication.
 */
const {sameSource}=require('./browser_probe_core.cjs');
const goodCount=n=>Number.isSafeInteger(n)&&n>=0;
const goodUrl=u=>typeof u==='string'&&/^https:\/\/[^\s/]+\//.test(u);
const key=v=>typeof v==='string'&&/^\d+:\d+$/.test(v);
function proofKind(v){
 if(!v||typeof v!=='object'||!key(v.image_key)||!v.current_src_identity_verified||
    !goodUrl(v.stored_url)||!goodUrl(v.current_src)||
    !sameSource(v.stored_url,v.current_src)||v.complete!==true)return 'unresolved';
 if(v.result==='loaded_in_probe_browser'&&v.verified_broken_in_browser===false&&
    Number.isSafeInteger(v.natural_width)&&v.natural_width>0&&
    Number.isSafeInteger(v.natural_height)&&v.natural_height>0&&
    v.http_status===200&&goodUrl(v.request_url)&&
    sameSource(v.current_src,v.request_url)&&
    v.loaded_network_proof_verified===true&&
    v.network_final_identity_verified===true&&
    /^image\//.test(String(v.response_mime_type||''))&&
    Number.isSafeInteger(v.transfer_bytes)&&v.transfer_bytes>0&&
    v.redirected_image_identity_unverified!==true)return 'loaded';
 if(v.result==='confirmed_broken_in_probe_browser'&&v.verified_broken_in_browser===true&&
    v.natural_width===0&&v.natural_height===0&&goodUrl(v.request_url)&&
    v.network_final_identity_verified===true&&
    v.redirected_image_identity_unverified!==true&&
    sameSource(v.current_src,v.request_url)){
  if(typeof v.network_failure==='string'&&v.network_failure.trim()&&v.visual_failure_kind==='network_error')return 'broken';
  if(Number.isInteger(v.http_status)&&v.http_status>=400&&v.visual_failure_kind==='http_error')return 'broken';
  const mime=String(v.response_mime_type||'').toLowerCase();
  if(v.http_status>=200&&v.http_status<300&&v.visual_failure_kind==='non_image_error_payload'&&
     ['text/html','application/json','application/xml','text/xml'].includes(mime))return 'broken';
  // A 200 image response with positive uncached bytes can still fail decoding.
  // The browser classifier already demands completed zero-width pixels and exact
  // CDP final-request proof. Preserve those guards at the independent census gate.
  if(v.http_status===200&&v.visual_failure_kind==='image_decode_failure'&&
     mime.startsWith('image/')&&Number.isSafeInteger(v.transfer_bytes)&&v.transfer_bytes>0&&
     v.loaded_network_proof_verified===true&&v.network_final_identity_verified===true&&
     v.redirected_image_identity_unverified!==true&&!v.network_failure&&
     sameSource(v.current_src,v.request_url))return 'broken';
 }
 return 'unresolved';
}
function assessPage(x){
 const errors=[];
 if(!x||typeof x!=='object'||Array.isArray(x))return {complete:false,state:'INCOMPLETE',errors:['invalid_page'],expected_image_slots:null,observed_image_slots:0,known_loaded_count:0,known_broken_count:0,unresolved_keys:[],confirmed_broken_count:null};
 const expected=x.stored_image_count,items=Array.isArray(x.stored_images)?x.stored_images:[];
 if(!goodCount(expected))errors.push('invalid_expected_slot_count');
 if(!Array.isArray(x.stored_images)||items.length!==expected)errors.push('stored_slot_count_mismatch');
 if(x.page_result!=='inspected_browser'||x.scroll_coverage?.complete!==true||x.scroll_coverage?.state!=='full_height_scanned')errors.push('page_or_scroll_not_verified');
 const seen=new Set(),unresolved=[];let loaded=0,broken=0;
 for(const v of items){
  const k=v?.image_key;
  if(!key(k)||seen.has(k))errors.push('invalid_or_duplicate_slot_key');
  if(key(k))seen.add(k);
  const p=proofKind(v);
  if(p==='loaded')loaded++;
  else if(p==='broken')broken++;
  else unresolved.push(key(k)?k:'<invalid-key>');
 }
 if(unresolved.length)errors.push('unresolved_image_identity_or_network_evidence');
 const complete=errors.length===0;
 return {complete,state:complete?'COMPLETE':'INCOMPLETE',errors:[...new Set(errors)],
  expected_image_slots:goodCount(expected)?expected:null,observed_image_slots:items.length,
  known_loaded_count:loaded,known_broken_count:broken,unresolved_keys:unresolved,
  confirmed_broken_count:complete?broken:null};
}
function assessRun(pages,requestedPages){
 const errors=[];if(!Array.isArray(pages)||!goodCount(requestedPages)||requestedPages===0||pages.length!==requestedPages)errors.push('requested_page_set_incomplete');
 const seen=new Set(),summaries=[];
 for(const p of (Array.isArray(pages)?pages:[])){
  const id=p?.post_id;
  if(!Number.isSafeInteger(id)||id<=0||seen.has(id))errors.push('invalid_or_duplicate_post_id');
  else seen.add(id);
  const result=assessPage(p);summaries.push({post_id:id??null,...result});
  if(!result.complete)errors.push('post_image_census_incomplete:'+id);
 }
 const complete=errors.length===0;
 const knownBroken=summaries.reduce((n,r)=>n+r.known_broken_count,0);
 return {complete,state:complete?'COMPLETE':'INCOMPLETE',requested_pages:goodCount(requestedPages)?requestedPages:null,
  observed_pages:Array.isArray(pages)?pages.length:0,complete_pages:summaries.filter(x=>x.complete).length,
  known_broken_count:knownBroken,confirmed_broken_count:complete?knownBroken:null,
  unresolved_slot_count:summaries.reduce((n,r)=>n+r.unresolved_keys.length,0),
  errors:[...new Set(errors)],per_page:summaries};
}
module.exports={proofKind,assessPage,assessRun};
