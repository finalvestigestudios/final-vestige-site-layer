"use strict";
// Source-integrity only: offline, no HTTP/WordPress/media downloads or media changes.
// Run: node qa/media-recovery/validate_teton_291_six_20261110.cjs
const FILE="qa/media-recovery/teton_291_six_nara_byui_identity_20261110.json";
const KEYS=["291:0","291:1","291:2","291:3","291:4","291:5"];
const SHA="94924b3111c7c004ec146943d64307ed1c0f8b3a";
const FROZEN_SHA="92a904c8da1ace1f972b2f00adf1a4847dde2b99";
function verify(a,now,prev,f) {
  const errors=[],check=(x,s)=>{if(!x) errors.push(s);};
  check(a?.schema==="fv-media-teton-291-six-20261110-v1","audit_schema");
  check(now?.schema==="fv-media-coverage-246-exact-v1","current_schema");
  check(prev?.schema==="fv-media-coverage-240-exact-v1","previous_schema");
  check(f?.schema==="fv-teton-291-originals-fixture-v1","fixture_schema");
  if(!a?.rows||!now?.rows||!prev?.rows||!f?.images) return [...errors,"missing_rows"];
  check(a.rows.length===6&&f.images.length===6,"six_rows");
  check(now.rows.length===288&&prev.rows.length===288,"frozen_288_positions");
  check(new Set(a.rows.map(x=>x.slot)).size===6&&KEYS.every(s=>a.rows.some(x=>x.slot===s)),"unique_exact_keys");
  check(new Set(now.rows.map(x=>x.slot)).size===288,"unique_coverage_slots");
  check(a.frozen_source?.git_blob_sha===FROZEN_SHA&&f.frozen_source_blob_sha===FROZEN_SHA,"original_frozen_git_blob");
  check(a.live_wordpress_read_only?.exact_src_matches===6&&a.live_wordpress_read_only?.status==="publish","live_source_recheck");
  check(a.summary?.unique_original_urls===5&&a.summary?.positions===6&&a.summary?.guest_http_confirmed===0,"no_double_count_no_guest");
  check(now.counts?.researched_unique===246&&now.counts?.unresearched===42&&now.counts?.total_external===288,"coverage_246_of_288");
  check(now.counts?.total_evidence_records===251&&now.counts?.duplicated_with_prior===2,"evidence_251");
  check(now.counts?.guest_browser_confirmed_loaded===0&&now.counts?.guest_browser_confirmed_broken===0,"no_browser_claim");
  check(now.counts?.reported_42_broken_browser_confirmed===false&&now.counts?.wire_reduction_76_percent_measured===false,"unmeasured_42_and_76");
  check(now.counts?.oversized_wp_originals_gt_1500000===15&&now.counts?.oversized_stored_original_bytes===47096779,"storage_not_wire");
  const byPrev=new Map(prev.rows.map(x=>[x.slot,x])),byNow=new Map(now.rows.map(x=>[x.slot,x])),byF=new Map(f.images.map(x=>[x.slot,x]));
  const refs=now.batch_sources.filter(x=>x.file===FILE);
  check(refs.length===1&&refs[0].blob_sha===SHA&&refs[0].source_records===6,"precise_batch_blob");
  let changed=0;
  for(const slot of KEYS){
    const row=a.rows.find(x=>x.slot===slot), before=byPrev.get(slot), after=byNow.get(slot),original=byF.get(slot);
    if(!row||!before||!after||!original){errors.push("missing_"+slot);continue;}
    check(before.evidence.length===0&&before.candidate_sources.length===0,"previously_unresearched_"+slot);
    check(row.post_id===291&&row.published_src===original.src&&row.published_alt===original.alt&&row.post_url===original.post_url,"original_source_and_alt_"+slot);
    check(before.stored_url===row.published_src&&after.stored_url===before.stored_url&&after.origin_host===before.origin_host,"frozen_url_"+slot);
    check(after.evidence.length===1&&after.evidence[0].path===FILE&&after.evidence[0].blob_sha===SHA,"source_evidence_binding_"+slot);
    check(after.candidate_sources.length===1&&after.candidate_sources[0].authoritative_primary_url===row.authoritative_primary_url,"catalog_binding_"+slot);
    check(row.catalog_px===null&&row.conditional_960px===null,"dont_invent_intrinsic_px_"+slot);
    check(row.authoritative_primary_url?.startsWith("https://")===true&&row.catalog_url?.startsWith("https://")===true,"authoritative_url_"+slot);
    for(const key of ["origin_http_status","guest_http_status","guest_current_src","guest_decoded_px","guest_wire_bytes","guest_broken"])check(row[key]===null,"unmeasured_"+slot+"_"+key);
    for(const key of ["rights_cleared","same_photo_binary_identity_proved","download_authorized","cache_authorized","wordpress_media_upload_authorized","post_rewrite_authorized"])check(row[key]===false,"release_hold_"+slot+"_"+key);
    for(const key of ["rights_cleared","exact_pixel_match_verified","download_authorized","cache_authorized","wordpress_media_upload_authorized","post_rewrite_authorized"])check(after[key]===false,"register_hold_"+slot+"_"+key);
    for(const key of ["guest_http_status","guest_current_src","guest_decoded_px","guest_wire_bytes","guest_broken"])check(after[key]===null,"register_unmeasured_"+slot+"_"+key);
    check(row.web_retriever_observation.includes("NOT_GUEST")||row.web_retriever_observation.includes("NOT_ORIGIN_STATUS"),"retriever_not_http_"+slot);
  }
  for(const [key,row] of byPrev){const b=byNow.get(key);if(!b)continue;if(JSON.stringify(row)!==JSON.stringify(b)){changed++;if(!KEYS.includes(key))errors.push("unrelated_position_modified_"+key);}}
  check(changed===6,"exactly_six_rows_changed");
  check(now.rows.filter(x=>x.evidence.length).length===246&&now.rows.filter(x=>!x.evidence.length).length===42,"recomputed_coverage");
  const cleanup=a.rows.find(x=>x.slot==="291:2"),repeat=a.rows.find(x=>x.slot==="291:5");
  const nara=a.rows.find(x=>x.slot==="291:0"),byui=a.rows.find(x=>x.slot==="291:3");
  check(!!(cleanup&&repeat&&cleanup.published_src===repeat.published_src&&cleanup.published_alt!==repeat.published_alt),"identical_url_conflicting_alt");
  check(!!(cleanup?.visual_integrity_note?.includes("debris cleanup")&&cleanup?.proposed_alt_editor_review?.includes("debris")),"wrong_scene_flag");
  check(!!nara?.rights_observation?.includes("contractor"),"nara_contract_worker_not_public_domain");
  check(!!byui?.rights_observation?.includes("permission"),"byui_licensing_hold");
  return errors;
}
module.exports={verify};
if(require.main===module){
  const fs=require("node:fs"),path=require("node:path");
  const p=x=>JSON.parse(fs.readFileSync(path.join(__dirname,x),"utf8"));
  const errors=verify(p("teton_291_six_nara_byui_identity_20261110.json"),p("coverage_246_exact_pr1703_20261110.json"),p("coverage_240_exact_pr1703_20261110.json"),p("fixture_teton_291_source_20261110.json"));
  if(errors.length){console.error(errors.join("\n"));process.exitCode=1;}
  else console.log("Teton #291: six exact-source identities + 282 unaffected slots + safety gates PASS");
}
