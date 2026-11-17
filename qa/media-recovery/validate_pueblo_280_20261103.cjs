'use strict';
function validate(a,f){
 const e=[],fail=s=>e.push(s),z=(f.images||[]).filter(x=>x.post_id===280).sort((x,y)=>x.slot-y.slot);
 const ids=['428-GX-USN-1129207','NH 75559','NH 75561','K-64683',null,'K-64728'],pix=[[3263,2244],null,null,[6184,4978],null,null];
 if(a.schema!=='fv-pueblo-280-20261103-v1'||a.observed_date!=='2026-11-03'||a.wordpress.id!==280||a.wordpress.status!=='publish'||a.wordpress.exact_match!==6||!a.wordpress.read_only||a.frozen.blob_sha!=='49183f66f880f7c4dfd363acca906876877f2e5e')fail('baseline');
 if(z.length!==6||a.images.length!==6)return [...e,'six slots'];
 for(let i=0;i<6;i++){
  const r=a.images[i],s=z[i],q=r.observed_exact_source,p=pix[i];
  if(r.key!==s.key||r.stored_url!==s.source_url||r.stored_alt!==s.alt||JSON.stringify(r.stored_dimensions)!==JSON.stringify([s.width_px,s.height_px]))fail('source '+i);
  if(r.archival.catalog_id!==ids[i]||!r.archival.catalog_url.startsWith('https://www.history.navy.mil/')||JSON.stringify(r.archival.full_tiff_pixels)!==JSON.stringify(p)||r.archival.exact_binary_verified!==false||r.archival.exact_crop_verified!==false)fail('archive '+i);
  if(q.method!=='web.open'||q.result!==(i===4?'inaccessible_no_numeric_status':'wrapper_502')||q.wrapper_http_code!==(i===4?null:502))fail('retriever '+i);
  for(const k of ['real_origin_http_code','real_browser_http_code','real_browser_decode','real_browser_bytes'])if(q[k]!==null)fail('invented HTTP/browser '+i);
  if(JSON.stringify(r.conditional_derivative_px)!==JSON.stringify(p?[960,Math.round(p[1]*960/p[0])]:null)||r.max_width_px!==960||r.no_upscale!==true)fail('pixel '+i);
  if(r.rights.item_review_required!==true||r.rights.cleared_to_republish!==false||r.wp_upload_allowed!==false||r.wp_edit_allowed!==false)fail('rights '+i);
 }
 if(!a.images[4].alt_integrity_warning?.includes('chronology')||!a.images[3].alt_integrity_warning?.includes('one sailor'))fail('caption');
 if(a.related_banner?.catalog_id!=='NH 68705'||a.related_banner.same_binary_not_verified!==true||a.related_banner.only_related_candidate!==true||JSON.stringify(a.related_banner.conditional_derivative_px)!=='[960,722]')fail('Banner distinct');
 const t=a.counts;
 if(t.slots!==6||t.external!==6||t.official_catalog_id_matches!==5||t.unmatched_banner_accession!==1||t.web_retriever_502!==5||t.web_retriever_no_numeric_status!==1||t.guest_broken_verified!==0||t.production_fixed!==0)fail('tallies');
 if(a.rights_and_release.wordpress_cache_and_upload!==false||a.rights_and_release.production_post_write!==false||a.sitewide.claim_42_broken_verified!==false||a.sitewide.claim_76_percent_wire_savings_measured!==false)fail('claims');
 return e;
}
module.exports={validate};
if(require.main===module){const fs=require('node:fs'),path=require('node:path');const a=JSON.parse(fs.readFileSync(path.join(__dirname,'pueblo_280_20261103.json'),'utf8')),f=JSON.parse(fs.readFileSync(path.join(__dirname,'parts/03.json'),'utf8'));const e=validate(a,f);console.log(e.length?e:'PASS');process.exitCode=e.length?1:0;}
