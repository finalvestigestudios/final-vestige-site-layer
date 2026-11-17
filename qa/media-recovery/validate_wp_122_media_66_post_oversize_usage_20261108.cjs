'use strict';
// Read-only audit validator. WP original storage bytes are NOT visitor transfer bytes.
const fs=require('node:fs');
const EXPECT={388:[8176362,299],1258:[5553669,621],1257:[4798395,621],39:[2892087,34],43:[2836245,38],389:[2822969,299],40:[2552136,35],41:[2498247,36],42:[2488823,37],382:[2318980,299],482:[2293016,null],405:[2201573,null],293:[2090327,null],2148:[2030948,null],1714:[1543002,269]};
const site=s=>typeof s==='string'&&/^https:\/\/finalvestige\.com\/[^?#]+/.test(s);
function validate(a){
 const errors=[],fail=m=>errors.push(m);
 if(!a||typeof a!=='object'||Array.isArray(a))return ['invalid_snapshot'];
 if(a.schema!=='fv-oversized-wordpress-image-exposure-v1'||a.capture_date_local!=='2026-11-08'||a.source_baseline_blob!=='223d598d244ff496e861f8330346b341cec29fae'||!String(a.method).includes('66 raw posts.get'))fail('provenance');
 if(a.current_published_post_count!==66||a.media_library_image_count_latest_read!==122||!Array.isArray(a.current_published_post_ids)||a.current_published_post_ids.length!==66||new Set(a.current_published_post_ids).size!==66)fail('census');
 if(!Array.isArray(a.rows)||a.rows.length!==15)return [...new Set([...errors,'15_rows'])];
 const seen=new Set(),posts=new Set();let bytes=0,used=0,matches=0,usedBytes=0;
 for(const r of a.rows){
  const ex=EXPECT[r.media_id];
  if(!ex||seen.has(r.media_id)){fail('unexpected_media');continue;}seen.add(r.media_id);
  if(r.stored_original_bytes!==ex[0]||!site(r.original_source_url)||!r.original_source_url.includes('/wp-content/uploads/2026/'))fail('source_or_storage');
  bytes+=r.stored_original_bytes;
  const n=r.native_wp_dimensions,d=r.conditional_no_upscale_px;
  if(!Array.isArray(n)||!Array.isArray(d)||n.length!==2||d.length!==2||
     !n.every(v=>Number.isSafeInteger(v)&&v>0)||!d.every(v=>Number.isSafeInteger(v)&&v>0)||
     d[0]>960||d[0]>n[0]||d[1]>n[1]||Math.abs(d[0]*n[1]-d[1]*n[0])>Math.max(...n))fail('no_upscale_or_aspect');
  if(r.rights_release_authorized!==false||!r.rights_status||r.actual_guest_currentSrc!==null||r.actual_guest_http_status!==null||r.actual_guest_encoded_bytes!==null)fail('fabricated_browser_or_rights');
  if(!Array.isArray(r.raw_published_post_occurrences)||r.raw_published_post_occurrences.length!==(ex[1]===null?0:1)){fail('usage_count');continue;}
  if(r.raw_published_post_occurrences.length){used++;usedBytes+=r.stored_original_bytes;}
  for(const o of r.raw_published_post_occurrences){
   matches++;posts.add(o.post_id);
   if(o.post_id!==ex[1]||!a.current_published_post_ids.includes(o.post_id)||!site(o.post_link)||!Number.isSafeInteger(o.img_index)||o.img_index<0||!o.post_title||!String(o.post_modified).startsWith('2026-')||typeof o.alt!=='string')fail('post_identity');
   if(o.source_url_in_raw_html===r.original_source_url){
    if(o.identity!=='src_and_wp_image_id'&&o.identity!=='exact_src')fail('identity_type');
   } else {
    const path=r.original_source_url.replace('https://finalvestige.com','');
    if(o.identity!=='wp_image_id_with_transformed_src'||!String(o.source_url_in_raw_html).includes(path)||!/^https:\/\/i\d?\.wp\.com\//.test(o.source_url_in_raw_html))fail('jetpack_identity');
   }
  }
 }
 const c=a.counts||{},s=a.safeguards||{};
 if(seen.size!==15||bytes!==47096779||used!==11||matches!==11||posts.size!==8||usedBytes!==38480915||
   [34,35,36,37,38,269,299,621].some(id=>!posts.has(id))||
   c.oversized_originals!==15||c.oversized_original_stored_bytes!==bytes||
   c.inline_matched_originals!==used||c.unmatched_to_published_inline_images!==15-used||
   c.published_inline_occurrences!==matches||c.published_post_count_with_inline_matches!==posts.size||
   c.inline_matched_original_stored_bytes!==usedBytes||c.unmatched_original_stored_bytes!==bytes-usedBytes)
   fail('math_or_media_usage');
 if(c.source_img_http_statuses_measured!==0||c.guest_browser_bytes_measured!==0||c.visitor_confirmed_broken!==null||c.reported_42_broken_verified!==false||c.reported_76_percent_transfer_reduction_verified!==false)fail('false_42_or_76');
 if(s.max_image_width_px!==960||s.no_upscale!==true||s.rights_and_crop_clearance_required!==true||s.wordpress_production_writes!==0||s.external_binary_downloads_or_caches!==0||s.homepage_design_edits!==0||s.spend_usd!==0||s.release_authorized!==false||!Array.isArray(a.scan_errors)||a.scan_errors.length)fail('unsafe_or_incomplete');
 return [...new Set(errors)];
}
module.exports={validate};
if(require.main===module){
 const a=JSON.parse(fs.readFileSync(process.argv[2]||'qa/media-recovery/wp_122_media_66_posts_oversize_usage_20261108.json','utf8'));
 const e=validate(a);if(e.length){console.error('HOLD '+e.join(','));process.exitCode=1;}else console.log('PASS 15 originals; 11 in 8 published posts; zero visitor wire claims or writes');
}
