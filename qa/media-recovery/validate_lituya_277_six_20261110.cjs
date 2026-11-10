"use strict";
// Offline, fail-closed external-media source audit; NO HTTP, media downloads or WordPress writes.
const KEYS=["277:0","277:1","277:2","277:3","277:4","277:5"];
const AUDIT_PATH="qa/media-recovery/lituya_277_six_usgs_nasa_composite_rights_20261110.json";
const AUDIT_SHA="22b917e632f9429456c0582355f2f912c2ed614b";
const PREV_SHA="874304f7b77534c336edf79916b6e70c76108d9c";
const FROZEN_SHA="92a904c8da1ace1f972b2f00adf1a4847dde2b99";
function verify(a,now,prev,f){
  const errors=[],check=(ok,why)=>{if(!ok)errors.push(why);};
  check(a?.schema==="fv-media-lituya-277-six-20261110-v1","audit_schema");
  check(now?.schema==="fv-media-coverage-252-exact-v1","current_schema");
  check(prev?.schema==="fv-media-coverage-246-exact-v1","prior_schema");
  check(f?.schema==="fv-lituya-277-original-live-source-fixture-v1","live_fixture_schema");
  if(!Array.isArray(a?.rows)||!Array.isArray(now?.rows)||!Array.isArray(prev?.rows)||!Array.isArray(f?.images))return [...errors,"missing_rows"];
  check(a.rows.length===6&&f.images.length===6,"exactly_six_live_sources");
  check(a.live_wordpress_read_only?.status==="publish"&&a.live_wordpress_read_only?.exact_src_matches_frozen===6&&a.live_wordpress_read_only?.live_alt_captured===6&&a.live_wordpress_read_only?.historical_alt_match_verified===false,"published_live_source_recheck");
  check(a.live_wordpress_read_only?.modified===f.live_modified,"frozen_live_modified");
  check(a.scope_note?.includes("NOT independently matched")===true,"no_invented_historical_alt_match");
  check(a.frozen_source?.git_blob_sha===FROZEN_SHA&&f.frozen_source_blob_sha===FROZEN_SHA,"frozen_git_anchor");
  check(now.prior_246_register?.blob_sha===PREV_SHA,"previous_register_git_anchor");
  check(now.rows.length===288&&prev.rows.length===288,"288_frozen_slots");
  check(new Set(now.rows.map(x=>x.slot)).size===288,"unique_register_keys");
  check(new Set(a.rows.map(x=>x.slot)).size===6&&KEYS.every(s=>a.rows.some(x=>x.slot===s)),"six_unique_lituya_slots");
  check(now.counts?.researched_unique===252&&now.counts?.unresearched===36&&now.counts?.total_external===288,"coverage_252");
  check(now.counts?.total_evidence_records===257&&now.counts?.duplicated_with_prior===2,"exact_evidence_count");
  check(now.counts?.guest_browser_confirmed_broken===0&&now.counts?.guest_browser_confirmed_loaded===0,"no_guest_status_claim");
  check(now.counts?.reported_42_broken_browser_confirmed===false&&now.counts?.wire_reduction_76_percent_measured===false,"42_and_76_unproven");
  check(now.counts?.oversized_wp_originals_gt_1500000===15&&now.counts?.oversized_stored_original_bytes===47096779,"stored_not_transferred");
  check(a.summary?.web_retriever_displayed===4&&a.summary?.web_retriever_inaccessible===2&&a.summary?.guest_http_confirmed===0,"retriever_not_guest");
  check(a.summary?.unique_original_urls===6&&new Set(a.rows.map(x=>x.published_src)).size===6,"unique_original_urls");
  check(now.rows.filter(x=>x.evidence.length).length===252&&now.rows.filter(x=>!x.evidence.length).length===36,"recomputed_coverage");
  const refs=now.batch_sources.filter(x=>x.file===AUDIT_PATH);
  check(refs.length===1&&refs[0].blob_sha===AUDIT_SHA&&refs[0].source_records===6,"source_audit_blob_binding");
  const byNow=new Map(now.rows.map(x=>[x.slot,x])),byPrev=new Map(prev.rows.map(x=>[x.slot,x])),byLive=new Map(f.images.map(x=>[x.slot,x]));
  let changed=0;
  for(const slot of KEYS){
    const row=a.rows.find(x=>x.slot===slot),before=byPrev.get(slot),after=byNow.get(slot),live=byLive.get(slot);
    if(!(row&&before&&after&&live)){errors.push("missing_"+slot);continue;}
    check(row.post_id===277&&row.post_url===live.post_url&&row.published_src===live.src&&row.published_alt===live.alt,"live_url_alt_"+slot);
    check(row.live_source_confirmed===true&&row.published_src===before.stored_url&&after.stored_url===before.stored_url,"immutable_original_"+slot);
    check(before.evidence.length===0&&before.candidate_sources.length===0,"new_only_"+slot);
    check(after.evidence.length===1&&after.evidence[0].path===AUDIT_PATH&&after.evidence[0].blob_sha===AUDIT_SHA,"register_evidence_"+slot);
    check(after.candidate_sources.length===1&&after.candidate_sources[0].authoritative_primary_url===row.authoritative_primary_url,"candidate_match_"+slot);
    check(row.catalog_url?.startsWith("https://")&&row.authoritative_primary_url?.startsWith("https://"),"primary_http_urls_"+slot);
    check(row.web_retriever_observation.endsWith("NOT_GUEST")||row.web_retriever_observation.endsWith("NOT_ORIGIN_STATUS"),"retriever_not_http_"+slot);
    for(const x of ["origin_http_status","guest_http_status","guest_current_src","guest_decoded_px","guest_wire_bytes","guest_broken"])check(row[x]===null,"unmeasured_"+slot+"_"+x);
    for(const x of ["guest_http_status","guest_current_src","guest_decoded_px","guest_wire_bytes","guest_broken"])check(after[x]===null,"register_unmeasured_"+slot+"_"+x);
    for(const x of ["rights_cleared","exact_binary_identity_proved","download_authorized","cache_authorized","wordpress_media_upload_authorized","post_rewrite_authorized"])check(row[x]===false,"release_hold_"+slot+"_"+x);
    for(const x of ["rights_cleared","exact_pixel_match_verified","download_authorized","cache_authorized","wordpress_media_upload_authorized","post_rewrite_authorized"])check(after[x]===false,"register_hold_"+slot+"_"+x);
    check(row.dimension_rule?.includes("Never upscale"),"geometry_rule_"+slot);
    if(slot!=="277:5")check(row.source_original_intrinsic_px===null&&row.conditional_960px===null,"no_unverified_intrinsics_"+slot);
    check(after.candidate_sources[0].conditional_960px?.[0]<=960,"candidate_no_upscale_"+slot);
  }
  for(const [slot,old] of byPrev){const current=byNow.get(slot);if(!current)continue;if(JSON.stringify(current)!==JSON.stringify(old)){changed++;if(!KEYS.includes(slot))errors.push("unrelated_mutated_"+slot);}}
  check(changed===6,"only_six_changed");
  const diagram=a.rows.find(x=>x.slot==="277:0"),research=a.rows.find(x=>x.slot==="277:1"),greeting=a.rows.find(x=>x.slot==="277:3"),arrows=a.rows.find(x=>x.slot==="277:4"),nasa=a.rows.find(x=>x.slot==="277:5");
  check(diagram?.visual_integrity_note?.includes("two-panel")&&diagram?.proposed_alt_editor_review?.includes("Two-panel"),"real_two_panel_not_single_photo");
  check(research?.rights_observation?.includes("copyright")&&research?.visual_integrity_note?.includes("MULTIPANEL"),"research_composite_rights");
  check(greeting?.rights_observation?.includes("greeting-card")&&greeting?.cache_authorized===false,"no_commercial_greeting_card_mirror");
  check(arrows?.proposed_alt_editor_review?.includes("arrows"),"annotated_arrows_alt");
  check(JSON.stringify(nasa?.source_original_intrinsic_px)==="[720,480]"&&JSON.stringify(nasa?.conditional_960px)==="[720,480]","nasa_native_720_no_upscale");
  check(nasa?.source_authority?.includes("NASA")&&nasa?.visual_integrity_note?.includes("false-color"),"nasa_2020_false_color_not_1958");
  return errors;
}
module.exports={verify};
if(require.main===module){
const fs=require("node:fs"),path=require("node:path");
const read=n=>JSON.parse(fs.readFileSync(path.join(__dirname,n),"utf8"));
const errors=verify(read("lituya_277_six_usgs_nasa_composite_rights_20261110.json"),read("coverage_252_exact_pr1703_20261110.json"),read("coverage_246_exact_pr1703_20261110.json"),read("fixture_lituya_277_live_source_20261110.json"));
if(errors.length){console.error(errors.join("\n"));process.exitCode=1;}else console.log("Lituya post 277 six sources, 282 preserved slots, and rights/browser holds PASS");
}
