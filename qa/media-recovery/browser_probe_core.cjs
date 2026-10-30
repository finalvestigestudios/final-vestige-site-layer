'use strict';
/** Conservative classification: a viewer 403 or an absent stored image is NOT a broken browser image. */
function clean(u){try{return new URL(String(u)).href}catch{return null}}
function imageIdentity(url){
 const u=clean(url);if(!u)return null;
 try{const p=new URL(u);const host=p.hostname.toLowerCase();
  if(/^i\d?\.wp\.com$/.test(host)){
   const segments=p.pathname.replace(/^\//,'').split('/');
   if(segments.length>1&&segments[0].includes('.'))return clean('https://'+segments.join('/'));
  }
  return p.origin+p.pathname;
 }catch{return null}
}
function normalizedAlt(t){return String(t||'').toLowerCase().replace(/\s+/g,' ').trim()}
function sameSource(a,b){
 const x=imageIdentity(a),y=imageIdentity(b);if(!x||!y)return false;
 if(x===y)return true;
 try{const xa=new URL(x),ya=new URL(y);return xa.hostname===ya.hostname&&decodeURIComponent(xa.pathname)===decodeURIComponent(ya.pathname)}
 catch{return false}
}
function matchStoredImages(stored,rendered){
 return stored.map(s=>{
  const byUrl=rendered.filter(r=>[r.src,r.currentSrc,r.dataSrc].some(u=>sameSource(s.source_url,u)));
  if(byUrl.length===1)return{key:s.key,match:'exact_url_or_jetpack_origin',rendered:byUrl[0]};
  if(byUrl.length>1)return{key:s.key,match:'ambiguous_url',rendered:null};
  const a=normalizedAlt(s.alt),byAlt=a?rendered.filter(r=>normalizedAlt(r.alt)===a):[];
  if(byAlt.length===1)return{key:s.key,match:'alt_only_unverified',rendered:byAlt[0]};
  return{key:s.key,match:byAlt.length>1?'ambiguous_alt':'unmatched',rendered:null};
 });
}
function classifyImages(stored,rendered,network,pageVerified){
 return matchStoredImages(stored,rendered).map(j=>{
  const r=j.rendered,s=stored.find(x=>x.key===j.key);
  const req=r&&network.findLast(n=>[n.url,...(n.url_aliases||[])].some(u=>sameSource(u,r.currentSrc||r.src)||sameSource(u,r.src)));
  const responseStatus=req&&Number.isInteger(req.status)?req.status:null,reqError=req?.failed_error||null;
  const visiblyBroken=!!(pageVerified&&r&&j.match!=='alt_only_unverified'&&r.complete===true&&r.naturalWidth===0&&(reqError||(responseStatus!==null&&responseStatus>=400)));
  const verifiedLoaded=!!(pageVerified&&r&&r.complete===true&&r.naturalWidth>0);
  let state='unverified';
  if(!pageVerified)state='page_not_verified';
  else if(!r)state='not_mapped';
  else if(visiblyBroken)state='confirmed_broken_in_probe_browser';
  else if(verifiedLoaded)state='loaded_in_probe_browser';
  else if(r.complete===true&&r.naturalWidth===0)state='zero_intrinsic_width_needs_review';
  else state='pending_lazy_or_incomplete';
  return{image_key:j.key,match:j.match,stored_url:s.source_url,rendered_src:r?.src||null,
   current_src:r?.currentSrc||null,complete:r?.complete??null,natural_width:r?.naturalWidth??null,
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
