"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),p=require("node:path"),{test}=require("node:test");
const {validate}=require("./validate_franklin_433.cjs");
const original=JSON.parse(fs.readFileSync(p.join(__dirname,"franklin_433_five_source_20261109.json"),"utf8")),clone=()=>JSON.parse(JSON.stringify(original));
test("five-source read-only audit passes",()=>assert.equal(validate(original).ok,true));
const edits=[
["invented source HTTP 404",x=>x.rows[0].retrieval.origin_http_status=404],
["invented browser 404",x=>x.rows[0].visitor.http_status=404],
["invented browser broken",x=>x.rows[0].visitor.confirmed_broken=true],
["invented transferred bytes",x=>x.rows[0].visitor.encoded_transfer_bytes=55333],
["false savings",x=>x.historical_baseline.claimed_76pct_reduction_measured=true],
["changed original URL",x=>x.rows[0].original_url="https://example.org/altered"],
["duplicated slot",x=>x.rows[1].slot="433:1"],
["rights bypass",x=>x.rows[3].release.rights_cleared=true],
["unlicensed cache",x=>x.rows[4].release.cache=true],
["WordPress rewrite",x=>x.rows[2].release.blocks_rewritten=true],
["bad small image enlargement",x=>x.rows[1].conditional_max_960px_dimensions=[960,1444]],
["invented CloudFront dimensions",x=>x.rows[4].conditional_max_960px_dimensions=[726,1119]],
["unverified status claim",x=>x.retriever_counts.actual_visitor_http_results=5],
["changed source snapshot SHA",x=>x.frozen_fixture.blob_sha="0".repeat(40)],
["removed source credit",x=>x.rows[0].credit_to_verify=""]
];
for(const [label,mutate] of edits)test("reject "+label,()=>{const x=clone();mutate(x);assert.equal(validate(x).ok,false)});
