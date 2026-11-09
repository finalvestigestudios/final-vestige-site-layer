"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {check}=require("./validate_lady_be_good_278_20261109.cjs");
const good=JSON.parse(fs.readFileSync(path.join(__dirname,"lady_be_good_278_seven_20261109.json"),"utf8"));
const clone=()=>structuredClone(good);
test("control: full exact-source batch",()=>assert.deepEqual(check(clone()),[]));
const mutants=[
 ["fabricated visitor 404",a=>a.rows[0].visitor.http_status=404],
 ["visitor browser broken assertion",a=>a.rows[0].visitor.confirmed_broken=true],
 ["fabricated transfer savings",a=>a.measurements.transfer_reduction_76pct_measured=true],
 ["reported 42 verification",a=>a.measurements.original_reported_broken_42_verified=true],
 ["original source URL mutation",a=>a.rows[0].stored_url+="?changed=1"],
 ["ALT chronology mutation",a=>a.rows[1].original_alt="post-crash photograph"],
 ["source corpus conflated",a=>a.source_inventory.posts=66],
 ["source provenance SHA changed",a=>a.rows[1].original_source_fixture.blob_sha="not-original"],
 ["unauthorized caching",a=>a.rows[0].hold.cache_approved=true],
 ["unauthorized WP upload",a=>a.rows[0].hold.wordpress_upload_approved=true],
 ["third-party rights assumed clear",a=>a.rows[4].catalog.rights="CLEARED"],
 ["invented binary comparison",a=>a.rows[2].catalog.source_match="VERIFIED_BINARY"],
 ["distorted 960 image",a=>a.rows[2].catalog.conditional_960_px=[960,900]],
 ["upscaled over 960",a=>a.rows[2].catalog.conditional_960_px=[1080,715]],
 ["invented dimensions",a=>a.rows[0].catalog.conditional_960_px=[960,700]],
 ["canary non-matching slot",a=>a.rows[0].slot="999:0"],
 ["dropped slot",a=>a.rows.pop()],
 ["duplicated slot",a=>a.rows[1]=structuredClone(a.rows[0])],
 ["canteen overclaim review removed",a=>a.rows[3].catalog.scene_note="Definitely the recovered canteen"],
 ["NARA alt review removed",a=>a.rows[5].catalog.scene_note="Existing ALT accurate"],
 ["method recast as browser",a=>a.rows[0].retrieval.method="CHROMIUM"],
 ["unknown guest cache changed",a=>a.rows[2].visitor.cache_state=false]
];
for(const [name,mutate] of mutants)test(name,()=>{const a=clone();mutate(a);assert.ok(check(a).length>0)});
