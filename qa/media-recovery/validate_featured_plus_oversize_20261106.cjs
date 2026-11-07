'use strict';
function validate(d){
 let e=[];const bad=s=>e.push(s);
 if(!d||d.schema!=='fv-featured-plus-oversize-cms-source-v1')return {ok:false,errors:['schema']};
 const expect={pages:83,posts:66,published_objects:149,media_images:116,featured_refs:25,featured_unique:25,featured_oversize:7,oversize_originals:13,oversize_original_storage_bytes:43522829,oversize_threshold_exclusive:1572864};
 for(const k of Object.keys(expect))if(d.cohort?.[k]!==expect[k])bad('cohort '+k);
 if(!Array.isArray(d.featured)||!Array.isArray(d.oversize))return {ok:false,errors:['missing rows']};
 if(d.featured.length!==25||d.oversize.length!==13)bad('row cardinality');
 if(d.guest_browser_verified!==false||d.reported_42_broken_verified!==false||d.reported_76pct_wire_saving_measured!==false)bad('invented visitor measurement');
 if(d.wordpress_writes!==0||d.homepage_design_writes!==0||d.additional_spend_usd!==0)bad('production boundary');
 const posts=new Set(),fids=new Set(),ids=new Set();
 const row=(x,name)=>{
  if(!Number.isInteger(x?.media_id)||x.media_id<1){bad(name+' id');return;}
  if(!/^https:\/\/finalvestige\.com\/wp-content\/uploads\/\d{4}\/\d{2}\//.test(x.source_url||''))bad(name+' source URL');
  if(!Number.isSafeInteger(x.original_storage_bytes)||x.original_storage_bytes<1)bad(name+' bytes');
  const w=x.native_width_metadata,h=x.native_height_metadata;
  if(!Number.isInteger(w)||!Number.isInteger(h)||w<1||h<1)bad(name+' dimensions');
  else if(x.preview_max_width!==Math.min(960,w)||x.preview_height_at_max_width!==Math.round(h*Math.min(960,w)/w))bad(name+' geometry');
  if(x.rights_clearance!=='HOLD_ITEM_LEVEL'||x.production_upload_allowed!==false||x.visual_approval!==false)bad(name+' rights hold');
  if(x.guest_http_status!==null||x.guest_browser_image_decoded!==null||x.cold_transfer_bytes!==null)bad(name+' fake browser data');
  if(!Array.isArray(x.sizes_reported))bad(name+' virtual variants');
 };
 for(const x of d.featured){row(x,'featured');if(posts.has(x.post_id)||fids.has(x.media_id))bad('duplicate post/media');posts.add(x.post_id);fids.add(x.media_id);if(!['post','page'].includes(x.post_type)||!/^https:\/\/finalvestige\.com\//.test(x.post_url||''))bad('post identity');if(x.featured_metadata_only!==true)bad('unproved guest placement');}
 let sum=0;
 for(const x of d.oversize){row(x,'oversize');if(ids.has(x.media_id))bad('duplicate large item');ids.add(x.media_id);if(x.original_storage_bytes<=1572864)bad('below threshold');sum+=x.original_storage_bytes;if(!Array.isArray(x.featured_on))bad('no crosswalk');else {const a=d.featured.filter(z=>z.media_id===x.media_id).map(z=>z.post_id).sort();const b=x.featured_on.map(z=>z.id).sort();if(JSON.stringify(a)!==JSON.stringify(b))bad('mismatched featured relation');}}
 if(sum!==43522829)bad('oversize total');
 if(d.featured.filter(x=>x.original_storage_bytes>1572864).length!==7)bad('seven featured oversized');
 if(d.featured.filter(x=>x.post_type==='post').length!==24||d.featured.filter(x=>x.post_type==='page').length!==1)bad('post/page metadata');
 return {ok:e.length===0,errors:e};
}
module.exports={validate};
if(typeof require==='function'&&require.main===module){const fs=require('node:fs');const p=process.argv[2]||'qa/media-recovery/featured_plus_oversize_20261106.json';const r=validate(JSON.parse(fs.readFileSync(p,'utf8')));console.log(JSON.stringify(r));if(!r.ok)process.exitCode=1;}
