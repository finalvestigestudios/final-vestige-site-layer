'use strict';
const fs=require('node:fs');
function validate(a){
 const e=[];
 const err=x=>e.push(x);
 if(a?.schema!=='fv-media-live-frozen-part04-v1')err('schema');
 if(a?.method!=='WORDPRESS_AUTHENTICATED_EDIT_CONTEXT_READ_ONLY')err('method');
 const rows=a?.rows??[];
 if(rows.length!==56||a?.counts?.images!==56||a?.counts?.posts!==8)err('56-row cohort');
 if(new Set(rows.map(r=>r.slot)).size!==56)err('unique-slots');
 if(new Set(rows.map(r=>r.post_id)).size!==8)err('8-posts');
 if(rows.filter(r=>r.source_equal).length!==56 || rows.filter(r=>r.alt_equal).length!==56)err('source-alt-integrity');
 if(rows.some(r=>String(r.live_source_url).replace(/&amp;/g,'&')!==String(r.frozen_source_url).replace(/&amp;/g,'&')))err('source-url-drift');
 if(rows.some(r=>!r.source_equal||!r.alt_equal||r.guest_http_status!==null||r.actual_origin_http_status!==null||r.guest_broken!==null||r.guest_current_src!==null||r.guest_decoded_px!==null||r.guest_image_transfer_bytes!==null||r.measured_cls!==null))err('fake-browser-evidence');
 if(rows.some(r=>r.cache_approved!==false||r.wordpress_media_upload_approved!==false||r.post_rewrite_approved!==false||r.item_rights_cleared!==false||r.exact_photo_identity_verified!==false))err('unauthorized-release');
 if(rows.some(r=>!Array.isArray(r.catalog_candidates)||r.catalog_candidates.some(c=>c.item_rights_cleared===true||c.exact_image_match_verified===true)))err('candidate-rights-hold');
 if(rows.some(r=>r.staging?.max_width_px!==960||r.staging?.no_upscale!==true||r.staging?.require_same_scene!==true))err('staging');
 if(rows.some(r=>r.catalog_candidates.some(c=>{const x=c.conditional_960px;return Array.isArray(x)&&(!Number.isInteger(x[0])||!Number.isInteger(x[1])||x[0]<1||x[1]<1||x[0]>960||x.length!==2)})))err('invalid-960');
 const count=(fn)=>rows.filter(fn).length;
 if(count(r=>r.html_width_px==null&&r.html_height_px==null)!==54||count(r=>r.html_width_px!=null&&r.html_height_px!=null)!==2)err('dimensions');
 if(count(r=>r.literal_srcset)!==0)err('srcset');
 if(count(r=>r.source_kind==='external')!==34||count(r=>r.source_kind==='wikimedia_redirect')!==15||count(r=>r.source_kind==='first_party')!==7)err('source-kinds');
 if(rows.some(r=>r.oversized_original_matches.some(m=>m.real_wire_bytes!==null||m.derivative_authorized!==false)))err('oversized-measurements');
 if(a?.claims?.reported_broken_images!==42||a?.claims?.guest_confirmed_broken_images!==null||a?.claims?.claimed_reduction_percent!==76||a?.claims?.actual_reduction_percent!==null||a?.claims?.actual_cold_before_bytes!==null||a?.claims?.actual_cold_after_bytes!==null)err('historical-claims');
 if(a?.claims?.oversized_original_count_sitewide!==15||a?.claims?.oversized_original_bytes_stored_sitewide!==47096779)err('sitewide-stored');
 if(a?.release?.wordpress_production_write!==false||a?.release?.third_party_download!==false||a?.release?.asset_cache!==false||a?.release?.license_approval!==false||a?.release?.deployment!==false||a?.release?.home_page_visual_changes!==false||a?.release?.subscription_spend_usd!==0)err('production-safety');
 return e;
}
if(require.main===module){
 const filename=process.argv[2]||'qa/media-recovery/live_part04_8posts_56_images_20261112.json';
 const a=JSON.parse(fs.readFileSync(filename,'utf8')),issues=validate(a);
 if(issues.length){console.error('FAIL '+issues.join(', '));process.exitCode=1;}
 else console.log('PASS 56 rows / eight posts, source+rights+guest+weight holds');
}
module.exports={validate};
