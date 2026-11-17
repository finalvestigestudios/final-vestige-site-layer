"use strict";
const test=require("node:test"), assert=require("node:assert/strict"), fs=require("node:fs"), path=require("node:path");
const {validate}=require("./validate_west_loch_370.cjs");
const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,"west_loch_370_custody_20261031.json"),"utf8"));
const census=JSON.parse(fs.readFileSync(path.join(__dirname,"parts/02.json"),"utf8"));
const clone=()=>JSON.parse(JSON.stringify(manifest));
test("8 exact source/ALT entries and closed rights, dimension and browser gates",()=>assert.deepEqual(validate(clone(),census),[]));
const mutations=[
 ["deleted slot",x=>x.records.pop()],
 ["duplicate slot",x=>x.records[7].key="370:0"],
 ["incorrect source URL",x=>x.records[0].source_url="https://example.org/fake.jpg"],
 ["incorrect source ALT",x=>x.records[2].alt="historically wrong"],
 ["source host substitution",x=>x.records[0].source_host="other.example"],
 ["false first-party",x=>x.records[1].source_kind="first_party"],
 ["false external",x=>x.records[2].source_kind="external"],
 ["incorrect Navy catalog ID",x=>x.records[0].catalog_id="80-G-000000"],
 ["misidentified image id in URL",x=>x.records[3].source_url=x.records[0].source_url],
 ["false official source",x=>x.records[0].authoritative_record_url="https://example.org/80-G-276907.html"],
 ["different official photo",x=>x.records[0].authoritative_record_url=x.records[3].authoritative_record_url],
 ["first-party exact attribution overclaim",x=>x.records[5].catalog_match="exact_id_in_source"],
 ["headstone attribution invented",x=>x.records[7].attribution_candidate="US Navy confirmed"],
 ["headstone record invented",x=>x.records[7].authoritative_record_url="https://example.org/id"],
 ["rights promoted",x=>x.records[4].rights_review="approved"],
 ["fake master SHA",x=>x.records[0].asset_sha256="a".repeat(64)],
 ["unlicensed image copy",x=>x.records[0].asset_copied=true],
 ["WordPress upload",x=>x.records[0].wp_upload_authorized=true],
 ["post rewrite",x=>x.records[0].post_rewrite_authorized=true],
 ["invented visitor 404",x=>x.records[0].visitor_http_status=404],
 ["invented visitor 200",x=>x.records[0].visitor_http_status=200],
 ["invented visitor failure",x=>x.records[0].visitor_broken=true],
 ["invented browser currentSrc",x=>x.records[0].visitor_current_src=x.records[0].source_url],
 ["invented transferred bytes",x=>x.records[0].visitor_encoded_bytes=12345],
 ["invented naturalWidth",x=>x.records[0].visitor_natural_width=960],
 ["invented derivative file",x=>x.records[0].derivative_dimensions_px=[960,1007]],
 ["output size 1200 px",x=>x.records[0].max_width_px=1200],
 ["conditional dimensions malformed",x=>x.records[0].conditional_960_derivative.conditional_h=100],
 ["conditional width invalid",x=>x.records[0].conditional_960_derivative.conditional_w=1280],
 ["conditional master upscaling",x=>x.records[0].conditional_960_derivative.catalog_master_w=500],
 ["removes 1943 date caveat",x=>x.records[1].historical_note="Generic historical image description with no temporal differentiation."],
 ["changes uncertain Woodbine claim",x=>x.records[4].historical_note="This image depicts USS LST-480 and USCGC Woodbine with absolute certainty."],
 ["42 image claim promoted",x=>x.prior_sitewide_inventory.reported_42_broken_browser_verified=true],
 ["76 percent claim promoted",x=>x.prior_sitewide_inventory.reported_76pct_savings_measured=true],
 ["partial readback",x=>x.wp_readonly_source_matches.full_alt=7],
 ["missing rights policy",x=>x.records[4].rights_policy_urls=[]]
];
for(const [name,mutate] of mutations)test("rejects "+name,()=>{
 const d=clone();mutate(d);assert.notDeepEqual(validate(d,census),[],name);
});
