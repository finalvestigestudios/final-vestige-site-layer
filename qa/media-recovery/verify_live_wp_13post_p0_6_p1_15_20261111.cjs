'use strict';
// Offline verification. Does not fetch, alter or cache media.
function verify(s){
 const e=[],req=(x,n)=>{if(!x)e.push(n)},r=s.release||{};
 req(s.schema==="fv-live-cms-13-post-media-verified-v1","schema");
 req(s.cohort?.current_published_posts===66&&s.cohort?.current_media_images===122&&s.cohort?.posts_fetched===13&&s.cohort?.inline_images_in_fetched_posts===58,"cohort");
 req(s.media_totals?.original_stored_bytes===70627679&&s.media_totals?.oversize_original_count===15&&s.media_totals?.oversize_bytes===47096779&&s.media_totals?.oversize_threshold_bytes===1500000,"media totals");
 req(s.media_totals?.recent_small_item?.bytes===72773,"recent item");
 req(s.p0?.length===6&&new Set(s.p0.map(x=>x.slot)).size===6,"P0 count");
 for(const x of s.p0||[]){
  req(x.post_status==="publish"&&x.exact_src_match===true&&x.stored_src===x.expected_src&&/^https:\/\//.test(x.stored_src||""),"P0 source "+x.slot);
  req(x.post_id===Number(x.slot.split(":")[0])&&/^https:\/\//.test(x.primary_or_publisher_catalog||""),"P0 identity "+x.slot);
  req(x.prior_retriever_wrapper?.method==="EXTERNAL_WEB_RETRIEVER_NOT_GUEST","P0 wrapper "+x.slot);
  req(x.guest_http===null&&x.origin_http===null&&x.guest_decoded_px===null&&x.cold_wire_bytes===null&&x.visitor_broken===null,"P0 guest hold "+x.slot);
  req(x.rights_cleared===false&&x.cache_approved===false&&x.wp_upload_approved===false,"P0 rights "+x.slot);
 }
 req(s.oversized?.length===15&&new Set(s.oversized.map(x=>x.media_id)).size===15,"P1 15 unique");
 let b=0,inline=0,inlineB=0;
 for(const x of s.oversized||[]){
  b+=x.bytes||0;req(x.bytes>1500000&&x.bytes===x.expected_bytes&&x.exact_url_match===true&&x.source_url===x.expected_url,"P1 exact original "+x.media_id);
  req(JSON.stringify(x.native_px)===JSON.stringify(x.expected_native_px)&&x.native_px[0]>0&&x.native_px[1]>0,"P1 native "+x.media_id);
  req(x.conditional_960px?.[0]<=Math.min(960,x.native_px[0])&&x.conditional_960px?.[1]<=x.native_px[1],"P1 no upscale "+x.media_id);
  req(x.guest_current_src===null&&x.guest_wire_bytes===null&&x.painted_css_px===null&&x.dpr===null,"P1 guest hold "+x.media_id);
  req(x.rights_cleared===false&&x.derivative_approved===false&&x.cache_approved===false&&x.wp_upload_approved===false,"P1 rights "+x.media_id);
  if(x.live_inline_post_ids?.length){inline++;inlineB+=x.bytes;req(JSON.stringify(x.live_inline_post_ids)===JSON.stringify(x.expected_inline_post_ids)&&x.matched_srcs?.length>0,"P1 published match "+x.media_id);}
 }
 req(b===47096779&&inline===11&&inlineB===38480915,"P1 aggregate");
 req(r.claimed_broken===42&&r.guest_confirmed_broken===0&&r.claimed_weight_reduction_percent===76&&r.measured_reduction===false&&r.guest_wire_bytes===null,"false claims");
 req(["wordpress_writes","third_party_downloads","caches","prod_repairs","homepage_changes","deployments","spend_usd"].every(k=>r[k]===0),"no mutation");
 return {ok:e.length===0,errors:e};
}
module.exports={verify};
