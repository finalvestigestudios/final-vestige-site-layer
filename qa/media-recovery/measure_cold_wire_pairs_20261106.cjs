'use strict';
// Offline comparator of explicit *guest-browser* image transfer observations.
// No network collection, WordPress modifications, image copying, or caching.
const HTTPS=/^https:\/\/[^\s/?#@]+(?:\/[^\s]*)?$/i;
function url(x){return typeof x==='string'&&x.length<4096&&HTTPS.test(x);}
function equal(a,b){return JSON.stringify(a)===JSON.stringify(b);}
function evaluate(input){
 const errors=[],check=(v,m)=>{if(!v)errors.push(m);};
 if(!input||typeof input!=='object')return {ok:false,errors:['missing evidence'],measured:null};
 check(input.schema==='fv-cold-image-wire-pairs-v1','schema');
 check([61,66].includes(input.published_cohort_size),'cohort size must be 61 or 66');
 const pages=input.expected_page_urls,pairs=input.pairs;
 check(Array.isArray(pages)&&pages.length>0&&pages.length<=66,'expected page count');
 check(Array.isArray(pairs)&&pairs.length>0&&pairs.length<=66,'pairs count');
 if(!Array.isArray(pages)||!Array.isArray(pairs))return {ok:false,errors,measured:null};
 check(pages.every(url)&&new Set(pages).size===pages.length,'unique HTTPS pages');
 check(pairs.length===pages.length,'one pair per expected page');
 const seen=new Set(),perPage=[],envKeys=['browser','browser_version','device_profile','viewport_width','viewport_height','dpr','network_profile'];
 let beforeTotal=0,afterTotal=0,requestsTotal=0;
 function read(run,page,side){
  const prefix=page+' '+side;
  if(!run||typeof run!=='object'){errors.push(prefix+' missing capture');return null;}
  for(const k of ['guest_browser_verified','cache_disabled','service_worker_bypassed','scrolled_to_bottom','all_images_loaded','capture_complete'])check(run[k]===true,prefix+' '+k);
  for(const k of envKeys)check(run[k]!==undefined&&run[k]!==null,prefix+' '+k);
  for(const k of ['browser','browser_version','device_profile','network_profile'])check(typeof run[k]==='string'&&run[k].length>0,prefix+' valid '+k);
  for(const k of ['viewport_width','viewport_height'])check(Number.isInteger(run[k])&&run[k]>=1&&run[k]<=8192,prefix+' valid '+k);
  check(typeof run.dpr==='number'&&Number.isFinite(run.dpr)&&run.dpr>=0.5&&run.dpr<=5,prefix+' valid dpr');
  check(typeof run.captured_at==='string'&&!Number.isNaN(Date.parse(run.captured_at)),prefix+' timestamp');
  const reqs=run.image_requests,dom=run.dom_images;
  const empty=run.zero_image_page_verified===true;
  check(Array.isArray(reqs)&&reqs.length<=500&&(reqs.length>0||empty),prefix+' network requests / empty attestation');
  check(Array.isArray(dom)&&dom.length<=500&&(dom.length>0||empty),prefix+' DOM images / empty attestation');
  if(Array.isArray(reqs)&&Array.isArray(dom))check((reqs.length===0)===(dom.length===0),prefix+' zero-image capture mismatch');
  if(!Array.isArray(reqs)||!Array.isArray(dom))return null;
  let bytes=0,source=null;const urls=new Set(),slots=new Set();
  for(const [i,r] of reqs.entries()){
   const name=prefix+' request '+i;
   if(!r||typeof r!=='object'){errors.push(name+' missing');continue;}
   check(url(r.url),name+' image URL');
   check(r.status===200,name+' browser HTTP 200 required (failure belongs in separate defect report)');
   check(r.from_cache===false,name+' cache hit');
   check(['image/jpeg','image/png','image/webp','image/avif','image/gif','image/svg+xml'].includes(r.content_type),name+' image MIME');
   check(Number.isSafeInteger(r.wire_bytes)&&r.wire_bytes>0,name+' observed positive wire bytes');
   check(['chrome_har_entry_transferSize','cdp_loadingFinished_encodedDataLength'].includes(r.wire_source),name+' genuine browser wire source');
   if(source===null)source=r.wire_source;else check(source===r.wire_source,name+' mixed byte source');
   check(!urls.has(r.url),name+' duplicate image URL; capture independent request IDs instead');
   urls.add(r.url);if(Number.isSafeInteger(r.wire_bytes)&&r.wire_bytes>0)bytes+=r.wire_bytes;
  }
  for(const [i,d] of dom.entries()){
   const name=prefix+' DOM '+i;
   if(!d||typeof d!=='object'){errors.push(name+' missing');continue;}
   check(typeof d.slot==='string'&&/^\d+:\d+$/.test(d.slot),name+' post:image slot');
   check(!slots.has(d.slot),name+' duplicate slot');
   slots.add(d.slot);
   check(url(d.current_src)&&urls.has(d.current_src),name+' network/DOM mismatch');
   check(d.complete===true&&Number.isInteger(d.natural_width)&&d.natural_width>0&&Number.isInteger(d.natural_height)&&d.natural_height>0,name+' failed decode');
  }
  requestsTotal+=reqs.length;
  return {bytes,source,slots:[...slots].sort(),env:envKeys.map(k=>run[k])};
 }
 for(const [i,p] of pairs.entries()){
  if(!p||typeof p!=='object'){errors.push('missing pair '+i);continue;}
  check(url(p.page_url)&&pages.includes(p.page_url),'pair '+i+' unexpected URL');
  check(!seen.has(p.page_url),'pair '+i+' duplicate');
  seen.add(p.page_url);
  const before=read(p.before,p.page_url,'before'),after=read(p.after,p.page_url,'after');
  if(before&&after){
   check(equal(before.env,after.env),p.page_url+' changed browser/viewport/network');
   check(equal(before.slots,after.slots),p.page_url+' changed DOM image coverage');
   check(before.source===after.source,p.page_url+' incompatible wire byte methods');
   beforeTotal+=before.bytes;afterTotal+=after.bytes;
   perPage.push({page_url:p.page_url,before_wire_bytes:before.bytes,after_wire_bytes:after.bytes});
  }
 }
 check(seen.size===pages.length&&pages.every(p=>seen.has(p)),'unobserved published URLs');
 check(beforeTotal>0&&afterTotal>0,'zero transferred bytes across entire cohort');
 if(errors.length)return {ok:false,errors,measured:null,sitewide_claim_allowed:false};
 const percentage=Math.round((1-afterTotal/beforeTotal)*10000)/100;
 const sitewide=pages.length===input.published_cohort_size;
 return {ok:true,errors:[],measured:{basis:'sum of complete cold-browser image network bytes, equally configured per-page loads, UNWEIGHTED by visits',before_wire_bytes:beforeTotal,after_wire_bytes:afterTotal,saved_wire_bytes:beforeTotal-afterTotal,saving_percent:percentage,total_image_network_requests:requestsTotal,pages:perPage},sitewide_claim_allowed:sitewide,claim_76_percent_supported:sitewide&&percentage>=76,reason:sitewide?'complete published cohort':'sample only; no site-wide saving claim'};
}
if(typeof module!=='undefined')module.exports={evaluate};
if(typeof require==='function'&&require.main===module){
 const fs=require('node:fs');if(process.argv.length!==3){console.error('Usage: node measure_cold_wire_pairs_20261106.cjs EVIDENCE.json');process.exit(2);}
 const result=evaluate(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));
 console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1;
}