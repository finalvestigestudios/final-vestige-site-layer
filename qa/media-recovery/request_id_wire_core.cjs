'use strict';
/**
 * Savings-grade article-photo bytes from the exact CDP request that was bound to
 * each decoded DOM image. Offline and fail-closed: no HTTP or CMS operations.
 *
 * Canonical URL matching alone is insufficient: a theme/logo, preload, retry,
 * or a different responsive image request may share the same normalized URL.
 * CDP requestId is stable through redirects; repeated DOM uses of one request
 * are counted once. An extra same-photo network request not bound to any DOM
 * slot makes article-only transfer attribution unknown, not "optimized".
 */
const {sameSource}=require('./browser_probe_core.cjs');
const isId=x=>typeof x==='string'&&x.length>0&&x.length<=128&&!/\s/.test(x);
const bytes=x=>Number.isSafeInteger(x)&&x>0;
const identity=(a,b)=>typeof a==='string'&&typeof b==='string'&&sameSource(a,b);
function scopeByRequestId(slots,network){
 const errors=[],seenKeys=new Set(),byId=new Map(),bound=new Set();
 let unmeasured=0,unattributed=0;
 if(!Array.isArray(slots)||!slots.length)errors.push('article_slots_missing');
 if(!Array.isArray(network)||!network.length)errors.push('image_network_log_missing');
 for(const n of (Array.isArray(network)?network:[])){
  if(!n||!isId(n.request_id)){errors.push('network_request_id_missing');continue}
  if(byId.has(n.request_id)){errors.push('duplicate_network_request_id');continue}
  byId.set(n.request_id,n);
 }
 for(const v of (Array.isArray(slots)?slots:[])){
  if(!v||typeof v.image_key!=='string'||seenKeys.has(v.image_key)){
   errors.push('duplicate_or_missing_image_key');continue;
  }
  seenKeys.add(v.image_key);
  if(v.result!=='loaded_in_probe_browser'||v.verified_broken_in_browser!==false||
    !['exact_url_or_jetpack_origin','exact_url_unique_alt'].includes(v.match)||
    v.current_src_identity_verified!==true||v.network_final_identity_verified!==true||
    v.loaded_network_proof_verified!==true||v.redirected_image_identity_unverified===true||
    !identity(v.stored_url,v.current_src)||!identity(v.current_src,v.request_url)||
    !Number.isSafeInteger(v.natural_width)||v.natural_width<=0||
    !Number.isSafeInteger(v.natural_height)||v.natural_height<=0||
    v.http_status!==200||!bytes(v.transfer_bytes)||
    typeof v.response_mime_type!=='string'||!/^image\//i.test(v.response_mime_type)){
   errors.push('slot_not_network_verified:'+v.image_key);continue;
  }
  if(!isId(v.request_id)){errors.push('slot_request_id_missing:'+v.image_key);continue}
  const n=byId.get(v.request_id);
  if(!n){errors.push('slot_request_id_not_found:'+v.image_key);continue}
  if(!identity(v.request_url,n.url)||!identity(v.current_src,n.url)||
    n.status!==200||typeof n.mime_type!=='string'||!/^image\//i.test(n.mime_type)||
    // Missing cache flags never prove a cold transfer, and the CDP MIME
    // must agree with the decoded DOM image response before counting bytes.
    n.error||n.was_cached!==false||n.from_disk_cache!==false||
    n.from_service_worker!==false||!bytes(n.encoded_data_length)||
    String(v.response_mime_type).split(';')[0].trim().toLowerCase()!==
      String(n.mime_type).split(';')[0].trim().toLowerCase()||
    v.transfer_bytes!==n.encoded_data_length){
   errors.push('slot_cdp_response_mismatch:'+v.image_key);unmeasured++;continue;
  }
  bound.add(v.request_id);
 }
 // Never silently assign an extra request with the same canonical photo to the
 // article. It could be a page-chrome duplicate, speculative preload or old srcset.
 // Report unknown until the extra request has independent element attribution.
 for(const n of (Array.isArray(network)?network:[])){
  if(!n||bound.has(n.request_id))continue;
  const possiblyArticle=(Array.isArray(slots)?slots:[]).some(s=>
   s&&(identity(s.current_src,n.url)||identity(s.request_url,n.url)||
      (Array.isArray(n.url_aliases)&&n.url_aliases.some(u=>identity(s.current_src,u)))));
  if(possiblyArticle)errors.push('unbound_same_photo_request');
  else if(Number.isSafeInteger(n.encoded_data_length)&&n.encoded_data_length>=0)
   unattributed+=n.encoded_data_length;
 }
 const sum=[...bound].reduce((n,id)=>n+byId.get(id).encoded_data_length,0);
 const reasons=[...new Set(errors)];
 return{article_bytes:reasons.length?null:sum,
  complete:reasons.length===0,reasons,
  matched_request_count:bound.size,unmeasured_article_requests:unmeasured,
  unverified_slot_count:Array.isArray(slots)?slots.length-seenKeys.size:0,
  unattributed_bytes:unattributed,
  attribution_mode:'strict_cdp_request_id'};
}
module.exports={scopeByRequestId};
