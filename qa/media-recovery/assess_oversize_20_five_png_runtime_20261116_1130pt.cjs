'use strict';
const okUrl=(u,host)=>typeof u==='string'&&u.startsWith('https://'+host+'/');
const same=(a,b)=>Array.isArray(a)&&a.length===b.length&&a.every((v,i)=>v===b[i]);
function hold(m){throw Error('MEDIA_HOLD: '+m)}
function assess(d){
 if(d?.schema!=='fv-oversize-runtime-proxy-crosscheck-v1'||d.source_scope?.site!=='finalvestige.com'||d.source_scope.scanned_image_count!==132)hold('source scope');
 const o=d.oversize;if(o?.count!==20||o.decimal_byte_threshold!==1500000||o.assets?.length!==20)hold('20 originals');
 let bytes=0,ids=new Set(),none=[];
 for(const a of o.assets){
  if(!Number.isInteger(a.media_id)||ids.has(a.media_id)||!Number.isInteger(a.bytes)||a.bytes<=1500000||a.native_width<=0||a.native_height<=0||!okUrl(a.source_url,'finalvestige.com')||!a.source_url.includes('/wp-content/uploads/')||!/^image\/(png|jpeg)$/.test(a.mime)||!Array.isArray(a.wordpress_variant_keys))hold('individual original');
  ids.add(a.media_id);bytes+=a.bytes;if(!a.wordpress_variant_keys.length)none.push(a.media_id);
 }
 if(bytes!==64385752||o.original_storage_bytes!==bytes||!same(none.sort((a,b)=>a-b),[39,40,41,42,43]))hold('aggregate/variant inventory');
 const f=d.focus;if(f?.count!==5||f.records?.length!==5||!same(f.ids,[39,40,41,42,43])||!same(f.post_ids,[34,35,36,37,38]))hold('five-post cohort');
 let focusBytes=0;
 for(let i=0;i<5;i++){
  const r=f.records[i],a=o.assets.find(a=>a.media_id===39+i);
  if(!r||r.media_id!==39+i||r.post_id!==34+i||r.featured_media_id!==39+i||r.post_status!=='publish'||!okUrl(r.post_url,'finalvestige.com')||r.wp_original_url!==a.source_url||r.wp_original_bytes!==a.bytes||!same(r.wp_original_native_px,[1672,941])||a.native_width!==1672||a.native_height!==941||!same(r.wp_media_api_sizes_keys,[]))hold('source/post pairing');
  if(r.rendered_img_src!=='https://i0.wp.com/'+r.wp_original_url.slice(8)+'?resize=1024%2C576&ssl=1')hold('actual Jetpack VIEW src');
  if(r.view_img_width!==1024||r.view_img_height!==576||r.view_srcset_present!==false||r.view_sizes_present!==false||r.alt_text_present!==true||!same(r.conditional_960_max_no_upscale_px,[960,540])||r.ai_reconstruction_caption_in_media!==true)hold('markup and 960px constraint');
  if(r.currentSrc_in_guest_browser!==null||r.guest_get_http_status!==null||r.guest_decoded!==null||r.guest_transfer_bytes!==null||r.visual_comparison!==null||r.item_rights_review!=='PENDING'||r.production_write_authorized!==false)hold('guest/rights fabrication');
  focusBytes+=r.wp_original_bytes;
 }
 if(focusBytes!==13267538||f.stored_bytes!==focusBytes)hold('five stored bytes');
 const h=d.historical_counts_not_replaced;if(h?.historical_posts!==61||h.historical_image_refs!==355||h.reported_broken_unverified!==42||h.savings_76_percent_measured!==false)hold('historical measurement confusion');
 if(!d.release?.startsWith('HOLD:')||!d.qa_owner?.includes('Site QA #154'))hold('release/QA ownership');
 return {decision:'HOLD_WIRE_BYTES_RIGHTS_AND_VISUAL_IDENTITY',scanned:132,oversized:20,stored_bytes:bytes,metadata_variantless_pngs:5,variantless_stored_bytes:focusBytes,Jetpack_VIEW_resized_srcs:5,visitor_http_confirmed:0,percent_76_verified:false,wordpress_writes:0};
}
module.exports={assess};
if(require.main===module){const fs=require('node:fs'),path=require('node:path');const file=process.argv[2]||path.join(__dirname,'oversize_20_five_png_runtime_20261116_1130pt.json');console.log(JSON.stringify(assess(JSON.parse(fs.readFileSync(file,'utf8'))),null,2))}
