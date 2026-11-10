"use strict";
// Offline, fail-closed media evidence gate. No network, WordPress, images or file writes.
function validate(previous, audit, current, auditBlobSha) {
  const errors = [], bad = (why) => errors.push(why);
  const prior = previous.rows, rows = current.rows, ar = audit.rows;
  if (prior.length !== 288 || rows.length !== 288 || ar.length !== 6) bad("Inventory cardinality");
  if (current.counts.total_external !== 288 || current.counts.researched_unique !== 269 || current.counts.unresearched !== 19 || current.counts.total_evidence_records !== 274) bad("Coverage totals");
  if (current.counts.guest_browser_confirmed_broken !== 0 || current.counts.wire_reduction_76_percent_measured !== false) bad("Guest evidence overstated");
  if (audit.post.live_original_src_exact_frozen !== "6/6" || audit.post.historical_alt_equality_verified !== false || audit.counts.wordpress_writes !== 0) bad("Live source/read-only metadata");
  if (audit.rows.some(x => x.guest_http_status !== null || x.origin_http_status !== null || x.guest_wire_bytes !== null || x.guest_broken !== null || x.rights_cleared || x.download_authorized || x.cache_authorized || x.wordpress_media_upload_authorized || x.post_rewrite_authorized)) bad("Invented status or unauthorized use");
  if (new Set(ar.map(x => x.slot)).size !== 6 || ar.some((x,i) => x.slot !== "290:"+i)) bad("Audit slot identity");
  for (let i=0;i<prior.length;i++) {
    const old=prior[i], now=rows[i];
    if (now.slot !== old.slot || now.stored_url !== old.stored_url) bad("Frozen URL or slot mutated: "+i);
    if (old.post_id !== 290 && JSON.stringify(now) !== JSON.stringify(old)) bad("Unrelated row changed: "+old.slot);
    if (old.post_id === 290) {
      const x=ar.find(a=>a.slot===old.slot);
      if (!x || x.original_url !== old.stored_url || now.evidence.length !== 1 || now.evidence[0].blob_sha !== auditBlobSha || now.evidence[0].path !== "qa/media-recovery/camp_century_290_six_nasa_usace_geus_20261110.json" || now.candidate_sources.length !== 1) bad("Unreconciled batch: "+old.slot);
      if (old.evidence.length !== 0) bad("Previously researched batch collision: "+old.slot);
    }
    if (now.guest_http_status !== null || now.guest_wire_bytes !== null || now.guest_broken !== null || now.rights_cleared || now.download_authorized || now.cache_authorized || now.wordpress_media_upload_authorized || now.post_rewrite_authorized) bad("Unsupported guest/rights claim: "+old.slot);
  }
  if (rows.filter(x=>x.evidence.length).length !== 269 || rows.filter(x=>!x.evidence.length).length !== 19) bad("Research-position recomputation");
  if (ar.filter(x=>x.web_retriever_observation==="IMAGE_DISPLAYED").length !== 5 || ar.filter(x=>x.web_retriever_observation==="RETRIEVER_UNAVAILABLE").length !== 1) bad("Retriever classifications");
  if (ar[5].web_retriever_wrapper_code !== "DisabledError" || ar[5].guest_http_status !== null) bad("DisabledError misreported as HTTP status");
  for (const x of ar) {
    if (!x.primary_source_url || !x.candidate_catalog_url || !x.rights_review || !x.identity_review || !x.proposed_alt) bad("Missing source or rights evidence: "+x.slot);
    if (x.candidate_native_px && x.conditional_max960_px) {
      const [w,h]=x.candidate_native_px, [tw,th]=x.conditional_max960_px;
      if (!Number.isInteger(tw) || tw > 960 || tw > w || th > h || Math.abs((tw/th)-(w/h)) > 0.003) bad("Illegal candidate resize: "+x.slot);
    }
  }
  if (JSON.stringify(current.original_six_p0_guest_queue) !== JSON.stringify(previous.original_six_p0_guest_queue)) bad("Site QA queue changed");
  if (audit.publication_authorized !== false) bad("Publication not held");
  return {ok:errors.length===0,errors};
}
module.exports = {validate};
