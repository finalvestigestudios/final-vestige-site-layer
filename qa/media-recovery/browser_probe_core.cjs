'use strict';
/** Conservative, offline browser identity classification. URL equivalence is NOT a rights or binary-hash check. */
const {isFormatSensitive,materialSelectors}=require('./format_variant_identity_core_20261104.cjs');
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
function contentQuery(p,viaJetpack=false){
 // Static-image transform names are NOT globally equivalent to size-only changes.
 // WP Site Accelerator documents ?fit=W,H as aspect-preserving; imgix and other
 // CDNs use ?fit=crop|smart-crop|facearea to discard historical photo content.
 // Only trust numeric W,H fit on a Jetpack proxy or our WP uploads host.
 const staticImage=/\.(?:jpe?g|png|webp|gif|svg|avif|bmp|tiff?)$/i.test(p.pathname);
 const wpManaged=viaJetpack||(p.hostname==='finalvestige.com'&&
   p.pathname.startsWith('/wp-content/uploads/'));
 const fits=[...p.searchParams].filter(([k])=>k.toLowerCase()==='fit').map(([,v])=>v);
 const safeNumericFit=wpManaged&&fits.length===1&&/^\d{1,5},\d{1,5}$/.test(fits[0]);
 const keys=new Set([...p.searchParams].map(([k])=>k.toLowerCase()));
 // Some CDNs crop whenever BOTH axes are supplied, even without fit=crop.
 // Preserve those dimensions. Width-only image scaling can remain equivalent.
 const twoAxes=(keys.has('w')||keys.has('width'))&&(keys.has('h')||keys.has('height'));
 const mayChangeComposition=twoAxes||(fits.length>0&&!safeNumericFit);
 const sizeOnly=new Set(['quality','q','ssl']);
 // Do not equate a lossy or rasterized rendering of archival diagrams, GIFs
 // or SVGs with the original: animation, transparency or line detail may differ.
 if(!isFormatSensitive(p.pathname))for(const k of ['auto','format','fm'])sizeOnly.add(k);
 if(!mayChangeComposition){
  for(const key of ['width','height','w','h']){
   const values=[...p.searchParams].filter(([k])=>k.toLowerCase()===key).map(([,v])=>v);
   // Real-world Drupal image style URLs use h=3e6ca723 as a crop/style
   // identity hash, NOT a pixel height. Unknown or mixed values are selectors.
   if(values.length&&values.every(v=>/^[1-9]\d{0,5}$/.test(v)))sizeOnly.add(key);
  }
 }
 if(safeNumericFit)sizeOnly.add('fit');
 // Retain all other selectors, including resize=, crop=, VersionId= and
 // source identifiers. A resulting false negative must be reviewed—not fixed
 // by weakening archival provenance.
 const navyRendition=p.hostname==='www.history.navy.mil'&&p.pathname==='/bin/imageDownload';
 const selectors=[...p.searchParams].filter(([k])=>
   !(staticImage&&sizeOnly.has(k.toLowerCase()))&&
   !(navyRendition&&k.toLowerCase()==='rendition'));
 return selectors.length?'?'+new URLSearchParams(selectors).toString():'';
}
function imageIdentity(url,viaJetpack=false){
 const u=clean(url);if(!u)return null;
 try{
  const p=new URL(u),host=p.hostname.toLowerCase();
  if(/^i\d?\.wp\.com$/.test(host)){
   const seg=p.pathname.replace(/^\//,'').split('/');
   if(seg.length>1&&seg[0].includes('.')){
    // A Jetpack proxy wraps the source URL. Dropping ALL its query parameters can
    // collapse dynamic image selectors (image=, file=, id=) or material crops into
    // a different historical photograph. Only ssl= is unambiguously proxy-only.
    // For static images, contentQuery() independently drops resize-only knobs.
    const q=new URLSearchParams([...p.searchParams].filter(([k])=>k.toLowerCase()!=='ssl')).toString();
    return imageIdentity('https://'+seg.join('/')+(q?'?'+q:''),true);
   }
  }
  const filename=commonsFile(p);
  if(filename){
   // Commons title canonicalization also needs to retain explicit output-format
   // transformations for sensitive source files, not only the filename.
   const material=materialSelectors(filename,p.searchParams);
   return 'commons-file:'+filename+(material.length?'?'+new URLSearchParams(material).toString():'');
  }
  return p.origin+p.pathname+contentQuery(p,viaJetpack);
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
  // When the same canonical image has multiple CDP Image requests, URL matching
  // cannot prove which response belongs to the decoded DOM element. Never use
  // findLast(): a retry, preload or theme copy might have the opposite status.
  const matchingRequests=r?.currentSrc?network.filter(n=>
   [n.url,...(n.url_aliases||[])].some(u=>sameSource(u,r.currentSrc))):[];
  const ambiguousRequestIdentity=matchingRequests.length>1;
  const req=matchingRequests.length===1?matchingRequests[0]:null;
  const responseStatus=req&&Number.isInteger(req.status)?req.status:null,reqError=req?.failed_error||null;
  const responseMime=typeof req?.mime_type==='string'?req.mime_type.split(';')[0].trim().toLowerCase():null;
  // The DOM currentSrc retains the requested URL after HTTP redirects. A successful
  // redirect to a different photograph must NOT certify that archival photograph.
  // Commons redirect->hashed upload and verified resize proxies are allowed by
  // sameSource. Unknown CDN/name changes remain unresolved, never automatically fixed.
  const finalNetworkIdentityVerified=!!(req&&r?.currentSrc&&sameSource(r.currentSrc,req.url));
  const finalRedirectIdentityUnverified=!!(req&&r?.currentSrc&&!finalNetworkIdentityVerified&&
   (req.url_aliases||[]).some(u=>sameSource(u,r.currentSrc)));
  // Successful HTTP does not imply a valid image: some publishers return 200 HTML/XML/JSON error bodies.
  // Require a completed, zero-width decode and a matching real CDP network response.
  const incompatibleResponse=!!(responseStatus>=200&&responseStatus<300&&responseMime&&
   ['text/html','application/json','application/xml','text/xml'].includes(responseMime));
  // HTTP 200 image/* can still be broken if Chrome receives bytes but cannot decode pixels.
  // Only accept an uncached, exact final CDP response for the completed currentSrc.
  const decodeFailure=!!(req&&finalNetworkIdentityVerified&&responseStatus===200&&
   responseMime&&responseMime.startsWith('image/')&&!reqError&&
   r?.complete===true&&r.naturalWidth===0&&
   Number.isSafeInteger(req.encodedDataLength)&&req.encodedDataLength>0&&
   req.was_cached!==true&&req.from_disk_cache!==true&&req.from_service_worker!==true);
  const domMapped=j.match==='exact_url_or_jetpack_origin'||j.match==='exact_url_unique_alt';
  const identityVerified=domMapped&&activeImageIdentity(s,r);
  // A redirect whose final CDP URL is not the displayed historical source cannot
  // establish that source's 404/network/HTML failure. Fail closed for *all* failure
  // kinds, not only the successful-200 decode-failure branch.
  const visiblyBroken=!!(pageVerified&&r&&identityVerified&&finalNetworkIdentityVerified&&
   !finalRedirectIdentityUnverified&&r.complete===true&&r.naturalWidth===0&&
   (reqError||(responseStatus!==null&&responseStatus>=400)||incompatibleResponse||decodeFailure));
  const failureKind=visiblyBroken?(reqError?'network_error':responseStatus>=400?'http_error':
   incompatibleResponse?'non_image_error_payload':decodeFailure?'image_decode_failure':null):null;
  // Decoded pixels without independent successful CDP image network evidence are
  // NOT proof that the historical source loaded (even if naturalWidth > 0).
  const loadedNetworkProof=!!(req&&finalNetworkIdentityVerified&&responseStatus===200&&
   responseMime&&responseMime.startsWith('image/')&&!reqError&&
   Number.isSafeInteger(req.encodedDataLength)&&req.encodedDataLength>0&&
   req.was_cached!==true&&req.from_disk_cache!==true&&req.from_service_worker!==true);
  const verifiedLoaded=!!(pageVerified&&r&&identityVerified&&r.complete===true&&
   r.naturalWidth>0&&loadedNetworkProof);
  let state='unverified';
  if(!pageVerified)state='page_not_verified';
  else if(!r)state='not_mapped';
  else if(j.match==='alt_only_unverified')state='alt_only_identity_unverified';
  else if(ambiguousRequestIdentity)state='ambiguous_network_request_identity';
  else if(domMapped&&!identityVerified)state='current_src_identity_unverified';
  else if(visiblyBroken)state='confirmed_broken_in_probe_browser';
  else if(finalRedirectIdentityUnverified)state='redirected_image_identity_unverified';
  else if(verifiedLoaded)state='loaded_in_probe_browser';
  else if(r.complete===true&&r.naturalWidth>0)state='decoded_without_verified_response';
  else if(r.complete===true&&r.naturalWidth===0)state='zero_intrinsic_width_needs_review';
  else state='pending_lazy_or_incomplete';
  return{image_key:j.key,match:j.match,stored_url:s.source_url,
   rendered_index:Number.isSafeInteger(r?.index)&&r.index>=0?r.index:null,
   rendered_alt:r?.alt??null,rendered_src:r?.src||null,
   current_src:r?.currentSrc||null,current_src_identity_verified:identityVerified,
   loaded_network_proof_verified:loadedNetworkProof,
   complete:r?.complete??null,natural_width:r?.naturalWidth??null,natural_height:r?.naturalHeight??null,
   request_url:req?.url||null,request_id:typeof req?.request_id==='string'?req.request_id:null,
   matching_cdp_image_request_count:matchingRequests.length,
   ambiguous_network_request_identity:ambiguousRequestIdentity,
   network_final_identity_verified:req?finalNetworkIdentityVerified:null,
   redirected_image_identity_unverified:finalRedirectIdentityUnverified,
   http_status:responseStatus,response_mime_type:responseMime,
   network_failure:reqError,visual_failure_kind:failureKind,
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

// Network Image responses include logos, UI icons and unrelated page chrome.
// A claim about ARTICLE image transfer size must count only requests attributable
// to a browser-visible, identity-verified stored article image, once per request.
// Multiple DOM slots can share a single request; separate real requests still count.
// Savings-grade article bytes require every stored article slot to be bound to
// decoded pixels AND a fresh, exact-identity CDP Image response. Unknown != zero.
function scopeArticleImageWire(slots,networkImages){
 const empty={article_bytes:null,unattributed_bytes:null,matched_request_count:0,
  unmeasured_article_requests:0,unverified_slot_count:0,unmatched_verified_slot_count:0};
 if(!Array.isArray(slots)||!Array.isArray(networkImages)||slots.length===0)return empty;
 const eligible=v=>!!(v&&v.result==='loaded_in_probe_browser'&&
  (v.match==='exact_url_or_jetpack_origin'||v.match==='exact_url_unique_alt')&&
  v.current_src_identity_verified===true&&v.network_final_identity_verified===true&&
  v.loaded_network_proof_verified===true&&v.verified_broken_in_browser===false&&
  v.stored_url&&v.current_src&&v.request_url&&
  sameSource(v.stored_url,v.current_src)&&sameSource(v.current_src,v.request_url));
 const valid=slots.filter(eligible),unverified=slots.length-valid.length;
 const applies=(v,n)=>!!(n?.url&&sameSource(v.current_src,n.url)&&sameSource(v.request_url,n.url));
 let article=0,unattributed=0,matched=0,unmeasured=0;
 for(const n of networkImages){
  const attributed=valid.some(v=>applies(v,n));
  const bytes=n?.encoded_data_length;
  if(attributed){
   matched++;
   if(!Number.isSafeInteger(bytes)||bytes<=0||n.status!==200||
     typeof n.mime_type!=='string'||!/^image\//i.test(n.mime_type)||
     n.error||n.was_cached===true||n.from_disk_cache===true||n.from_service_worker===true)unmeasured++;
   else article+=bytes;
  }else if(Number.isSafeInteger(bytes)&&bytes>=0)unattributed+=bytes;
 }
 const unmatched=valid.filter(v=>!networkImages.some(n=>applies(v,n))).length;
 return{article_bytes:unverified||unmatched||!matched||unmeasured?null:article,
  unattributed_bytes:unattributed,matched_request_count:matched,
  unmeasured_article_requests:unmeasured,
  unverified_slot_count:unverified,unmatched_verified_slot_count:unmatched};
}

module.exports={imageIdentity,sameSource,matchStoredImages,classifyImages,pageHostVerified,countTransfer,scopeArticleImageWire};
