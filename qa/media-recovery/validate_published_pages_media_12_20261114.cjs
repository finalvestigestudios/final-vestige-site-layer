'use strict';
// Offline-only: validates published-page stored-image provenance, not browser failures.
const fs=require('node:fs');
const IDS=[1484,1480,2017,2088,2089,529,77,76,531,525,1304,1868];
const K={ 'finalvestige.com':'first_party','i.ytimg.com':'youtube_thumbnail','awin1.com':'affiliate_dynamic_banner','drive.google.com':'google_drive_thumbnail','upload.wikimedia.org':'wikimedia_binary' };
const check=(v,e)=>{if(!v)throw Error(e)};
function origin(src){
 check(typeof src==='string'&&src.length>10&&src.length<2048,'invalid_src_length');
 const u=new URL(src);
 check(u.protocol==='https:'&&!u.username&&!u.password,'invalid_https_src');
 return K[u.hostname.toLowerCase().replace(/^www\./,'')]||'other_external';
}
function validate(a){
 check(a?.schema==='fv-published-pages-media-source-pilot-v1'&&a.observed_date_pt==='2026-11-14','schema');
 check(a.pages_scanned===12&&a.images_found===49&&a.excluded_page_ids?.length===1&&a.excluded_page_ids[0]===6,'scope');
 check(Array.isArray(a.rows)&&a.rows.length===12,'pages');
 const seen=new Set(),totals={};let total=0;
 for(const p of a.rows){
  check(IDS.includes(p.id)&&!seen.has(p.id),'page_identity');seen.add(p.id);
  check(p.status==='publish'&&/^https:\/\/finalvestige\.com\//.test(p.url)&&/^2026-\d\d-\d\dT/.test(p.modified),'cms_page_custody');
  check(Array.isArray(p.images)&&p.images.length===p.image_count,'page_image_count');
  for(let i=0;i<p.images.length;i++){
   const x=p.images[i],type=origin(x.src);
   check(x.slot===p.id+':'+i&&x.origin_group===type,'image_slot_source_binding');
   check(x.guest_http_status===null&&x.guest_current_src===null&&x.guest_transfer_bytes===null&&x.guest_natural_px===null&&x.guest_broken===null,'fabricated_browser_result');
   check(x.rehost_authorized===false,'rights_hold');
   check(typeof x.alt==='string'&&(type==='youtube_thumbnail'||x.alt.trim().length>0),'alt_context');
   for(const k of ['html_width','html_height'])check(x[k]===null||(Number.isSafeInteger(x[k])&&x[k]>0),'invalid_size');
   totals[type]=(totals[type]||0)+1;total++;
  }
  check(Array.isArray(p.shorts_cards)&&(p.id===529||p.shorts_cards.length===0),'card_scope');
 }
 check(seen.size===12&&IDS.every(x=>seen.has(x))&&total===49,'complete_pilot');
 check(JSON.stringify(Object.entries(totals).sort())===JSON.stringify(Object.entries(a.images_by_origin_group||{}).sort()),'origin_totals');
 check(totals.youtube_thumbnail===40&&totals.affiliate_dynamic_banner===2&&totals.google_drive_thumbnail===1&&totals.wikimedia_binary===3&&totals.first_party===3,'source_group_custody');
 const f=a.rows.find(p=>p.id===529);
 check(f.image_count===40&&f.shorts_cards.length===40&&a.video_id_pairs===40&&a.video_pair_mismatches===0,'film_totals');
 for(let i=0;i<40;i++){
  const c=f.shorts_cards[i],x=f.images[i];
  check(c.index===i&&/^[a-zA-Z0-9_-]{11}$/.test(c.video_id||'')&&c.video_id===c.thumbnail_video_id,'video_link_id');
  check(x.src==='https://i.ytimg.com/vi/'+c.video_id+'/hqdefault.jpg','thumbnail_link_pair');
  check(c.anchor_accessible_label===true&&c.visible_title===true&&c.thumbnail_decorative_alt===true&&x.alt==='','decorative_alt_accessibility');
 }
 check(a.guest_browser_tested===false&&a.confirmed_browser_broken_images===null&&a.visitor_wire_bytes===null,'unmeasured_browser');
 check(a.sitewide_61_post_355_image_baseline_unchanged===true&&a.reported_42_broken_not_verified===true&&a.claimed_76_percent_wire_reduction_not_measured===true,'unsupported_claim');
 check(a.wp_image_attachments_last_read===125&&a.oversized_originals_decimal_gt_1500000===16&&a.oversized_stored_original_bytes===49107665,'storage_only_census');
 const r=a.release||{};
 for(const k of ['wordpress_write','binary_scraping','third_party_cache','homepage_changes','merges'])check(r[k]===false,'unsafe_release_'+k);
 for(const k of ['requires_browser_cdp','requires_item_rights','requires_exact_scene_and_caption','requires_visual_density','no_upscale'])check(r[k]===true,'missing_release_gate_'+k);
 check(r.max_derivative_width_px===960&&r.subscriptions_usd===0,'resize_or_spend');
 return {verdict:'SOURCE_PILOT_ONLY',pages:12,stored_image_slots:49,video_pairs_checked:40,third_party_slots:46,guest_failures_verified:null,wordpress_writes:0};
}
if(require.main===module){
 try{if(process.argv.length!==3)throw Error('Usage: node validate_published_pages_media_12_20261114.cjs audit.json');
 const file=process.argv[2];if(fs.statSync(file).size>1024*1024)throw Error('Input too large');
 console.log(JSON.stringify(validate(JSON.parse(fs.readFileSync(file,'utf8'))),null,2));
 }catch(e){console.error('PUBLISHED_PAGE_MEDIA_HOLD: '+e.message);process.exitCode=2}
}
module.exports={validate,origin};
