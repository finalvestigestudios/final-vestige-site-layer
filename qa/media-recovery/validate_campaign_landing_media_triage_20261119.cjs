'use strict';
const fs = require('node:fs');
function validate(a) {
 const errors=[]; const check=(condition,name)=>{if(!condition)errors.push(name)};
 check(a.schema==='fv-traffic-media-recovery-20261119-v1','schema');
 check(a.window?.days===30&&a.window?.end_date==='2026-11-18','window');
 check(a.window?.video_or_social_campaign_attribution===false&&a.window?.attributed_destination_pages===null,'attribution');
 check(a.source_custody?.historical_posts===61&&a.source_custody?.historical_images===355&&a.source_custody?.current_posts===66&&a.source_custody?.current_images===361,'separate_cohorts');
 check(a.source_custody?.source_snapshot_blob_sha==='9c9966be78d4e4abe7ec5bc9826ce56fbad8a1a0','source_sha');
 check(a.source_custody?.oversize_media_blob_sha==='d1ed574a527b9b431febdcb15ea91b48316812f2','oversize_sha');
 check(a.reported_failures_42_guest_verified===false&&a.claimed_76_percent_all_image_transfer_verified===false,'no_unverified_claims');
 check(a.stored_oversize_originals?.count===20&&a.stored_oversize_originals?.total_bytes===64385752&&a.stored_oversize_originals?.visitor_transfer_bytes===null,'stored_not_wire');
 const ids=new Set(); let sources404=0;
 for(const p of a.priority_posts||[]) {
  check(Number.isInteger(p.post_id)&&!ids.has(p.post_id),'unique_post_id');ids.add(p.post_id);
  check(p.url?.startsWith('https://finalvestige.com/'),'canonical_url');
  check(Number.isInteger(p.views_30d)&&p.views_30d>=0,'views');
  check(p.image_count===p.direct_external+p.jetpack_external+p.jetpack_first_party,'slot_partition');
  check(p.missing_dimension_pair<=p.image_count&&p.missing_srcset_or_sizes<=p.image_count,'markup_count');
  check(p.mobile?.independent_test===false&&p.mobile?.current_src===null&&p.mobile?.actual_transfer_bytes===null&&p.mobile?.lcp_ms===null&&p.mobile?.cls===null&&p.mobile?.inp_ms===null&&p.mobile?.screenshot_sha256===null,'no_fake_mobile');
  check(p.desktop?.independent_test===false&&p.desktop?.actual_transfer_bytes===null,'no_fake_desktop');
  check(p.stage_approved===false&&p.wordpress_write_authorized===false,'approval_hold');
  for(const o of p.known_origin_http_404||[]){
   sources404++; check(o.slot.startsWith(p.post_id+':')&&o.exact_url?.startsWith('https://')&&o.origin_response===404,'source_404_identity');
   check(o.guest_response===null&&o.guest_decode===null&&o.guest_broken_confirmed===false,'origin_not_guest_404');
  }
  for(const m of p.large_originals||[]) check(m.original_stored_bytes>1500000&&m.guest_original_download_confirmed===null&&m.rights_cleared===false,'stored_not_download');
 }
 check(ids.size===16&&sources404===3,'focus_count');
 check(ids.has(1922)&&a.priority_posts.find(p=>p.post_id===1922)?.image_count===0,'zero_image_control');
 check(a.official_candidates?.length===6&&a.official_candidates.every(c=>c.rehosting_approved===false&&c.exact_image_and_crop_confirmed===false),'candidate_rights');
 check(a.release_policy?.wordPress_production_writes===false&&a.release_policy?.automatic_downloads===false&&a.release_policy?.cached_rehosting===false&&a.release_policy?.max_width_px===960&&a.release_policy?.upscale===false,'safe_release');
 check(a.fresh_20261119_probe?.new_http_status_claims===0&&a.fresh_20261119_probe?.mobile_chromium==='UNAVAILABLE','fresh_limit');
 return errors;
}
if(require.main===module){
 const file=process.argv[2]||require('node:path').join(__dirname,'campaign_landing_media_triage_20261119.json');
 const e=validate(JSON.parse(fs.readFileSync(file,'utf8')));if(e.length){console.error(e.join('\n'));process.exitCode=1}else console.log('PASS - traffic/media source audit (no mobile or rights approval asserted)');
}
module.exports={validate};
