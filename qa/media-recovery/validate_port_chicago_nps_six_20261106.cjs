'use strict';
function validate(a){
 const errors=[],err=s=>errors.push(s);
 if(!a||a.schema!=='fv-nps-port-chicago-six-v1')return{ok:false,errors:['wrong schema']};
 if(a.post?.id!==211||a.post?.status!=='publish'||a.scope?.legacy_images!==355||a.scope?.current_images!==361)err('article baseline drift');
 if(a.scope?.verified_guest_broken!==null||a.scope?.measured_wire_reduction_percent!==null)err('fabricated measured claim');
 if(a.scope?.original_storage_bytes!==43522829||a.release?.wordpress_writes!==0||a.release?.downloads!==0||a.release?.caches!==0||a.release?.production_fixes!==0||a.release?.duplicate_site_qa_collector!==false)err('forbidden modification');
 if(!Array.isArray(a.images)||a.images.length!==6)return{ok:false,errors:errors.concat('need 6 exact images')};
 const names=['POCH 2.078','POCH 2.115','POCH 2-113','POCH 2-056','U.S. Navy/NARA trial','POCH 2-055'];
 const seen=new Set();
 a.images.forEach((r,i)=>{
  if(r.slot!=='211:'+i||seen.has(r.original_src)||r.archival_id!==names[i])err('slot, identity or source duplication '+i);
  seen.add(r.original_src);
  if(!r.original_src?.startsWith('https://www.nps.gov/')||!r.primary_catalog_url?.startsWith('https://www.nps.gov/'))err('noncanonical NPS URL '+i);
  if(!r.alt||!r.caption||r.html_srcset!==null)err('markup changed '+i);
  if(r.exact_binary_identity_verified!==false||r.native_pixels!==null||r.catalog_orientation_verified!==false)err('invented binary/crop geometry '+i);
  if(!['image_rendered','tool_internal_error'].includes(r.independent_retriever_result)||r.origin_http_status!==null||r.guest_http_status!==null||r.guest_natural_pixels!==null||r.guest_wire_bytes!==null||r.visitor_broken!==null)err('invented browser HTTP/bytes '+i);
  if(r.reuse_rights!=='ITEM_REVIEW_HOLD'||r.credit_preserved!==true||r.no_upscale!==true||r.max_preview_width!==960||r.third_party_downloaded!==false||r.source_cached!==false||r.wordpress_written!==false||r.preview_rendered!==false||r.approved!==false)err('unsafe publication/license '+i);
  const w=r.html_width,h=r.html_height,pr=r.conditional_preview_html_only;
  if(i===4){if(w!==null||h!==null||pr!==null)err('invented trial image geometry');}
  else if(!Number.isInteger(w)||!Number.isInteger(h)||w<=0||h<=0||!Array.isArray(pr)||pr[0]!==960||pr[1]!==Math.round(960*h/w))err('unsafe conditional aspect '+i);
 });
 if(a.catalog_geometry_conflicts?.join(',')!=='211:1,211:2,211:3,211:5')err('catalog orientation hold missing');
 return {ok:errors.length===0,errors,images_checked:a.images.length};
}
if(typeof module!=='undefined')module.exports={validate};
if(typeof require!=='undefined'&&typeof module!=='undefined'&&require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const d=JSON.parse(fs.readFileSync(path.join(__dirname,'port_chicago_nps_six_20261106.json'),'utf8'));
 const result=validate(d);console.log(JSON.stringify(result,null,2));process.exit(result.ok?0:1);
}
