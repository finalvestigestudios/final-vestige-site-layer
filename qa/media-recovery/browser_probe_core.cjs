'use strict';
/** Conservative, offline browser identity classification. URL equivalence is NOT a rights or binary-hash check. */
function clean(u){try{const v=new URL(String(u));return v.protocol==='https:'||v.protocol==='http:'?v.href:null}catch{return null}}
function wikiName(s){try{return decodeURIComponent(s).replaceAll(' ','_')}catch{return null}}
function commonsFile(p){
 const host=p.hostname.toLowerCase(),path=p.pathname;
 if(host==='commons.wikimedia.org'){
  let m=path.match(/^\/wiki\/(?:Special:Redirect\/file\/|File:)(.+)$/);
  if(!m)return null;
  return wikiName(m[1]);
 }
 if(host==='upload.wikimedia.org'){
  // Explicit Commons hash-path only: reject unrelated Wikimedia project or a lookalike host.
  const m=path.match(/^\/wikipedia\/commons\/(thumb\/)?[0-9a-f]\/([0-9a-f]{2})\/([^/]+)(?:\/([^/]+))?$/i);
  if(!m)return null;
  const thumb=!!m[1],original=m[3],variant=m[4];
  if(thumb){
   if(!variant||!/^\d+px-/.test(variant))return null;
   const bare=variant.replace(/^\d+px-/,'');
   // Extension transforms (e.g. SVG->PNG) require their own review.
   if(bare!==original)return null;
  }else if(variant)return null;
  return wikiName(original);
 }
 return null;
}
function contentQuery(p){
 // Preserve query values which may select different archival photos at the same path.
 // Only established image resizing/format knobs are excluded from file identity.
 const transforms=new Set(['width','height','w','h','fit','resize','crop','quality','q','ssl','auto','format','fm']);
 const selectors=[...p.searchParams].filter(([k])=>!transforms.has(k.toLowerCase()));
 return selectors.length?'?'+new URLSearchParams(selectors).toString():'';
}
function imageIdentity(url){
 const u=clean(url);if(!u)return null;
 try{
  const p=new URL(u),host=p.hostname.toLowerCase();
  if(/^i\d?\.wp\.com$/.test(host)){
   const seg=p.pathname.replace(/^\//,'').split('/');
   if(seg.length>1&&seg[0].includes('.'))return imageIdentity('https://'+seg.join('/'));
  }
  const filename=commonsFile(p);
  if(filename)return 'commons-file:'+filename;
  return p.origin+p.pathname+contentQuery(p);
 }catch{return null}
}
function sameSource(a,b){
 const x=imageIdentity(a),y=imageIdentity(b);if(!x||!y)return false;
 if(x===y)return true;
 try{const xa=new URL(x),ya=new URL(y);return xa.origin===ya.origin&&decodeURIComponent(xa.pathname)===decodeURIComponent(ya.pathname)&&xa.search===ya.search}
 catch{return false}
}
function normalizedAlt(t){return String(t||'').toLowerCase().replace(/\s+/g,' ').trim()}
function activeImageIdentity(s,r){
 // DOM src/data-src may retain the original while srcset/lazy-loading displays another asset.
 // Only the actual currentSrc can prove the stored image's decoded identity.
 return !!(r&&typeof r.currentSrc==='string'&&r.currentSrc.trim()&&
   sameSource(s.source_url,r.currentSrc));
}
function renderSrcMatch(s,r){return [r.src,r.currentSrc,r.dataSrc].some(u=>sameSource(s.source_url,u))}
function matchStoredImages(stored,rendered){
 const rows=stored.map(s=>({s,urls:rendered.filter(r=>renderSrcMatch(s,r))}));
 return rows.map(({s,urls})=>{
  if(urls.length>1){
   // ALT disambiguates DOM positions ONLY after each URL independently matches.
   const alt=normalizedAlt(s.alt);
   const candidates=alt?urls.filter(r=>normalizedAlt(r.alt)===alt):[];
   if(candidates.length===1){
    const owners=rows.filter(x=>x.urls.includes(candidates[0])&&normalizedAlt(x.s.alt)===alt);
    if(owners.length===1)return{key:s.key,match:'exact_url_unique_alt',rendered:candidates[0]};
   }
   return{key:s.key,match:'ambiguous_url',rendered:null};
  }
  if(urls.length===1){
   // Distinct stored slots may not reuse one DOM element as two verified image loads.
   const colliders=rows.filter(x=>x.urls.includes(urls[0]));
   if(colliders.length!==1)return{key:s.key,match:'ambiguous_shared_url',rendered:null};
   return{key:s.key,match:'exact_url_or_jetpack_origin',rendered:urls[0]};
  }
  const a=normalizedAlt(s.alt),byAlt=a?rendered.filter(r=>normalizedAlt(r.alt)===a):[];
  if(byAlt.length===1)return{key:s.key,match:'alt_only_unverified',rendered:byAlt[0]};
  return{key:s.key,match:byAlt.length>1?'ambiguous_alt':'unmatched',rendered:null};
 });
}
function classifyImages(stored,rendered,network,pageVerified){
 return matchStoredImages(stored,rendered).map(j=>{
  const r=j.rendered,s=stored.find(x=>x.key===j.key);
  // Never attribute a stale src/data-src request to the decoded currentSrc.
  const req=r&&r.currentSrc&&network.findLast(n=>[n.url,...(n.url_aliases||[])].some(u=>sameSource(u,r.currentSrc)));
  const responseStatus=req&&Number.isInteger(req.status)?req.status:null,reqError=req?.failed_error||null;
  const domMapped=j.match==='exact_url_or_jetpack_origin'||j.match==='exact_url_unique_alt';
  const identityVerified=domMapped&&activeImageIdentity(s,r);
  const visiblyBroken=!!(pageVerified&&r&&identityVerified&&r.complete===true&&r.naturalWidth===0&&(reqError||(responseStatus!==null&&responseStatus>=400)));
  const verifiedLoaded=!!(pageVerified&&r&&identityVerified&&r.complete===true&&r.naturalWidth>0);
  let state='unverified';
  if(!pageVerified)state='page_not_verified';
  else if(!r)state='not_mapped';
  else if(j.match==='alt_only_unverified')state='alt_only_identity_unverified';
  else if(domMapped&&!identityVerified)state='current_src_identity_unverified';
  else if(visiblyBroken)state='confirmed_broken_in_probe_browser';
  else if(verifiedLoaded)state='loaded_in_probe_browser';
  else if(r.complete===true&&r.naturalWidth===0)state='zero_intrinsic_width_needs_review';
  else state='pending_lazy_or_incomplete';
  return{image_key:j.key,match:j.match,stored_url:s.source_url,rendered_src:r?.src||null,
   current_src:r?.currentSrc||null,current_src_identity_verified:identityVerified,complete:r?.complete??null,natural_width:r?.naturalWidth??null,
   request_url:req?.url||null,http_status:responseStatus,network_failure:reqError,
   transfer_bytes:Number.isInteger(req?.encodedDataLength)?req.encodedDataLength:null,
   result:state,verified_broken_in_browser:visiblyBroken?true:verifiedLoaded?false:null};
 });
}
function pageHostVerified(url,title,documentUrl,hasArticle,requestFailed){
 if(requestFailed)return false;
 try{return new URL(documentUrl).hostname==='finalvestige.com'&&new URL(url).pathname===new URL(documentUrl).pathname&&hasArticle&&!/chrome-error|not reachable|not found/i.test(title||'')}
 catch{return false}
}
function countTransfer(network){
 return network.filter(n=>Number.isInteger(n.encodedDataLength)&&n.encodedDataLength>=0).reduce((n,r)=>n+r.encodedDataLength,0);
}
module.exports={imageIdentity,sameSource,matchStoredImages,classifyImages,pageHostVerified,countTransfer};
