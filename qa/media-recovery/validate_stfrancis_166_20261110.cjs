"use strict";
// Offline-only evidence validator: never fetches source URLs, images, WP, or browsers.
const fs = require("node:fs");
const pth = require("node:path");
const root = pth.resolve(__dirname, "../..");
function load(relative) { return JSON.parse(fs.readFileSync(pth.join(root, relative), "utf8")); }
const auditPath = "qa/media-recovery/stfrancis_166_six_loc_usgs_ucla_20261110.json";
const currentPath = "qa/media-recovery/coverage_228_exact_pr1703_20261110.json";
const priorPath = "qa/media-recovery/coverage_222_exact_pr1703_20261110.json";
const fixturePath = "qa/media-recovery/parts/07.json";
const auditBlob = "fc3edafdb8c3fe0e49027e3276b952e49cb59672";
const priorBlob = "d5db23b0ac958a6f3438f147500b54d9b0511bfc";
function check(condition, reason) { if (!condition) throw new Error(reason); }
function validate(audit, current, prior, fixture) {
 check(audit.schema === "fv-media-stfrancis-166-six-v1", "bad_audit_schema");
 check(audit.frozen_cms_fixture?.blob_sha === "21095161e633aba093b74c0ead9936c9f6186d00", "fixture_blob_changed");
 check(audit.preceding_register?.blob_sha === priorBlob, "prior_blob_changed");
 check(audit.status_semantics?.guest_browser_http === null && audit.status_semantics?.origin_http === null, "claim_http_without_evidence");
 check(audit.reported_42_guest_verified === false && audit.reported_76_percent_wire_savings_measured === false, "invented_claim");
 check(audit.rows.length === 6, "batch_six_required");
 check(prior.rows.length === 288 && current.rows.length === 288, "288_total_required");
 check(prior.counts.researched_unique === 222 && prior.counts.unresearched === 66, "prior_count");
 check(current.counts.researched_unique === 228 && current.counts.unresearched === 60 && current.counts.total_external === 288, "new_count");
 check(current.counts.total_evidence_records === prior.counts.total_evidence_records+6, "evidence_count");
 check(current.counts.new_research_source_rows === prior.counts.new_research_source_rows+6, "new_records_count");
 check(current.counts.unique_research_increase === prior.counts.unique_research_increase+6, "unique_increase_count");
 check(current.counts.oversized_wp_originals_gt_1500000 === 15 &&
 current.counts.oversized_stored_original_bytes === 47096779, "preserve_storage_baseline");
 check(current.counts.reported_42_broken_browser_confirmed === false &&
 current.counts.wire_reduction_76_percent_measured === false, "not_real_guest_measurement");
 const expected = ["166:1","166:2","166:3","166:4","166:5","166:6"];
 const originals = fixture.images.filter(x=>x.post_id === 166 && x.slot>0);
 check(originals.length===6, "fixture_six_required");
 const keys = new Set(), a = new Map();
 for (const r of audit.rows) {
  check(!keys.has(r.slot) && expected.includes(r.slot), "unknown_or_duplicate_slot");
  keys.add(r.slot); a.set(r.slot,r);
  const f = originals.find(x=>x.key===r.slot);
  check(f && f.source_url === r.published_src && f.alt === r.published_alt &&
    f.post_url === r.post_url && f.source_host === r.source_host, "frozen_published_source_mismatch:"+r.slot);
  check(r.web_retriever==="TOOL_INACCESSIBLE_NOT_ORIGIN_STATUS", "unsupported_retriever_claim");
  for (const field of ["origin_http_status","guest_http_status","guest_current_src","guest_decoded_px","guest_wire_bytes","guest_broken"]) check(r[field]===null, "invented_http_or_visitor_evidence:"+r.slot+":"+field);
  for (const field of ["rights_cleared","exact_binary_match","download_authorized","cache_authorized","wordpress_media_upload_authorized","post_rewrite_authorized"]) check(r[field]===false, "unsafe_permission:"+r.slot+":"+field);
  check(r.license_review.startsWith("HOLD"), "unreviewed_license_assumed_cleared:"+r.slot);
  check(r.catalog_url.startsWith("https://"),"catalog_missing:"+r.slot);
  if (r.catalog_px===null) check(r.conditional_960px===null && r.slot==="166:1", "unknown_geometry_false_certainty");
  else {
   const [w,h]=r.catalog_px, [tw,th]=r.conditional_960px;
   check(Number.isInteger(w)&&Number.isInteger(h)&&w>0&&h>0,"invalid_catalog_dimensions");
   check(tw===Math.min(960,w) && th===Math.round(h*tw/w), "wrong_or_upscaled_960_geometry:"+r.slot);
  }
 }
 check(keys.size===6,"missing_slot");
 let diffs=0;
 for (let i=0;i<288;i++) {
  const p=prior.rows[i],c=current.rows[i];
  check(p.slot===c.slot && p.stored_url===c.stored_url, "moved_or_mutated_original_source");
  if (!keys.has(c.slot)) check(JSON.stringify(c)===JSON.stringify(p),"unrelated_row_changed:"+c.slot);
  else {
   diffs++;
   check(p.evidence.length===0 && p.candidate_sources.length===0,"overwrote_existing_research:"+c.slot);
   check(c.evidence.length===1&&c.evidence[0].path===auditPath &&
     c.evidence[0].blob_sha===auditBlob, "missing_evidence_or_wrong_git_blob:"+c.slot);
   check(c.candidate_sources.length===1 && c.candidate_sources[0].catalog_url===a.get(c.slot).catalog_url &&
     c.candidate_sources[0].item_rights_cleared===false &&
     c.candidate_sources[0].exact_image_match_verified===false, "bad_candidate_provenance:"+c.slot);
   for (const field of ["guest_http_status","guest_current_src","guest_decoded_px","guest_wire_bytes","guest_broken"])check(c[field]===null,"fabricated_guest_result:"+c.slot);
   for(const field of ["rights_cleared","download_authorized","cache_authorized","wordpress_media_upload_authorized","post_rewrite_authorized"])check(c[field]===false,"unsafe_permission_in_register:"+c.slot);
  }
 }
 check(diffs===6,"wrong_changed_row_count");
 check(current.rows.filter(x=>x.evidence.length>0).length===228 && current.rows.filter(x=>x.evidence.length===0).length===60, "derived_research_count");
 check(current.batch_sources.some(x=>x.file===auditPath&&x.blob_sha===auditBlob&&x.source_records===6),"missing_batch_sha");
 check(current.prior_222_register?.blob_sha===priorBlob,"missing_prior_snapshot_pin");
 return {verified:6,coverage:228,total:288,untouched:282,guest_broken_confirmed:0};
}
module.exports={validate,load};
if (require.main===module) {
 try { console.log(JSON.stringify(validate(load(auditPath),load(currentPath),load(priorPath),load(fixturePath)))); }
 catch(e) { console.error(e.message); process.exitCode=1; }
}
