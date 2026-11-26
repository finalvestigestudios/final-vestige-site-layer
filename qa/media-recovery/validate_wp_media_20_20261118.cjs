'use strict';
// Deterministic, offline review of a read-only WordPress Media List snapshot.
// No network, image downloads, media mutations, or production publishing.
const isObj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const pos=x=>Number.isSafeInteger(x)&&x>0;
const nonneg=x=>Number.isSafeInteger(x)&&x>=0;
const localMedia=u=>{
  try {const x=new URL(u);return x.protocol==='https:'&&x.hostname==='finalvestige.com'&&x.pathname.startsWith('/wp-content/uploads/')&&!x.username&&!x.password;}
  catch{return false;}
};
const validVirtual=u=>u===null || (()=>{
  try {const x=new URL(u);return x.protocol==='https:'&&/^i[0-9]\.wp\.com$/.test(x.hostname)&&x.pathname.startsWith('/finalvestige.com/wp-content/uploads/')&&x.searchParams.has('fit')&&x.searchParams.get('ssl')==='1'&&!x.username&&!x.password;}
  catch{return false;}
})();
function validateWpMediaOversize(a){
 const errors=[];const reject=x=>{if(errors.length<80)errors.push(x)};
 if(!isObj(a)||a.schema!=='fv-live-wp-media-oversize-v1')return {gate:'HOLD',errors:['schema']};
 if(a.site!=='finalvestige.com'||a.capture_date!=='2026-11-18'||!pos(a.media_records_scanned)||
    a.threshold_bytes!==1500000||a.visitor_transfer_measured!==false||
    a.network_claim_verified!==false||a.wordpress_writes!==0||!Array.isArray(a.records))reject('capture_or_claim');
 if(!Array.isArray(a.records))return {gate:'HOLD',errors};
 let total=0;const ids=new Set(),urls=new Set();
 for(let i=0;i<a.records.length;i++){
  const r=a.records[i],p='record_'+i;
  if(!isObj(r)){reject(p+':object');continue;}
  if(!pos(r.id)||ids.has(r.id))reject(p+':id'); else ids.add(r.id);
  if(typeof r.title!=='string'||!r.title.trim()||typeof r.mime_type!=='string'||!/^image\/(jpeg|png|webp|avif)$/i.test(r.mime_type))reject(p+':title_mime');
  if(!localMedia(r.source_url)||urls.has(r.source_url))reject(p+':url'); else urls.add(r.source_url);
  if(!(r.media_parent_post===null||pos(r.media_parent_post)))reject(p+':parent');
  if(!pos(r.original_bytes)||r.original_bytes<=a.threshold_bytes||!pos(r.width_px)||!pos(r.height_px))reject(p+':size');
  if(pos(r.original_bytes)) {total+=r.original_bytes;if(!Number.isSafeInteger(total))reject('unsafe_sum');}
  const d=r.proposed_derivative;
  const targetW=Math.min(960,r.width_px), targetH=Math.max(1,Math.round(r.height_px*targetW/r.width_px));
  if(!isObj(d)||d.mode!=='FIT_NO_CROP_NO_UPSCALE'||d.max_width_px!==960||
     d.width_px!==targetW||d.height_px!==targetH||d.width_px>r.width_px||d.height_px>r.height_px||
     !validVirtual(d.existing_virtual_large_url))reject(p+':derivative');
  const rights=r.rights;
  if(!isObj(rights)||rights.approval!=='HOLD_ITEM_LEVEL'||rights.reuse_authorized!==false||
     typeof rights.metadata_credit!=='string'||typeof rights.metadata_copyright!=='string')reject(p+':rights');
  const b=r.browser;
  if(!isObj(b)||b.final_http!==null||b.decoded!==null||b.transfer_bytes!==null||
      r.status!=='STORAGE_ONLY_UNVERIFIED_TRANSFER')reject(p+':unsupported_browser_claim');
  if(!(r.known_inline_slot===null||/^\d+:\d+$/.test(r.known_inline_slot)))reject(p+':slot');
 }
 if(!nonneg(a.oversize_count)||a.oversize_count!==a.records.length||a.oversize_count>a.media_records_scanned)reject('count');
 if(!nonneg(a.oversize_total_original_bytes)||total!==a.oversize_total_original_bytes)reject('sum');
 return {gate:errors.length?'HOLD':'PASS_STORAGE_ONLY',errors,oversize_count:a.records.length,
 original_bytes:total,visitor_savings_verified:false,production_write_authorized:false};
}
module.exports={validateWpMediaOversize};
