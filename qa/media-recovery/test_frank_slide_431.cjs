"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const manifest = require("./frank_slide_431_primary_20261031.json");
const frozen = require("./parts/01.json");
const {validateFrankSlide431} = require("./validate_frank_slide_431.cjs");
const fresh = () => structuredClone(manifest);
const bad = (label, fn, pattern) => test(label, () => {
  const doc = fresh();
  fn(doc);
  assert.throws(() => validateFrankSlide431(doc,frozen), pattern);
});

test("six frozen slots / five external, no guest failure or weight assertions", () => {
  assert.deepEqual(validateFrankSlide431(fresh(),frozen), {
    pass:true,slots:6,external_slots:5,actual_guest_browser_failures:null,production_writes:0
  });
});
bad("reject changed exact stored source", x => x.images[1].stored_url="https://example.org/a.jpg", /source identity/);
bad("reject altered original ALT", x => x.images[4].stored_alt="generic map", /source identity/);
bad("reject duplicate/misordered slot", x => x.images[4].image_key="431:3", /slot\/order/);
bad("reject invented guest 404", x => x.images[2].actual_guest_browser_http_status=404, /fabricated real-browser/);
bad("reject invented successful currentSrc", x => x.images[3].actual_guest_browser_current_src=x.images[3].stored_url, /fabricated real-browser/);
bad("reject invented content-type", x => x.images[4].actual_guest_browser_content_type="image/jpeg", /fabricated real-browser/);
bad("reject invented transfer bytes", x => x.images[5].actual_guest_browser_transfer_bytes=12345, /fabricated real-browser/);
bad("reject invented image hash", x => x.images[2].original_binary_sha256="a".repeat(64), /fabricated real-browser/);
bad("reject 42 broken as verified", x => x.scope.reported_broken_sitewide_42_verified=true, /42 verified/);
bad("reject 76 percent savings as verified", x => x.scope.reported_weight_savings_76_percent_verified=true, /76 verified/);
bad("reject wrongful rights release", x => x.images[5].rights_status="CLEARED", /rights clearance/);
bad("reject undocumented WordPress upload", x => x.images[1].wordpress_upload_authorized=true, /unauthorized/);
bad("reject asset copying", x => x.images[4].asset_copied=true, /unauthorized/);
bad("reject oversized derivative", x => x.images[2].candidate_target_width_px=1200, /invalid max-width/);
bad("reject 960px upscale of already-small first party control", x => x.images[0].candidate_target_width_px=960, /invalid max-width/);
bad("reject incorrect aspect ratio", x => x.images[5].candidate_target_height_px=768, /aspect ratio/);
bad("reject invented metadata for unknown publisher dimensions", x => x.images[1].candidate_target_width_px=960, /partially invented/);
bad("reject wrong pre-slide interpretation", x => x.images[2].editorial_caption_note="Destroyed Frank after slide", /before-slide archival/);
bad("reject loss of exact 1934 hazard map dating", x => x.images[4].editorial_caption_note="A historical map", /1934 danger-zone/);
bad("reject loss of attribution/share-alike", x => x.images[5].rights_note="Permission review needed for contributor rights. No known licence.", /Commons CC BY-SA/);
bad("reject converting redirect viewer failure into a browser-broken claim", x => x.scope.actually_broken_in_guest_browser=1, /unknown broken count/);
bad("reject billing or added spend", x => x.publication_safety.spend_usd=2, /unsafe resize\/spend/);
bad("reject unrelated homepage changes", x => x.publication_safety.homepage_files_changed=true, /unsafe publication/);
bad("reject drift from frozen source SHA", x => x.census_blob_sha="unknown", /frozen census SHA/);
