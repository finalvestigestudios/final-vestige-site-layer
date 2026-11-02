'use strict';
/** Offline strict wire-byte comparison. No server contact, no claims from originals. */
const {sameSource}=require('./browser_probe_core.cjs');
const {scopeByRequestId}=require('./request_id_wire_core.cjs');
const good=n=>Number.isSafeInteger(n)&&n>0;
const https=u=>typeof u==='string'&&/^https:\/\/[a-z0-9.-]+\//i.test(u);
const page=u=>typeof u==='string'&&/^https:\/\/finalvestige\.com\//.test(u);
function inspectRun(r){
 const e=[],posts=new Map();
 if(!r||typeof r!=='object'||Array.isArray(r))return{ok:false,errors:['invalid_run'],posts};
 if(r.schema_version!==1||r.probe_version!==4)e.push('probe_v4_request_id_proof_required');
 if(r.probe!=='logged-out Chrome CDP, no npm dependencies or WordPress writes')e.push('unrecognized_probe');
 if(!['390x844','1440x900'].includes(r.viewport))e.push('unrecognized_viewport');
 if(typeof r.browser_product!=='string'||!/^Chrome\/\d+\./.test(r.browser_product))e.push('unknown_browser_version');
 const p=r.run_profile;
 if(!p||p.cache_disabled!==true||p.service_worker_bypassed!==true||
    p.scroll_step_px!==720||p.scroll_wait_ms!==220||p.settle_wait_ms!==1000)e.push('cache_scroll_protocol_unverified');
 if(!Number.isFinite(Date.parse(r.created)))e.push('invalid_created_date');
 if(!Array.isArray(r.pages)||r.requested_pages!==r.pages.length||r.verified_pages!==r.requested_pages||!good(r.requested_pages))e.push('incomplete_page_set');
 for(const x of (Array.isArray(r.pages)?r.pages:[])){
  const id=x.post_id;
  if(!good(id)||posts.has(id)){e.push('invalid_or_duplicate_post:'+id);continue}
  if(!page(x.url)||x.document_url!==x.url||x.page_result!=='inspected_browser')e.push('unverified_page:'+id);
  if(!Array.isArray(x.document_network_failures)||x.document_network_failures.length)e.push('page_request_failed:'+id);
  if(x.scroll_coverage?.complete!==true||x.scroll_coverage?.state!=='full_height_scanned')e.push('incomplete_viewport_scroll_coverage:'+id);
  const slots=Array.isArray(x.stored_images)?x.stored_images:[],net=Array.isArray(x.network_images)?x.network_images:[];
  if(slots.length!==x.stored_image_count||!good(x.stored_image_count)||x.rendered_image_count<x.stored_image_count)e.push('incomplete_image_slots:'+id);
  const keys=slots.map(v=>v.image_key);
  if(new Set(keys).size!==keys.length)e.push('duplicate_image_slot:'+id);
  for(const v of slots)if(v.result!=='loaded_in_probe_browser'||v.verified_broken_in_browser!==false||
   !good(v.natural_width)||v.current_src_identity_verified!==true||
   v.network_final_identity_verified!==true||v.loaded_network_proof_verified!==true||
   !['exact_url_or_jetpack_origin','exact_url_unique_alt'].includes(v.match)||
   !sameSource(v.stored_url,v.current_src)||!https(v.current_src)||
   !https(v.request_url)||v.http_status!==200||!good(v.transfer_bytes))
   e.push('unsettled_or_unmeasured:'+id+':'+v.image_key);
  if(!net.length)e.push('no_image_network_log:'+id);
  if(x.article_wire_attribution_mode!=='strict_cdp_request_id'||
   x.article_wire_evidence_complete!==true||
   !Array.isArray(x.article_wire_evidence_errors)||x.article_wire_evidence_errors.length)
   e.push('strict_article_wire_provenance_missing:'+id);
  let total=0,validNetwork=[];
  for(const n of net){
   if(!https(n.url)||n.status!==200||!/^image\//.test(n.mime_type||'')||
      n.error||n.was_cached===true||n.from_disk_cache===true||n.from_service_worker===true||
      !good(n.encoded_data_length)){e.push('invalid_image_response:'+id);continue}
   total+=n.encoded_data_length;
   validNetwork.push(n);
  }
  // Each classified slot must have actual image-network proof of its byte count.
  // Shared network requests may legitimately serve multiple DOM slots.
  for(const v of slots){
   const proof=validNetwork.some(n=>typeof v.request_id==='string'&&
    n.request_id===v.request_id&&
    [n.url,...(Array.isArray(n.url_aliases)?n.url_aliases:[])]
    .some(u=>sameSource(u,v.request_url))&&n.status===v.http_status&&
    n.encoded_data_length===v.transfer_bytes&&sameSource(v.current_src,v.request_url));
   if(!proof)e.push('slot_network_evidence_missing:'+id+':'+v.image_key);
  }
  if(!good(x.image_wire_bytes_total)||total!==x.image_wire_bytes_total)e.push('wire_total_mismatch:'+id);
  // Do not turn decorative image changes into claimed article-photo compression.
  const articleScope=scopeByRequestId(slots,net);
  if(!articleScope.complete||!good(articleScope.article_bytes)||
    x.article_image_wire_bytes_total!==articleScope.article_bytes)
   e.push('article_wire_scope_mismatch:'+id);
  posts.set(id,{url:x.url,keys:keys.sort().join('|'),stored:x.stored_image_count,
    rendered:x.rendered_image_count,bytes:articleScope.article_bytes,
    all_image_bytes:x.image_wire_bytes_total,unattributed_bytes:articleScope.unattributed_bytes,
    // Stored historical media and visible descriptions must remain consistent across runs.
    // A changed CDN currentSrc is permitted, but swapping historical media is not.
    assets:new Map(slots.map(v=>[v.image_key,{source_url:v.stored_url,alt:v.rendered_alt??null}]))});
 }
 return{ok:!e.length,errors:e,posts};
}
function compareWireRuns(before,after){
 const b=inspectRun(before),a=inspectRun(after),errors=[
  ...b.errors.map(x=>'before:'+x),...a.errors.map(x=>'after:'+x)];
 if(!b.ok||!a.ok)return{comparable:false,status:'NOT_COMPARABLE',reasons:errors};
 if(before.viewport!==after.viewport)errors.push('viewport_changed');
 if(before.mode!==after.mode)errors.push('scope_changed');
 if(before.browser_product!==after.browser_product)errors.push('browser_changed');
 if(JSON.stringify(before.run_profile)!==JSON.stringify(after.run_profile))errors.push('protocol_changed');
 if(Date.parse(after.created)<=Date.parse(before.created))errors.push('date_order_invalid');
 if(b.posts.size!==a.posts.size)errors.push('page_count_changed');
 let sumBefore=0,sumAfter=0;const perPost=[];
 for(const [id,x]of b.posts){
  const y=a.posts.get(id);
  if(!y){errors.push('missing_post:'+id);continue}
  if(x.url!==y.url||x.keys!==y.keys||x.stored!==y.stored||x.rendered!==y.rendered)
   errors.push('image_or_article_identity_changed:'+id);
  // A swapped photo or revised historical caption cannot be counted as image compression.
  // Approved content replacement requires a separate provenance/rights-aware comparison.
  for(const [key,original] of x.assets){
   const later=y.assets.get(key);
   if(!later)continue; // Changed-slot gate above already rejects this pair.
   if(original.source_url!==later.source_url)errors.push('stored_asset_changed:'+id+':'+key);
   if(original.alt!==later.alt)errors.push('historical_alt_changed:'+id+':'+key);
  }
  sumBefore+=x.bytes;sumAfter+=y.bytes;
  perPost.push({post_id:id,url:x.url,before_bytes:x.bytes,after_bytes:y.bytes,
   change_bytes:x.bytes-y.bytes,reduction_percent:Math.round(10000*(x.bytes-y.bytes)/x.bytes)/100,
   before_all_page_image_bytes:x.all_image_bytes,after_all_page_image_bytes:y.all_image_bytes,
   before_unattributed_image_bytes:x.unattributed_bytes,after_unattributed_image_bytes:y.unattributed_bytes});
 }
 if(!sumBefore)errors.push('zero_baseline');
 if(errors.length)return{comparable:false,status:'NOT_COMPARABLE',reasons:errors};
 const pct=100*(sumBefore-sumAfter)/sumBefore;
 return{comparable:true,status:'PAIR_ELIGIBLE_FOR_INDEPENDENT_REVIEW',viewport:before.viewport,
  browser:before.browser_product,scope:before.mode,post_count:perPost.length,
  metric:'actual browser encoded network bytes matched to stored article image slots; NOT all page chrome images or WordPress originals',
  before_image_wire_bytes:sumBefore,after_image_wire_bytes:sumAfter,
  delta_bytes:sumBefore-sumAfter,reduction_percent:Math.round(pct*100)/100,
  reaches_76pct_in_pair:pct>=76,per_post:perPost,
  warning:'Not a deployed-site claim. Human HAR, screenshot, license and provenance review required.'};
}
module.exports={inspectRun,compareWireRuns};

