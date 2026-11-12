'use strict';
// Read-only offline audit validator. Never loads original image binaries.
function validate(a){
 const errors=[],check=(ok,k)=>{if(!ok)errors.push(k)},r=a?.release||{},c=a?.cohorts||{},m=a?.current_media||{};
 check(a?.schema==="fv-media-20261111-live-cms-readback-v1","schema");
 check(c.historical_posts===61&&c.historical_inline===355&&c.historical_external===288&&c.current_published_posts===66&&c.current_media_image_records===122&&c.post_bodies_checked===13&&c.inline_tags_in_those_posts===58,"cohort");
 check(m.total_original_bytes===70627679&&m.previous_original_bytes===70554906&&m.delta_bytes===m.total_original_bytes-m.previous_original_bytes&&m.delta_bytes===72773&&m.delta_image_id===2267,"library_delta");
 check(m.large_originals_gt_1500000===15&&m.large_originals_bytes===47096779&&m.large_originals_live_inline_matches===11&&m.matched_inline_original_bytes===38480915,"large_original_aggregate");
 check(a.p0_originals?.length===6&&new Set(a.p0_originals.map(x=>x.slot)).size===6,"p0_count");
 for(const p of a.p0_originals||[]){
  check(p.post_id===Number(p.slot.split(":")[0])&&p.live_wordpress_source_identical===true&&/^https:\/\//.test(p.stored_original_url||""),"p0_source_"+p.slot);
  check(p.web_retriever_only?.method==="EXTERNAL_WEB_RETRIEVER_NOT_GUEST","p0_retriever_"+p.slot);
  check(/^https:\/\//.test(p.candidate_catalog||"")&&typeof p.candidate_rights==="string","p0_catalog_"+p.slot);
  check(p.origin_http_status===null&&p.guest_http_status===null&&p.guest_current_src===null&&p.guest_decoded_px===null&&p.guest_wire_bytes===null,"p0_no_guest_"+p.slot);
  check(p.rights_cleared===false&&p.cache_authorized===false&&p.wordpress_upload_authorized===false,"p0_release_hold_"+p.slot);
 }
 check(a.oversized?.length===15&&new Set(a.oversized.map(x=>x.media_id)).size===15,"large_count");
 let sum=0,n=0,inlineB=0;
 for(const x of a.oversized||[]){
  sum+=x.stored_bytes||0;
  check(x.stored_bytes>1500000&&x.live_wp_stored_bytes_identical===true&&x.live_wp_original_url_identical===true&&x.live_wp_native_dimensions_identical===true,"large_exact_"+x.media_id);
  check(x.conditional_960px?.[0]<=Math.min(960,x.native_dimensions?.[0]||0)&&x.conditional_960px?.[1]<=x.native_dimensions?.[1],"large_no_upscale_"+x.media_id);
  check(x.guest_current_src===null&&x.guest_wire_bytes===null&&x.css_width===null&&x.dpr===null,"large_no_guest_"+x.media_id);
  check(x.derivative_authorized===false&&x.rehosting_authorized===false,"large_no_publish_"+x.media_id);
  if(x.live_inline_source_verified){n++;inlineB+=x.stored_bytes;check(x.inline_posts?.length>0&&x.live_published_srcs?.length>0,"live_inline_"+x.media_id)}
 }
 check(sum===47096779&&n===11&&inlineB===38480915,"sum_mismatch");
 check(r.reported_42_guest_confirmed===false&&r.confirmed_guest_failures===0&&r.proposed_76pct_measured===false&&r.actual_guest_transfer_bytes===null,"unproven_claims");
 check(["wordpress_writes","downloads","caches","production_repairs","deployments","homepage_changes","spend_usd"].every(k=>r[k]===0),"no_writes");
 return {ok:!errors.length,errors};
}
module.exports={validate};
