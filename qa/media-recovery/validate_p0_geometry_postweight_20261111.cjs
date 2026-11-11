"use strict";
function validate(plan, bridge) {
  const e = [];
  const bad = (cond, msg) => { if (cond) e.push(msg); };
  bad(!plan || plan.schema !== "fv-media-geometry-postweight-triage-v1", "schema");
  bad(!bridge || bridge.schema !== "fv-media-recovery-siteqa-bridge-v1", "bridge");
  if (e.length) return { ok:false, errors:e };
  bad(plan.authority.bridge_blob_sha !== "d1a9c7a499510ec37bcdba5858d45165752587e0", "immutable_bridge_sha");
  const expected=["285:5","285:2","287:5","418:1","418:2","407:1"];
  bad(JSON.stringify(plan.p0_source_queue.map(r=>r.slot))!==JSON.stringify(expected),"queue_order");
  for(const src of bridge.p0_queue) {
    const r=plan.p0_source_queue.find(x=>x.slot===src.slot);
    bad(!r || r.original_src!==src.original_src, "source_drift:"+src.slot);
    if(!r) continue;
    bad(JSON.stringify(r.retriever_only)!==JSON.stringify(src.retriever_only),"retriever_drift:"+src.slot);
    bad(r.guest_http_status!==null || r.guest_current_src!==null || r.guest_natural_px!==null || r.cold_encoded_image_bytes!==null,"fabricated_guest_evidence:"+src.slot);
    bad(r.exact_visual_identity_proven!==false || r.reuse_rights_cleared!==false || r.cache_or_wp_upload_approved!==false, "unapproved_candidate:"+src.slot);
  }
  const t=plan.tmi_285_5_geometry;
  bad(!t || t.source_request_url !== bridge.p0_queue[0].original_src,"tmi_source");
  if(t){
    bad(JSON.stringify(t.commons_native_px)!=="[819,614]" || t.width_limited_if_preserve_all_pixels_px!==819,"no_upscale");
    bad(t.saymedia_source_transform.aspect_ratio!=="16:9" || t.saymedia_source_transform.crop_mode!=="fill" || t.saymedia_source_transform.requested_width_px!==1200 || t.saymedia_source_transform.requested_dimensions_are_actual_browser_dimensions!==false,"source_transform");
    bad(JSON.stringify(t.hypothetical_16_9_crop_px)!=="[819,461]" || t.hypothetical_vertical_pixels_removed!==153 || Math.abs(t.direct_original_aspect_ratio-819/614)>1e-12, "hypothetical_crop_math");
    bad(t.crop_scene_parity_verified!==false || t.crop_approved!==false || t.no_upscale!==true || t.observed_bytes!==null || t.browser_rendered_dimensions!==null || t.file_bytes_are_not_guest_transfer_bytes!==true,"crop_evidence_honesty");
    bad(t.decision!=="HOLD_FOR_GUEST_CAPTURE_SCENE_CROP_RIGHTS_EDITOR", "crop_release_hold");
  }
  const arr=bridge.oversized_media, q=plan.oversized_media;
  bad(arr.length!==15 || q.source_record_count!==15 || q.decimal_threshold_bytes!==1500000, "oversize_scope");
  const all=arr.reduce((s,r)=>s+r.stored_original_bytes,0);
  const inline=arr.filter(r=>r.inline_post_ids.length);
  const not=arr.filter(r=>!r.inline_post_ids.length);
  bad(all!==47096779 || q.total_stored_original_bytes!==all, "all_storage_sum");
  bad(inline.length!==11 || q.inline_linked_original_count!==11 || q.inline_linked_stored_original_bytes!==inline.reduce((s,r)=>s+r.stored_original_bytes,0), "inline_sum");
  bad(not.length!==4 || q.not_linked_inline_original_count!==4 || q.not_linked_inline_stored_original_bytes!==not.reduce((s,r)=>s+r.stored_original_bytes,0), "not_inline_sum");
  const p=arr.filter(r=>r.generated_subsizes===0);
  bad(p.length!==5 || q.no_subsize_pngs.original_count!==5 || q.no_subsize_pngs.stored_original_bytes!==p.reduce((s,r)=>s+r.stored_original_bytes,0)||JSON.stringify(q.no_subsize_pngs.media_ids)!==JSON.stringify(p.map(r=>r.media_id).sort((a,b)=>a-b)),"png_sum");
  bad(JSON.stringify(q.no_subsize_pngs.conditional_output_px)!=="[960,540]" || q.no_subsize_pngs.rights_clearance!==false,"png_release_hold");
  const derived=new Map();
  for(const r of arr)for(const pid of r.inline_post_ids){
    if(!derived.has(pid))derived.set(pid,{post_id:pid,media_ids:[],stored_original_bytes:0,delivery:"direct_original_in_stored_src"});
    const x=derived.get(pid);x.media_ids.push(r.media_id);x.stored_original_bytes+=r.stored_original_bytes;
    if(r.published_direct_srcs.some(s=>s.startsWith("https://i0.wp.com/")))x.delivery="jetpack_fit_transformed_in_stored_src";
  }
  const expectedPost=[...derived.values()].map(x=>({...x,media_ids:x.media_ids.sort((a,b)=>a-b)})).sort((a,b)=>b.stored_original_bytes-a.stored_original_bytes);
  bad(JSON.stringify(q.per_post_storage_priority.map(x=>({post_id:x.post_id,media_ids:x.media_ids,stored_original_bytes:x.stored_original_bytes,delivery:x.delivery})))!==JSON.stringify(expectedPost),"post_storage_grouping");
  const target=plan.claimed_76_percent;
  bad(target.target_pct!==76 || target.actual_cold_baseline_image_wire_bytes!==null || target.actual_cold_candidate_image_wire_bytes!==null || target.actual_saving_pct!==null || target.eligible_to_report!==false,"fabricated_76_percent");
  bad(plan.release.guest_verified_broken!==0 || plan.release.wp_production_writes!==0 || plan.release.asset_downloads!==0 || plan.release.asset_caching!==0 || plan.release.homepage_design_changes!==0 || plan.release.spend_usd!==0 || plan.release.staging_approved!==false || plan.release.production_approved!==false,"unauthorized_release");
  return {ok:e.length===0,errors:e};
}
module.exports={validate};
