"use strict";
// Read-only custody validator: Thresher / post 220; no requests, image downloads, CMS writes.
const EXPECTED_IDS = ["NH 97545","NH 97552","NH 97310","NH 97567",null,"NH 97570","NH 97557"];
const NULL_OBSERVATIONS = [
  "observed_live_browser_image_status","observed_image_http_status",
  "observed_currentSrc","observed_naturalWidth","observed_transferred_bytes",
  "original_binary_sha256"
];
function validate(manifest, census) {
  const errors = [];
  const reject = (condition, message) => { if (!condition) errors.push(message); };
  reject(manifest?.schema === "fv-media-recovery-thresher-custody-v1", "schema");
  reject(manifest?.post_id === 220, "post_id");
  reject(manifest?.confirmed_visitor_broken_images === null, "unverified site failures must remain null");
  reject(manifest?.claimed_42_sitewide_broken_images_verified === false, "42 failure claim gate");
  reject(manifest?.sitewide_76_percent_weight_reduction_verified === false, "76 percent claim gate");
  reject(manifest?.rights_review_complete === false && manifest?.all_wordpress_writes_prohibited === true, "release gate");
  reject(manifest?.cms_read_verified?.exact_url_and_alt_matches === 7, "CMS matched-count");
  reject(Array.isArray(manifest?.items) && manifest.items.length === 7, "seven image records");
  const frozen = Array.isArray(census?.images) ? census.images.filter(x => x.post_id === 220) : [];
  reject(frozen.length === 7, "frozen source 7 slots");
  const seen = new Set();
  for (let slot = 0; slot < 7; slot++) {
    const item = manifest?.items?.[slot], s = frozen[slot];
    if (!item || !s) { errors.push("missing slot " + slot); continue; }
    reject(item.key === "220:" + slot && item.post_id === 220 && item.slot === slot, "slot key " + slot);
    reject(!seen.has(item.key), "duplicate " + item.key); seen.add(item.key);
    reject(item.published_original_url === s.source_url && item.published_original_alt === s.alt, "source/ALT changed " + slot);
    reject(item.current_cms_source_verified === true && item.current_cms_alt_verified === true, "unverified CMS match " + slot);
    reject(/^https:\/\/commons\.wikimedia\.org\/wiki\/Special:Redirect\/file\//.test(item.published_original_url), "not frozen Commons source " + slot);
    reject(item.commons_file_page_url.startsWith("https://commons.wikimedia.org/wiki/File:"), "Commons provenance " + slot);
    reject(item.navy_catalog_number === EXPECTED_IDS[slot], "Navy photo ID " + slot);
    reject(item.source_match_level === (slot === 4 ? "commons_only_not_independent_navy_id" : "nhhc_exact"), "source confidence " + slot);
    reject(slot === 4 ? item.navy_catalog_page_url === null : item.navy_catalog_page_url?.endsWith("/" + EXPECTED_IDS[slot].replace(" ", "-") + ".html"), "Navy page " + slot);
    const o = item.commons_original_metadata_dimensions, d = item.derivative_target_dimensions;
    reject(Number.isInteger(o?.width) && o.width > 0 && Number.isInteger(o?.height) && o.height > 0, "original dimensions " + slot);
    reject(Number.isInteger(d?.width) && Number.isInteger(d?.height) && d.width > 0 && d.width <= 960 &&
      d.width <= o?.width && d.height <= o?.height &&
      d.width === Math.min(960,o?.width) && d.height === Math.round(o?.height * d.width / o?.width), "no-upscale geometry " + slot);
    reject(item.allow_upscaling === false, "upscaling forbidden " + slot);
    for (const key of NULL_OBSERVATIONS) reject(item[key] === null, "invented live/binary evidence " + slot + "/" + key);
    reject(item.copyright_release_status === "pending_individual_item_review" &&
      item.editorial_release_approved === false &&
      item.mirror_authorized === false &&
      item.wordpress_media_upload_authorized === false, "release gate " + slot);
    reject(typeof item.historical_context === "string" && item.historical_context.length > 20, "historical context " + slot);
  }
  reject(manifest?.items?.[2]?.historical_context?.includes("NOT demonstrably captured during the April 1963") === true, "Skylark photo chronology");
  reject(manifest?.items?.[4]?.historical_context?.includes("official standalone image ID remains unverified") === true, "Trieste II archive uncertainty");
  return errors;
}
if (typeof module !== "undefined" && module.exports) module.exports = {validate, EXPECTED_IDS};
if (typeof require !== "undefined" && typeof module !== "undefined" && require.main === module) {
  const fs = require("node:fs"), path = require("node:path");
  const here = __dirname;
  const manifest = JSON.parse(fs.readFileSync(path.join(here,"thresher_220_navy_primary_20261031.json"),"utf8"));
  const census = JSON.parse(fs.readFileSync(path.join(here,"parts","05.json"),"utf8"));
  const errors = validate(manifest,census);
  if (errors.length) { console.error(errors.join("\n")); process.exitCode = 1; }
  else console.log("Thresher source/rights/geometry gates: PASS, 7/7 slots, 6 exact Navy records, no live claims");
}
