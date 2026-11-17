'use strict';
/** Pure fail-closed review of read-only live WP inventory evidence. No HTTP, downloads or CMS writes. */
function validateLiveRecheck(a){
 const reasons=[],reject=m=>reasons.push(m),isInt=x=>Number.isSafeInteger(x)&&x>0;
 if(a?.schema!=='fv-live-wordpress-p0-and-oversize-recheck-v1')reject('schema_unknown');
 if(a?.staging_plan?.no_write_this_batch!==true||a?.staging_plan?.no_media_binary_download_this_batch!==true||
   a?.staging_plan?.no_homepage_design_change!==true)reject('unsafe_action_or_scope');
 if(a?.performance_claims?.reported_42_broken!=='UNVERIFIED_IN_LOGGED_OUT_BROWSER'||
    a?.performance_claims?.reported_76_percent_reduction!=='UNMEASURED'||
    a?.performance_claims?.stored_bytes_not_network_bytes!==true||
    a?.performance_claims?.production_repair_count_claimed_by_this_batch!==null)reject('unsupported_performance_claim');
 if(a?.fresh_sitewide_posts_count!==null||a?.fresh_sitewide_post_image_count!==null)reject('fabricated_fresh_sitewide_census');
 if(a?.frozen_baseline?.posts!==61||a?.frozen_baseline?.images!==355||
    a?.frozen_baseline?.external_refs!==288)reject('frozen_inventory_drift');
 const inventory=a?.live_media_inventory;
 if(inventory?.image_media_items_count!==113||inventory?.pages_read!==2||
    inventory?.threshold_bytes_exclusive!==1572864||
    inventory?.visitor_transfer_bytes!==null)reject('wp_media_census_invalid');
 const rows=a?.oversized_media;
 if(!Array.isArray(rows)||rows.length!==13)reject('oversized_13_required');
 const seen=new Set();let sum=0,unsub=0,mapped=0;
 for(const r of Array.isArray(rows)?rows:[]){
  if(!isInt(r?.media_id)||seen.has(r.media_id))reject('duplicate_or_invalid_media_id');
  seen.add(r?.media_id);
  if(typeof r?.source_url!=='string'||!r.source_url.startsWith('https://finalvestige.com/wp-content/uploads/2026/08/'))
    reject('original_not_first_party_wp');
  if(!isInt(r?.wp_original_stored_bytes)||r.wp_original_stored_bytes<=1572864)reject('size_not_above_threshold');
  else sum+=r.wp_original_stored_bytes;
  const dim=r?.wp_metadata_dimensions_px,out=r?.proposed_max_derivative_px;
  if(!Array.isArray(dim)||dim.length!==2||!dim.every(isInt)||
    !Array.isArray(out)||out.length!==2||!out.every(isInt)||
    out[0]!==Math.min(960,dim[0])||out[1]!==Math.round(dim[1]*out[0]/dim[0]))
    reject('960px_proportional_no_upscale_failed');
  if(r?.wp_declared_nonfull_subsizes===false)unsub++;
  if(r?.live_published_post_exact_image_source_confirmed===true){
   mapped++;
   if(!isInt(r.live_published_post_id)||typeof r.live_published_post_title!=='string')
     reject('unsupported_live_article_reference');
  }else if(r?.live_published_post_id!==null)reject('unverified_live_article_reference');
  if(r?.media_rights!=='HOLD'||r?.image_downloaded!==false||
    r?.local_cache_authorized!==false||r?.wp_upload_authorized!==false||
    r?.post_rewrite_authorized!==false)reject('unsafe_rights_or_action');
  if(r?.visitor_http_status!==null||r?.visitor_transfer_bytes!==null||r?.visitor_broken!==null)
    reject('invented_browser_evidence');
 }
 if(sum!==43522829||inventory?.oversized_original_storage_bytes!==sum||
    inventory?.oversized_original_count!==13)reject('storage_bytes_not_reconciled');
 if(unsub!==5||mapped!==10)reject('live_usage_group_reconciliation_failed');
 const p=a?.prioritized_existing_p0_exact_live_sources;
 const keys=['285:5','285:2','287:5','418:1','418:2','407:1'];
 if(!Array.isArray(p)||p.length!==keys.length)reject('p0_queue_missing');
 else for(let i=0;i<p.length;i++){
  const row=p[i];
  if(row.image_key!==keys[i]||row.post_id!==Number(keys[i].split(':')[0])||
    typeof row.live_source_url!=='string'||!row.live_source_url.startsWith('https://')||
    row.frozen_source_url_matches_latest_read_only_wp!==true||
    row.actual_browser_status!==null||row.actual_browser_current_src!==null||
    row.visitor_transferred_bytes!==null||row.visitor_broken!==null||
    row.localize_or_rewrite_authorized!==false)reject('p0_unverified_or_action_unsafe');
 }
 return {pass:reasons.length===0,reasons:[...new Set(reasons)],
  live_large_originals:rows?.length??null,live_original_storage_bytes:reasons.length?null:sum,
  guest_browser_verified:false,production_media_changes_authorized:false};
}
module.exports={validateLiveRecheck};
