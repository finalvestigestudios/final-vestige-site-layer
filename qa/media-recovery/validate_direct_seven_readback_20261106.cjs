'use strict';
const GOLD=[
[34,39,'bceca0bd-a16f-44f7-be08-16376fbf08ca.png',2892087,1672,941,0],
[35,40,'377e08da-e121-4f57-9174-1548343402b3.png',2552136,1672,941,0],
[36,41,'a44f673d-a8a8-4c83-9f29-7e24dd55156b.png',2498247,1672,941,0],
[37,42,'c1237ffd-4a47-4988-8254-e3b021069e72.png',2488823,1672,941,0],
[38,43,'01340c2e-1165-4ca0-aa96-87398a83d13a.png',2836245,1672,941,0],
[621,1257,'edit-017-v01-malbone-tunnel-generalpunger-original.jpg',4798395,4000,3000,0],
[621,1258,'edit-017-v02-nypl-5003296-original.jpg',5553669,5667,3831,1]];
function check(a){
 const errors=[],e=x=>errors.push(x);
 if(!a||a.schema!=='fv-direct-original-seven-20261106'||a.prior_blob_sha!=='6e6fb1048f643a33fb6e0e1d5881657400e74968')return{ok:false,errors:['schema']};
 if(a.baseline_article_count!==61||a.baseline_images!==355||a.current_articles!==66||a.wordPress_originals_over_1_5_mib!==13||a.wordPress_originals_over_1_5_mib_bytes!==43522829||a.five_png_storage_bytes!==13267538||a.two_malbone_storage_bytes!==10352064||a.seven_total_storage_bytes!==23619602)e('baseline_storage');
 if(a.source_only!==true||a.asserted_42_broken_browser_verified!==false||a.asserted_76pct_actual_wire_saving_measured!==false||a.production_wordpress_writes!==0||a.image_downloads!==0||a.third_party_caches!==0||a.preview_max_width!==960||a.rights!=='HOLD'||a.site_qa_owner!=='#154')e('claim_release_safety');
 if(a.source_png_have_markup_width_height!==true||a.source_malbone_missing_markup_width_height!==true)e('dimension_claim');
 if(!Array.isArray(a.rows)||a.rows.length!==7)return {ok:false,errors:[...errors,'row_count']};
 for(let i=0;i<7;i++){
  const r=a.rows[i],[p,m,f,bytes,w,h,slot]=GOLD[i];
  if(!r||r.media_id!==m||r.post_id!==p||r.slot!==slot||r.stored_image_src!=='https://finalvestige.com/wp-content/uploads/2026/08/'+f||r.wp_original_storage_bytes!==bytes||JSON.stringify(r.native_pixels)!==JSON.stringify([w,h])){e('exact_image_mapping');continue}
  if(typeof r.alt!=='string'||r.alt.length<10)e('alt_identity');
  if(r.markup_has_srcset!==false||r.markup_has_sizes!==false)e('markup_responsive_claim');
  if(r.guest_http!==null||r.cold_image_wire_bytes!==null||r.guest_image_failure!==null||r.reuse_approval!=='HOLD'||r.downloaded!==false||r.wp_write!==false||r.rights_checked!==false)e('no_invented_browser_rights');
  const x=Math.min(w,960);if(JSON.stringify(r.proposed_preview_pixels)!==JSON.stringify([x,Math.round(x*h/w)]))e('geometry');
  if(r.conditional_24pct_storage_budget_not_wire!==Math.floor(bytes*.24))e('hypothetical_not_measured');
  if(i<5){
   if(JSON.stringify(r.markup_dimensions)!=='[1024,576]'||!r.article_caption_kind.includes('AI-assisted historical reconstruction')||r.registered_768px_src!==undefined||r.full_resolution_map_access_required!==false)e('png_stored_markup');
  }else{
   if(JSON.stringify(r.markup_dimensions)!=='[null,null]'||!r.registered_768px_src.startsWith('https://finalvestige.com/wp-content/uploads/2026/08/')||!r.registered_768px_src.includes('-768x')||r.full_resolution_map_access_required!==(i===6))e('malbone_stored_markup');
   if(i===5&&!r.article_caption_kind.includes('CC BY-SA 4.0')||i===6&&!r.article_caption_kind.includes('New York Public Library Digital Collections'))e('rights_caveat');
  }
 }
 return {ok:!errors.length,errors};
}
module.exports={check};
if(require.main===module){const fs=require('node:fs');const a=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const v=check(a);console.log(v);process.exitCode=v.ok?0:1;}
