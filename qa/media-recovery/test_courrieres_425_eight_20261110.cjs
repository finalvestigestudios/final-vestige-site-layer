"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {validate,PINS,target}=require("./validate_courrieres_425_eight_20261110.cjs");
const original=JSON.parse(fs.readFileSync(path.join(__dirname,"courrieres_425_eight_catalog_20261110.json"),"utf8"));
const clone=()=>JSON.parse(JSON.stringify(original));
test("all 8 source entries validate",()=>assert.deepEqual(validate(original),[]));
test("frozen source and alt exact",()=>PINS.forEach((p,i)=>{assert.equal(original.rows[i].stored_original_url,p.src);assert.equal(original.rows[i].stored_original_alt,p.alt);}));
test("960 geometry is proportional, never upscale",()=>{assert.deepEqual(target(798,1024),[798,1024]);assert.deepEqual(target(994,625),[960,604]);assert.deepEqual(target(5098,3193),[960,601]);});
test("1280 requests exceed native widths",()=>{assert.match(original.rows[2].stored_original_url,/width=1280/);assert.equal(original.rows[2].catalog.native_catalog_px[0],798);assert.match(original.rows[4].stored_original_url,/width=1280/);assert.equal(original.rows[4].catalog.native_catalog_px[0],994);});
for(const [label,mutate] of [
["source swapped",a=>a.rows[0].stored_original_url=a.rows[1].stored_original_url],
["ALT swapped",a=>a.rows[7].stored_original_alt="marching"],
["slot duplicated",a=>a.rows[0].slot="425:2"],
["fixture SHA altered",a=>a.frozen_fixture_sha="bad"],
["row removed",a=>a.rows.pop()],
["invented origin 404",a=>a.rows[1].independent_redirect_probe.origin_http_status=404],
["invented visitor 200",a=>a.rows[2].independent_redirect_probe.visitor_http_status=200],
["invented visitor broken",a=>a.rows[3].independent_redirect_probe.visitor_broken=true],
["invented bytes",a=>a.rows[4].independent_redirect_probe.visitor_encoded_bytes=1234],
["false 76 percent",a=>a.counts.proposed_76_percent_wire_savings_measured=true],
["false 42 corroboration",a=>a.counts.reported_42_broken_confirmed=true],
["rights bypass",a=>a.rows[5].release_gate.individual_rights_cleared=true],
["download bypass",a=>a.rows[5].release_gate.download_authorized=true],
["cache bypass",a=>a.rows[2].release_gate.cache_authorized=true],
["WordPress upload",a=>a.rows[1].release_gate.wp_upload_authorized=true],
["block rewrite",a=>a.rows[6].release_gate.block_rewrite_authorized=true],
["unearned primary verification",a=>a.rows[7].catalog.primary_catalog_item_independently_verified=true],
["wrong proportional width",a=>a.rows[5].conditional_sizing.target_px=[960,1148]],
["narrow image enlarged",a=>a.rows[2].conditional_sizing.target_px=[960,1232]],
["fake derivative",a=>a.rows[0].conditional_sizing.derivative_created=true],
["falsified loaded",a=>a.counts.actual_visitor_loaded_confirmed=8],
["storage bytes mistaken",a=>a.counts.oversize_wp_original_stored_bytes=12345],
["wrong catalog match",a=>a.rows[0].catalog.title="other image.jpg"],
["invented resolved URL",a=>a.rows[0].independent_redirect_probe.final_location="https://example.com/1.jpg"]
])test("reject "+label,()=>{const x=clone();mutate(x);assert.notDeepEqual(validate(x),[]);});
