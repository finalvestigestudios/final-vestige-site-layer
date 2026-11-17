'use strict';
// Offline, fail-closed evidence gate. No network, media downloads, or WordPress writes.
function verify(report, oversize, parts, summary) {
  const errors=[], check=(v,m)=>{if(!v)errors.push(m);};
  const imgs=parts.flatMap(p=>p.images), keys=new Set(), seenMedia=new Set();
  check(parts.length===8 && parts.reduce((n,p)=>n+p.posts.length,0)===61,'61-post source corpus');
  check(imgs.length===355,'355-image source corpus');
  const originals=new Map(oversize.map(o=>[o.media_id,o]));
  check(oversize.length===13 && report.rows.length===13,'13 oversize originals');
  check(report.source_evidence.oversize_file==='qa/media-recovery/oversize_originals_20261030.json','oversize provenance file');
  check(report.audit_kind==='offline_wordpress_original_bytes_not_page_weight','evidence class');
  check(report.metrics.all_original_media_bytes===summary.media_library_original_total_bytes,'library total');
  const rsum=xs=>xs.reduce((n,r)=>n+r.original_bytes,0);
  for(const r of report.rows){
    const o=originals.get(r.media_id);
    check(!!o && !seenMedia.has(r.media_id),'original unique '+r.media_id);
    seenMedia.add(r.media_id);
    if(!o)continue;
    check(o.original_bytes>1572864 && Number.isSafeInteger(o.original_bytes) && r.original_bytes===o.original_bytes,'original measured bytes '+r.media_id);
    check(r.original_url===o.url && /^https:\/\/finalvestige\.com\/wp-content\/uploads\//.test(r.original_url),'first-party original identity '+r.media_id);
    check(r.original_width_px===o.original_width_px && r.original_height_px===o.original_height_px,'intrinsic metadata '+r.media_id);
    const matches=imgs.filter(im=>im.source_url===o.url), slots=matches.map(im=>im.key).sort(), urlMatches=matches.map(im=>im.post_url).sort();
    check(JSON.stringify(slots)===JSON.stringify(r.exact_oct30_inline_slots),'source URL join '+r.media_id);
    check(JSON.stringify(slots)===JSON.stringify(o.referenced_inline_positions.slice().sort()),'archived inline references '+r.media_id);
    check(JSON.stringify(urlMatches)===JSON.stringify(r.snapshot_post_urls),'post URL join '+r.media_id);
    check(r.is_referenced_in_61_post_snapshot===(matches.length>0),'use classification '+r.media_id);
    const w=Math.min(960,o.original_width_px),h=Math.round(o.original_height_px*w/o.original_width_px);
    check(r.conditional_max_width_px===w && r.conditional_height_px===h && r.derivative_pixels_are_plan_only===true,'960px no-upscale geometry '+r.media_id);
    check(r.existing_wp_1024_variant_url===o.existing_wp_1024_variant,'existing candidate URL '+r.media_id);
    check(r.item_rights_status==='REVIEW_REQUIRED' && r.cache_permission_verified===false && r.wordpress_write_authorized===false && r.original_binary_downloaded===false,'rights and production HOLD '+r.media_id);
    check(r.exact_original_http_status===null && r.guest_image_decode_success===null && r.guest_transferred_bytes===null && r.current_runtime_currentSrc===null,'no invented browser evidence '+r.media_id);
  }
  const linked=report.rows.filter(r=>r.is_referenced_in_61_post_snapshot), other=report.rows.filter(r=>!r.is_referenced_in_61_post_snapshot);
  const m=report.metrics;
  check(m.posts_in_snapshot===61 && m.inline_images_in_snapshot===355 && m.media_library_items===110,'corpus counts');
  check(m.oversized_original_count===13 && m.oversized_original_bytes===rsum(report.rows),'oversized storage bytes');
  check(m.oversized_with_exact_inline_source_count===linked.length && m.oversized_with_exact_inline_source_original_bytes===rsum(linked),'linked originals');
  check(m.oversized_without_exact_inline_source_count===other.length && m.oversized_without_exact_inline_source_original_bytes===rsum(other),'not-linked originals');
  check(m.oversized_share_original_media_pct===Math.round(10000*rsum(report.rows)/m.all_original_media_bytes)/100,'storage-share percent');
  check(m.potential_savings_bytes===null && m.site_cold_image_transfer_baseline_bytes===null && m.site_cold_image_transfer_after_bytes===null && m.validated_weight_reduction_pct===null,'no false performance claims');
  check(m.reported_76_percent_reduction_verified===false && m.reported_42_browser_broken_verified===false,'unverified claims held');
  check(report.claims_guard.number_76.includes('no before/after transferred-byte evidence'),'76% basis');
  return {ok:errors.length===0,errors,metrics:{oversized_originals:report.rows.length,linked_originals:linked.length,unlinked_originals:other.length,stored_oversize_bytes:rsum(report.rows),stored_linked_bytes:rsum(linked)}};
}
if(typeof require!=='undefined' && require.main===module){
 const fs=require('node:fs'),path=require('node:path'),root=__dirname;
 const load=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
 const result=verify(load('oversize_storage_priority_20261103.json'),load('oversize_originals_20261030.json'),Array.from({length:8},(_,i)=>load('parts/'+String(i+1).padStart(2,'0')+'.json')),load('summary_20261030.json'));
 console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1;
}
module.exports={verify};
