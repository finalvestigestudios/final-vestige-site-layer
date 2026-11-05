'use strict';
/**
 * Offline reconciliation of FV's six priority external-image slots against its EXISTING
 * guest-Chromium probe. This is NOT a probe, network client, downloader or release tool.
 * A third-party retriever wrapper status is never a visitor HTTP status.
 */
const fs=require('node:fs');
const {sameSource}=require('./browser_probe_core.cjs');
const {proofKind}=require('./image_census_coverage_core.cjs');
const ORDER=['285:5','285:2','287:5','418:1','418:2','407:1'];
const safeInt=x=>Number.isSafeInteger(x)&&x>=0;
const validHttps=s=>{try{const u=new URL(s);return u.protocol==='https:'&&!u.username&&!u.password&&!!u.hostname}catch{return false}};
const isObject=x=>!!x&&typeof x==='object'&&!Array.isArray(x);
function sourceRows(early,later){
 if(early?.schema!=='fv-p0-retriever-source-recheck-v1'||early.source_count!==6||
     !Array.isArray(early.rows)||early.rows.length!==6||
     later?.schema!=='fv-media-p0-retriever-two-source-20261105-v1'||
     !Array.isArray(later.rows)||later.rows.length!==2)
   throw Error('Pinned P0 source ledgers required');
 const byKey=new Map();
 for(const r of early.rows){
  if(!ORDER.includes(r.image_key)||byKey.has(r.image_key)||r.post_id!==Number(r.image_key.split(':')[0])||
     r.published_source_read_back_from_wp!==true||!validHttps(r.exact_published_original_url)||
     r.retriever?.guest_browser_http_status!==null||r.retriever?.visitor_broken!==null||
     r.production_write_authorized!==false||r.archival_candidate?.source_authorization_to_cache!==false)
    throw Error('Unsafe original source/rights or fabricated visitor evidence: '+r.image_key);
  byKey.set(r.image_key,{image_key:r.image_key,post_id:r.post_id,original_url:r.exact_published_original_url,
   retriever_wrapper_code:r.retriever?.wrapper_error_code??null,
   retriever_result:r.retriever?.tool_result??null,
   candidate_record:r.archival_candidate?.archive_record_url??null,
   candidate_rights:r.archival_candidate?.rights_review??'HOLD'});
 }
 if(byKey.size!==6)throw Error('Six distinct P0 keys required');
 const followups=new Set();
 for(const r of later.rows){
  if(!['285:5','418:1'].includes(r.image_key)||followups.has(r.image_key)||
      r.post_id!==Number(r.image_key.split(':')[0])||
      !byKey.has(r.image_key)||r.current_published_url_unchanged!==true||
      r.published_url!==byKey.get(r.image_key).original_url||
      r.wrapper_observation?.guest_browser_http_status!==null||
      r.wrapper_observation?.guest_broken!==null||
      r.actions?.wp_upload!==false||r.actions?.publish!==false||
      r.primary_catalog?.cache_authorized_by_workflow!==false)
   throw Error('Follow-up drift or unapproved rights: '+r.image_key);
  followups.add(r.image_key);
  const row=byKey.get(r.image_key);row.retriever_wrapper_code=r.wrapper_observation.wrapper_status??null;
  row.retriever_result=r.wrapper_observation.result??null;
 }
 if(followups.size!==2)throw Error('Missing both final follow-up rows');
 return ORDER.map(k=>byKey.get(k));
}
function pageEvidence(run){
 if(!isObject(run)||run.probe_version<3||!['priority','all'].includes(run.mode)||
    !['390x844','1440x900'].includes(run.viewport)||
    !isObject(run.run_profile)||run.run_profile.cache_disabled!==true||
    run.run_profile.service_worker_bypassed!==true||!Array.isArray(run.pages)||
    !safeInt(run.requested_pages)||run.pages.length!==run.requested_pages||
    !isObject(run.image_census_coverage))return null;
 const map=new Map();
 for(const p of run.pages){
  if(!safeInt(p?.post_id)||map.has(p.post_id))return null;
  map.set(p.post_id,p);
 }
 return map;
}
function validateNetwork(slot,page,kind){
 const net=page.network_images;
 if(!Array.isArray(net)||!isObject(slot)||typeof slot.request_id!=='string'||!slot.request_id||
    !validHttps(slot.request_url)||!validHttps(slot.current_src)||
    !Array.isArray(page.stored_images))return null;
 const matches=net.filter(n=>n?.request_id===slot.request_id);
 if(matches.length!==1)return null;
 const n=matches[0];
 if(n.url!==slot.request_url||!sameSource(slot.current_src,n.url)||
    slot.network_final_identity_verified!==true||slot.redirected_image_identity_unverified===true||
    n.status!==slot.http_status||String(n.mime_type||'').split(';')[0].trim().toLowerCase()!==
       String(slot.response_mime_type||'').split(';')[0].trim().toLowerCase())return null;
 if(kind==='loaded'){
  if(n.status!==200||!/^image\//i.test(n.mime_type||'')||
     !Number.isSafeInteger(n.encoded_data_length)||n.encoded_data_length<=0||
     slot.transfer_bytes!==n.encoded_data_length||n.error||
     n.was_cached!==false||n.from_disk_cache!==false||n.from_service_worker!==false)return null;
 } else if(kind==='broken'){
  if(slot.natural_width!==0)return null;
  const networkFailure=typeof n.error==='string'&&!!n.error.trim()&&
     slot.visual_failure_kind==='network_error'&&n.error===slot.network_failure;
  const httpError=safeInt(n.status)&&n.status>=400&&slot.visual_failure_kind==='http_error';
  const nonImage=n.status>=200&&n.status<300&&
     ['text/html','application/json','application/xml','text/xml'].includes(String(n.mime_type||'').toLowerCase())&&
     slot.visual_failure_kind==='non_image_error_payload';
  const decoding=n.status===200&&/^image\//i.test(n.mime_type||'')&&
     slot.visual_failure_kind==='image_decode_failure'&&safeInt(n.encoded_data_length)&&
     n.encoded_data_length>0&&slot.transfer_bytes===n.encoded_data_length&&
     !n.error&&n.was_cached===false&&n.from_disk_cache===false&&n.from_service_worker===false;
  if(![networkFailure,httpError,nonImage,decoding].some(Boolean))return null;
 } else return null;
 return n;
}
function adjudicate(early,later,run=null){
 const source=sourceRows(early,later),pages=run===null?null:pageEvidence(run);
 const rows=source.map(s=>{
  const base={...s,visitor_classification:'PENDING_GUEST_BROWSER',visitor_http_status:null,
   visitor_request_url:null,visitor_request_id:null,visitor_decode_px:null,visitor_encoded_bytes:null,
   screenshot_proven:false,replacement_authorized:false,wordPress_write_authorized:false,
   media_cache_authorized:false,rights_release:'HOLD',reason:'no_matching_complete_guest_browser_evidence'};
  if(!pages)return base;
  const p=pages.get(s.post_id);
  if(!p||p.page_result!=='inspected_browser'||p.scroll_coverage?.complete!==true||
     p.scroll_coverage.state!=='full_height_scanned'||!Array.isArray(p.stored_images)||
     p.stored_images.length!==p.stored_image_count||!validHttps(p.url)||
     new URL(p.url).hostname!=='finalvestige.com')return {...base,reason:'page_unverified_or_partial'};
  const slots=p.stored_images.filter(v=>v?.image_key===s.image_key);
  if(slots.length!==1)return {...base,reason:'missing_or_duplicate_exact_slot'};
  const v=slots[0],kind=proofKind(v);
  if(v.stored_url!==s.original_url||!sameSource(v.stored_url,v.current_src)||
      !['loaded','broken'].includes(kind))return {...base,reason:'image_identity_or_decode_unresolved'};
  const n=validateNetwork(v,p,kind);
  if(!n)return {...base,reason:'cdp_network_proof_incomplete_or_conflicted'};
  const screenshots=Array.isArray(p.screenshots)?p.screenshots:[];
  const screenshot=screenshots.some(x=>x?.image_key===s.image_key&&x.result==='captured'&&
    x.current_src===v.current_src&&/^broken-\d+-\d+-\d+\.png$/.test(x.filename||''));
  return {...base,visitor_classification:kind==='broken'?'BROWSER_CONFIRMED_BROKEN':'BROWSER_VERIFIED_LOADED',
   visitor_http_status:safeInt(n.status)?n.status:null,visitor_request_url:n.url,
   visitor_request_id:n.request_id,visitor_decode_px:[v.natural_width,v.natural_height],
   visitor_encoded_bytes:safeInt(n.encoded_data_length)?n.encoded_data_length:null,
   screenshot_proven:screenshot,reason:kind==='broken'?'browser_missing_image_proven_rights_and_replacement_still_hold':'browser_image_loaded_no_replacement_needed'};
 });
 const knownBroken=rows.filter(r=>r.visitor_classification==='BROWSER_CONFIRMED_BROKEN').length;
 const knownLoaded=rows.filter(r=>r.visitor_classification==='BROWSER_VERIFIED_LOADED').length;
 const complete=knownBroken+knownLoaded===rows.length;
 return {schema:'fv-p0-guest-disposition-v1',source_count:6,guest_capture_present:run!==null,
   guest_capture_valid:run!==null&&pages!==null,guest_capture_viewport:pages?run.viewport:null,
   p0_census_complete:complete,confirmed_broken_count:complete?knownBroken:null,
   known_broken_slots:knownBroken,known_loaded_slots:knownLoaded,
   reported_42_broken_claim_verified:false,claimed_76_percent_wire_reduction_verified:false,
   replacement_release_authorized:false,production_changes:0,rows};
}
if(require.main===module){
 const args=process.argv.slice(2);
 if(args.length>1){console.error('Usage: node adjudicate_p0_guest_evidence_v1.cjs [existing_browser_probe.json]');process.exitCode=2;}
 else try{
  const dir=__dirname;
  const first=JSON.parse(fs.readFileSync(require('node:path').join(dir,'p0_retriever_source_recheck_20261104.json')));
  const last=JSON.parse(fs.readFileSync(require('node:path').join(dir,'p0_remaining_two_source_wrapper_20261105.json')));
  const run=args.length?JSON.parse(fs.readFileSync(args[0])):null;
  const report=adjudicate(first,last,run);
  console.log(JSON.stringify(report,null,2));
  if(args.length&&!report.p0_census_complete)process.exitCode=2;
 }catch(e){console.error('P0_EVIDENCE_HOLD '+String(e?.message||e));process.exitCode=2;}
}
module.exports={adjudicate,sourceRows,validateNetwork,ORDER};
