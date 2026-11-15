#!/usr/bin/env node
"use strict";
const test=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs");
const {validate}=require("./validate_coastal_12_20261109.cjs");
const data=JSON.parse(fs.readFileSync("qa/media-recovery/coastal_scotch_cap_prinsendam_12_20261109.json","utf8"));
const census=JSON.parse(fs.readFileSync("qa/media-recovery/offsite_upstream_288_20261109.json","utf8"));
const clone=()=>structuredClone(data);
test("baseline frozen 12-source independent audit",()=>assert.equal(validate(data,census).new_slots,10));
const mutations=[
["source URL",d=>d.rows[0].original_url="https://example.com/x.jpg"],
["post URL",d=>d.rows[0].post_url="https://example.com"],
["source origin",d=>d.rows[0].source_upstream_host="other.test"],
["duplicate slot",d=>d.rows.push(structuredClone(d.rows[0]))],
["invented browser failure",d=>d.rows[0].retrieval_observation.visitor_broken=true],
["invented visitor HTTP",d=>d.rows[0].retrieval_observation.visitor_http_status=403],
["invented decoded image geometry",d=>d.rows[0].retrieval_observation.visitor_decoded_px=[960,100]],
["invented transferred bytes",d=>d.rows[0].retrieval_observation.visitor_transferred_bytes=400],
["fake rights clearance",d=>d.rows[0].candidate.rights_cleared=true],
["fake binary identity",d=>d.rows[0].candidate.exact_binary_match_confirmed=true],
["unauthorized WordPress upload",d=>d.rows[0].release.wordpress_upload=true],
["unauthorized caching",d=>d.rows[0].release.cdn_cache=true],
["unauthorized post rewrite",d=>d.rows[0].release.post_block_rewrite=true],
["unrelated homepage change",d=>d.rows[0].release.homepage_visual_change=true],
["guessed derivative dimension",d=>d.rows[0].candidate.conditional_960_max_rendition_px=[960,999]],
["incorrect official proportional rendition",d=>d.rows.find(r=>r.slot==="292:3").candidate.conditional_960_max_rendition_px=[960,900]],
["fabricated census SHA",d=>d.origin_census_blob_sha="0".repeat(40)],
["pretend logged-out browser",d=>d.rows[0].retrieval_observation.service="CHROMIUM_NETWORK"],
["fabricated 42 failures",d=>d.counts.confirmed_guest_failures=42],
["invented retrieval outcome",d=>d.rows[0].retrieval_observation.result="GUEST_BROKEN"]
];
for(const [label,change] of mutations)test("fail-closed: "+label,()=>{const d=clone();change(d);assert.throws(()=>validate(d,census))});
