'use strict';
/** Read-only verification of 5 published first-party reconstruction PNG records.
 * All filesize values are WP ORIGINAL STORAGE, never measured browser bytes.
 */
const fs=require('node:fs'),path=require('node:path');
function validate(x){
 const errors=[],assert=(p,m)=>{if(!p)errors.push(m)};
 const expected=[39,40,41,42,43],postIds=[34,35,36,37,38];
 assert(x.schema_version===1&&x.observed_on==='2026-11-03','schema/date');
 assert(x.evidence_method==='authenticated_read_only_WordPress_com_wpcom_mcp_media_get_and_posts_get_context_edit','read-only provenance');
 assert(x.batch?.count===5&&x.rows?.length===5,'exact five');
 assert(x.batch?.original_storage_bytes===13267538,'original stored bytes exact');
 assert(x.sitewide_context?.published_posts===61&&x.sitewide_context?.stored_image_references===355&&x.sitewide_context?.oversized_wordpress_originals===13,'site-wide counts');
 assert(x.sitewide_context?.founder_reported_42_broken_browser_verified===null&&!x.sitewide_context?.claimed_76_percent_page_transfer_saving_measured&&x.sitewide_context?.production_media_repairs===0,'unsupported 42/76/repairs');
 assert(x.batch?.actual_guest_bytes_known===0&&x.batch?.stored_originals_are_not_visitor_transfer_bytes===true,'byte measurement gate');
 assert(x.batch?.all_are_inline_featured_images===true&&x.batch?.all_media_registered_sizes_empty===true&&x.batch?.all_post_captions_disclose_ai_assistance===true,'batch evidence flags');
 let sum=0;
 for(let i=0;i<5&&i<(x.rows?.length||0);i++){
  const r=x.rows[i];sum+=r.media_original_bytes;
  assert(r.media_id===expected[i]&&r.post_id===postIds[i]&&r.published_image_key===r.post_id+':0'&&r.featured_media_id===r.media_id,'record keys '+i);
  assert(r.media_source_url===r.published_img_source_url&&r.media_source_url.startsWith('https://finalvestige.com/wp-content/uploads/2026/08/')&&r.media_source_url.endsWith('.png'),'exact src '+i);
  assert(r.post_url.startsWith('https://finalvestige.com/2026/08/16/')&&typeof r.post_modified==='string','post source '+i);
  assert(r.media_mime==='image/png'&&r.media_original_bytes>1.5*1024*1024&&r.media_registered_sizes_count===0,'media facts '+i);
  assert(r.media_dimensions_px.width===1672&&r.media_dimensions_px.height===941&&r.published_html_dimensions_px.width===1024&&r.published_html_dimensions_px.height===576,'pixel geometry '+i);
  assert(r.published_block_size_slug==='large'&&r.published_img_has_srcset===false&&r.asset_kind==='AI-assisted historical reconstruction','source identity '+i);
  assert(/AI-assisted historical reconstruction/.test(r.published_figcaption)&&/AI-assisted historical reconstruction/.test(r.media_library_alt)&&r.published_caption_explicitly_discloses_ai===true,'historical disclosure '+i);
  assert(r.screenreader_alt_explicit_ai===false&&!/AI.assisted/i.test(r.published_inline_alt),'ALT observation '+i);
  assert(r.guest_current_src===null&&r.guest_http_status===null&&r.guest_decoded===null&&r.guest_encoded_transfer_bytes===null&&r.measured_savings_bytes===null,'no invented browser telemetry '+i);
  assert(r.conditional_max_width_px===960&&r.conditional_max_height_px===540&&r.conditional_no_upscale===true,'safe geometry '+i);
  assert(r.rights_ownership_and_tool_terms_cleared===false&&r.derivative_authorized===false&&r.wordpress_production_write_authorized===false,'rights/write hold '+i);
 }
 assert(sum===13267538,'sum originals');
 assert(x.safety?.licensed_republication_assumed===false&&x.safety?.wordpress_upload_authorized===false&&x.safety?.wordpress_post_update_authorized===false&&x.safety?.image_binary_downloaded===false,'safe bounds');
 return {ok:errors.length===0,errors,original_storage_bytes:sum,rows_checked:Math.min(5,x.rows?.length||0)};
}
if(require.main===module){const p=process.argv[2]||path.join(__dirname,'five_png_no_subsizes_live_wp_20261103.json');const res=validate(JSON.parse(fs.readFileSync(p,'utf8')));console.log(JSON.stringify(res));if(!res.ok)process.exitCode=1}
module.exports={validate};
