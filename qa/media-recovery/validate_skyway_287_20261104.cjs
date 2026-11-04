"use strict";

/** Pure, offline provenance validator. Does not issue HTTP or write WordPress. */
function validateSkyway287(audit, frozenPart) {
  const errors = [];
  const must = (condition, message) => { if (!condition) errors.push(message); };
  if (!audit || typeof audit !== "object" || !frozenPart || !Array.isArray(frozenPart.images))
    return { ok: false, errors: ["audit and frozen part are required"] };
  const originals = frozenPart.images.filter(x => x.post_id === 287).sort((a,b) => a.slot-b.slot);
  must(audit.schema === "fv.media.skyway_287_primary_source_20261104.v1", "schema mismatch");
  must(audit.inventory?.git_blob_sha === "49183f66f880f7c4dfd363acca906876877f2e5e", "wrong pinned frozen blob");
  must(audit.inventory?.source_path === "qa/media-recovery/parts/03.json", "wrong frozen part path");
  must(originals.length === 6 && audit.images?.length === 6, "expected exactly six published slots");
  must(audit.live_wp_readback?.status === "publish" &&
       audit.live_wp_readback?.last_modified === "2026-11-02T21:40:01" &&
       audit.live_wp_readback?.same_src_count === 6 &&
       audit.live_wp_readback?.same_alt_count === 6 &&
       audit.live_wp_readback?.images_with_both_width_height === 1 &&
       audit.live_wp_readback?.html_verified === true, "live readback custody drift");
  must(audit.retriever_method?.includes("NOT a guest Chrome/origin HTTP"), "retriever distinction missing");
  must(audit.images?.every(x => x.source_url?.startsWith("https://") && x.rights_review==="HOLD" &&
       x.wp_upload_authorized===false && x.caching_authorized===false), "image rights, URL or caching gate");
  const seen = new Set();
  for (const original of originals) {
    const item = audit.images?.find(x => x.key === original.key);
    if (!item) { errors.push("missing "+original.key); continue; }
    must(!seen.has(item.key), "duplicate "+item.key); seen.add(item.key);
    must(item.slot === original.slot && item.source_url === original.source_url &&
         item.source_host === original.source_host && item.alt === original.alt &&
         item.stored_html_width_px === original.width_px &&
         item.stored_html_height_px === original.height_px, "frozen src/alt/dim drift "+original.key);
    must(item.live_wp_src_alt_match === true && item.live_wp_width_height_pair === (original.slot===0),
         "incorrect readback status "+original.key);
    must(item.retriever?.requested_url === original.source_url &&
         item.retriever?.method === "web.open" &&
         item.retriever?.origin_http_status_verified === false &&
         typeof item.retriever?.tool_reference === "string" &&
         /^turn[0-9]+view[0-9]+$/.test(item.retriever.tool_reference),
         "untraceable retriever method "+original.key);
    const brokenRetriever = original.slot===5;
    must(item.retriever?.outcome === (brokenRetriever ? "tool_reported_404" : "image_displayed") &&
         item.retriever?.tool_reported_code === (brokenRetriever ? 404 : null),
         "tool observation changed "+original.key);
    const browser = item.browser || {};
    for (const name of ["http_status","final_request_url","content_type","decoded","natural_width_px",
      "natural_height_px","transferred_bytes","broken_in_browser","cls"]) {
      must(browser[name] === null, "fabricated visitor evidence "+original.key+" "+name);
    }
    const geometry = item.conditional_960px_geometry;
    if (original.slot===0) must(geometry?.width_px===960 && geometry?.height_px===630 &&
       geometry?.basis==="live_html_1024x672_only_not_binary_master" &&
       geometry?.verified_image_pixels===false,"conditional HTML geometry altered");
    else must(geometry===null, "fabricated intrinsic geometry "+original.key);
  }
  must(audit.images?.length===seen.size,"extra or duplicate slots");
  const migration = audit.source_host_migration || {};
  const published = originals.find(x=>x.slot===5)?.source_url;
  must(migration.key==="287:5" && migration.published_url===published &&
       migration.published_url_retriever_outcome==="tool_reported_404" &&
       migration.publisher_article_url==="https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/" &&
       migration.publisher_current_asset_url==="https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg" &&
       migration.publisher_current_asset_retriever_outcome==="image_displayed" &&
       migration.publisher_article_photo_credit==="University Press of Florida" &&
       migration.same_filename===true &&
       migration.binary_identity_verified===false &&
       migration.exact_crop_verified===false &&
       migration.publisher_explicit_republication_permission===false,"migration proof/rights drift");
  must(audit.editorial_integrity?.key==="287:5" &&
       audit.editorial_integrity.current_alt===originals[5]?.alt &&
       audit.editorial_integrity.classification==="P1_caption_visual_accuracy_needs_editorial_review" &&
       audit.editorial_integrity.remedy_requires_editorial_decision===true, "visual-integrity gate drift");
  const candidates = audit.replacement_candidates;
  must(Array.isArray(candidates) && candidates.length===3, "expected exactly three candidates");
  for (const c of candidates || []) {
    must(c.for_key==="287:5" && c.rights_status==="HOLD" &&
         c.wp_upload_authorized===false && c.caching_authorized===false &&
         c.auto_replace_allowed===false && c.derivative_max_width_px===960 &&
         typeof c.catalog_url==="string" && c.catalog_url.startsWith("https://"), "candidate rights/url gate");
    must(c.source_image_width_px===null ||
         (Number.isInteger(c.source_image_width_px) && c.source_image_width_px>0 &&
          Number.isInteger(c.source_image_height_px) && c.source_image_height_px>0), "invalid master dimensions");
    must(c.derivative_width_px===null || (Number.isInteger(c.derivative_width_px) &&
         c.derivative_width_px<=960 && c.derivative_width_px<=c.source_image_width_px &&
         Number.isInteger(c.derivative_height_px) && c.derivative_height_px>0), "upscaled/improper derivative");
    must(c.source_image_width_px!==null || c.derivative_width_px===null, "invented derivative geometry");
  }
  const publisher = candidates?.find(c=>c.candidate_id==="publisher_media_host_same_filename");
  const commons = candidates?.find(c=>c.candidate_id==="florida_memory_K894127_commons_1987");
  const second = candidates?.find(c=>c.candidate_id==="florida_memory_K893521_archival_option");
  must(publisher?.asset_url===migration.publisher_current_asset_url &&
       publisher?.source_image_width_px===null && publisher?.derivative_width_px===null &&
       publisher?.historical_match==="same_event_and_filename_not_byte_verified", "publisher candidate identity not gated");
  must(commons?.archival_id==="K894127" && commons?.photographer==="H. Milo Stewart" &&
       commons?.photographed_date==="1987 (circa)" &&
       commons?.source_image_width_px===600 && commons?.source_image_height_px===595 &&
       commons?.derivative_width_px===600 && commons?.derivative_height_px===595 &&
       commons?.historical_match==="different_photo_1987_not_1980" &&
       commons?.rights_evidence?.includes("Uploader tag alone"), "Commons dimensions/rights misleading");
  must(second?.archival_id==="K893521" && second?.photographed_date==="1989" &&
       second?.source_image_width_px===null && second?.derivative_width_px===null &&
       second?.historical_match==="different_photo_1989_not_1980", "second archival candidate drift");
  const g = audit.release_gates || {};
  for (const key of ["source_binary_downloaded","actual_origin_get_recorded","guest_browser_qa_complete",
     "guest_browser_404_confirmed","historical_image_identity_approved","rights_cleared",
     "visual_before_after_approved","wp_upload_authorized","wp_post_block_edit_authorized","publish_authorized"]) {
    must(g[key]===false, "release gate unexpectedly enabled "+key);
  }
  const b = audit.baseline || {};
  must(b.published_posts===61 && b.image_references===355 && b.external_original_references===288 &&
       b.oversized_wp_originals_over_1_5_MiB===13 && b.alleged_broken_external_images===42 &&
       b.verified_broken_external_images===null && b.claimed_reduction_percent===76 &&
       b.measured_wire_reduction_percent===null && b.production_image_repairs===0,
       "unmeasured claims or sitewide baseline drift");
  must(audit.context_source?.investigation_id==="DCA80AM050" &&
       audit.verification_limitations?.length>=4, "missing provenance limitations");
  return { ok: errors.length===0, errors };
}

module.exports = { validateSkyway287 };
