'use strict';
/** Offline, fail-closed validation of the St Francis Dam #166 source-only audit. No network/WP writes. */
const EXPECTED=["https://finalvestige.com/wp-content/uploads/2026/08/IMG_3479.jpeg","https://tile.loc.gov/storage-services/service/pnp/habshaer/ca/ca3000/ca3095/sheet/00002a.gif","https://commons.wikimedia.org/wiki/Special:Redirect/file/St.%20Francis%20abutment.jpg?width=1280","https://commons.wikimedia.org/wiki/Special:Redirect/file/Twisted_Tracks.jpg?width=1280","https://commons.wikimedia.org/wiki/Special:Redirect/file/St.%20Francis%20Dam%20after%20the%201928%20failure.jpg?width=1280","https://commons.wikimedia.org/wiki/Special:Redirect/file/Standing_section.jpg?width=1280","https://commons.wikimedia.org/wiki/Special:Redirect/file/Man%20pointing%20at%20crack%20in%20Saint%20Francis%20Dam%20after%20its%20collapse.jpg?width=1280"];
const RIGHTS_SENSITIVE=new Set([1,5,6]);
function validate(a){
 const e=[];
 if(a?.schema_version!==1)e.push('schema');
 if(a?.post?.id!==166||a?.post?.status!=='publish')e.push('post');
 if(a?.archived_inventory?.blob_sha!=='21095161e633aba093b74c0ead9936c9f6186d00'||a?.archived_inventory?.all_published_sources_match_live_wp!==true)e.push('pinned source');
 if(!Array.isArray(a?.rows)||a.rows.length!==7)return [...e,'exact seven rows'];
 const seen=new Set();
 a.rows.forEach((r,i)=>{
  if(seen.has(r.key)||r.key!=='166:'+i||r.slot!==i||r.post_id!==166)e.push('row identity '+i);
  seen.add(r.key);
  if(r.published_src!==EXPECTED[i])e.push('source drift '+i);
  if(r.source_reconciled_live_wp!==true||r.source_snapshot_blob_sha!=='21095161e633aba093b74c0ead9936c9f6186d00')e.push('source provenance '+i);
  if(r.origin_browser_http_status!==null||r.origin_browser_mime!==null||r.origin_browser_decode_ok!==null||r.visitor_broken!==null||r.cold_browser_transfer_bytes!==null)e.push('fabricated browser evidence '+i);
  if(r.probe?.method!=='web.open independent text retriever'||r.probe?.result!=='inaccessible_without_origin_status'||r.probe?.http_status!==null||r.probe?.origin_status_verified!==false)e.push('misattributed probe '+i);
  if(r.derivative_max_width_px!==960||r.candidate_visual_match_verified!==false||r.rights_review_complete!==false||r.wp_media_upload_authorized!==false||r.production_rewrite_authorized!==false||r.source_binary_sha256!==null||r.recovery_state!=='HOLD_BROWSER_IDENTITY_RIGHTS')e.push('unsafe rights/production gate '+i);
  const d=r.catalog?.master_dimensions_px,t=r.derivative_dimensions_px;
  if(d===null){if(t!==null)e.push('invented dimensions '+i);}
  else if(!Array.isArray(d)||d.length!==2||!d.every(v=>Number.isSafeInteger(v)&&v>0)||!Array.isArray(t)||t[0]!==Math.min(960,d[0])||t[1]!==Math.round(d[1]*t[0]/d[0]))e.push('dimensions '+i);
  if(!r.catalog?.url && i!==0)e.push('missing catalog '+i);
  if(RIGHTS_SENSITIVE.has(i)&&!r.catalog?.rights_basis)e.push('rights explanation '+i);
 });
 if(a.stats?.image_slots!==7||a.stats?.offsite_stored!==6||a.stats?.commons_redirects!==5||a.stats?.loc_direct_gif!==1||a.stats?.first_party!==1||a.stats?.catalog_identifications!==5||a.stats?.confirmed_visitor_broken!==0||a.stats?.actual_origin_http_status_count!==0||a.stats?.actual_cold_wire_bytes_measured!==false||a.stats?.claimed_broken_42_verified!==false||a.stats?.claimed_reduction_76pct_verified!==false||a.stats?.production_changes!==0)e.push('unsupported totals');
 return e;
}
module.exports={validate};
