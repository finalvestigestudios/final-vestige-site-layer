"use strict";
const fs = require("node:fs");
const path = require("node:path");
const { URL } = require("node:url");

const ALLOWED_VIEWER = new Set([
  "decoded_in_independent_viewer",
  "viewer_redirect_access_error",
  "not_tested"
]);
const ALLOWED_MATCH = new Set([
  "filename_lead_only",
  "publisher_exact_inline_url",
  "exact_commons_file_and_accession",
  "official_publisher_filename_and_caption",
  "exact_commons_file_name"
]);
const nullGuestFields = [
  "actual_guest_browser_http_status",
  "actual_guest_browser_current_src",
  "actual_guest_browser_content_type",
  "actual_guest_browser_transfer_bytes",
  "actual_guest_browser_decoded_dimensions",
  "original_binary_sha256"
];

function validateFrankSlide431(manifest, frozen) {
  const errors = [];
  const fail = (msg) => errors.push(msg);
  if (!manifest || typeof manifest !== "object" || Array.isArray(manifest)) {
    throw Error("manifest must be object");
  }
  if (!frozen || !Array.isArray(frozen.images)) throw Error("frozen inventory required");
  if (manifest.schema_version !== 1 || manifest.audit_date !== "2026-10-31") fail("schema/date");
  if (manifest.census_blob_sha !== "948bc1b65b42799aa40cfdb810ddf6ffd80886b6") fail("frozen census SHA");
  const expected = frozen.images.filter((r) => r.post_id === 431).sort((a,b) => a.slot-b.slot);
  const images = manifest.images;
  if (!Array.isArray(images) || expected.length !== 6 || images.length !== 6) {
    throw Error("expected six image rows");
  }
  if (manifest.post?.id !== 431 || manifest.post?.url !== expected[0].post_url) fail("post identity");
  if (manifest.scope?.stored_images !== 6 || manifest.scope?.stored_external_images !== 5) fail("scope counts");
  if (manifest.scope?.actually_broken_in_guest_browser !== null) fail("unknown broken count");
  if (manifest.scope?.reported_broken_sitewide_42_verified !== false) fail("42 verified without browser");
  if (manifest.scope?.reported_weight_savings_76_percent_verified !== false) fail("76 verified without wire data");
  const safety = manifest.publication_safety || {};
  for (const key of ["homepage_files_changed","site_qa_pr154_changed","third_party_assets_downloaded","production_wordpress_writes","licensing_auto_approved","original_file_hashes_acquired","cache_enabled"]) {
    if (safety[key] !== false) fail("unsafe publication action " + key);
  }
  if (safety.spend_usd !== 0 || safety.max_derivative_width_px !== 960 || safety.no_upscale !== true) fail("unsafe resize/spend plan");
  const seen = new Set();
  for (let i=0;i<images.length;i++) {
    const row=images[i], exp=expected[i];
    if (!row || row.image_key !== exp.key || row.post_id !== 431) { fail("slot/order at "+i); continue; }
    if (seen.has(row.image_key)) fail("duplicate "+row.image_key);
    seen.add(row.image_key);
    if (row.stored_url !== exp.source_url || row.stored_alt !== exp.alt || row.source_kind !== exp.source_kind) fail("source identity "+row.image_key);
    if (row.stored_intrinsic_width_px !== exp.width_px || row.stored_intrinsic_height_px !== exp.height_px) fail("source dimensions modified "+row.image_key);
    if (!ALLOWED_VIEWER.has(row.viewer_observation_kind)) fail("viewer category "+row.image_key);
    if (!ALLOWED_MATCH.has(row.candidate_match_level)) fail("match category "+row.image_key);
    for (const key of nullGuestFields) if (row[key] !== null) fail("fabricated real-browser/binary evidence "+row.image_key+":"+key);
    if (typeof row.candidate_record_url !== "string") fail("missing candidate "+row.image_key);
    else {
      try {
        const u = new URL(row.candidate_record_url);
        if (u.protocol !== "https:") fail("insecure record "+row.image_key);
      } catch (_) { fail("invalid record "+row.image_key); }
    }
    if (!/^HOLD_/.test(row.rights_status || "")) fail("rights clearance fabricated "+row.image_key);
    if (typeof row.rights_note !== "string" || row.rights_note.length < 32) fail("rights explanation "+row.image_key);
    if (typeof row.suggested_credit !== "string" || row.suggested_credit.length < 12) fail("missing credit "+row.image_key);
    if (row.asset_copied !== false || row.wp_media_item_id !== null || row.wordpress_upload_authorized !== false) fail("unauthorized cache/write "+row.image_key);
    const ow = row.candidate_original_width_px, oh=row.candidate_original_height_px, tw=row.candidate_target_width_px, th=row.candidate_target_height_px;
    const allKnown=[ow,oh,tw,th].every(Number.isInteger);
    const allUnknown=[ow,oh,tw,th].every((x)=>x===null);
    if (!allKnown && !allUnknown) fail("partially invented dimensions "+row.image_key);
    if (allKnown) {
      if (ow<1 || oh<1 || tw<1 || th<1 || tw>960 || tw>ow || th>oh) fail("invalid max-width/no-upscale "+row.image_key);
      const targetW = Math.min(ow,960);
      if (tw !== targetW || th !== Math.round(oh*targetW/ow)) fail("aspect ratio "+row.image_key);
    }
  }
  if (!images[2].candidate_record_id?.includes("A15276") || !images[2].editorial_caption_note?.includes("before") || images[2].rights_status !== "HOLD_US_AND_ITEM_REVIEW") fail("before-slide archival correction");
  if (!images[4].candidate_record_id?.includes("1934") || !images[4].editorial_caption_note?.includes("1934") || !images[4].editorial_caption_note?.includes("blue")) fail("1934 danger-zone map provenance");
  if (!images[5].rights_note?.includes("CC BY-SA 3.0") || !images[5].suggested_credit?.includes("Fourtildas")) fail("Commons CC BY-SA attribution");
  if (images[5].viewer_observation_kind !== "viewer_redirect_access_error" || manifest.scope?.actually_broken_in_guest_browser !== null) fail("viewer error falsely treated as browser failure");
  if (errors.length) throw Error(errors.join("; "));
  return {pass:true,slots:6,external_slots:5,actual_guest_browser_failures:null,production_writes:0};
}
module.exports = {validateFrankSlide431};
if (require.main === module) {
  const dir=__dirname;
  const manifest=JSON.parse(fs.readFileSync(path.join(dir,"frank_slide_431_primary_20261031.json"),"utf8"));
  const frozen=JSON.parse(fs.readFileSync(path.join(dir,"parts","01.json"),"utf8"));
  console.log(JSON.stringify(validateFrankSlide431(manifest,frozen)));
}
