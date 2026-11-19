'use strict';
// Supplement to #154's existing browser collector and image-wire inline gate.
// No network, WordPress, download, rewriting, or publication side effects.
const https=u=>typeof u==='string'&&/^https:\/\/[^/?#\s]+(?:[/?#]|$)/.test(u);
const safe=n=>Number.isSafeInteger(n)&&n>=0;
const okHash=s=>typeof s==='string'&&/^[a-f0-9]{64}$/.test(s);
const isObj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const imageMime=m=>typeof m==='string'&&/^image\/[a-z0-9.+-]+$/i.test(m);
function evaluateTotalImageWire(inline, full){
 const errors=[], totals={}, add=s=>{if(errors.length<100)errors.push(s);};
 if(!isObj(inline)||inline.schema!=='fv-image-wire-parity-v1'||
    !isObj(full)||full.schema!=='fv-cdp-all-image-requests-v1')
   return {gate:'HOLD',errors:['schema'],threshold_met:false,claim_publicly_verified:false};
 const cohort=inline.cohort?.id;
 if(!['historic-61','current-66'].includes(cohort)||full.cohort_id!==cohort||
    !okHash(inline.manifest_sha256)||full.manifest_sha256!==inline.manifest_sha256)
   add('cohort_or_manifest');
 const expected=cohort==='historic-61'?61:cohort==='current-66'?66:0;
 for(const device of ['desktop','mobile']){
   totals[device]={before_bytes:0,after_bytes:0,other_image_requests_before:0,
     other_image_requests_after:0,broken_before:0,broken_after:0};
   for(const phase of ['before','after']){
     const tag=phase+'-'+device;
     const c=inline[phase]?.[device], n=full[phase]?.[device];
     if(!isObj(c)||!isObj(n)||!Array.isArray(c.pages)||!Array.isArray(n.pages)||
        c.pages.length!==expected||n.pages.length!==expected||
        !okHash(c.trace_sha256)||n.trace_sha256!==c.trace_sha256||
        n.trace_evidence_url!==c.trace_evidence_url){add(tag+':capture_or_trace');continue;}
     const official=new Map();
     for(const page of c.pages){
       const k=String(page?.post_id??'');
       if(!/^\d+$/.test(k)||official.has(k)||!https(page.url)||!Array.isArray(page.images)){
         add(tag+':inline_page');continue;
       }
       official.set(k,page);
     }
     const seen=new Set(); let bytes=0,extra=0,broken=0;
     for(const page of n.pages){
       const pid=String(page?.post_id??''), p=official.get(pid);
       if(!p||seen.has(pid)||page.url!==p.url||page.complete_image_requests!==true||
          page.cdp_image_events_complete!==true||!Array.isArray(page.image_requests)||
          !safe(page.cdp_image_request_count)||page.image_requests.length!==page.cdp_image_request_count){
         add(tag+':page_or_event_coverage');continue;
       }
       seen.add(pid);
       const ids=new Map();
       for(const r of page.image_requests){
         if(!isObj(r)||typeof r.request_id!=='string'||!r.request_id||ids.has(r.request_id)||
           r.resource_type!=='Image'||!https(r.final_url)||!Number.isInteger(r.http_status)||
           r.http_status<200||r.http_status>599||r.from_cache!==false||
           r.from_service_worker!==false||r.transfer_metric!=='CDP_ENCODED_DATALENGTH'||
           !safe(r.transfer_bytes)||typeof r.decoded!=='boolean'){
           add(tag+':invalid_or_duplicate_image_event');continue;
         }
         ids.set(r.request_id,r);
         const success=r.http_status>=200&&r.http_status<300&&imageMime(r.mime);
         const failure=r.http_status>=400&&r.decoded===false;
         if(!(success||failure)||(success&&r.transfer_bytes===0)||
            (phase==='after'&&r.decoded===false))add(tag+':unusable_image_event');
         if(failure)broken++;
         if(success){
           bytes+=r.transfer_bytes;
           if(!Number.isSafeInteger(bytes))add(tag+':unsafe_total');
         }
       }
       const inlineIds=new Set();
       for(const m of p.images){
         const r=ids.get(m?.request_id);
         if(!r||r.final_url!==m.final_url||r.http_status!==m.http_status||
            r.mime!==m.mime||r.transfer_bytes!==m.transfer_bytes||r.decoded!==m.decoded||
            r.from_cache!==m.from_cache||r.from_service_worker!==m.from_service_worker){
           add(tag+':inline_to_cdp_mismatch');continue;
         }
         inlineIds.add(m.request_id);
       }
       extra+=ids.size-inlineIds.size;
     }
     if(seen.size!==official.size)add(tag+':missing_pages');
     totals[device][phase+'_bytes']=bytes;
     totals[device]['other_image_requests_'+phase]=extra;
     totals[device]['broken_'+phase]=broken;
   }
 }
 const meets=d=>safe(d.before_bytes)&&d.before_bytes>0&&safe(d.after_bytes)&&
   100n*BigInt(d.after_bytes)<=24n*BigInt(d.before_bytes);
 const met=errors.length===0&&expected>0&&meets(totals.desktop)&&meets(totals.mobile);
 return {gate:met?'AWAIT_INDEPENDENT_TRACE_AND_VISUAL_QA':'HOLD',threshold_met:met,
   claim_publicly_verified:false,scope:'ALL_CDP_IMAGE_REQUESTS_IN_ARTICLE_NAVIGATION',cohort,
   totals,errors:errors.length?errors:(met?['independent_trace_authenticity_and_visual_review_pending']:['total_image_byte_threshold_not_met'])};
}
module.exports={evaluateTotalImageWire};
