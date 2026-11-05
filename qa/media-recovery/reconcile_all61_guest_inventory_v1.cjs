'use strict';
/** Offline consumer of the existing Site QA Chromium/CDP collector, NOT a new collector.
 * Refuses site-wide 42-broken or image-weight claims without 61-post, 355-slot proof.
 * Never requests an image, caches media, edits WordPress or authorizes publication.
 */
const isInt=n=>Number.isSafeInteger(n)&&n>=0;
const isURL=u=>{try{const x=new URL(u);return ['https:','http:'].includes(x.protocol)&&!!x.hostname&&!x.username&&!x.password;}catch{return false}};
const samePage=(a,b)=>{try{const x=new URL(a),y=new URL(b);return x.hostname===y.hostname&&x.pathname===y.pathname;}catch{return false}};
const P0=new Set(['285:5','285:2','287:5','418:1','418:2','407:1']);
function census(parts,limits={parts:8,posts:61,images:355}){
 const ps=new Map(),imgs=new Map();
 if(!Array.isArray(parts)||parts.length!==limits.parts)throw Error('inventory_part_count');
 for(const [i,b] of parts.entries()){
  if(b.batch!==i+1||!Array.isArray(b.posts)||b.post_count!==b.posts.length||!Array.isArray(b.images)||b.image_count!==b.images.length)throw Error('inventory_batch_'+i);
  for(const p of b.posts){
   if(!isInt(p.id)||!p.id||ps.has(p.id)||!isURL(p.url)||!isInt(p.images))throw Error('post_identity');
   ps.set(p.id,p);
  }
  for(const v of b.images){
   if(!v||!isInt(v.post_id)||!isInt(v.slot)||v.key!==v.post_id+':'+v.slot||imgs.has(v.key)||
    !isURL(v.source_url)||new URL(v.source_url).hostname.toLowerCase()!==String(v.source_host).toLowerCase()||
    v.actual_http_status!==null||v.broken_in_browser!==null||v.allowed_to_localize!==false||v.target_max_width_px!==960)
     throw Error('source_rights_or_visitor_claim_'+(v?.key??'?'));
   imgs.set(v.key,v);
  }
 }
 if(ps.size!==limits.posts||imgs.size!==limits.images)throw Error('inventory_totals');
 for(const p of ps.values()){
  const ss=[...imgs.values()].filter(v=>v.post_id===p.id);
  if(ss.length!==p.images||ss.some((v,i)=>v.slot!==i||!samePage(v.post_url,p.url)))throw Error('post_slot_integrity_'+p.id);
 }
 for(const v of imgs.values())if(!ps.has(v.post_id))throw Error('unknown_post_ref');
 return {posts:ps,images:imgs};
}
function guestPages(run,posts){
 if(run===null)return {valid:false,reason:'NO_GUEST_CAPTURE',pages:new Map()};
 if(!run||run.probe_version<3||!['all','priority'].includes(run.mode)||
  !['390x844','1440x900'].includes(run.viewport)||run.run_profile?.cache_disabled!==true||
  run.run_profile?.service_worker_bypassed!==true||!Array.isArray(run.pages)||
  run.pages.length!==run.requested_pages||!run.pages.length)
   return {valid:false,reason:'CAPTURE_PROFILE_UNTRUSTED',pages:new Map()};
 const pages=new Map();
 for(const p of run.pages){
  if(!p||!posts.has(p.post_id)||pages.has(p.post_id)||!samePage(p.url,posts.get(p.post_id).url)||
   p.page_result!=='inspected_browser'||p.scroll_coverage?.complete!==true||
   p.scroll_coverage?.state!=='full_height_scanned'||!Array.isArray(p.stored_images)||
   !Array.isArray(p.network_images)||p.stored_images.length!==p.stored_image_count||
   p.stored_image_count!==posts.get(p.post_id).images)
    return {valid:false,reason:'PAGE_OR_SOURCE_DRIFT',pages:new Map()};
  pages.set(p.post_id,p);
 }
 return {valid:true,reason:'CAPTURE_STRUCTURE_ACCEPTED',pages};
}
function checkSlot(v,p,source){
 const hold=k=>({kind:null,code:k,http:null,bytes:null,id:null});
 if(!v||v.image_key!==source.key||v.stored_url!==source.source_url||
  v.complete!==true||v.current_src_identity_verified!==true||
  v.network_final_identity_verified!==true||v.redirected_image_identity_unverified===true||
  !isURL(v.current_src)||!isURL(v.request_url)||!v.request_id||
  !isInt(v.natural_width)||!isInt(v.natural_height))return hold('SLOT_IDENTITY_UNVERIFIED');
 const matching=p.network_images.filter(n=>n?.request_id===v.request_id);
 if(matching.length!==1)return hold('CDP_REQUEST_AMBIGUOUS');
 const n=matching[0],mime=String(n.mime_type||'').split(';')[0].trim().toLowerCase();
 if(n.url!==v.request_url||n.status!==v.http_status||
   mime!==String(v.response_mime_type||'').split(';')[0].trim().toLowerCase()||
   n.encoded_data_length!==v.transfer_bytes||n.was_cached!==false||
   n.from_disk_cache!==false||n.from_service_worker!==false)
    return hold('CDP_CONFLICT_OR_CACHE');
 const bytes=isInt(n.encoded_data_length)?n.encoded_data_length:null;
 const loaded=v.result==='loaded_in_probe_browser'&&v.verified_broken_in_browser===false&&
  v.loaded_network_proof_verified===true&&v.natural_width>0&&v.natural_height>0&&
  n.status===200&&mime.startsWith('image/')&&bytes>0&&!n.error;
 const broken=v.result==='confirmed_broken_in_probe_browser'&&v.verified_broken_in_browser===true&&
  v.natural_width===0&&v.natural_height===0&&(
   (typeof n.error==='string'&&!!n.error.trim()&&v.network_failure===n.error&&v.visual_failure_kind==='network_error')||
   (isInt(n.status)&&n.status>=400&&v.visual_failure_kind==='http_error')||
   (n.status>=200&&n.status<300&&['text/html','application/json','application/xml','text/xml'].includes(mime)&&v.visual_failure_kind==='non_image_error_payload')||
   (n.status===200&&mime.startsWith('image/')&&bytes>0&&!n.error&&v.visual_failure_kind==='image_decode_failure'));
 const screenshot=Array.isArray(p.screenshots)&&p.screenshots.some(s=>
   s.image_key===source.key&&s.result==='captured'&&s.current_src===v.current_src&&
   /^broken-\d+-\d+-\d+\.png$/.test(s.filename||''));
 if(!loaded&&!(broken&&screenshot))return hold(broken?'MISSING_BROKEN_SCREENSHOT':'IMAGE_EVIDENCE_UNRESOLVED');
 return {kind:loaded?'loaded':'broken',code:loaded?'BROWSER_VERIFIED_LOADED':'BROWSER_CONFIRMED_BROKEN',
   http:isInt(n.status)?n.status:null,bytes,id:v.request_id};
}
function reconcile(parts,run=null,limits={parts:8,posts:61,images:355}){
 const inv=census(parts,limits),cap=guestPages(run,inv.posts),rows=[],charged=new Set();
 let loaded=0,broken=0,byteTotal=0;
 for(const v of inv.images.values()){
  const p=cap.valid?cap.pages.get(v.post_id):null;
  const matching=p?p.stored_images.filter(s=>s?.image_key===v.key):[];
  const j=p?(matching.length===1?checkSlot(matching[0],p,v):
    {kind:null,code:'STORED_SLOT_MISSING_OR_DUPLICATE',http:null,bytes:null,id:null}):
    {kind:null,code:'PENDING_GUEST_BROWSER',http:null,bytes:null,id:null};
  if(j.kind==='loaded'){
   loaded++;const key=v.post_id+':'+j.id;
   if(!charged.has(key)){byteTotal+=j.bytes;charged.add(key);}
  }
  if(j.kind==='broken')broken++;
  rows.push({key:v.key,post_id:v.post_id,post_url:v.post_url,original_url:v.source_url,
    original_source_host:v.source_host,origin_class:v.source_kind,p0:P0.has(v.key),
    browser_verdict:j.code,actual_browser_http_status:j.http,
    actual_cdp_encoded_data_length:j.bytes,cdp_request_id:j.id,
    html_width:v.width_px??null,html_height:v.height_px??null,
    archival_rights:'HOLD',max_derivative_width:960,no_upscale:true,
    caching_authorized:false,wp_edit_authorized:false});
 }
 const full=cap.valid&&cap.pages.size===inv.posts.size&&loaded+broken===inv.images.size;
 return {schema:'fv-all61-frozen-source-guest-evidence-gate-v1',
  reference_snapshot:'2026-10-30 Gutenberg source inventory; not a fresh live census',
  sitewide_browser_verification_complete:full,
  totals:{published_posts:inv.posts.size,image_slots:inv.images.size,
   distinct_exact_urls:new Set(rows.map(x=>x.original_url)).size,
   guest_capture_present:run!==null,valid_capture_profile:cap.valid,
   capture_reason:cap.reason,guest_pages:cap.pages.size,
   verified_loaded:loaded,verified_broken:broken,unverified:rows.length-loaded-broken,
   sitewide_confirmed_broken:full?broken:null,
   reported_42_broken_confirmed:full&&broken===42,
   cold_article_image_encoded_bytes:full&&broken===0?byteTotal:null,
   reported_76_pct_reduction_verified:false,production_repairs:0},rows};
}
module.exports={census,guestPages,checkSlot,reconcile};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),args=process.argv.slice(2);
 try{
  const opt=k=>{const i=args.indexOf(k);return i<0?null:args[i+1]};
  const dir=opt('--inventory-dir');if(!dir)throw Error('usage: --inventory-dir DIR [--guest capture.json] [--output result.json]');
  const parts=Array.from({length:8},(_,i)=>JSON.parse(fs.readFileSync(path.join(dir,'parts',String(i+1).padStart(2,'0')+'.json'))));
  const g=opt('--guest'),report=reconcile(parts,g?JSON.parse(fs.readFileSync(g)):null),out=opt('--output'),s=JSON.stringify(report,null,2)+'\n';
  if(out)fs.writeFileSync(out,s);else process.stdout.write(s);
  if(g&&!report.sitewide_browser_verification_complete)process.exitCode=2;
 }catch(e){console.error('MEDIA_CENSUS_HOLD '+e.message);process.exitCode=2;}
}
