"use strict";
const { validateSkyway287 } = require("./validate_skyway_287_20261104.cjs");

function runSkyway287Tests(canonical, frozenPart) {
  const clone = x => JSON.parse(JSON.stringify(x));
  let assertions = 0;
  const baseline = validateSkyway287(canonical, frozenPart);
  if (!baseline.ok) throw new Error("valid evidence rejected: "+baseline.errors.join("; "));
  assertions++;
  const mutations = [
    ["invented inventory blob", x=>{x.inventory.git_blob_sha="0000000000000000000000000000000000000000";}],
    ["unpublished WordPress state", x=>{x.live_wp_readback.status="draft";}],
    ["faked newer WordPress timestamp", x=>{x.live_wp_readback.last_modified="2026-11-04T12:00:00";}],
    ["inexact source count", x=>{x.live_wp_readback.same_src_count=5;}],
    ["invented HTML width pairs", x=>{x.live_wp_readback.images_with_both_width_height=6;}],
    ["source URL changed", x=>{x.images[0].source_url="https://example.com/false.jpg";}],
    ["ALT changed", x=>{x.images[2].alt="Unverified caption";}],
    ["source host changed", x=>{x.images[3].source_host="example.com";}],
    ["source slot dropped", x=>{x.images.pop();}],
    ["source slot duplicated", x=>{x.images[1].key=x.images[0].key;}],
    ["invented HTML width", x=>{x.images[1].stored_html_width_px=960;}],
    ["conditional HTML geometry upscaled", x=>{x.images[0].conditional_960px_geometry.width_px=1280;}],
    ["fabricated intrinsic geometry", x=>{x.images[3].conditional_960px_geometry={width_px:960,height_px:700};}],
    ["original tool 404 called displayed", x=>{x.images[5].retriever.outcome="image_displayed";}],
    ["origin status claimed from wrapper", x=>{x.images[5].retriever.origin_http_status_verified=true;}],
    ["tool 404 rewritten as origin 200", x=>{x.images[5].retriever.tool_reported_code=200;}],
    ["untraceable retriever reference", x=>{x.images[5].retriever.tool_reference="unverified";}],
    ["fabricated browser 404", x=>{x.images[5].browser.http_status=404;}],
    ["fabricated broken image claim", x=>{x.images[5].browser.broken_in_browser=true;}],
    ["fabricated image decoder", x=>{x.images[5].browser.decoded=false;}],
    ["fabricated currentSrc", x=>{x.images[5].browser.final_request_url=x.images[5].source_url;}],
    ["fabricated transfer weight", x=>{x.images[0].browser.transferred_bytes=99;}],
    ["fabricated CLS value", x=>{x.images[5].browser.cls=0.12;}],
    ["migrated URL not actually observed", x=>{x.source_host_migration.publisher_current_asset_url="https://unrelated.test/photo.jpg";}],
    ["false same-binary assertion", x=>{x.source_host_migration.binary_identity_verified=true;}],
    ["false identical crop", x=>{x.source_host_migration.exact_crop_verified=true;}],
    ["false publisher copyright approval", x=>{x.source_host_migration.publisher_explicit_republication_permission=true;}],
    ["lost original publisher credit", x=>{x.source_host_migration.publisher_article_photo_credit="Unknown";}],
    ["editorial alternative asserted as verified", x=>{x.editorial_integrity.classification="no_issue";}],
    ["wrong primary inventory ALT in editorial finding", x=>{x.editorial_integrity.current_alt="An entirely different photograph";}],
    ["candidate source path altered", x=>{x.replacement_candidates[0].asset_url="https://unrelated.test/photo.jpg";}],
    ["replacement rights silently approved", x=>{x.replacement_candidates[1].rights_status="CLEARED";}],
    ["WordPress upload without rights", x=>{x.replacement_candidates[1].wp_upload_authorized=true;}],
    ["unlicensed first-party cache", x=>{x.replacement_candidates[0].caching_authorized=true;}],
    ["automatic post block rewrite", x=>{x.replacement_candidates[0].auto_replace_allowed=true;}],
    ["Commons 600-wide enlarged to 960", x=>{x.replacement_candidates[1].derivative_width_px=960;}],
    ["Commons archival identity changed", x=>{x.replacement_candidates[1].archival_id="FABRICATED";}],
    ["Commons author rights warning removed", x=>{x.replacement_candidates[1].rights_evidence="CC0 means universally unrestricted";}],
    ["invented publisher native size", x=>{x.replacement_candidates[0].source_image_width_px=960;}],
    ["unknown master but derivative guessed", x=>{x.replacement_candidates[2].derivative_width_px=960;x.replacement_candidates[2].derivative_height_px=700;}],
    ["sitewide 42 all verified", x=>{x.baseline.verified_broken_external_images=42;}],
    ["claimed 76 percent treated as measured", x=>{x.baseline.measured_wire_reduction_percent=76;}],
    ["production repairs fabricated", x=>{x.baseline.production_image_repairs=1;}],
    ["publication authorization enabled", x=>{x.release_gates.publish_authorized=true;}],
    ["WordPress block edit enabled", x=>{x.release_gates.wp_post_block_edit_authorized=true;}],
    ["binary download claimed", x=>{x.release_gates.source_binary_downloaded=true;}]
  ];
  const failures = [];
  for (const [label, mutate] of mutations) {
    const candidate = clone(canonical);
    mutate(candidate);
    if (validateSkyway287(candidate, frozenPart).ok) failures.push(label);
    else assertions++;
  }
  const sourceDrift=clone(frozenPart);
  sourceDrift.images.find(x=>x.key==="287:5").source_url="https://unrelated.test/not-same.jpg";
  if (validateSkyway287(canonical,sourceDrift).ok) failures.push("frozen corpus drift not rejected");
  else assertions++;
  if (failures.length) throw new Error("FAIL OPEN: "+failures.join(", "));
  return { passed: assertions, failed: 0, mutation_cases: mutations.length+1,
     note: "Offline source/rights/HTTP evidence gate only; no visitor network measurement" };
}
module.exports={runSkyway287Tests};
if (require.main===module) {
  const fs=require("node:fs"), crypto=require("node:crypto"), path=require("node:path");
  const read=(p)=>fs.readFileSync(path.join(__dirname,p),"utf8");
  const raw=read("parts/03.json");
  const blob=crypto.createHash("sha1").update("blob "+Buffer.byteLength(raw)+String.fromCharCode(0)).update(raw).digest("hex");
  if(blob!=="49183f66f880f7c4dfd363acca906876877f2e5e") throw new Error("Frozen source blob SHA drift");
  const out=runSkyway287Tests(JSON.parse(read("skyway_287_original_host_migration_20261104.json")),JSON.parse(raw));
  process.stdout.write(JSON.stringify(out)+String.fromCharCode(10));
}
