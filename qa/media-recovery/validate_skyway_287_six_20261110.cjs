"use strict";
/**
 * Fail-closed, offline source-evidence validator. No fetches, media writes or WP calls.
 * Invocation: require("./validate_skyway_287_six_20261110.cjs").validateSkyway(audit, next, prev)
 */
function validateSkyway(audit, next, prev) {
  const errors=[];
  const test=(ok,code)=>{if(!ok)errors.push(code);};
  if(!audit||!next||!prev||!Array.isArray(audit.rows)||!Array.isArray(next.rows)||!Array.isArray(prev.rows)) {
    return {ok:false,errors:["MISSING_REQUIRED_ROWS"]};
  }
  const changedSlots=new Set(["287:0","287:1","287:2","287:3","287:4"]);
  const allSlots=["287:0","287:1","287:2","287:3","287:4","287:5"];
  const oldBy=new Map(prev.rows.map(x=>[x.slot,x]));
  const newBy=new Map(next.rows.map(x=>[x.slot,x]));
  const auditBy=new Map(audit.rows.map(x=>[x.slot,x]));
  test(audit.schema==="fv-skyway-287-six-image-source-reconciliation-v1","SCHEMA");
  test(audit.post?.source_urls_exact_six_of_six===true&&audit.post?.live_alt_captured_count===6,"LIVE_SOURCE_READBACK");
  test(audit.post?.historical_alt_equality_verified===false,"DO_NOT_CLAIM_HISTORICAL_ALT_PROOF");
  test(prev.rows.length===288&&next.rows.length===288,"EXACT_288_SLOTS");
  test(oldBy.size===288&&newBy.size===288&&auditBy.size===6,"UNIQUE_SLOTS");
  test(allSlots.every(s=>auditBy.has(s)&&oldBy.has(s)&&newBy.has(s)),"ALL_SKYWAY_SLOTS");
  test(next.counts?.researched_unique===257&&next.counts?.unresearched===31&&next.counts?.total_external===288,"COVERAGE_COUNT");
  test(next.counts?.total_evidence_records===262,"SOURCE_EVIDENCE_COUNT");
  test(next.counts?.guest_browser_confirmed_broken===0&&next.counts?.guest_browser_confirmed_loaded===0,"NO_GUEST_CLAIMS");
  test(next.counts?.wire_reduction_76_percent_measured===false&&next.counts?.reported_42_broken_browser_confirmed===false,"NO_FAKE_PERFORMANCE");
  test(next.counts?.oversized_wp_originals_gt_1500000===15&&next.counts?.oversized_stored_original_bytes===47096779,"STORAGE_ONLY_BASELINE");
  test(next.rows.filter(x=>x.evidence?.length).length===257&&next.rows.filter(x=>!x.evidence?.length).length===31,"DERIVED_COVERAGE");
  test(next.rows.reduce((sum,x)=>sum+(x.evidence||[]).length,0)===262,"DERIVED_EVIDENCE_ROWS");
  test(audit.rows.filter(x=>x.retriever_observation==="IMAGE_RENDERED_THROUGH_WEB_RETRIEVER").length===5,"FIVE_RETRIEVER_PREVIEWS");
  test(auditBy.get("287:5")?.retriever_wrapper_status===404,"LEGACY_URL_WRAPPER_404_NOT_GUEST");
  test(auditBy.get("287:5")?.candidate_asset_url==="https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg","PUBLISHER_CDN_CANDIDATE");
  test(auditBy.get("287:4")?.proposed_alt_for_editor?.includes("crane barge"),"CRANE_SCENE_ALT_CORRECTION");
  test(auditBy.get("287:2")?.rights_issue?.includes("newspaper"),"NEWSPAPER_DIAGRAM_COPYRIGHT");
  test(audit.rows.filter(x=>x.proposed_alt_for_editor).length===2,"TWO_EDITORIAL_HOLDS");
  test(audit.counts?.new_positions_researched===5&&audit.counts?.previously_researched===1,"NO_DOUBLE_COUNT");
  test(audit.rows.every(x=>x.source_native_px===null&&x.conditional_max960_px===null&&x.exact_binary_match_verified===false),"NO_INVENTED_GEOMETRY");
  test(audit.rows.every(x=>x.guest_http_status===null&&x.origin_http_status===null&&x.guest_transfer_bytes===null&&x.guest_broken===null),"NO_INVENTED_HTTP_OR_BYTES");
  test(audit.rows.every(x=>x.rights_cleared===false&&!x.download_authorized&&!x.cache_authorized&&!x.wordpress_upload_authorized&&!x.post_rewrite_authorized),"NO_UNLICENSED_ACTION");
  test(audit.rows.every(x=>x.sizing_rule.includes("verified_native_width")&&x.sizing_rule.includes("no upscaling")),"NO_UPSCALE_RULE");
  test(newBy.get("287:5")&&JSON.stringify(newBy.get("287:5"))===JSON.stringify(oldBy.get("287:5")),"PRIOR_P0_SLOT_UNCHANGED");
  const changed=[];
  for(const before of prev.rows) {
    const after=newBy.get(before.slot);
    if(!after){errors.push("MISSING_SLOT_"+before.slot);continue}
    if(JSON.stringify(before)!==JSON.stringify(after))changed.push(before.slot);
    if(!changedSlots.has(before.slot))test(JSON.stringify(before)===JSON.stringify(after),"UNRELATED_MUTATED_"+before.slot);
  }
  test(changed.length===5&&changed.every(x=>changedSlots.has(x)),"EXACT_FIVE_CHANGED");
  for(const slot of changedSlots) {
    const b=oldBy.get(slot),n=newBy.get(slot),a=auditBy.get(slot);
    if(!b||!n||!a){errors.push("MISSING_TARGET_"+slot);continue;}
    test(b.stored_url===n.stored_url&&a.original_url===b.stored_url,"SOURCE_IDENTITY_"+slot);
    test((b.evidence||[]).length===0&&(n.evidence||[]).length===1,"ONE_NEW_EVIDENCE_"+slot);
    test(n.evidence?.[0]?.blob_sha===next.batch_sources?.at(-1)?.blob_sha,"BATCH_SHA_PIN_"+slot);
    test(n.evidence?.[0]?.path==="qa/media-recovery/skyway_287_six_live_retriever_rights_20261110.json","BATCH_PATH_"+slot);
    test(n.guest_http_status===null&&n.guest_broken===null&&n.guest_wire_bytes===null,"GUEST_NULL_"+slot);
    test(n.rights_cleared===false&&!n.cache_authorized&&!n.wordpress_media_upload_authorized&&!n.post_rewrite_authorized,"PERMISSIONS_BLOCKED_"+slot);
    test(n.candidate_sources?.length===1&&n.candidate_sources[0].conditional_960px===null&&!n.candidate_sources[0].item_rights_cleared,"CANDIDATE_HOLD_"+slot);
  }
  return {ok:errors.length===0,errors,changed,checks:"fail-closed source/rights/browser gates"};
}
module.exports={validateSkyway};
