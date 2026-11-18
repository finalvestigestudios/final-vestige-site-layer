"use strict";
/** Offline image-wire parity gate. No network requests or WP writes. Approval requires independent trace review. */
const evaluate=function evaluate(report) {
 const errors=[], sums={}; const fail=(s)=>{if(errors.length<100)errors.push(s);};
 const obj=x=>x!==null&&typeof x==="object"&&!Array.isArray(x);
 const https=s=>typeof s==="string"&&/^https:\/\/[A-Za-z0-9.-]+(?::[0-9]+)?(?:[/?#]|$)/.test(s);
 const int=n=>Number.isSafeInteger(n)&&n>0;
 if(!obj(report)||report.schema!=="fv-image-wire-parity-v1")return {gate:"HOLD",errors:["schema"],threshold_met:false,claim_publicly_verified:false};
 const cohort=report.cohort?.id, expected=cohort==="historic-61"?61:cohort==="current-66"?66:report.cohort?.expected_posts;
 if(!["historic-61","current-66","targeted"].includes(cohort)||!int(expected)||expected>1000||(cohort==="targeted"&&expected>=61)) fail("cohort");
 if(!/^[a-f0-9]{64}$/.test(report.manifest_sha256||""))fail("manifest_sha");
 if(report.estimated_bytes===true||report.stored_original_bytes_used===true)fail("not_real_wire");
 function inspect(c,phase,device){
  const tag=phase+"-"+device;
  if(!obj(c)){fail(tag+":capture_missing");return null;}
  if(c.instrument!=="CDP_NETWORK"||c.capture_type!=="GUEST_CHROMIUM"||c.viewport!==device||
     c.cache_disabled!==true||c.service_worker_bypassed!==true||c.complete_image_requests!==true)fail(tag+":control");
  if(!https(c.trace_evidence_url)||!/^[a-f0-9]{64}$/.test(c.trace_sha256||""))fail(tag+":trace");
  if(!Array.isArray(c.pages)||c.pages.length!==expected)fail(tag+":post_coverage");
  let bytes=0,broken=0;const pages=new Map(),requests=new Map();
  for(const p of Array.isArray(c.pages)?c.pages:[]){
   const pid=String(p?.post_id??"");
   if(!/^\d+$/.test(pid)||pages.has(pid)||!https(p.url)){fail(tag+":bad_post");continue;}
   if(p.complete_image_requests!==true||!Array.isArray(p.images)||!p.images.length)fail(tag+":"+pid+":incomplete_images");
   const assets=new Map();
   for(const m of Array.isArray(p.images)?p.images:[]){
    if(!obj(m)||typeof m.asset_id!=="string"||!m.asset_id||assets.has(m.asset_id)){fail(tag+":"+pid+":duplicate_asset");continue;}
    assets.set(m.asset_id,m);
    if(!https(m.authored_src)||!https(m.current_src)||!https(m.final_url)||!https(m.source_identity))fail(tag+":"+pid+":source_url");
    if(!m.request_id||typeof m.request_id!=="string"||m.from_cache!==false||m.from_service_worker!==false||
       m.transfer_metric!=="CDP_ENCODED_DATALENGTH"||!int(m.transfer_bytes))fail(tag+":"+pid+":unmeasured_wire");
    if(!Number.isInteger(m.http_status)||m.http_status<100||m.http_status>599||
       typeof m.mime!=="string"||!m.mime.startsWith("image/"))fail(tag+":"+pid+":response");
    if(typeof m.decoded!=="boolean"||(m.decoded&&(!int(m.natural_width)||!int(m.natural_height)))||
       (!m.decoded&&(m.natural_width!==0||m.natural_height!==0)))fail(tag+":"+pid+":decode_inconsistent");
    if(m.decoded&&(m.http_status<200||m.http_status>=300))fail(tag+":"+pid+":decoded_error");
    if(!m.decoded)broken++;
    if(typeof m.screenshot!=="string"||!m.screenshot.trim())fail(tag+":"+pid+":screenshot");
    if(m.request_id){
      const prev=requests.get(m.request_id);
      if(prev){if(prev.final_url!==m.final_url||prev.http_status!==m.http_status||prev.transfer_bytes!==m.transfer_bytes)fail(tag+":"+pid+":request_collision");}
      else {requests.set(m.request_id,m);if(int(m.transfer_bytes))bytes+=m.transfer_bytes;}
    }
   }
   pages.set(pid,{p,assets});
  }
  return {pages,bytes,broken,requests:requests.size};
 }
 for(const device of ["desktop","mobile"]){
  const b=inspect(report.before?.[device],"before",device),a=inspect(report.after?.[device],"after",device);
  if(!b||!a)continue;
  if(b.pages.size!==a.pages.size)fail(device+":posts_changed");
  for(const [pid,entry] of b.pages){
    const next=a.pages.get(pid);
    if(!next||entry.p.url!==next.p.url){fail(device+":"+pid+":post_drift");continue;}
    if(entry.assets.size!==next.assets.size)fail(device+":"+pid+":asset_count_drift");
    for(const [id,m] of entry.assets){
      const n=next.assets.get(id);
      if(!n){fail(device+":"+pid+":missing_asset");continue;}
      if(n.source_identity!==m.source_identity){
        const ok=n.approval;
        if(!obj(ok)||ok.rights!=="CLEARED"||ok.exact_frame!==true||
           !https(ok.catalog)||!https(ok.license)||!ok.editorial_id||
           !/^[a-f0-9]{64}$/.test(ok.master_sha256||"")||!int(ok.target_width)||ok.target_width>960||ok.no_upscale!==true)
           fail(device+":"+pid+":unapproved_replacement");
      }
      if(n.decoded!==true)fail(device+":"+pid+":broken_after");
    }
    for(const id of next.assets.keys())if(!entry.assets.has(id))fail(device+":"+pid+":unmatched_new_asset");
  }
  sums[device]={before_bytes:b.bytes,after_bytes:a.bytes,request_count_before:b.requests,request_count_after:a.requests,
    broken_before:b.broken,broken_after:a.broken,reduction_percent:b.bytes>0&&a.bytes>0?Math.round((1-a.bytes/b.bytes)*10000)/100:null};
 }
 const sitewide=cohort==="historic-61"||cohort==="current-66";
 const met=errors.length===0&&sitewide&&sums.desktop&&sums.mobile&&
   sums.desktop.reduction_percent>=76&&sums.mobile.reduction_percent>=76;
 return {gate:met?"AWAIT_INDEPENDENT_TRACE_AND_VISUAL_QA":"HOLD",threshold_met:!!met,
   claim_publicly_verified:false,cohort,expected_posts:expected,devices:sums,
   errors:errors.length?errors:(met?["external_trace_authenticity_and_visual_review_pending"]:["threshold_or_sitewide_coverage_not_met"])};
};
module.exports={evaluate};
if(require.main===module){const fs=require("node:fs");if(!process.argv[2]){console.error("Usage: node image_wire_parity_gate_20261118.cjs path/to/existing-site-qa-export.json");process.exit(2);}const result=evaluate(JSON.parse(fs.readFileSync(process.argv[2],"utf8")));process.stdout.write(JSON.stringify(result,null,2)+"\n");if(result.gate!=="AWAIT_INDEPENDENT_TRACE_AND_VISUAL_QA")process.exitCode=1;}
