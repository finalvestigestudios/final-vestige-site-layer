'use strict';
function check(a) {
 const errors=[],e=x=>errors.push(x);
 if(!a||a.schema!=='fv-wp-fresh-oversize-20261106'||a.site!=='https://finalvestige.com')return{ok:false,errors:['schema']};
 if(a.fresh_published_posts!==66||a.fresh_wp_image_media_items!==115||a.full_66_post_markup_recensused!==false) e('counts');
 if(JSON.stringify(a.selected_current_published_post_img_counts)!=='{"34":1,"35":1,"36":1,"37":1,"38":1,"299":8,"621":6}')e('published_markup');
 if(a.threshold_exclusive!==1572864||a.oversized_originals!==13||a.original_storage_bytes!==43522829)e('original_storage');
 if(a.alleged_42_broken_browser_verified!==false||a.claimed_76_percent_actual_transfer_reduction_measured!==false||a.measured_browser_transfer_bytes!==null||a.copyright_reuse_review!=='HOLD'||a.wp_production_writes!==0||a.third_party_asset_downloads!==0||a.max_preview_width!==960||a.site_qa_browser_owner!=='#154')e('safety_and_claims');
 if(!Array.isArray(a.rows)||a.rows.length!==13)return{ok:false,errors:[...errors,'13_rows']};
 const ids=new Set(),urls=new Set(),counts={direct:0,jetpack:0,not_matched_in_seven_posts:0},totals={direct:0,jetpack:0,not_matched_in_seven_posts:0};
 for(const r of a.rows){
  if(!Number.isInteger(r.id)||ids.has(r.id))e('duplicate_id');ids.add(r.id);
  if(r.id===405&&r.wp_parent!==85)e('wp_parent_405');
  if(typeof r.original_url!=='string'||!r.original_url.startsWith('https://finalvestige.com/wp-content/uploads/2026/08/')||urls.has(r.original_url))e('original_url');urls.add(r.original_url);
  if(!Number.isInteger(r.original_stored_bytes)||r.original_stored_bytes<=1572864)e('size_threshold');
  const [w,h]=r.wp_original_pixels||[];const tw=Math.min(w,960);
  if(!Number.isInteger(w)||!Number.isInteger(h)||w<=0||h<=0||JSON.stringify(r.conditional_960px_geometry)!==JSON.stringify([tw,Math.round(tw*h/w)]))e('no_upscale_geometry');
  if(r.actual_guest_http_status!==null||r.actual_cold_wire_bytes!==null||r.reuse_rights!=='HOLD'||r.wp_publish_allowed!==false||r.downloaded!==false)e('rights_and_http');
  let bucket='not_matched_in_seven_posts';
  if(r.observed_route==='direct'){
   bucket='direct';
   if(r.actual_published_img_src!==r.original_url||![34,35,36,37,38,621].includes(r.observed_published_post))e('direct_identity');
   if([34,35,36,37,38].includes(r.observed_published_post)&&(r.wp_has_nonfull_subsizes!==false||w!==1672||h!==941||!r.original_url.endsWith('.png')))e('no_subsize_png');
  }else if(r.observed_route==='jetpack'){
   bucket='jetpack';
   if(r.observed_published_post!==299||r.wp_has_nonfull_subsizes!==true||typeof r.actual_published_img_src!=='string'||!r.actual_published_img_src.startsWith('https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/')||!r.actual_published_img_src.includes('?fit=1024%2C'))e('jetpack_identity');
  }else if(r.observed_route==='unknown'){
   if(r.observed_published_post!==null||r.actual_published_img_src!==null)e('unknown_scope');
  }else e('route');
  counts[bucket]++;totals[bucket]+=r.original_stored_bytes;
 }
 if(JSON.stringify(counts)!=='{"direct":7,"jetpack":3,"not_matched_in_seven_posts":3}')e('group_counts');
 if(JSON.stringify(totals)!=='{"direct":23619602,"jetpack":13318311,"not_matched_in_seven_posts":6584916}')e('group_bytes');
 for(const k of Object.keys(counts))if(a.buckets?.[k]?.count!==counts[k]||a.buckets[k].original_storage_bytes!==totals[k])e('bucket_manifest');
 return{ok:errors.length===0,errors,counts,totals};
}
module.exports={check};
if(require.main===module){const f=require('node:fs');const r=check(JSON.parse(f.readFileSync(process.argv[2],'utf8')));console.log(r);process.exitCode=r.ok?0:1}
