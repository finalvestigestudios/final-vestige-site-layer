"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {validate}=require("./validate_live_part01_52_20261112.cjs");
const baseline=JSON.parse(fs.readFileSync(path.join(__dirname,"live_part01_8posts_52_images_20261112.json"),"utf8"));
const clone=()=>JSON.parse(JSON.stringify(baseline));
let ok=0;function test(label,fn){fn();ok++;console.log("ok "+ok+" "+label)}
test("valid live source inventory",()=>assert.equal(validate(clone()).images,52));
const mutationCases=[
 ["source changed",d=>d.rows[0].live_src="https://wrong.example/image.jpg"],
 ["source is not HTTPS",d=>{d.rows[0].live_src="http://wrong.example/image.jpg";d.rows[0].frozen_src=d.rows[0].live_src}],
 ["source_equal forged",d=>d.rows[0].source_equal=false],
 ["ALT changed",d=>d.rows[0].live_alt="Different scene"],
 ["ALT flagged changed",d=>d.rows[0].alt_equal=false],
 ["invalid zero dimension",d=>{d.rows[0].html_width=0;d.rows[0].html_height=500}],
 ["partial dimension",d=>{d.rows[0].html_width=300;d.rows[0].html_height=null}],
 ["fabricated origin 404",d=>d.rows[0].origin_http_status=404],
 ["fabricated guest 200",d=>d.rows[0].guest_http_status=200],
 ["fabricated guest broken",d=>d.rows[0].guest_failure_confirmed=true],
 ["fabricated guest size",d=>d.rows[0].guest_natural_px=[960,640]],
 ["fabricated bytes",d=>d.rows[0].guest_encoded_wire_bytes=24576],
 ["cache authorized",d=>d.rows[0].rehost_or_cache_approved=true],
 ["WP production authorized",d=>d.rows[0].wordpress_write_approved=true],
 ["duplicate slot",d=>d.rows[1].slot=d.rows[0].slot],
 ["foreign post",d=>d.rows[1].post_id=9999],
 ["srcset invented",d=>d.rows[0].literal_srcset_present=true],
 ["post unpublished",d=>d.posts[0].status="draft"],
 ["post count inflated",d=>d.counts.posts=9],
 ["image count inflated",d=>d.counts.images=53],
 ["dimension tally false",d=>d.counts.missing_dimensions=0],
 ["source tally false",d=>d.counts.source_equal=51],
 ["reported browser broken promoted",d=>d.cohort.reported_broken_unconfirmed=0],
 ["76 percent wrongly measured",d=>d.cohort.wire_savings_76pct_measured=true],
 ["siteqa ownership revoked",d=>d.policy.siteqa_browser_owner=false],
 ["no downloads revoked",d=>d.policy.no_binary_downloads=false],
 ["worklist classifier provenance swapped",d=>d.provenance.frozen_blob="0000000000000000000000000000000000000000"],
 ["loss of candidate catalog",d=>{const r=d.rows.find(x=>x.candidate_catalogs.length);r.candidate_catalogs[0].catalog_url="invalid"}],
 ["invented rights approval",d=>{const r=d.rows.find(x=>x.candidate_catalogs.length);r.candidate_catalogs[0].item_rights_cleared=true}],
 ["invented scene proof",d=>{const r=d.rows.find(x=>x.candidate_catalogs.length);r.candidate_catalogs[0].exact_visual_match_verified=true}],
 ["upscaling plan >960",d=>{const r=d.rows.find(x=>x.candidate_catalogs.some(c=>c.conditional_960px));r.candidate_catalogs.find(c=>c.conditional_960px).conditional_960px[0]=1920}],
 ["URL with port/javascript",d=>d.rows[0].live_src="javascript:alert(1)"],
 ["tampered featured count",d=>d.posts[0].live_images=99],
];
for(const [name,mutate] of mutationCases)test("reject "+name,()=>{const d=clone();mutate(d);assert.throws(()=>validate(d))});
console.log(ok+"/"+(mutationCases.length+1)+" tests passed");
