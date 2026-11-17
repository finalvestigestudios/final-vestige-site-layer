"use strict";
const test=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {validate}=require("./validate_general_slocum_253.cjs");
const record=JSON.parse(fs.readFileSync(path.join(__dirname,"general_slocum_253_primary_20261031.json"),"utf8"));
const census=JSON.parse(fs.readFileSync(path.join(__dirname,"parts/05.json"),"utf8"));
const fresh=()=>JSON.parse(JSON.stringify(record));
test("seven exact WordPress sources, LOC/Commons identity and closed rights gates",()=>assert.deepEqual(validate(fresh(),census),[]));
const attacks=[
 ["missing image",d=>d.records.pop()],
 ["duplicate slot",d=>d.records[1].key="253:0"],
 ["swapped original photo",d=>d.records[2].source_url=d.records[3].source_url],
 ["false ALT",d=>d.records[3].alt="different image"],
 ["mismatched host",d=>d.records[4].source_host="example.org"],
 ["wrong source type",d=>d.records[0].source_kind="first_party"],
 ["modified query",d=>d.records[0].source_url=d.records[0].source_url.replace("1280","960")],
 ["wrong LOC number",d=>d.records[2].catalog_id="2009632220"],
 ["wrong LOC reproduction",d=>d.records[2].catalog_repro_id="LC-USZ62-999999"],
 ["wrong LOC record URL",d=>d.records[2].catalog_url=d.records[3].catalog_url],
 ["wrong original LCCN",d=>d.records[2].source_url=d.records[2].source_url.replace("2009632218","2009632220")],
 ["wrong Commons record",d=>d.records[6].catalog_url=d.records[0].catalog_url],
 ["false binary match",d=>d.records[3].binary_identity_verified=true],
 ["fake master hash",d=>d.records[0].master_sha256="a".repeat(64)],
 ["unlicensed image copy",d=>d.records[0].asset_copied=true],
 ["copyright promoted",d=>d.records[1].rights_review="CLEARED"],
 ["WordPress upload",d=>d.records[6].wp_upload_authorized=true],
 ["post rewrite",d=>d.records[4].post_rewrite_authorized=true],
 ["invented HTTP 404",d=>d.records[1].visitor_http_status=404],
 ["invented HTTP 200",d=>d.records[2].visitor_http_status=200],
 ["invented browser failure",d=>d.records[3].visitor_broken=true],
 ["invented currentSrc",d=>d.records[6].visitor_current_src=d.records[6].source_url],
 ["invented transfer bytes",d=>d.records[2].visitor_encoded_bytes=11234],
 ["invented naturalWidth",d=>d.records[0].visitor_natural_width=800],
 ["overwide derivative limit",d=>d.records[6].max_width_px=1280],
 ["invented LOC dimensions",d=>d.records[2].source_w=960],
 ["upscaled small photograph",d=>d.records[1].proposed_derivative_px.width=960],
 ["incorrect memorial aspect",d=>d.records[6].proposed_derivative_px.height=960],
 ["lost memorial photo date",d=>d.records[6].date_caveat="Memorial in New York"],
 ["false LOC release",d=>d.records[4].rights_signal="public_domain_worldwide"],
 ["false 42 confirmed",d=>d.reported_breakages_42_browser_verified=true],
 ["false 76 percent",d=>d.claimed_weight_reduction_76_percent_measured=true],
 ["wrong site inventory",d=>d.sitewide_inventory.stored_image_slots=356],
 ["false CMS readback",d=>d.wordpress_readback.exact_alt_texts=6],
 ["missing LOC policy",d=>d.records[3].rights_policy_urls=[]]
];
for(const [label,modify] of attacks)test("reject "+label,()=>{const d=fresh();modify(d);assert.notDeepEqual(validate(d,census),[],label)});
