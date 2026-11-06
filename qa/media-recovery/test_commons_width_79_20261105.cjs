"use strict";
const test=require("node:test"), assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {validate}=require("./validate_commons_width_79_20261105.cjs");
const original=JSON.parse(fs.readFileSync(path.join(__dirname,"commons_width_79_20261105.json"),"utf8"));
test("79 original URLs, candidate requests and strict source/rights gates",()=>assert.deepEqual(validate(original),[]));
const mutate=[["wrong domain",x=>x.rows[0].proposed_same_file_url_960="https://evil.example/img.jpg?width=960"],
["1280 not 960",x=>x.rows[0].proposed_same_file_url_960=x.rows[0].original_url],
["old width mutated",x=>x.rows[0].original_url=x.rows[0].original_url.replace("width=1280","width=1024")],
["extra candidate query",x=>x.rows[0].proposed_same_file_url_960+="&foo=bar"],
["fabricated HTTP 200",x=>x.rows[0].guest_browser_http_status=200],
["fabricated transfer bytes",x=>x.rows[0].measured_cold_transfer_before_bytes=123],
["fictional license",x=>x.rows[0].rights_license="CC0"],
["fictional copyright review",x=>x.rows[0].copyright_reuse_reviewed=true],
["unauthorized WP edit",x=>x.rows[0].wordpress_change_approved=true],
["unauthorized caching",x=>x.rows[0].local_cache_approved=true],
["unauthorized processing",x=>x.rows[0].derivative_processing_approved=true],
["unauthorized publication",x=>x.rows[0].publication_approved=true],
["no-upscale proof invented",x=>x.rows[0].no_upscale_proven=true],
["skip visual review",x=>x.rows[0].quality_review_required=false],
["wrong review queue",x=>x.rows[0].review_queue="APPROVED"],
["incorrect file identity",x=>x.rows[0].commons_file_description_page="https://commons.wikimedia.org/wiki/File:Different.jpg"],
["duplicate key",x=>x.rows[0].key=x.rows[1].key],
["missing image row",x=>x.rows.pop()],
["wrong post count",x=>x.underlying_census.affected_posts=1],
["untrusted source blob",x=>x.sources[0].git_blob_sha="0000000000000000000000000000000000000000"],
["invented 76% savings",x=>x.interpretation.measured_76_percent_wire_reduction=76],
["invented 42 broken",x=>x.interpretation.reported_42_broken="VERIFIED"],
["fictional publication",x=>x.interpretation.production_changes=1],
["fictional intrinsic geometry",x=>x.rows[0].source_intrinsic_dimensions_px=[1000,800]],
["detail classification changed",x=>x.rows[0].detail_sensitive=!x.rows[0].detail_sensitive]];
for(const [label,fn]of mutate)test("fail-closed "+label,()=>{const x=JSON.parse(JSON.stringify(original));fn(x);assert.ok(validate(x).length>0)});
