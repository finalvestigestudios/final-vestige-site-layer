"use strict";
// Offline fail-closed verifier: no URL fetch, no WordPress changes, no image binary operations.
// Run from repository root: node qa/media-recovery/validate_quebec_276_six_20261110.cjs
const KEYS = ["276:0","276:1","276:2","276:3","276:4","276:5"];
const BATCH = "qa/media-recovery/quebec_276_six_1907_1916_archival_20261110.json";
function verify(audit, current, preceding, fixture) {
  const errors=[];
  const check=(ok,reason)=>{if(!ok) errors.push(reason);};
  check(audit && audit.schema==="fv-media-quebec-276-six-20261110-v1","audit_schema");
  check(current && current.schema==="fv-media-coverage-240-exact-v1","coverage_schema");
  check(preceding && preceding.schema==="fv-media-coverage-234-exact-v1","predecessor_schema");
  check(fixture && fixture.schema==="fv-six-source-frozen-fixture-276-v1","fixture_schema");
  if(!audit?.rows || !current?.rows || !preceding?.rows || !fixture?.images) return [...errors,"missing_rows"];
  const a=audit.rows,c=current.rows,p=preceding.rows,f=fixture.images;
  check(a.length===6 && f.length===6,"batch_and_fixture_six");
  check(c.length===288 && p.length===288,"cohort_288");
  check(new Set(a.map(x=>x.slot)).size===6 && KEYS.every(x=>a.some(y=>y.slot===x)),"six_exact_unique_slots");
  check(new Set(c.map(x=>x.slot)).size===288,"unique_coverage_slots");
  check(audit.frozen_fixture?.blob_sha===fixture.origin_blob_sha && fixture.origin_blob_sha==="6df3251e5a67a971d87a516a1ba4a0cc32f51f96","frozen_source_blob");
  check(current.counts?.researched_unique===240 && current.counts?.unresearched===48 && current.counts?.total_external===288,"coverage_counts");
  check(current.counts?.total_evidence_records===245 && current.counts?.duplicated_with_prior===2,"evidence_counts");
  check(current.counts?.guest_browser_confirmed_broken===0 && current.counts?.guest_browser_confirmed_loaded===0,"no_guest_proof");
  check(current.counts?.reported_42_broken_browser_confirmed===false && current.counts?.wire_reduction_76_percent_measured===false,"no_invented_sitewide_metrics");
  check(current.counts?.oversized_wp_originals_gt_1500000===15 && current.counts?.oversized_stored_original_bytes===47096779,"oversized_storage_not_transfer");
  const prev=new Map(p.map(x=>[x.slot,x])), now=new Map(c.map(x=>[x.slot,x])), frozen=new Map(f.map(x=>[x.key,x]));
  const batches=current.batch_sources.filter(x=>x.file===BATCH);
  check(batches.length===1 && batches[0].source_records===6 && /^[0-9a-f]{40}$/.test(batches[0].blob_sha),"batch_reference_sha");
  let changed=0, confirmedDisplay=0, errors520=0;
  for(const key of KEYS) {
    const item=a.find(x=>x.slot===key), record=now.get(key), original=prev.get(key), snapshot=frozen.get(key);
    if(!item || !record || !original || !snapshot) {errors.push("missing_"+key);continue;}
    check(original.evidence.length===0 && original.candidate_sources.length===0,"previously_pending_"+key);
    check(item.post_id===276 && item.post_url===snapshot.post_url && item.published_src===snapshot.source_url && item.published_alt===snapshot.alt,"literal_html_identity_"+key);
    check(item.published_src===original.stored_url && record.stored_url===original.stored_url && record.origin_host===original.origin_host,"frozen_ledger_identity_"+key);
    check(record.evidence.length===1 && record.evidence[0].path===BATCH && record.evidence[0].blob_sha===batches[0].blob_sha,"evidence_binding_"+key);
    check(record.candidate_sources.length===1 && record.candidate_sources[0].authoritative_primary_url===item.authoritative_primary_url,"candidate_binding_"+key);
    const hold=["download_authorized","cache_authorized","wordpress_media_upload_authorized","post_rewrite_authorized","item_rights_cleared","exact_binary_match_verified"];
    for(const field of hold) check(item[field]===false,"release_hold_"+key+"_"+field);
    for(const field of ["origin_http_status","guest_http_status","guest_current_src","guest_decoded_px","guest_wire_bytes","guest_broken"]) check(item[field]===null,"unmeasured_status_"+key+"_"+field);
    for(const field of ["guest_http_status","guest_current_src","guest_decoded_px","guest_wire_bytes","guest_broken"]) check(record[field]===null,"coverage_unmeasured_"+key+"_"+field);
    for(const field of ["rights_cleared","exact_pixel_match_verified","download_authorized","cache_authorized","wordpress_media_upload_authorized","post_rewrite_authorized"]) check(record[field]===false,"coverage_release_hold_"+key+"_"+field);
    if(item.web_retriever_observation==="IMAGE_DISPLAYED_BY_WEB_RETRIEVER_NOT_GUEST")confirmedDisplay++;
    if(item.web_retriever_observation==="WEB_RETRIEVER_520_ERROR_NOT_ORIGIN_STATUS")errors520++;
    if(item.catalog_px!==null) {
      const [w,h]=item.catalog_px;
      const expected=[Math.min(w,960),Math.round(Math.min(w,960)*h/w)];
      check(Array.isArray(item.conditional_960px) && item.conditional_960px[0]===expected[0] && item.conditional_960px[1]===expected[1],"no_upscaling_correct_ratio_"+key);
    } else check(item.conditional_960px===null,"unknown_native_dimensions_hold_"+key);
    check(item.web_retriever_observation!=="ORIGIN_HTTP_404" && !Number.isInteger(item.guest_http_status),"tool_not_origin_"+key);
    changed++;
  }
  check(changed===6,"six_changed");
  check(confirmedDisplay===5 && errors520===1 && a.find(x=>x.slot==="276:3").web_retriever_observation==="WEB_RETRIEVER_520_ERROR_NOT_ORIGIN_STATUS","web_observation_counts");
  check(a.find(x=>x.slot==="276:0").proposed_alt_editor_review.includes("exact date"),"alt_1907_temporal_caution");
  check(a.find(x=>x.slot==="276:4").media_class.includes("1916") && !a.find(x=>x.slot==="276:4").media_class.includes("NOT"),"separate_1916_event");
  for(const r of p) if(!KEYS.includes(r.slot)) check(JSON.stringify(now.get(r.slot))===JSON.stringify(r),"unrelated_slot_mutated_"+r.slot);
  check(c.filter(x=>x.evidence.length===0).length===48,"pending_count_from_rows");
  check(current.batch_sources.length===preceding.batch_sources.length+1,"batch_source_delta");
  check(audit.reported_42_guest_verified===false && audit.reported_76_percent_wire_savings_measured===false,"audit_metric_holds");
  return errors;
}
module.exports={verify,KEYS,BATCH};
if(require.main===module){
  const fs=require("node:fs"),path=require("node:path");
  const dir=__dirname;
  const read=name=>JSON.parse(fs.readFileSync(path.join(dir,name),"utf8"));
  const failures=verify(read("quebec_276_six_1907_1916_archival_20261110.json"),
    read("coverage_240_exact_pr1703_20261110.json"),
    read("coverage_234_exact_pr1703_20261110.json"),
    read("fixture_quebec_276_original_oct30_20261110.json"));
  if(failures.length){console.error(failures.join("\n"));process.exitCode=1;}
  else console.log("PASS Quebec 276 six-source rights/source/coverage fail-closed validation");
}
